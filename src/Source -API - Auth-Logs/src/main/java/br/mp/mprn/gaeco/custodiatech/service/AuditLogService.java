package br.mp.mprn.gaeco.custodiatech.service;

import br.mp.mprn.gaeco.custodiatech.dto.AuditAcaoTipo;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import br.mp.mprn.gaeco.custodiatech.model.auditoria.CustodiaTechLog;
import br.mp.mprn.gaeco.custodiatech.repository.auditoria.AuditLogRepository;
import io.jsonwebtoken.*;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.composite.CompositeMeterRegistry;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.util.Objects;

@Service
@Slf4j
public class AuditLogService {

    public static final String API = "custodiatech-api";
    private final AuditLogRepository repository;
    private final Counter logAuditAdd;
    private final Counter logAuditError;
    private final HttpServletRequest headers;
    private final JwtParser jwtParser;
    private CustodiaTechLog auditLog;
    private Throwable errorLog;

    private static final String[] IP_HEADER_CANDIDATES = {
            "X-Forwarded-For",
            "Proxy-Client-IP",
            "WL-Proxy-Client-IP",
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_FORWARDED",
            "HTTP_X_CLUSTER_CLIENT_IP",
            "HTTP_CLIENT_IP",
            "HTTP_FORWARDED_FOR",
            "HTTP_FORWARDED",
            "HTTP_VIA",
            "REMOTE_ADDR"
    };

    public AuditLogService(AuditLogRepository repository, CompositeMeterRegistry meterRegistry, HttpServletRequest headers, @Value("${custodiatech-api.jwt.secret}") String jwtSecret) {
        this.repository = repository;
        this.logAuditAdd = meterRegistry.counter("custodiatech.log-audit-add");
        this.logAuditError = meterRegistry.counter("custodiatech.log-audit-error");
        this.headers = headers;
        this.jwtParser = Jwts.parser().setSigningKey(jwtSecret.getBytes(StandardCharsets.UTF_8)).build();
        this.auditLog = new CustodiaTechLog();
    }

    /**
     * Persiste um log
     *
     * @param auditLog log
     * @throws CustodiaTechException error
     */
    public void save(CustodiaTechLog auditLog) throws CustodiaTechException {
        if (auditLog.getAcaoCompleta() == null || auditLog.getAcaoCompleta().isEmpty()) {
            throw new CustodiaTechException(HttpStatus.BAD_REQUEST, "Por favor, insira dados no parâmetro 'acaoCompleta'");
        }
        if (auditLog.getAcaoRealizada() == null || auditLog.getAcaoRealizada().isEmpty()) {
            throw new CustodiaTechException(HttpStatus.BAD_REQUEST, "Por favor, insira dados no parâmetro 'acaoRealizada'");
        }
        if (auditLog.getIpCliente() == null || auditLog.getIpCliente().isEmpty()) {
            throw new CustodiaTechException(HttpStatus.BAD_REQUEST, "Por favor, insira dados no parâmetro 'ipCliente'");
        }

        try {
            auditLog.setApi(API);
            auditLog.setDataInclusao(LocalDate.now());
            auditLog.setIdUsuario(this.auditLog.getIdUsuario());
            auditLog.setBrowser(this.auditLog.getBrowser());
            auditLog.setIpApi(this.auditLog.getIpApi());
            repository.save(auditLog);
            logAuditAdd.increment();
        } catch (Exception e) {
            logAuditError.increment();
            throw new CustodiaTechException(e);
        }
    }


    /**
     * Retorna o IP do cliente apartir do request
     *
     * @param request requisição
     * @return ip do cliente ou null quando não encontrado o ip
     */
    public String getClientIp(HttpServletRequest request) throws CustodiaTechException {
        String realIp;
        try {
            if (request == null) {
                if (RequestContextHolder.getRequestAttributes() == null) {
                    return null;
                }
                request = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();
            }
            realIp = InetAddress.getLocalHost().getHostAddress();
            if (!StringUtils.hasLength(realIp)) {
                return realIp;
            }
            for (String header : IP_HEADER_CANDIDATES) {
                String ipList = request.getHeader(header);
                if (ipList != null && !ipList.isEmpty() && !"unknown".equalsIgnoreCase(ipList)) {
                    return ipList.split(",")[0];
                }
            }
        } catch (Exception e) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Não foi possivel extrair o ip do cliente no request.");
        }
        return request.getRemoteAddr();
    }

    /**
     * Retorna o id do usuario apartir do token JWT
     *
     * @return id do usario
     */
    public Long getIdUsuarioToken() throws RuntimeException, CustodiaTechException {
        try {
            return Long.valueOf(getClaimFromToken("jti"));
        } catch (RuntimeException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Retorna o valor de uma Claim key
     *
     * @param claim Claim key
     * @return Claim value
     */
    private String getClaimFromToken(String claim) throws RuntimeException, CustodiaTechException {
        try {
            if (Objects.isNull(getTokenFromHeader())) {
                throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "O token JWT esta vazio.");
            }
            var claims = this.jwtParser.parseClaimsJws(getTokenFromHeader()).getBody();
            return String.valueOf(claims.get(claim));
        } catch (ExpiredJwtException | UnsupportedJwtException | MalformedJwtException | IllegalArgumentException e) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Não foi possivel decodificar a chave " + claim + " no token JWT.");
        }
    }

    /**
     * Retorna o token JWT do header
     *
     * @return token JWT
     */
    public String getTokenFromHeader() throws CustodiaTechException {
        try {
            var token = this.headers.getHeader("authorization");
            if (Objects.isNull(token)) {
                throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "O token JWT não esta presente.");
            }
            return token.replace("Bearer ", "");
        } catch (Exception e) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Não foi possivel localizar o token JWT no Header da requisição.");
        }
    }

    public AuditLogService acaoRealizada(AuditAcaoTipo acaoRealizada) {
        try {
            novoAudit();
            this.auditLog.setAcaoRealizada(acaoRealizada.name());
            return this;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private void novoAudit() {
        this.auditLog = new CustodiaTechLog();
    }

    /**
     * Recebe o valor da acao completa (texto com informação do que foi realizado) pela rotina
     *
     * @param acaoCompleta acao realizada
     * @return Builder chain
     */
    public AuditLogService acaoCompleta(String acaoCompleta) {
        try {
            this.auditLog.setAcaoCompleta(acaoCompleta);
            return this;
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public AuditLogService errorLog(Throwable e) {
        this.errorLog = e;
        return this;
    }

    public void sendLogs() throws CustodiaTechException {
        if (Objects.nonNull(this.auditLog)) {
            save(this.auditLog);
        }
        if (Objects.nonNull(this.errorLog)) {
            this.sendErrorLog();
        }
    }

    /**
     * Envia o log de error para persistencia
     */
    private void sendErrorLog() {
        try {
            log.error(this.auditLog.getAcaoCompleta(), this.errorLog);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Preenche o log
     */
    public AuditLogService parserHeadersFromLog(HttpServletRequest request, long idUsuario) throws CustodiaTechException {
        try {
            this.auditLog.setIpApi(InetAddress.getLocalHost().getHostAddress());
            this.auditLog.setBrowser(this.headers.getHeader("user-agent"));
            this.auditLog.setIpCliente(this.getClientIp(request));
            this.auditLog.setIdUsuario(idUsuario);
            return this;
        } catch (Exception e) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Não foi preencher os valores no objeto auditLog, Detalhe: " + e.getMessage());
        }
    }
}
