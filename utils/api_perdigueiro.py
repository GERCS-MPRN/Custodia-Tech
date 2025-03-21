import json
import os
import socket
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.ttk import Style

import requests

from utils.atualizador import verificar_versao
from utils.env_manager import (API_AUTORIZACAO, API_AUTORIZACAO_HOMOLOGACAO,
                               API_LOG, API_LOG_HOMOLOGACAO, API_LOGIN,
                               API_LOGIN_HOMOLOGACAO)

# Variável global para sinalizar o encerramento
stop_thread = False

co0 = "#f0f3f5"  # Preta / black
co1 = "#feffff"  # branca / white
co2 = "#3fb5a3"  # verde / green
co3 = "#38576b"  # valor / value
co4 = "#403d3d"  # letra / letters

def get_ip_publico():
    """
    Obtém o endereço IP público do usuário.

    Returns:
        str: O endereço IP público como uma string. Retorna uma string vazia em caso de falha.
    """
    try:
        ip_publico = requests.get('https://api.ipify.org/').text
    except:
        ip_publico = ''
    return ip_publico

def get_ip_local():
    return socket.gethostbyname(socket.gethostname())

def logar(login, senha, versao_usuario, janela_login, icone_custodia):
    """
    Realiza o login do usuário na aplicação.

    Args:
        login (str): A matricula do usuário para login.
        senha (str): A senha do usuário.
        versao_usuario (str): A versão da aplicação que o usuário está utilizando.
        janela_login (tk.Tk): A janela de login da aplicação.

    Returns:
        bool: Retorna True se o login for bem-sucedido, caso contrário, False.
    """
    global bearer_token
    
    response_data_logar = requests.post(
        API_LOGIN_HOMOLOGACAO, 
        json={"login": login, "senha": senha}, 
        verify=False
    )
    
    # print(f"Resposta da API: {response_data_logar}")
    # print(f"Resposta da API JSON: {response_data_logar.json()}")
    
    logon = response_data_logar.json()['logado']
    versao_atual = response_data_logar.json()['versionApp']
    link_download = response_data_logar.json()['linkDownload']
    
    if not logon:
        return logon
    else:
        bearer_token = response_data_logar.headers['Authorization']
        if versao_usuario != versao_atual:
            if verificar_versao(link_download, bearer_token, janela_login, icone_custodia):
                # Se verificar_versao retornar True, significa que o instalador foi executado
                # e o programa deve ser encerrado
                os._exit(0)
        else:
            messagebox.showinfo('Sucesso no logon!', f'Seja bem-vindo, {login}.')
        
        return logon
    
def autorizar():
    """
    Autoriza o usuário com o token Bearer.

    Returns:
        dict: Os dados da resposta da API de autorização.
    """
    global bearer_token
    header = {'Authorization': f'Bearer {bearer_token}'}
    response_data_autorizacao = requests.get(API_AUTORIZACAO_HOMOLOGACAO, headers=header, verify=False)
    return response_data_autorizacao

def gravar_log(acao_realizada, acao_completa, ip):
    """
    Grava uma ação no log do sistema.

    Args:
        acao_realizada (str): Descrição curta da ação realizada.
        acao_completa (str): Descrição detalhada da ação realizada.
        ip (str): O endereço IP do cliente.

    Returns:
        dict: Os dados da resposta da API após o registro do log.
    """
    global bearer_token
    header = {'Authorization': f'Bearer {bearer_token}'}
    response_data_log = requests.post(
        API_LOG_HOMOLOGACAO, 
        json={
            "acaoRealizada": acao_realizada,
            "acaoCompleta": acao_completa,
            "ipCliente": ip
        }, 
        headers=header, 
        verify=False
    )
    data = {
        "acaoRealizada": acao_realizada,
        "acaoCompleta": acao_completa,
        "ipCliente": ip
    }
    print(f"JSON enviado para a API: {json.dumps(data, indent=4)}")
    return response_data_log.json()

def registrar_acao(acao_realizada, acao_completa, usuario=None):
    """
    Registra uma ação no log do sistema.

    Args:
        acao_realizada (str): Descrição curta da ação.
        acao_completa (str): Descrição detalhada da ação.
        usuario (str, optional): Nome do usuário que realizou a ação.
    """
    gravar_log(acao_realizada, acao_completa, get_ip_publico()+' / '+get_ip_local())

