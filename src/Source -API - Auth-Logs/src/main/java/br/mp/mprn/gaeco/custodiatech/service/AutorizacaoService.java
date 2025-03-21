package br.mp.mprn.gaeco.custodiatech.service;

import br.mp.mprn.gaeco.custodiatech.dto.AuditAcaoTipo;
import br.mp.mprn.gaeco.custodiatech.dto.RespostaDTO;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.model.auth.UsuarioPerfil;
import br.mp.mprn.gaeco.custodiatech.repository.auth.UsuarioPerfilRepository;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.composite.CompositeMeterRegistry;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AutorizacaoService extends GenericService{

    private final UsuarioPerfilRepository usuarioPerfilRepository;

    @Value("${custodiatech-api.grupoAcesso}")
    private String grupoAcesso;
    @Value("${custodiatech-api.version-app}")
    private String versionApp;
    @Value("${custodiatech-api.link-download}")
    private String linkDownload;


    private final Counter verificacaoAcessoOkCounter;
    private final Counter verificacaoAcessoFailCounter;

    public AutorizacaoService(UsuarioPerfilRepository usuarioPerfilRepository, AuditLogService logService, CompositeMeterRegistry meterRegistry) {
        this.usuarioPerfilRepository = usuarioPerfilRepository;
        this.logService = logService;

        this.verificacaoAcessoOkCounter = meterRegistry.counter("custodiatech.verificacao-acesso-ok");
        this.verificacaoAcessoFailCounter = meterRegistry.counter("custodiatech.verificacao-acesso-fail");
    }

    public RespostaDTO verificaAcesso() throws CustodiaTechException {
        List<UsuarioPerfil> perfisUsuario = listPorUsuario(logService.getIdUsuarioToken());
        if (!perfisUsuario.isEmpty()) {
            for (UsuarioPerfil usuario : perfisUsuario) {
                if (usuario.getPerfil().getDescricao().equals(grupoAcesso)) {
                    verificacaoAcessoOkCounter.increment();
                    logSucesso(AuditAcaoTipo.DETAIL, "Verificação de acesso do usuário de id: [" + logService.getIdUsuarioToken() + "] ao módulo CustodiaTech com acesso permitido", logService.getIdUsuarioToken());
                    return new RespostaDTO("O usuário possui acesso ao módulo Custodia Tech", true, logService.getIdUsuarioToken(), versionApp, linkDownload);
                }
            }
        }
        verificacaoAcessoFailCounter.increment();
        logSucesso(AuditAcaoTipo.DETAIL, "Verificação de acesso do usuário de id: [" + logService.getIdUsuarioToken() + "] ao módulo CustodiaTech com acesso negado", logService.getIdUsuarioToken());
        return new RespostaDTO("O usuário não possui autorização para acessar este módulo", false, logService.getIdUsuarioToken(), "", "");
    }

    public RespostaDTO verificaAcesso(long idUsuario) throws CustodiaTechException {
        List<UsuarioPerfil> perfisUsuario = listPorUsuario(idUsuario);
        if (!perfisUsuario.isEmpty()) {
            for (UsuarioPerfil usuario : perfisUsuario) {
                if (usuario.getPerfil().getDescricao().equals(grupoAcesso)) {
                    return new RespostaDTO("O usuário possui acesso ao módulo Custodia Tech", true, idUsuario, versionApp, linkDownload);
                }
            }
        }
        return new RespostaDTO("O usuário não possui autorização para acessar este módulo", false, idUsuario, "", "");
    }

    /**
     * Lista todos os perfis ao qual o usuario pertence
     * @param idUsuario
     * @return Lista de perfis por usuario
     */
    private List<UsuarioPerfil> listPorUsuario(Long idUsuario) throws CustodiaTechException {
        try {
            return usuarioPerfilRepository.findAllByUsuarioIdAndDeletadoFalse(idUsuario);
        } catch (Exception e) {
            throw new CustodiaTechException(HttpStatus.INTERNAL_SERVER_ERROR, "Não foi possível listar os registros.");
        }
    }
}

