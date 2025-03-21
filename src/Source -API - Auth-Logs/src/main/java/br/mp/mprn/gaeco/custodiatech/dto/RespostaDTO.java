package br.mp.mprn.gaeco.custodiatech.dto;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.*;

@NoArgsConstructor
@AllArgsConstructor
@ToString
@Getter
@Setter
@Builder
public class RespostaDTO {

    private String msgRetorno;
    private boolean logado;
    @JsonIgnore
    private long idUsuario;
    private String versionApp;
    private String linkDownload;
}
