package br.mp.mprn.gaeco.custodiatech.dto;

import br.mp.mprn.gaeco.custodiatech.model.auth.Usuario;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.*;

import java.util.Base64;
import java.util.Date;
import java.util.Objects;

@NoArgsConstructor
@AllArgsConstructor
@ToString
@Getter
@Setter
@Builder
public class UsuarioDTO {

    private Long id;
    private String nome;
    private String userName;
    private String apelido;
    private String unidadeOrganizacional;
    private String matricula;
    private String foto;

    @JsonFormat(pattern = "yyyy-MM-dd")
    private Date dateExpiredAcount;
    private String email;
    private boolean ativoAD;
    private boolean ativo;

    private String senha;

    public UsuarioDTO(Usuario usuario) {
        this.id = Objects.isNull(usuario.getId()) ? 0 : usuario.getId();
        this.nome = usuario.getNome();
        this.apelido = usuario.getUserName();
        this.email = usuario.getEmail();
        this.matricula = usuario.getMatricula();
        this.ativo = usuario.isAtivo();

        if (usuario.getImagem() != null) {
            this.foto = String.format("data:image/png;base64,%s", Base64.getEncoder().encodeToString(usuario.getImagem()));
        }
    }
}
