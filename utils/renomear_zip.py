import os
import re
import zipfile
from datetime import datetime

def renomear_zip(zip_file_path, metadata, nome_base_arquivo):
    """
    Renomeia o arquivo ZIP para incluir a data e hora de criação no nome do arquivo,
    substituindo a data e hora antiga.

    Args:
        zip_file_path (str): Caminho do arquivo ZIP.
        file_metadata (dict): Dicionário contendo os metadados do arquivo, incluindo 'Data de Criação'.

    Returns:
        str: Caminho do arquivo ZIP renomeado.
        Retorna None se ocorrer um erro.
    """
    # 1. Renomeia para remover o timestamp do nome (ficará "screenshot_.zip")
    diretorio_zip = os.path.dirname(zip_file_path)
    nome_base_zip = os.path.join(diretorio_zip, f"{nome_base_arquivo}.zip")
    os.rename(zip_file_path, nome_base_zip)
    print(f"Arquivo renomeado para {nome_base_zip} (timestamp removido)")

    # 2. Lê o timestamp de "Data de Criação" dos metadados e converte para o novo formato.
    data_criacao = metadata.get('Data de Criação')
    # print(f"Data de Criação: {data_criacao}")
    
    # Substitui pelos grupos reorganizados no novo formato
    padrao = r"(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2}) UTC(-\d{2})"
    novo_timestamp = re.sub(padrao, r"\1-\2-\3_\4-\5-\6_UTC\7", data_criacao)
    # print(f"Novo timestamp: {novo_timestamp}")
    
    # 3. Insere o novo timestamp no nome do zip
    nome_final_zip = os.path.join(diretorio_zip, f"{nome_base_arquivo}{novo_timestamp}.zip")
    os.rename(nome_base_zip, nome_final_zip)
    print(f"Arquivo final renomeado para {nome_final_zip}")
    
    # Atualiza os metadados se necessário (por exemplo, inserindo o novo nome do arquivo)
    metadata['Nome do Arquivo'] = os.path.basename(nome_final_zip)
    
    return metadata, nome_final_zip