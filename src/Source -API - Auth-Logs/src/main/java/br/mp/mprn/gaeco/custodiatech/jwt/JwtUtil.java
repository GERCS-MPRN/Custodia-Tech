package br.mp.mprn.gaeco.custodiatech.jwt;

import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import java.util.Date;
import java.util.Objects;

@Component
public class JwtUtil {

    @Value("${custodiatech-api.jwt.secret}")
    @Getter
    private String secret;

    @Value("${custodiatech-api.jwt.expiration-time}")
    private Long expiration;

    public String generationToken(String user, Long id, String name, String ip) throws CustodiaTechException {
        if (Objects.isNull(user) || Objects.isNull(id) || Objects.isNull(name) || Objects.isNull(ip)) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Dados para geração do token são invalidos.");
        }
        String token = Jwts.builder()
                .setSubject(user)
                .setId(Long.toString(id))
                .claim("usuario", name)
                .claim("ip", ip)
                .setExpiration(new Date(System.currentTimeMillis() + expiration))
                .signWith(SignatureAlgorithm.HS512, secret.getBytes())
                .compact();
        if (tokenIsValid(token)) {
            return token;
        } else {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "O token gerado não é válido, por favor verificar a chave do ambiente.");
        }
    }

    public boolean tokenIsValid(String token) throws CustodiaTechException {
        Claims claims = getClaims(token);
        if (claims != null) {
            String userName = claims.getSubject();
            Date expirationDate = claims.getExpiration();
            Date now = new Date(System.currentTimeMillis());
            return userName != null && expirationDate != null && now.before(expirationDate);
        }
        return false;
    }

    private Claims getClaims(String token) throws CustodiaTechException {
        try {
            return Jwts.parser().setSigningKey(secret.getBytes()).build().parseClaimsJws(token).getBody();
        } catch (Exception e) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "O token gerado não é válido, por favor verificar a chave do ambiente.");
        }
    }

}
