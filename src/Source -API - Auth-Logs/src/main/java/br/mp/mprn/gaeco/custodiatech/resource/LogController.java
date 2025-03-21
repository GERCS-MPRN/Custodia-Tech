package br.mp.mprn.gaeco.custodiatech.resource;

import br.mp.mprn.gaeco.custodiatech.model.auditoria.CustodiaTechLog;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.service.AuditLogService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@ControllerAdvice
@CrossOrigin(origins = "*")
@RequestMapping("/log")
public class LogController {

    private final AuditLogService service;

    public LogController(AuditLogService service) {
        this.service = service;
    }

    @PostMapping(produces = "application/json", consumes = "application/json")
    public ResponseEntity<?> gravaLog(@RequestBody CustodiaTechLog auditLog, HttpServletRequest request) {
        try {
            service.parserHeadersFromLog(request, service.getIdUsuarioToken());
            service.save(auditLog);
            return ResponseEntity.ok(true);
        } catch (CustodiaTechException e) {
            return ResponseEntity.status(e.getStatus()).body(e.getMessage());
        }
    }
}
