package br.mp.mprn.gaeco.custodiatech.service;

import br.mp.mprn.gaeco.custodiatech.dto.*;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.jwt.JwtUtil;
import br.mp.mprn.gaeco.custodiatech.repository.auth.UsuarioRepository;
import br.mp.mprn.gaeco.custodiatech.service.rest.AuthLDAPRestClient;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.composite.CompositeMeterRegistry;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.text.MessageFormat;
import java.util.Objects;

@Service
public class LoginService extends GenericService {

    private final UsuarioRepository usuarioRepository;
    private final AuthLDAPRestClient ldapRestClient;
    private final JwtUtil jwtUtil;


    private final Counter loginOkCounter;
    private final Counter loginFailCounter;
    private final Counter usuarioSemPermissaoCounter;
    private final Counter usuarioDesativadoCounter;
    private final AutorizacaoService autorizacaoService;

    public LoginService(UsuarioRepository usuarioRepository, AuthLDAPRestClient ldapRestClient, JwtUtil jwtUtil, AuditLogService logService,
                        CompositeMeterRegistry meterRegistry, AutorizacaoService autorizacaoService) {
        this.usuarioRepository = usuarioRepository;
        this.ldapRestClient = ldapRestClient;
        this.jwtUtil = jwtUtil;
        this.logService = logService;
        this.loginOkCounter = meterRegistry.counter("custodiatech.login-ok");
        this.loginFailCounter = meterRegistry.counter("custodiatech.login-fail");
        this.usuarioSemPermissaoCounter = meterRegistry.counter("custodiatech.usuario-sem-permissoes");
        this.usuarioDesativadoCounter = meterRegistry.counter("custodiatech.usuario-desativado");
        this.autorizacaoService = autorizacaoService;
    }

    /**
     * Rotina responsável por autenticar usuario em uma base Active Directory e
     * SGDB. Verificar através do parametro retorno se a validação foi realizada
     * com sucesso
     *
     * @author Maria Emília Eidelwein, Rivaldo Xavier
     */
    public UsuarioPermissaoDTO autentica(String login, String senha, String ip) throws CustodiaTechException {
        UsuarioPermissaoDTO permissoesUsr = new UsuarioPermissaoDTO();
        try {
            if (senha == null || senha.trim().isEmpty() || senha.trim().isBlank()) {
                permissoesUsr.setLogado(false);
                permissoesUsr.setMsgRetorno("Por favor, digite uma senha");
                return permissoesUsr;
            }
            UsuarioAD usuarioDTO = new UsuarioAD(login, senha);
            RespostaLDAPDTO respostaAD = ldapRestClient.autenticaAD(usuarioDTO);

            // Usuario encontrado no AD, verifica se ele tem permissão de acesso ao sistema
            if (respostaAD.isLogado()) {
                var list = usuarioRepository.findUsuarioByUserNameAndDeletadoFalse(login)
                        .stream()
                        .map(UsuarioDTO::new).toList();

                if (!list.isEmpty()) {
                    var usuario = list.getFirst();
                    if (respostaAD.getUsuario() != null) {
                        usuario.setDateExpiredAcount(respostaAD.getUsuario().getDateExpiredAcount());
                    }
                    if (Objects.nonNull(usuario)) {
                        usuario = list.getFirst();

                        //verifica se o usuário está no grupo de acesso
                        RespostaDTO verificacaoAcesso = autorizacaoService.verificaAcesso(usuario.getId());
                        if (!verificacaoAcesso.isLogado()) {
                            permissoesUsr.setLogado(false);
                            permissoesUsr.setMsgRetorno("Não foi possível autenticar. " + verificacaoAcesso.getMsgRetorno());
                            return permissoesUsr;
                        }

                        /* Verifica se usuário informado está desativado*/
                        if (!usuario.isAtivo()) {
                            permissoesUsr.setLogado(false);
                            String msgUsuarioDesativado = MessageFormat.format("Não foi possível autenticar. O usuário {0} está desabilitado.", login);
                            this.usuarioDesativadoCounter.increment();
                            permissoesUsr.setMsgRetorno(msgUsuarioDesativado);
                        } else {
                            String token = jwtUtil.generationToken(usuario.getMatricula(),
                                    usuario.getId(),
                                    usuario.getNome(),
                                    ip);
                            permissoesUsr.setUsuario(usuario);
                            permissoesUsr.setAccessToken("Bearer " + token);
                            permissoesUsr.setMsgRetorno("Login realizado com sucesso");
                            permissoesUsr.setLogado(true);
                            logSucesso(AuditAcaoTipo.LOGIN_OK, "Usuário de Matrícula " + permissoesUsr.getUsuario().getMatricula() + " logado com sucesso.", usuario.getId());
                            this.loginOkCounter.increment();
                            return permissoesUsr;
                        }
                    } else {
                        permissoesUsr.setLogado(false);
                        permissoesUsr.setMsgRetorno("Não foi possível autenticar. Usuário sem privilégios.");
                        this.usuarioSemPermissaoCounter.increment();
                    }
                } else { //usuario não consta na base do perdigueiro
                    permissoesUsr.setLogado(false);
                    String msgNaoConstaBase = "Não foi possível autenticar. Usuário não foi localizado";
                    permissoesUsr.setMsgRetorno(msgNaoConstaBase);
                    this.usuarioSemPermissaoCounter.increment();
                    logSucesso(AuditAcaoTipo.LOGIN_ERRO, "Usuário de Matrícula " + login + " sem acesso ao perdigueiro", 0);
                }
            } else {
                // Usuário não consta no (AD)
                permissoesUsr.setLogado(false);
                permissoesUsr.setMsgRetorno(respostaAD.getMsgRetorno());
                this.loginFailCounter.increment();
                logSucesso(AuditAcaoTipo.LOGIN_ERRO, "Usuário de Matricula " + login + " não consta no catálogo de usuários.", 0);
            }
        } catch (Exception e) {
            this.loginFailCounter.increment();
            logErro("Tentativa de login com a matrícula " + login, e, 0);
            throw new CustodiaTechException(HttpStatus.INTERNAL_SERVER_ERROR, "Não foi possível fazer o login. Detalhe: " + e.getMessage());
        }
        if (!permissoesUsr.isLogado()) {
            this.loginFailCounter.increment();

            logSucesso(AuditAcaoTipo.LOGIN_ERRO, "Erro de login com a matrícula " + login + " Detalhe : " + permissoesUsr.getMsgRetorno(), 0);
        }
        return permissoesUsr;
    }
}
