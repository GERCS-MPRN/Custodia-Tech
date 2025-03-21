package br.mp.mprn.gaeco.custodiatech.resource;

import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.service.AutorizacaoService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/autorizacao")
@CrossOrigin(origins = "*")
public class AutorizacaoController {

    private final AutorizacaoService autorizacaoService;

    public AutorizacaoController(AutorizacaoService loginService) {
        this.autorizacaoService = loginService;
    }

    @GetMapping
    public ResponseEntity<?> verificaAutorizacao() {
        try {
            return ResponseEntity.status(200).body(autorizacaoService.verificaAcesso());
        } catch (CustodiaTechException e) {
            return ResponseEntity.status(e.getStatus()).body(e.getMessage());
        }
    }

}
