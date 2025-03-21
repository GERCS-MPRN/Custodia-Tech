package br.mp.mprn.gaeco.custodiatech.model.auditoria;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDate;

@Data
@Entity
@Table(name="custodiatech_audit_log", schema="audit")
public class CustodiaTechLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "id_usuario")
    @JsonIgnore
    private Long idUsuario;
    @JsonIgnore
    private String api;
    @JsonIgnore
    private String browser;

    @Column(name = "acao_realizada")
    private String acaoRealizada;
    @Column(columnDefinition = "TEXT", name = "acao_completa")
    private String acaoCompleta;
    @Column(name = "ip_cliente")
    private String ipCliente;
    @Column(name = "ip_api")
    @JsonIgnore
    private String ipApi;

    @JsonIgnore
    @Column(name="data_inclusao", columnDefinition = "datetime default GETDATE()", insertable = false, nullable = false)
    private LocalDate dataInclusao;
}
