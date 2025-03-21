package br.mp.mprn.gaeco.custodiatech.interceptors;

import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.SignatureException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.web.servlet.AsyncHandlerInterceptor;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Date;
import java.util.Objects;
import java.util.stream.Stream;

@Slf4j
public class AuthInterceptor implements AsyncHandlerInterceptor {

    static final String HEADER_STRING = "Authorization";
    static final String TOKEN_PREFIX = "Bearer ";
    static final String URL_LOGIN = "logar";
    private final JwtParser jwtParser;

    public AuthInterceptor(String jwtSecret) {
        this.jwtParser = Jwts.parser().setSigningKey(jwtSecret.getBytes(StandardCharsets.UTF_8)).build();
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object Handler) throws IOException {
        try {
            var splitPath = request.getRequestURI().split("/");
            var isTokenJwt = Collections.list(request.getHeaderNames()).stream().anyMatch(s -> s.equalsIgnoreCase(HEADER_STRING));
            var isLoginUrl = Stream.of(splitPath).anyMatch(s -> s.equalsIgnoreCase(URL_LOGIN));
            if (!isTokenJwt && isLoginUrl) {
                String token = request.getHeader(HEADER_STRING.toLowerCase());
                response.addHeader(HEADER_STRING, token);
                return true;
            } else if (isTokenJwt) {
                String token = request.getHeader(HEADER_STRING.toLowerCase());
                if (Objects.isNull(token)) {
                    response.setStatus(HttpStatus.UNAUTHORIZED.value());
                    return false;
                }
                Claims decode = decodeToken(token);
                if (decode.getExpiration().before((new Date(System.currentTimeMillis())))) {
                    response.setStatus(HttpStatus.UNAUTHORIZED.value());
                    return false;
                }
                response.addHeader(HEADER_STRING, token);
                return true;
            } else {
                response.setStatus(HttpStatus.UNAUTHORIZED.value());
                return false;
            }
        } catch (CustodiaTechException e) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
            response.setStatus(HttpStatus.UNAUTHORIZED.value());
            return false;
        }
    }

    /**
     * Retorna os claims de um token JWT
     *
     * @param token token a se removido os claims
     * @return claims
     */
    public Claims decodeToken(String token) throws CustodiaTechException {
        try {
            return jwtParser.parseClaimsJws(token.replace(TOKEN_PREFIX, "")).getBody();
        } catch (ExpiredJwtException | UnsupportedJwtException | MalformedJwtException | SignatureException |
                 IllegalArgumentException e) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Não foi possível decodificar o token jwt.");
        }
    }
}
