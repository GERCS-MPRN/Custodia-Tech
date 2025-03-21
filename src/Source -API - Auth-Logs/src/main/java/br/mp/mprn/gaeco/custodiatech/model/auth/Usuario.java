package br.mp.mprn.gaeco.custodiatech.model.auth;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@NoArgsConstructor
@AllArgsConstructor
@ToString
@Getter
@Setter
@Builder

@Entity
@Table(schema = "login", name = "usuario")
public class Usuario implements Comparable<Usuario> {

    @Id
    @Column(name = "id_usuario")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "user_name")
    private String userName;
    private String nome;
    private String matricula;
    private String email;
    private boolean ativo;
    @JsonIgnore
    @Column(name = "cod_alfanum")
    private String codAlfanum;
    @Lob
    @JsonIgnore
    @Column(name = "foto")
    private byte[] imagem;
    @JsonIgnore
    @Column(name="deletado", columnDefinition = "BIT DEFAULT ((0))", length= 1, nullable = false)
    private boolean deletado;

    @JsonIgnore
    @Column(name="dataInserc", columnDefinition = "datetime default GETDATE()", nullable = false)
    private LocalDateTime dataInserc;

    @JsonIgnore
    @Column(name = "idUsuarioInserc")
    private Long idUsuarioInserc;

    @JsonIgnore
    @Column(name="dataMod",columnDefinition = "datetime")
    private LocalDateTime dataMod;

    @JsonIgnore
    @Column(name = "idUsuarioMod")
    private Long idUsuarioMod;

    @JsonIgnore
    @Column(name="dataDel", columnDefinition = "datetime")
    private LocalDateTime dataDel;

    @JsonIgnore
    @Column(name = "idUsuarioDel")
    private Long idUsuarioDel;

    @Override
    public int compareTo(Usuario o) {
        return this.getNome().compareTo(o.getNome());
    }
}
