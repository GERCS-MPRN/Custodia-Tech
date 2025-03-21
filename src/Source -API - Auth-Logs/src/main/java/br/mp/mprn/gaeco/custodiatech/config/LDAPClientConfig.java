package br.mp.mprn.gaeco.custodiatech.config;

import io.netty.handler.ssl.SslContextBuilder;
import io.netty.handler.ssl.util.InsecureTrustManagerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

@Configuration
public class LDAPClientConfig {

    @Value("${URL_SERVICO_AD}")
    private String auditApiBaseUrl;

    @Bean("webClientLDAP")
    public WebClient webClientAutenticacao(WebClient.Builder builder) throws RuntimeException {
        try {
            var sslContext = SslContextBuilder.forClient().trustManager(InsecureTrustManagerFactory.INSTANCE).build();
            var httpConnector = HttpClient.create().secure(t -> t.sslContext(sslContext));
            return builder
                    .baseUrl(this.auditApiBaseUrl)
                    .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                    .clientConnector(new ReactorClientHttpConnector(httpConnector))
                    .build();
        } catch (Exception e) {
            throw new RuntimeException("Erro na comunicacao com a api de consulta ao LDAP.", e);
        }
    }
}
