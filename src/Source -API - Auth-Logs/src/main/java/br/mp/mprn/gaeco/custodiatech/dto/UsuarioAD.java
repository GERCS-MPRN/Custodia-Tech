package br.mp.mprn.gaeco.custodiatech.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UsuarioAD {

    private String nome;
    private String apelido;
    private String matricula;
    private String senha;

    private boolean senhaNuncaExpira;
    private String telefone;
    private String cpf;
    private String orgao;
    private String escritorio;
    private String cargo;
    private String unidadeOrganizacional;
    private String email;


    public UsuarioAD(String login, String senha) {
        this.apelido = login;
        this.matricula = login;
        this.senha = senha;
    }
}
