package br.mp.mprn.gaeco.custodiatech.service.rest;

import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.dto.RespostaLDAPDTO;
import br.mp.mprn.gaeco.custodiatech.dto.UsuarioAD;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.composite.CompositeMeterRegistry;
import lombok.Getter;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.util.Optional;

@Service
public class AuthLDAPRestClient {

    private final WebClient webClientActiveDirectory;


    private final Counter authLdapErrorCounter;

    public AuthLDAPRestClient(@Qualifier("webClientLDAP") WebClient webClient,
                              CompositeMeterRegistry meterRegistry) {
        this.webClientActiveDirectory = webClient;
        this.authLdapErrorCounter = meterRegistry.counter("auth.auth-ldap-acess-http-error");
    }

    @Getter
    private String token;

    @Value("${URL_SERVICO_AD}")
    private String urlServico;

    /**
     * Método para acessar o serviço de autenticação via LDAP para autenticar o usuário no AD
     *
     * @param usuarioDTO
     * @return resposta LDAP
     * @throws CustodiaTechException
     */
    public RespostaLDAPDTO autenticaAD(UsuarioAD usuarioDTO) throws CustodiaTechException {
        try {
            Optional<ResponseEntity<RespostaLDAPDTO>> respostaDTO = this.webClientActiveDirectory
                    .method(HttpMethod.POST)
                    .uri(urlServico + "logar")
                    .bodyValue(usuarioDTO)
                    .retrieve()
                    .toEntity(RespostaLDAPDTO.class)
                    .blockOptional(Duration.ofSeconds(5));

            if (respostaDTO.isPresent() && respostaDTO.get().getBody().isLogado()) {
                this.token = respostaDTO.get().getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
            }
            return respostaDTO.get().getBody();
        } catch (Exception e) {
            this.authLdapErrorCounter.increment();
            throw new CustodiaTechException(HttpStatus.INTERNAL_SERVER_ERROR, e.getMessage());
        }
    }
}
