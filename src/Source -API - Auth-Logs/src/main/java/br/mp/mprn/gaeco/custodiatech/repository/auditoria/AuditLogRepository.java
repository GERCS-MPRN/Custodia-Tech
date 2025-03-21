package br.mp.mprn.gaeco.custodiatech.repository.auditoria;

import br.mp.mprn.gaeco.custodiatech.model.auditoria.CustodiaTechLog;
import org.springframework.data.repository.CrudRepository;

public interface AuditLogRepository extends CrudRepository<CustodiaTechLog, Long> {
}
