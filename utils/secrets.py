import os
import binascii

# Gera 32 bytes para a chave AES (256 bits)
AES_KEY = binascii.hexlify(os.urandom(32)).decode('utf-8')
# Gera 16 bytes para o IV (128 bits)
AES_IV = binascii.hexlify(os.urandom(16)).decode('utf-8')

print("AES_KEY:", AES_KEY)
print("AES_IV:", AES_IV)