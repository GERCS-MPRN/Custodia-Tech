import os
import re
import sys
from dotenv import load_dotenv
from pathlib import Path

class EnvManager:
    @staticmethod
    def get_base_path():
        """
        Obtém o caminho base da aplicação, seja em desenvolvimento ou no executável
        """
        if getattr(sys, 'frozen', False):
            # Se estiver executando como executável
            return Path(sys._MEIPASS)
        else:
            # Se estiver executando em desenvolvimento
            return Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @staticmethod
    def get_env(key, default=None):
        """
        Obtém uma variável de ambiente sempre atualizada
        """
        # Recarrega o .env antes de cada leitura
        env_path = EnvManager.get_base_path() / '.env'
        load_dotenv(env_path, override=True)
        
        value = os.getenv(key)
        if value and value.startswith("'") and value.endswith("'"):
            value = value[1:-1]  # Remove as aspas simples
        value = value.replace('–', '-') if value else value  # Substitui o caractere en dash por dash
        return value if value is not None else default
    
    @staticmethod
    def atualizar_env(key, value):
        """
        Atualiza ou adiciona uma variável no arquivo .env.

        Args:
            key (str): O nome da variável de ambiente.
            value (str): O novo valor para a variável.
        """
        env_path = EnvManager.get_base_path() / '.env'
        with open(env_path, 'r+') as f:
            content = f.read()
            
            # Cria um regex para encontrar a linha que contem a variável
            pattern = re.compile(rf"^{key}\s*=\s*(.+)$", re.MULTILINE)

            # Se a variável já existe
            if pattern.search(content):
                # Substitui o valor existente
                new_content = pattern.sub(f"{key} = '{value}'", content)
            else:
                # Adiciona a nova variável ao final do arquivo
                new_content = content + f"\n{key} = '{value}'"
            
            # Volta para o início do arquivo
            f.seek(0)
            # Escreve o novo conteúdo
            f.write(new_content)
            # Trunca o restante do arquivo para remover conteúdos antigos
            f.truncate()
            
            # Recarrega as variáveis de ambiente
            reload_env()

    @property
    def CTLOGO(self):
        return self.get_env('CTLOGO')
    
    @property
    def ORGAO(self):
        return self.get_env('ORGAO')
    
    @property
    def UNIDADE(self):
        return self.get_env('UNIDADE')
    
    @property
    def NUCLEO(self):
        return self.get_env('NUCLEO')
    
    @property
    def ENDERECO_TELEFONE(self):
        return self.get_env('ENDERECO_TELEFONE')
    
    @property
    def SITE_VALIDACAO(self):
        return self.get_env('SITE_VALIDACAO')
    
    @property
    def EMISSOR_RELATORIO(self):
        return self.get_env('EMISSOR_RELATORIO')
    
    @property
    def PRIMEIRO_LOGIN(self):
        return self.get_env('PRIMEIRO_LOGIN')

# Criar uma instância única do gerenciador
env = EnvManager()

def reload_env():
    """
    Recarrega as variáveis de ambiente do arquivo .env
    """
    env_path = EnvManager.get_base_path() / '.env'
    # Limpa as variáveis de ambiente existentes
    for key in list(os.environ.keys()):
        if key in ['CTLOGO','ORGAO', 'UNIDADE', 'NUCLEO', 'ENDERECO_TELEFONE']:
            del os.environ[key]
    
    # Recarrega o arquivo .env
    load_dotenv(env_path, override=True)
    
    # Atualiza as variáveis globais
    global CTLOGO, ORGAO, UNIDADE, NUCLEO, ENDERECO_TELEFONE, SITE_VALIDACAO, EMISSOR_RELATORIO
    CTLOGO = env.CTLOGO
    ORGAO = env.ORGAO
    UNIDADE = env.UNIDADE
    NUCLEO = env.NUCLEO
    ENDERECO_TELEFONE = env.ENDERECO_TELEFONE
    SITE_VALIDACAO = env.SITE_VALIDACAO
    EMISSOR_RELATORIO = env.EMISSOR_RELATORIO
    PRIMEIRO_LOGIN = env.PRIMEIRO_LOGIN

def hex_to_bytes(hex_str):
    """
    Converte uma string hexadecimal em bytes
    
    Args:
        hex_str (str): String hexadecimal
        
    Returns:
        bytes: Bytes correspondentes à string hexadecimal
    """
    try:
        return bytes.fromhex(hex_str)
    except ValueError as e:
        raise ValueError(f"Erro ao converter string hexadecimal: {e}")

def validate_aes_parameters(key, iv):
    """
    Valida os parâmetros AES
    
    Args:
        key (bytes): Chave AES
        iv (bytes): Vetor de Inicialização
        
    Raises:
        ValueError: Se os parâmetros forem inválidos
    """
    valid_key_sizes = [16, 24, 32]  # 128, 192, 256 bits
    key_size = len(key)
    iv_size = len(iv)
    
    if key_size not in valid_key_sizes:
        raise ValueError(
            f"Tamanho da chave AES inválido: {key_size * 8} bits. "
            f"Valores permitidos: {[size * 8 for size in valid_key_sizes]} bits"
        )
    
    if iv_size != 16:  # 128 bits
        raise ValueError(
            f"Tamanho do IV inválido: {iv_size * 8} bits. "
            "O IV deve ter exatamente 128 bits (16 bytes)"
        )
        
# HEADER PDF
CTLOGO = env.CTLOGO
ORGAO = env.ORGAO
UNIDADE = env.UNIDADE
NUCLEO = env.NUCLEO
ENDERECO_TELEFONE = env.ENDERECO_TELEFONE
SITE_VALIDACAO = env.SITE_VALIDACAO
EMISSOR_RELATORIO = env.EMISSOR_RELATORIO


PRIMEIRO_LOGIN = env.PRIMEIRO_LOGIN

# APIs
API_LOGIN = env.get_env('API_LOGIN')
API_LOGIN_HOMOLOGACAO = env.get_env('API_LOGIN_HOMOLOGACAO')
API_AUTORIZACAO = env.get_env('API_AUTORIZACAO')
API_AUTORIZACAO_HOMOLOGACAO = env.get_env('API_AUTORIZACAO_HOMOLOGACAO')
API_LOG = env.get_env('API_LOG')
API_LOG_HOMOLOGACAO = env.get_env('API_LOG_HOMOLOGACAO')

# Chaves de API
YOUTUBE_API_KEY = env.get_env('YOUTUBE_API_KEY')

# Criptografia
AES_KEY = hex_to_bytes(env.get_env('AES_KEY')) if env.get_env('AES_KEY') else None
AES_IV = hex_to_bytes(env.get_env('AES_IV')) if env.get_env('AES_IV') else None

# Validar parâmetros AES
if AES_KEY is not None and AES_IV is not None:
    validate_aes_parameters(AES_KEY, AES_IV)