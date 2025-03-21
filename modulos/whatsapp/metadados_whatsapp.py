import os
import re

from utils.metadata import calculate_hash, get_file_metadata


def metadados_whatsapp(case_directory, file_data_whatsapp):

        # Verifica se o diretório existe
        if not os.path.exists(case_directory):
            print(f"O diretório '{case_directory}' não existe.")
            return file_data_whatsapp
        
        pasta_whatsapp = os.path.join(case_directory, "Whatsapp")
        
        # Itera sobre os arquivos no diretório
        for file_name in os.listdir(pasta_whatsapp):
            # Verifica se o arquivo é um .zip e começa com "Whatsapp_"
            if re.match(r"^\d{3}_Whatsapp_", file_name) and file_name.endswith(".zip"):
                arquivozip = os.path.join(pasta_whatsapp, file_name)

                # Calcula os hashes do arquivo
                hashes = calculate_hash(arquivozip, algorithms=[
                                        'md5', 'sha1', 'sha256'])

                # Obtém os metadados do arquivo
                metadata = get_file_metadata(arquivozip)

                # Adiciona as informações do arquivo à lista
                file_data_whatsapp.append({
                    'nome_do_arquivo': file_name,
                    'hashes': hashes,
                    'metadata': metadata
                })

        return file_data_whatsapp