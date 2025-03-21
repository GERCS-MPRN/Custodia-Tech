import os
import tempfile


def limpar_relatorios_temp():
    try:
        temp_dir = tempfile.gettempdir()
        for arquivo in os.listdir(temp_dir):
            if arquivo.startswith("Relatório de evidência(s)"):
                caminho_arquivo = os.path.join(temp_dir, arquivo)
                try:
                    os.remove(caminho_arquivo)
                    print(f"Arquivo temporário removido: {arquivo}")
                except Exception as e:
                    print(f"Erro ao remover arquivo temporário {arquivo}: {e}")
    except Exception as e:
        print(f"Erro ao limpar diretório temporário: {e}")