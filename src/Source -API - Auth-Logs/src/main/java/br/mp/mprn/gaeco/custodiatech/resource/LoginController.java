package br.mp.mprn.gaeco.custodiatech.resource;

import br.mp.mprn.gaeco.custodiatech.dto.RespostaDTO;
import br.mp.mprn.gaeco.custodiatech.dto.UsuarioModel;
import br.mp.mprn.gaeco.custodiatech.dto.UsuarioPermissaoDTO;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.service.AuditLogService;
import br.mp.mprn.gaeco.custodiatech.service.LoginService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/logar")
@CrossOrigin(origins = "*")
public class LoginController {

    private final LoginService loginService;
    private final AuditLogService auditService;
    @Value("${custodiatech-api.version-app}")
    private String versionApp;
    @Value("${custodiatech-api.link-download}")
    private String linkDownload;

    public LoginController(LoginService loginService, AuditLogService auditService) {
        this.loginService = loginService;
        this.auditService = auditService;
    }

    @PostMapping
    public ResponseEntity<?> login(@RequestBody UsuarioModel usuario, HttpServletRequest request) {
        try {
            UsuarioPermissaoDTO autentica = loginService.autentica(usuario.getLogin(), usuario.getSenha(), auditService.getClientIp(request));
            HttpHeaders headers = new HttpHeaders();
            RespostaDTO respostaDTO;
            if (autentica.isLogado()) {
                headers.add(HttpHeaders.AUTHORIZATION, autentica.getAccessToken());
                headers.add("Access-Control-Allow-Headers", "*");
                headers.add("Access-Control-Expose-Headers", "Location, Authorization");
                respostaDTO = new RespostaDTO(autentica.getMsgRetorno(), autentica.isLogado(), autentica.getUsuario().getId(), versionApp, linkDownload);
            } else {
                respostaDTO = new RespostaDTO(autentica.getMsgRetorno(), autentica.isLogado(), 0L, "", "");
            }
            return ResponseEntity.status(200).headers(headers).body(respostaDTO);
        } catch (CustodiaTechException e) {
            return ResponseEntity.status(e.getStatus()).body(e.getMessage());
        }
    }

}
