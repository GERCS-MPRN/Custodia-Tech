package br.mp.mprn.gaeco.custodiatech.dto;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.*;

@NoArgsConstructor
@AllArgsConstructor
@ToString
@Getter
@Setter
@Builder
public class RespostaLDAPDTO {

    private String msgRetorno;
    private boolean logado;

    private UsuarioDTO usuario;

    @JsonIgnore
    private String ip;
}
