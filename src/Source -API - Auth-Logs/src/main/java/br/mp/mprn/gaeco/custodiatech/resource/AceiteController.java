package br.mp.mprn.gaeco.custodiatech.resource;

import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.service.AceiteTermoService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/aceite")
@CrossOrigin(origins = "*")
public class AceiteController {

    private final AceiteTermoService service;

    public AceiteController(AceiteTermoService aceiteTermoService) {
        this.service = aceiteTermoService;
    }

    @PostMapping
    public ResponseEntity<?> aceitarTermo() {
        try {
            return ResponseEntity.status(200).body(service.aceitarTermo());
        } catch (CustodiaTechException e) {
            return ResponseEntity.status(e.getStatus()).body(e.getMessage());
        }
    }

    @GetMapping
    public ResponseEntity<?> usuarioAceitou() {
        try {
            return ResponseEntity.status(200).body(service.isUsuarioAceite());
        } catch (CustodiaTechException e) {
            return ResponseEntity.status(e.getStatus()).body(e.getMessage());
        }
    }

}
