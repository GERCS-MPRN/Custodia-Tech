package br.mp.mprn.gaeco.custodiatech.service;

import br.mp.mprn.gaeco.custodiatech.dto.AuditAcaoTipo;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.model.auth.AceiteTermo;
import br.mp.mprn.gaeco.custodiatech.repository.auth.AceiteTermoRepository;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.composite.CompositeMeterRegistry;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
public class AceiteTermoService extends GenericService {

    private final AceiteTermoRepository repository;
    private final Counter aceiteOkCounter;
    private final Counter aceiteFailCounter;


    public AceiteTermoService(AceiteTermoRepository repository, AuditLogService logService, CompositeMeterRegistry meterRegistry) {
        this.repository = repository;
        this.logService = logService;

        this.aceiteOkCounter = meterRegistry.counter("custodiatech.aceite-termo-ok");
        this.aceiteFailCounter = meterRegistry.counter("custodiatech.aceite-termo-fail");
    }

    public boolean aceitarTermo() throws CustodiaTechException {
        try {
            AceiteTermo aceiteTermo = new AceiteTermo();
            aceiteTermo.setDataAceite(LocalDateTime.now());
            long idUsuario = logService.getIdUsuarioToken();
            aceiteTermo.setIdUsuarioAceite(idUsuario);
            aceiteTermo.setModulo("custodiatech");

            repository.save(aceiteTermo);
            logSucesso(AuditAcaoTipo.ACEITE_TERMO, "Usuário de id: [" + idUsuario + "] aceitou o termo de uso do módulo CustodiaTech", idUsuario);
            aceiteOkCounter.increment();
            return true;
        } catch (Exception e) {
            aceiteFailCounter.increment();
            logErro("Ocorreu um erro ao aceitar o termo do módulo CustodiaTech", e, logService.getIdUsuarioToken());
            return false;
        }
    }

    public boolean isUsuarioAceite() throws CustodiaTechException {
        Optional<AceiteTermo> aceiteTermo = repository.findFirstByIdUsuarioAceiteAndModulo(logService.getIdUsuarioToken(), "custodiatech");
        return aceiteTermo.isPresent();
    }
}
