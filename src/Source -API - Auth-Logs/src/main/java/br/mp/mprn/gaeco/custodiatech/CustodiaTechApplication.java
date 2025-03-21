package br.mp.mprn.gaeco.custodiatech;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class CustodiaTechApplication {

    public static void main(String[] args) {
        SpringApplication.run(CustodiaTechApplication.class, args);
        System.out.println("CUSTODIATECH API INICIADO COM SUCESSO!");
    }

}
