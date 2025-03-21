package br.mp.mprn.gaeco.custodiatech.service;

import br.mp.mprn.gaeco.custodiatech.dto.AuditAcaoTipo;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import jakarta.servlet.http.HttpServletRequest;

public abstract class GenericService {

    protected AuditLogService logService;
    private HttpServletRequest headers;

    protected void logErro(String mensagem, Throwable e, long idUsuario) {
        try {
            logService.acaoRealizada(AuditAcaoTipo.FAIL)
                    .parserHeadersFromLog(headers, idUsuario)
                    .acaoCompleta(mensagem)
                    .errorLog(e)
                    .sendLogs();
        } catch (CustodiaTechException ex) {
            throw new RuntimeException(ex);
        }
    }

    protected void logSucesso(AuditAcaoTipo tipo, String mensagem, long idUsuario) {
        try {
            logService.acaoRealizada(tipo)
                    .parserHeadersFromLog(headers, idUsuario)
                    .acaoCompleta(mensagem)
                    .sendLogs();
        } catch (CustodiaTechException e) {
            throw new RuntimeException(e);
        }
    }
}
