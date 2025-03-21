package br.mp.mprn.gaeco.custodiatech.dto;

import lombok.*;

import java.io.Serializable;

@NoArgsConstructor
@AllArgsConstructor
@ToString
@EqualsAndHashCode
@Getter
@Setter
@Builder
public class UsuarioPermissaoDTO implements Serializable {

    private UsuarioDTO usuario;
    private boolean logado;
    private String msgRetorno;
    private boolean passwordExpired;
    private String accessToken;
}
