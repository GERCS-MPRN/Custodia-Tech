import json
import os

from utils.criptografia import encrypt_AES_CBC
from utils.criptografia import decrypt_AES_CBC

def save_user_data(case_directory, usuario, dados_gerais):

    lista_usuarios = []
            
    # Volta dois diretórios para encontrar o caminho correto
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(case_directory)), "CustodiaTech_User.config")
    
    if os.path.exists(json_file_path):
        with open(json_file_path, "rb") as json_file:
            encrypted_data = json_file.read()
            decrypted_data = decrypt_AES_CBC(encrypted_data)
            lista_usuarios = json.loads(decrypted_data)

    # Atualiza os dados ou adiciona um novo usuário
    atualizado = False
    for user in lista_usuarios:
        if user.get("ID") == usuario:
            # Atualiza os campos existentes
            user["Nome"] = dados_gerais['Nome do Operador']
            user["Matricula"] = dados_gerais['Matrícula do Operador']
            user["Orgao"] = dados_gerais['Orgão do Operador']
            atualizado = True
            break

    if not atualizado:
        # Cria o novo registro de usuário
        lista_usuarios.append({
            "ID": usuario,
            "Nome": dados_gerais['Nome do Operador'],
            "Matricula": dados_gerais['Matrícula do Operador'],
            "Orgao": dados_gerais['Orgão do Operador']})
 
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(lista_usuarios, json_file, indent=4)
        print("Dados salvos com sucesso no arquivo CustodiaTech_User.config.")

        # Criptografar o arquivo JSON
        with open(json_file_path, 'rb') as json_file:
            json_data = json_file.read()
            encrypted_data = encrypt_AES_CBC(json_data.decode('utf-8'))

        # Salvar o arquivo criptografado
        with open(json_file_path, 'wb') as json_file:
            json_file.write(encrypted_data)
    except Exception as e:
        print(f"Erro ao salvar os dados no arquivo JSON: {e}")


def load_user_data(case_directory, usuario, operador_nome_entry, operador_matricula_entry, operador_orgao_entry):
    
    lista_usuarios = []

    # Volta dois diretórios para encontrar o arquivo JSON correto
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(case_directory)), "CustodiaTech_User.config")

    if os.path.exists(json_file_path):
        with open(json_file_path, "rb") as json_file:
            encrypted_data = json_file.read()
            decrypted_data = decrypt_AES_CBC(encrypted_data)
            lista_usuarios = json.loads(decrypted_data)

    # Busca o usuário e preenche os campos
    for user in lista_usuarios:
        if user.get("ID") == usuario:
            operador_nome_entry.delete(0, "end")
            operador_nome_entry.insert(0, user.get("Nome", ""))

            operador_matricula_entry.delete(0, "end")
            operador_matricula_entry.insert(0, user.get("Matricula", ""))

            operador_orgao_entry.delete(0, "end")
            operador_orgao_entry.insert(0, user.get("Orgao", ""))

            print(f"Dados do usuário {usuario} carregados com sucesso.")
            return

    print(f"Usuário {usuario} não encontrado no JSON.")

def salvar_dados_json(dados_completos, case_directory):
    """ 
    Salva os dados completos em um arquivo JSON CustodiaTech.config e o criptografa.
    
    Args:
        dados_completos (dict): Os dados a serem salvos no arquivo JSON.
        case_directory (str): O diretório onde o arquivo JSON será salvo.
    """
    if case_directory != '':
        # Caminho do arquivo JSON
        json_file_path = os.path.join(case_directory, "CustodiaTech.config")

        # Salvar os dados no arquivo JSON
        try:
            with open(json_file_path, 'w') as json_file:
                json.dump(dados_completos, json_file, indent=4)
            print("Dados salvos com sucesso no arquivo CustodiaTech.config.")

            # Criptografar o arquivo JSON
            with open(json_file_path, 'rb') as json_file:
                json_data = json_file.read()
                encrypted_data = encrypt_AES_CBC(json_data.decode('utf-8'))

            # Salvar o arquivo criptografado
            with open(json_file_path, 'wb') as json_file:
                json_file.write(encrypted_data)

        except Exception as e:
            print(f"Erro ao salvar os dados no arquivo JSON: {e}")