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
@Table(schema = "login", name = "aceite_termo")
public class AceiteTermo {

    @Id
    @Column(name = "id_aceite_termo")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String modulo;

    @JsonIgnore
    @Column(name="data_aceite", columnDefinition = "datetime default GETDATE()", nullable = false)
    private LocalDateTime dataAceite;

    @Column(name = "id_usuario_aceite")
    private Long idUsuarioAceite;

}
