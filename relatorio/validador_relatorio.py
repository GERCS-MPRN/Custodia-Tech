import hashlib
import io

import qrcode
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from PyPDF2 import PdfReader, PdfWriter

def gerar_chaves_criptograficas(private_key_password):
    """
    Gera um par de chaves criptográficas (privada e pública).

    Args:
        private_key_password (str): Senha para criptografar a chave privada.

    Returns:
        dict: Um dicionário contendo a chave privada e a chave pública em formato PEM.
    """
    # Gera a chave privada
    chave_privada = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Serializa a chave privada para o formato PEM
    chave_privada_pem = chave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(private_key_password.encode())
    )

    # Gera a chave pública
    chave_publica = chave_privada.public_key()
    chave_publica_pem = chave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    #chave_publica_pem = chave_publica_pem.replace('\n', '')
        
    chaves = {'chave_privada': chave_privada_pem, 'chave_publica': chave_publica_pem}
    
    return chaves

def gerar_hash_pdf(caminho_pdf):
    """
    Gera um hash SHA-256 para validar o PDF

    Args:
        caminho_pdf (str): Caminho para o arquivo PDF.

    Returns:
        str: O hash SHA-256 do conteúdo do PDF ou uma mensagem de erro.
    """
    try:
        # Cria um buffer para armazenar o conteúdo do PDF
        buffer = io.BytesIO()
        leitor = PdfReader(caminho_pdf)
        escritor = PdfWriter()

        # Adiciona páginas
        for pagina in leitor.pages:
            escritor.add_page(pagina)

        # Escreve o PDF no buffer
        escritor.write(buffer)
        buffer.seek(0)

        # Calcula o hash diretamente do conteúdo binário do buffer
        return hashlib.sha256(buffer.read()).hexdigest()

    except Exception as e:
        return f"Ocorreu um erro ao gerar hash do pdf: {str(e)}"
    
def assinar_hash(hash_documento, chave_privada):
    """
    Gera uma assinatura digital para um hash de documento usando uma chave privada.

    Args:
        hash_documento (str): O hash do documento a ser assinado.
        chave_privada (RSAPrivateKey): A chave privada usada para assinar o hash.

    Returns:
        str: A assinatura digital em formato hexadecimal.
    """
    assinatura = chave_privada.sign(
        hash_documento.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return assinatura.hex()

def gerar_qr_code(dados_json):
    """
    Gera um QR Code a partir de dados JSON.

    Args:
        dados_json (str): Os dados JSON a serem codificados no QR Code.

    Returns:
        str: O caminho para a imagem temporária do QR Code gerado.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(dados_json)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    temp_img = 'qr_code_temp.png' 
    img.save(temp_img)
    return temp_img