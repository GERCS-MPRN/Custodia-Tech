package br.mp.mprn.gaeco.custodiatech.dto;

import lombok.*;

@NoArgsConstructor
@AllArgsConstructor
@ToString
@Getter
@Setter
@Builder
public class UsuarioModel {

    private String login;
    private String senha;

}
