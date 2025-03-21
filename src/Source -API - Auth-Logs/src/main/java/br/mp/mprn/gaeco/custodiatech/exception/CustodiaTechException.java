package br.mp.mprn.gaeco.custodiatech.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;

public class CustodiaTechException extends Exception {

    @Getter
    private HttpStatus status;

    public CustodiaTechException(String message) {
        super(message);
    }

    public CustodiaTechException(String message, Throwable cause) {
        super(message, cause);
    }

    public CustodiaTechException(Throwable cause) {
        super(cause);
    }

    public CustodiaTechException(String message, Throwable cause, boolean enableSuppression, boolean writableStackTrace) {
        super(message, cause, enableSuppression, writableStackTrace);
    }

    public CustodiaTechException(HttpStatus status, String message) {
        super(message);
        this.status = status;
    }
}
