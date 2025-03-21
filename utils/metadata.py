import hashlib
import os
from datetime import datetime

def calculate_hash(file_path, algorithms=['md5', 'sha1', 'sha256']):
    """
    Calcula o hash de um arquivo usando algoritmos especificados.

    Parâmetros:
    file_path (str): O caminho do arquivo para o qual o hash será calculado.
    algorithms (list): Lista de algoritmos de hash a serem utilizados (padrão: ['md5', 'sha1', 'sha256']).

    Retorna:
    dict: Um dicionário contendo os hashes calculados para cada algoritmo especificado.
          Retorna None se ocorrer um erro ao ler o arquivo.
    """
    results = {}
    for algorithm in algorithms:
        hash_func = hashlib.new(algorithm)
        try:
            with open(file_path, 'rb') as file:
                while chunk := file.read(8192):
                    hash_func.update(chunk)
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            return None
        results[algorithm] = hash_func.hexdigest()
    return results

def get_file_metadata(file_path):
    """
    Obtém metadados de um arquivo, como nome, tamanho e data de modificação.

    Parâmetros:
    file_path (str): O caminho do arquivo para o qual os metadados serão obtidos.

    Retorna:
    dict: Um dicionário contendo os metadados do arquivo.
          Retorna um dicionário vazio se ocorrer um erro ao obter os metadados.
    """
    stat_info = os.stat(file_path)
    metadata = {}
    try:
        file_stats = os.stat(file_path)
        metadata['Nome do Arquivo'] = os.path.basename(file_path)
        metadata['Tamanho (bytes)'] = file_stats.st_size
        metadata['Data de Criação'] = datetime.fromtimestamp(stat_info.st_ctime).strftime('%d/%m/%Y %H:%M:%S')
    except Exception as e:
        print(f"Erro ao obter metadados do arquivo: {e}")
    return metadata