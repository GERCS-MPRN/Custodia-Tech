package br.mp.mprn.gaeco.custodiatech.model.auth;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.Hibernate;

import java.time.LocalDateTime;
import java.util.Objects;

@NoArgsConstructor
@AllArgsConstructor
@Builder
@Getter
@Setter
@ToString
@Entity
@Table(schema = "login", name = "perfil")
public class Perfil {

    @Id
    @Column(name = "id_perfil")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String descricao;

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
        Perfil perfil = (Perfil) o;
        return id != null && Objects.equals(id, perfil.id);
    }

}
