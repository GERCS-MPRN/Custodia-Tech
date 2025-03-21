import base64
import json
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import messagebox, ttk

import requests


def verificar_conexao(progress_bar, botao_download, label, stop_progress):
    while True:
        try:
            # Tente fazer uma requisição simples para verificar a conexão
            response = requests.get("http://www.google.com", timeout=5)
            if response.status_code == 200:
                # Conexão bem-sucedida, continue verificando
                time.sleep(3)
            else:
                # Se a resposta não for 200, interrompa a verificação
                break
        except requests.exceptions.RequestException:
            # Se houver um erro, interrompa a verificação
            break

    # Se a verificação falhar, reative o botão e atualize o label
    # botao_download.config(state=tk.NORMAL, bg="red")
    label.config(text="Sem conexão de internet.\n Verifique sua conexão e tente o download novamente em instantes!")
    
    # Interrompe a thread de progresso
    # progress_bar['value'] = 0  # Reseta a barra de progresso
    # stop_progress.set()  # Sinaliza para parar a thread de progresso

# Função para verificar a versão do programa
def verificar_versao(link_download, token, janela_login, icone_custodia):
    global stop_thread
    stop_thread = False
    
    # Criar uma nova janela de aviso
    janela_atualizacao = tk.Toplevel(janela_login)
    janela_atualizacao.title("CustodiaTech - Atualização necessária")
    
    # Bloqueia a janela de login
    janela_login.withdraw()  # Oculta a janela de login
    
    janela_atualizacao.iconbitmap(icone_custodia)  # Usar o caminho correto do ícone
    
    # Defina a largura e altura da janela
    largura_janela = 400  # Defina a largura desejada
    altura_janela = 100   # Defina a altura desejada

    # Obtém a largura e altura da tela
    largura_tela = janela_atualizacao.winfo_screenwidth()
    altura_tela = janela_atualizacao.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    pos_x = (largura_tela // 2) - (largura_janela // 2)
    pos_y = (altura_tela // 2) - (altura_janela // 2)

    # Define a geometria da janela
    janela_atualizacao.geometry(f'{largura_janela}x{altura_janela}+{pos_x}+{pos_y}')

    label = tk.Label(janela_atualizacao, text=f"Uma nova versão do CustodiaTech está disponível.\nAtualize o programa clicando em Download.")
    label.pack(pady=10)

    # Frame para conter os botões
    frame_botoes = tk.Frame(janela_atualizacao)
    frame_botoes.pack(pady=10) 
    
    # Barra de progresso
    progress_bar = ttk.Progressbar(frame_botoes, orient="horizontal", length=200, mode="determinate")
    progress_bar.pack(side=tk.LEFT, padx=5)
    
    # Botão de Download
    botao_download = tk.Button(
        frame_botoes, 
        text="Download", 
        width=18, 
        height=2,
        font=('Ivy 8 bold'), 
        bg="red",  # Mudamos a cor inicial para vermelho
        fg="white", 
        relief=tk.RAISED, 
        overrelief=tk.RIDGE,
        command=lambda: baixar_arquivo(link_download, progress_bar, token, botao_download, janela_atualizacao, label)
    )
    botao_download.pack(side=tk.LEFT, padx=5)

    def on_closing():
        global stop_thread
        if messagebox.askyesno("Cancelar Download", "Download da nova versão do Custódia Tech em andamento, tem certeza que deseja cancelar o download?"):
            stop_thread = True
            janela_atualizacao.quit()
            os._exit(0)  # Encerra o processo Python atual se o usuário cancelar
    
    janela_atualizacao.protocol("WM_DELETE_WINDOW", on_closing)
    
    janela_atualizacao.mainloop()
    
    # Mostra a janela de login novamente após o fechamento da janela de atualização
    janela_login.deiconify()
    
    # Se chegou aqui, significa que o mainloop foi encerrado sem executar o instalador
    return False

def executar_instalador(nome_arquivo, janela_atualizacao):
    try:
        # Obtém o caminho da pasta Downloads do usuário
        pasta_downloads = Path.home() / "Downloads"
        
        # Caminho completo do arquivo ZIP
        caminho_completo_zip = pasta_downloads / nome_arquivo
        
        # Nome do arquivo do instalador dentro do ZIP
        arquivo_instalador = "CustodiaTech_Setup.exe"
        
        # Extrai o conteúdo do ZIP
        with zipfile.ZipFile(caminho_completo_zip, 'r') as zip_ref:
            zip_ref.extract(arquivo_instalador, pasta_downloads)
        
        # Caminho completo do instalador extraído
        caminho_instalador = pasta_downloads / arquivo_instalador
        
        # Executa o instalador
        subprocess.Popen(str(caminho_instalador), shell=True)
        
        #messagebox.showinfo("Instalação Iniciada", "O instalador foi iniciado. O programa será encerrado.")
        
        # Fecha as janelas Tkinter
        if janela_atualizacao.winfo_exists():
            janela_atualizacao.quit()  # Use quit() ao invés de destroy()
        if janela_atualizacao.master and janela_atualizacao.master.winfo_exists():
            janela_atualizacao.master.quit()  # Use quit() ao invés de destroy()
        
        # Encerra o processo Python atual
        os._exit(0)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao executar o instalador: {str(e)}")
        # Encerra o processo Python atual mesmo em caso de erro
        os._exit(1)

def montar_arquivo(dados_json, pasta_downloads):
    try:
        # Decodifica o JSON
        dados = json.loads(dados_json)
        nome_arquivo = dados['nomeArquivo']
        arquivo_base64 = dados['arquivo']

        # Decodifica a string base64
        arquivo_bytes = base64.b64decode(arquivo_base64)

        # Cria o caminho completo para o arquivo
        caminho_completo = pasta_downloads / nome_arquivo

        # Escreve o arquivo
        with open(caminho_completo, 'wb') as f:
            f.write(arquivo_bytes)

        print(f"Arquivo montado com sucesso: {caminho_completo}")
        return nome_arquivo
    except Exception as e:
        print(f"Erro ao montar o arquivo: {str(e)}")
        return None

def baixar_arquivo(link_download, progress_bar, token, botao_download, janela_atualizacao, label):
    global stop_thread
    
    botao_download.config(state=tk.DISABLED, bg="gray")
    
    # Variável para controlar a thread de progresso
    stop_progress = threading.Event()  # Evento para controlar a thread de progresso
    
     # Inicia a thread de verificação de conexão
    thread_verificacao = threading.Thread(target=verificar_conexao, args=(progress_bar, botao_download, label, stop_progress), daemon=True)
    thread_verificacao.start()

    def update_progress():
        for i in range(99):
            if stop_thread or stop_progress.is_set() or not janela_atualizacao.winfo_exists():
                return
            if progress_bar['value'] < 99:
                progress_bar['value'] += 1
                progress_bar.update()
            time.sleep(1)

    def download_thread():
        try:
            if stop_thread:
                return
            
            label.config(text="Download da atualização do Custoditech em andamento, aguarde!")  # Atualiza o label
            
            # Inicia a thread de atualização da barra de progresso
            progress_thread = threading.Thread(target=update_progress, daemon=True)
            progress_thread.start()
            
            # Obtém o caminho da pasta Downloads do usuário
            pasta_downloads = Path.home() / "Downloads"
            
            # Garante que a pasta Downloads existe
            pasta_downloads.mkdir(parents=True, exist_ok=True)
            
            # Adiciona o token de autorização ao cabeçalho
            headers = {'Authorization': f'{token}'}
            
            response = requests.get(link_download, verify=False, headers=headers, timeout=40)
            response.raise_for_status()
            print(response)
            
            if stop_thread:
                return
            
            # Processa a resposta JSON
            dados_json = response.text
            nome_arquivo = montar_arquivo(dados_json, pasta_downloads)
            
            if nome_arquivo:
                # Garante que a barra de progresso chegue a 100%
                progress_bar['value'] = 100
                progress_bar.update()

                print(f"Nome do arquivo: {nome_arquivo}")
                print("Arquivo montado com sucesso")
                executar_instalador(nome_arquivo, janela_atualizacao)
            else:
                raise Exception("Falha ao montar o arquivo")

        except requests.exceptions.RequestException as e:
            if not stop_thread and janela_atualizacao.winfo_exists():
                label.config(text="Erro no download da atualização. Tente novamente!")  # Atualiza o label
                progress_bar['value'] = 0  # Reseta a barra de progresso
                botao_download.config(state=tk.NORMAL, bg="red")  # Reativa o botão de download
                stop_progress.set()  # Sinaliza para parar a thread de progresso
        except Exception as e:
            if not stop_thread and janela_atualizacao.winfo_exists():
                label.config(text="Erro no download da atualização. Tente novamente!")  # Atualiza o label
                progress_bar['value'] = 0  # Reseta a barra de progresso
                botao_download.config(state=tk.NORMAL, bg="red")  # Reativa o botão de download
                stop_progress.set()  # Sinaliza para parar a thread de progresso
        finally:
            if not stop_thread and janela_atualizacao.winfo_exists():
                botao_download.config(state=tk.NORMAL, bg="red")

    # Cria uma nova thread para executar o download
    thread_download = threading.Thread(target=download_thread, daemon=True)
    thread_download.start()