package br.mp.mprn.gaeco.custodiatech.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class AppDownload {

	private String nomeArquivo;
	private byte[] arquivo;

}
