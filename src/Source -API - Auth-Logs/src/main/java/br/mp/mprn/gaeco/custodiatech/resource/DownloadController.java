package br.mp.mprn.gaeco.custodiatech.resource;

import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.service.DownloadService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/download")
@CrossOrigin(origins = "*")
public class DownloadController {

    private final DownloadService service;

    public DownloadController(DownloadService downloadService) {
        this.service = downloadService;
    }

    @GetMapping
    public ResponseEntity<?> realizarDownloadAplicativo() {
        try {
            return ResponseEntity.status(200).body(service.download());
        } catch (CustodiaTechException e) {
            return ResponseEntity.status(e.getStatus()).body(e.getMessage());
        }
    }

}
