package br.mp.mprn.gaeco.custodiatech.model.auth;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.Hibernate;

import java.time.LocalDateTime;
import java.util.Objects;

@NoArgsConstructor
@AllArgsConstructor
@ToString
@Getter
@Setter
@Builder
@Entity
@Table(schema = "login", name = "usuario_perfil")
public class UsuarioPerfil {

    @Id
    @Column(name = "id_usuario_perfil")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "usuario_id")
    private Usuario usuario;

    @ManyToOne
    @JoinColumn(name = "perfil_id")
    private Perfil perfil;

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
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || Hibernate.getClass(this) != Hibernate.getClass(o)) return false;
        UsuarioPerfil that = (UsuarioPerfil) o;
        return Objects.equals(id, that.id);
    }

}
