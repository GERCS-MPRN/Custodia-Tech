from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from utils.env_manager import AES_KEY, AES_IV

def encrypt_AES_CBC(data):
    """ 
    Criptografa os dados usando o algoritmo AES em modo CBC.
    
    Args:
        data (str): Os dados a serem criptografados.
    
    Returns:
        bytes: Os dados criptografados.
    """
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode('utf-8'))
    padded_data += padder.finalize()

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext

def decrypt_AES_CBC(ciphertext):
    """ 
    Descriptografa os dados criptografados usando o algoritmo AES em modo CBC.
    
    Args:
        ciphertext (bytes): Os dados criptografados a serem descriptografados.
    
    Returns:
        str: Os dados descriptografados.
    """
    decryptor = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend()).decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data)
    unpadded_data += unpadder.finalize()
    return unpadded_data.decode('utf-8')