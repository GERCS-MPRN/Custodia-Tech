package br.mp.mprn.gaeco.custodiatech.service;

import br.mp.mprn.gaeco.custodiatech.dto.AppDownload;
import br.mp.mprn.gaeco.custodiatech.dto.AuditAcaoTipo;
import br.mp.mprn.gaeco.custodiatech.dto.RespostaDTO;
import br.mp.mprn.gaeco.custodiatech.exception.CustodiaTechException;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.composite.CompositeMeterRegistry;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileInputStream;
import java.util.Base64;

@Service
public class DownloadService extends GenericService {

    private final Counter downloadOkCounter;
    private final Counter downloadFailCounter;

    private final AceiteTermoService aceiteTermoService;
    private final AutorizacaoService autorizacaoService;

    public DownloadService(AuditLogService logService, CompositeMeterRegistry meterRegistry, AceiteTermoService aceiteTermoService, AutorizacaoService autorizacaoService) {
        this.aceiteTermoService = aceiteTermoService;
        this.autorizacaoService = autorizacaoService;
        this.logService = logService;

        this.downloadOkCounter = meterRegistry.counter("custodiatech.download-ok");
        this.downloadFailCounter = meterRegistry.counter("custodiatech.download-fail");
    }

    public AppDownload download() throws CustodiaTechException {

        RespostaDTO respostaDTO = autorizacaoService.verificaAcesso();
        if (!respostaDTO.isLogado()) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Acesso negado, o seu usuário não possui permissão para realizar o download.");
        }

        if (!aceiteTermoService.isUsuarioAceite()) {
            throw new CustodiaTechException(HttpStatus.UNAUTHORIZED, "Não é possível realizar o download do aplicativo, pois é preciso aceitar o termo.");
        }

        try {

            File arquivo = new File("/app/file/CustodiaTechApp.zip");
            FileInputStream fis = new FileInputStream(arquivo);
            byte[] arrayBytes = new byte[(int) arquivo.length()];
            fis.read(arrayBytes);
            fis.close();

            AppDownload appDownload = new AppDownload();
            appDownload.setNomeArquivo(arquivo.getName());
            appDownload.setArquivo(arrayBytes);
            logSucesso(AuditAcaoTipo.DOWNLOAD, "Download do app CustodiaTech realizado pelo usuário de id: [" + logService.getIdUsuarioToken() + "]", logService.getIdUsuarioToken());
            downloadOkCounter.increment();
            return appDownload;
        } catch (Exception e) {
            downloadFailCounter.increment();
            logErro("Ocorreu um erro ao realizar o download do aplicativo Custodia Tech", e, logService.getIdUsuarioToken());
            throw new CustodiaTechException(HttpStatus.INTERNAL_SERVER_ERROR, "Ocorreu um erro ao realizar o download do aplicativo Custodia Tech");
        }
    }
}
