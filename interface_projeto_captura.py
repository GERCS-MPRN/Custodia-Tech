import json
import os
import re
import shutil
import tempfile
import threading
import time
import tkinter as tk
import warnings
import zipfile
from collections import defaultdict
from datetime import datetime
from idlelib.tooltip import Hovertip
from pathlib import Path
from threading import Thread
from tkinter import *
from tkinter import Tk, filedialog, messagebox, ttk
from tkinter.ttk import Style

import keyboard
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from PIL import Image as PILImage
from PIL import ImageGrab, ImageTk
from PIL.ExifTags import TAGS
from PyPDF2 import PdfReader, PdfWriter
import pytz
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import (PageBreak, PageTemplate, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)
from ttkbootstrap import Style
from tzlocal import get_localzone

import utils.api_perdigueiro as api_perdigueiro
from modulos.captura_paginas.interface_captura_paginas import \
    iniciar_tela_captura_paginas
from modulos.captura_tela.interface_captura_tela import janela_captura_tela
from modulos.gravacao_tela.iniciar_gravacao_tela import iniciar_gravacao_tela
from modulos.metadados.interface_metadados import janela_extrair_metadados
from modulos.tiktok.interface_tiktok import janela_tiktok
from modulos.whatsapp.interface_whatsapp import janela_whatsapp
from modulos.x_twitter.interface_x_twitter import janela_x_twitter
from modulos.youtube.interface_youtube import janela_youtube
from relatorio.cabecalho_relatorio import cabecalho_relatorio
from relatorio.pagina_validador import adicionar_pagina_ao_pdf
from relatorio.validador_relatorio import (assinar_hash,
                                           gerar_chaves_criptograficas,
                                           gerar_hash_pdf, gerar_qr_code)
from utils.api_perdigueiro import registrar_acao
from utils.criptografia import decrypt_AES_CBC
from utils.ct_config import load_user_data, salvar_dados_json, save_user_data
from utils.env_manager import CTLOGO, EMISSOR_RELATORIO, PRIMEIRO_LOGIN, env
from utils.formatador_campo import verificar_cpf
from utils.item_path import get_resource_path
from utils.limpar_relatorios_temp import limpar_relatorios_temp
from utils.monitor import centraliza_janela_no_monitor_ativo
from utils.validar_campo import valida_campo_cpf, valida_campo_preenchido

global tema_configurado
global tk_custodia_tech, tempo_restante, tempo_restante_label

global thread_running_salvamento
global known_files
global e_usuario
global e_pass
global tempo
global stop_thread
global usuario
global l_sessao

# Número da versão do programa - Alterar sempre que for compilar uma nova versão para produção
versao_atual = "1.6"
icone_custodia = 'imagens\\iconecustodiatech.ico'
stop_monitoring = False
case_directory = ""
video_path = None
screenshot_paths = []
captured_screenshots = []
captured_screenshots_zip = []
captured_videos = []
pasta_selecionada = ""
checkboxes = []
files_frame = None
arquivos = []
dados_gerais = {}
json_file_path = {}
tema_configurado = False
acao_realizada = None
acao_completa = None

# Variável de controle da thread
thread_running_salvamento = True

file_data_youtube = []
file_data_x = []
file_data_instagram = []
file_data_tiktok = []
file_data_whatsapp = []
file_data_paginas = []
metadados_total = []
elements = []
videos_data = []
var_thread_atividades_caso = True

known_files = set()  # Inicialize known_files como um conjunto vazio

warnings.filterwarnings("ignore")

co0 = "#f0f3f5"  # Preta / black
co1 = "#feffff"  # branca / white
co2 = "#3fb5a3"  # verde / green
co3 = "#38576b"  # valor / value
co4 = "#403d3d"  # letra / letters

stop_thread = 0


def interface_login():
    global tk_login
    global e_usuario
    global e_pass
    global versao_atual, c02

    def key_return(event):
        verifica_senha(tk_login, get_resource_path(icone_custodia))

    tk_login = Tk()
    tk_login.withdraw()
    tk_login.iconbitmap(get_resource_path(icone_custodia))
    tk_login.title('CustodiaTech')
    tk_login.resizable(False, False)

    tk_login.attributes('-topmost', True)
    tk_login.update()
    tk_login.attributes('-topmost', False)
    tk_login.update_idletasks()
    tk_login.focus_force()

    style = Style(theme='simplex')

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(tk_login, "login")

    ALTURA_FRAME_CIMA = int(ALTURA_CT * 0.25)
    ALTURA_FRAME_BAIXO = ALTURA_CT - ALTURA_FRAME_CIMA

    frame_cima = tk.Frame(tk_login, width=LARGURA_CT, height=ALTURA_FRAME_CIMA)
    frame_cima.grid(row=0, column=0, pady=1, padx=0, sticky=NSEW)

    frame_baixo = tk.Frame(tk_login, width=LARGURA_CT, height=ALTURA_FRAME_BAIXO)
    frame_baixo.grid(row=1, column=0, pady=1, padx=0, sticky=NSEW)

    # Fator de escala para as fontes
    fator_escala = LARGURA_CT / 310
    print(f"Fator de Escala: {fator_escala}")

    fonte_pequena = ('Ivy', int(10 * fator_escala), 'bold')
    fonte_media = ('Ivy', int(15 * fator_escala), 'bold')
    fonte_grande = ('Ivy', int(20 * fator_escala), 'bold')

    POS_X_LABEL_VERSAO = int(LARGURA_CT * 0.74)
    POS_Y_LABEL_VERSAO = int(ALTURA_FRAME_CIMA * 0.06)

    POS_X_LOGIN_USUARIO = int(LARGURA_CT * 0.03)
    POS_Y_LOGIN_USUARIO = int(ALTURA_FRAME_CIMA * 0.06)

    LARGURA_LINHA = int(LARGURA_CT * 0.88)
    POS_X_LINHA = int(LARGURA_CT * 0.03)
    POS_Y_LINHA = int(ALTURA_FRAME_CIMA * 0.75)

    # Margem horizontal
    MARGEM_HORIZONTAL = int(LARGURA_CT * 0.03)

    # Largura dos componentes (Entry e Button), subtraindo as margens laterais
    LARGURA_COMPONENTES = LARGURA_CT - 2 * MARGEM_HORIZONTAL

    login_usuario = Label(frame_cima, text=("Versão " + versao_atual), anchor=NE,
                     font=fonte_pequena, bg=co1, fg=co4)
    login_usuario.place(x=POS_X_LABEL_VERSAO, y=POS_Y_LABEL_VERSAO)

    login_usuario = Label(frame_cima, text='Login', anchor=NE,
                        font=fonte_grande, bg=co1, fg=co4)
    login_usuario.place(x=POS_X_LOGIN_USUARIO, y=POS_Y_LOGIN_USUARIO)

    l_linha = Label(frame_cima, text='', width=LARGURA_LINHA,
                    anchor=NW, font=('Ivy', int(1 * fator_escala)), bg=co2, fg=co4)
    l_linha.place(x=POS_X_LINHA, y=POS_Y_LINHA)

    l_custodia_tech = Label(frame_cima, text='CustodiaTech', anchor=NE,
                            font=fonte_media, bg=co1, fg=co4)
    l_custodia_tech.place(x=POS_X_LOGIN_USUARIO, y=int(ALTURA_FRAME_CIMA * 0.62))

    l_usuario = Label(frame_baixo, text='Usuário:', anchor=NW,
                      font=fonte_pequena, bg=co1, fg=co4)
    l_usuario.place(x=MARGEM_HORIZONTAL, y=int(ALTURA_FRAME_BAIXO * 0.06))

    e_usuario = Entry(frame_baixo, width=int(LARGURA_COMPONENTES/8), justify='left', #Remove width
                    font=fonte_media, highlightthickness=1, relief='solid')
    e_usuario.place(x=MARGEM_HORIZONTAL, y=int(ALTURA_FRAME_BAIXO * 0.18), width=LARGURA_COMPONENTES)  # Define largura e posição
    e_usuario.focus_set()

    l_pass = Label(frame_baixo, text='Senha:', anchor=NW,
               font=fonte_pequena, bg=co1, fg=co4)
    l_pass.place(x=MARGEM_HORIZONTAL, y=int(ALTURA_FRAME_BAIXO * 0.33))

    e_pass = Entry(frame_baixo, width=int(LARGURA_COMPONENTES/8), justify='left', show='*',#Remove width
                font=fonte_media, highlightthickness=1, relief='solid')
    e_pass.place(x=MARGEM_HORIZONTAL, y=int(ALTURA_FRAME_BAIXO * 0.45), width=LARGURA_COMPONENTES)  # Define largura e posição

    b_confirmar = Button(frame_baixo, command=lambda: verifica_senha(tk_login, get_resource_path(icone_custodia)),
                     text='Entrar', height=2, font=fonte_pequena,
                     bg=co2, fg=co1, relief=RAISED, overrelief=RIDGE)
    b_confirmar.place(x=MARGEM_HORIZONTAL, y=int(ALTURA_FRAME_BAIXO * 0.65), width=LARGURA_COMPONENTES)  # Define largura e posição

    e_usuario.bind('<Return>', key_return)
    e_pass.bind('<Return>', key_return)
    b_confirmar.bind('<Return>', key_return)

    def on_closing():
        global stop_thread
        if messagebox.askokcancel("Sair", "Deseja fechar a janela de login?", parent=tk_login):
            tk_login.destroy()
            stop_thread = 1

    tk_login.after(0, e_usuario.focus_set)
    tk_login.deiconify()
    tk_login.protocol("WM_DELETE_WINDOW", on_closing)
    tk_login.mainloop()

def verifica_senha(tk_login, icone_custodia):
    global e_usuario
    global e_pass
    global usuario
    global acao_realizada
    global acao_completa

    usuario = e_usuario.get()
    senha = e_pass.get()

    if api_perdigueiro.logar(usuario, senha, versao_atual, tk_login, icone_custodia):
        
        registrar_acao(
            "Login efetuado",
            f"Login realizado pelo usuario {usuario}"
        )

        tk_login.withdraw()

        interface_custodia_tech()

    else:
        messagebox.showwarning('Falha de Autenticação',
                               'Verifique usuário e/ou senha!', parent=tk_login)
        e_pass.delete(0, 'end')
        if e_usuario.get() == '':
            e_usuario.focus_set()
        else:
            e_pass.focus_set()

# Interface principal do Custodia Tech
def interface_custodia_tech():
    COLETA_PROBATORIA = "Coleta Probatória"
    fuso_local = get_localzone()

    def adicionar_dados_no_relatorio(captured_screenshots, captured_screenshots_zip, videos_data, case_directory, dados_gerais,  metadados_total, file_data_youtube, file_data_x, file_data_instagram, file_data_tiktok, file_data_whatsapp, file_data_paginas):
        global nome_relatorio
        METADADOS_DO_ARQUIVO = "Metadados do Arquivo:"
        HASHES_DO_ARQUIVO = "Hashes do Arquivo:"
        
        data_hora_local = datetime.now(fuso_local)
        #data_hora_utc = data_hora_local.astimezone(pytz.utc)
        timestamp_arquivo = data_hora_local.strftime("%d-%m-%Y_%H-%M-%S_UTC%Z")
        data_hora_relatorio = data_hora_local.strftime("%d/%m/%Y %H:%M:%S UTC %Z")
        
        # fuso_local = get_localzone()
        # data_hora_local = datetime.now(fuso_local)
        # timestamp = data_hora_local.strftime("%d-%m-%Y_%H-%M-%S_UTC%Z")
        
        nome_relatorio = f"Relatório de evidência(s) digital(is) {timestamp_arquivo}.pdf"
        save_path = os.path.join(case_directory, nome_relatorio)
        
        try:
            doc = SimpleDocTemplate(save_path, pagesize=A4, topMargin=2.0*inch)
            styles = getSampleStyleSheet()
            
            styles.add(ParagraphStyle(
                name='Justify', 
                alignment=TA_JUSTIFY, 
                fontName='Times-Roman', 
                fontSize=12
            ))
            
            styles.add(ParagraphStyle(
                name='Bold', 
                alignment=TA_JUSTIFY, 
                fontName='Times-Bold',
                fontSize=12, 
                leading=14, 
                spaceAfter=10, 
                textColor='black'
            ))
            
            styles.add(ParagraphStyle(
                name='Footnote', 
                alignment=TA_JUSTIFY, 
                fontName='Times-Roman', 
                fontSize=8
            ))
            
            styles.add(ParagraphStyle(
                name='Header', 
                alignment=TA_CENTER, 
                fontName='Times-Roman', 
                fontSize=8
            ))
            
            styles.add(ParagraphStyle(
                name='IndentedFirstLine', 
                alignment=TA_JUSTIFY,
                fontName='Times-Roman', 
                fontSize=12, 
                firstLineIndent=18
            ))
            
            list_style = ParagraphStyle(
                name='List', 
                alignment=TA_JUSTIFY, 
                fontName='Times-Roman',
                fontSize=12, 
                spaceBefore=10, 
                spaceAfter=10, 
                leftIndent=18
            )
            
            gloss_style = ParagraphStyle(
                name='Glossary', 
                alignment=TA_JUSTIFY, 
                fontName='Times-Roman',
                fontSize=12, 
                spaceBefore=10, 
                spaceAfter=10, 
                leftIndent=18
            )
            
            dados_gerais_style = ParagraphStyle(
                name='GeralData', 
                alignment=TA_JUSTIFY, 
                fontName='Times-Roman', 
                fontSize=12, 
                leftIndent=0
            )
            
            chaves_style = ParagraphStyle(
                name='GeralData', 
                alignment=TA_JUSTIFY, 
                fontName='Courier', 
                fontSize=11, 
                leftIndent=0
            )
            
            styles.add(ParagraphStyle(
                name='Center', 
                alignment=TA_CENTER, 
                fontName='Times-Roman', 
                fontSize=12
            ))

            elements.append(PageBreak())

            # Adicionar o conteúdo do corpo
            elements.append(Paragraph("Relatório de Captura", styles['Title']))

            elements.append(Spacer(1, 12))

            elements.append(
                Paragraph("<b>Coleta de Vestígios Digitais</b>", styles['Bold']))
            elements.append(Spacer(1, 12))
            text = """
            No contexto atual, onde a maior parte das informações é gerada e armazenada digitalmente, a coleta de vestígios digitais tornou-se uma tarefa essencial em investigações criminais, auditorias, litígios legais e incidentes de segurança da informação. Entretanto, essa tarefa apresenta diversos desafios:
            """
            elements.append(Paragraph(text, styles['IndentedFirstLine']))
            elements.append(Spacer(1, 12))

            # Adicionar a lista de desafios
            challenges = [
                "<b>Variedade de Dispositivos e Sistemas</b>: Vestígios digitais podem ser encontrados em uma ampla gama de dispositivos e sistemas, incluindo computadores, smartphones, servidores e dispositivos de armazenamento, cada um com suas próprias características e métodos de armazenamento de dados.",
                "<b>Integridade e Autenticidade</b>: Manter a integridade e a autenticidade dos dados digitais é crucial para garantir sua admissibilidade como prova. Qualquer alteração ou manipulação pode comprometer a validade da evidência.",
                "<b>Complexidade Técnica</b>: O processo de identificação, coleta, aquisição e preservação de vestígios digitais requer conhecimentos técnicos especializados e ferramentas adequadas para garantir que os dados sejam capturados e armazenados corretamente.",
                "<b>Normas e Procedimentos</b>: A falta de clareza sobre os procedimentos técnicos necessários para garantir a admissibilidade dos vestígios digitais no processo criminal pode levar à rejeição das provas. É essencial seguir normas e procedimentos reconhecidos, como a ABNT NBR ISO/IEC 27037:2013, que estabelece diretrizes para o tratamento de vestígios digitais."
            ]

            for i, challenge in enumerate(challenges, start=1):
                elements.append(Paragraph(f"{i}. {challenge}", list_style))

            elements.append(Spacer(1, 12))

            elements.append(Paragraph("<b>Glossário</b>", styles['Bold']))

            glossary = [
                "<b>Autenticidade</b>: Garante que a prova digital é genuína e corresponde exatamente ao que pretende representar, sem alterações desde a sua criação ou captura.",
                "<b>Completude</b>: Refere-se à integridade dos dados apresentados como prova, assegurando que todas as partes relevantes da evidência estão presentes.",
                "<b>Integridade</b>: Garante que a prova digital não foi alterada ou manipulada desde o momento em que foi capturada até a sua apresentação em um processo.",
                "<b>Temporalidade</b>: Capacidade de demonstrar a data e a hora exatas em que a prova foi criada, modificada ou acessada, estabelecendo uma linha do tempo confiável dos eventos.",
                "<b>Auditabilidade</b>: Capacidade de verificar e rastrear todas as ações realizadas sobre a prova digital, mantendo um registro claro e detalhado de quem acessou, modificou ou manipulou os dados.",
                "<b>Cadeia de Custódia</b>: Documentação adequada da prova digital desde a coleta até sua apresentação, assegurando que a prova permaneça intacta e autêntica.",
                "<b>Vestígio Digital</b>: Qualquer dado ou informação gerada, armazenada ou transmitida por meios eletrônicos que pode ser usada como evidência em investigações criminais, procedimentos administrativos, auditorias ou litígios legais.",
                "<b>Coleta</b>: Processo de identificar, localizar e reunir dados relevantes, garantindo sua preservação de maneira adequada.",
                "<b>Aquisição</b>: Criação de uma cópia exata dos dados identificados, preservando todas as informações originais para análise futura.",
                "<b>Preservação</b>: Proteção dos dados identificados para garantir que não sejam alterados, corrompidos ou destruídos.",
                "<b>Printscreen</b>: Registro digital fotográfico da tela, capturando uma representação fiel e precisa do que foi exibido no momento da captura.",
                "<b>Gravação</b>: A gravação é o processo de captura contínua da atividade na tela de um dispositivo durante a coleta de dados digitais.",
                "<b>Metadados</b>: Dados que descrevem outros dados, fornecendo informações detalhadas sobre a origem, criação e modificações dos arquivos, essenciais para garantir a autenticidade e integridade dos vestígios digitais.",
                "<b>Hash</b>: Hash é um valor numérico gerado por uma função hash que representa de forma única um conjunto de dados.",
                "<b>Endereço IP</b>: Um endereço IP (Internet Protocol) é um identificador numérico único atribuído a cada dispositivo conectado a uma rede de computadores que utiliza o protocolo IP para comunicação."
            ]

            for term in glossary:
                elements.append(Paragraph(f"• {term}", gloss_style))

            elements.append(Spacer(1, 12))

            elements.append(Paragraph("Dados Capturados", styles['Title']))
            dados_validos = {key: value for key,
                             value in dados_gerais.items() if value}
            
            if dados_validos:  # Só adiciona o título e os dados se houver dados válidos
                elements.append(Paragraph("<b>Dados Gerais</b>:", styles['Bold']))

                for key, value in dados_validos.items():
                    elements.append(Paragraph(f"<b>{key}:</b> {value}", dados_gerais_style))
                    elements.append(Spacer(1, 9))

            elements.append(Spacer(1, 12))
            elements.append(Paragraph("<b>Dados de Captura</b>:", styles['Bold']))

            if captured_screenshots:
                try:
                    elements.append(
                        Paragraph("<b>ARQUIVOS DE CAPTURA DE TELA:</b>", styles['Bold']))

                    # Itera sobre ambas as listas simultaneamente, garantindo a correspondência entre a imagem e os dados.
                    for screenshot_data, screenshot_data_zip in zip(captured_screenshots, captured_screenshots_zip):
                        image_path = screenshot_data
                        
                        if image_path:
                            # Abre a imagem com PIL para obter as dimensões originais
                            try:
                                pil_image = PILImage.open(image_path)
                                original_width, original_height = pil_image.size
                            except Exception as e:
                                print(f"Erro ao abrir a imagem {image_path}: {e}")
                                continue 

                            max_width_pdf = 6.1 * inch

                            # Calcula a nova largura e altura mantendo a proporção
                            if original_width > max_width_pdf:
                                new_width = max_width_pdf
                                new_height = (original_height / original_width) * new_width
                            else:
                                new_width = original_width
                                new_height = original_height
                        
                        # Cria a imagem para o PDF com as novas dimensões
                        image = RLImage(image_path, width=new_width, height=new_height)

                        if image_path:
                            # Adiciona a imagem ao documento
                            elements.append(image)
                            elements.append(Spacer(1, 12))

                            # Captura os dados correspondentes do zip
                            hash_results, file_metadata, reason = screenshot_data_zip

                            # Adiciona os dados após a imagem
                            elements.append(
                                Paragraph("Data e hora da extração:", styles['Bold']))
                            elements.append(
                                Paragraph(data_hora_relatorio, styles['Justify']))
                            elements.append(Spacer(1, 12))

                            elements.append(
                                Paragraph("Motivo da captura:", styles['Bold']))
                            elements.append(Paragraph(reason, styles['Justify']))
                            elements.append(Spacer(1, 12))

                            elements.append(
                                Paragraph(METADADOS_DO_ARQUIVO, styles['Bold']))
                            for key, value in file_metadata.items():
                                elements.append(Paragraph(f"{key}: {value}", styles['Justify']))
                                elements.append(Spacer(1, 12))

                            elements.append(Paragraph(HASHES_DO_ARQUIVO, styles['Bold']))
                            for algorithm, hash_value in hash_results.items():
                                elements.append(
                                    Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                            elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos de captura de tela: {e}")

            if file_data_youtube:
                try:
                    file_data_by_url = defaultdict(list)
                    for data in file_data_youtube:
                        urlvideo = data['urlvideo']
                        file_data_by_url[urlvideo].append(data)

                    elements.append(
                        Paragraph("<b>ARQUIVOS DO YOUTUBE:</b>", styles['Bold']))

                    for urlvideo, files in file_data_by_url.items():
                        elements.append(
                            Paragraph(f"<b>URL:</b> {urlvideo}", styles['Bold']))
                        elements.append(Spacer(1, 12))  # Espaçamento após a URL

                        for data in files:
                            elements.append(
                                Paragraph(f"Arquivo: {data['nome_do_arquivo']}", styles['Bold']))
                            elements.append(Paragraph(HASHES_DO_ARQUIVO, styles['Bold']))
                            for algorithm, hash_value in data['hashes'].items():
                                elements.append(
                                    Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                            elements.append(Spacer(1, 12))

                            elements.append(
                                Paragraph("Metadados do Arquivo:", styles['Bold']))
                            for key, value in data['metadata'].items():
                                elements.append(
                                    Paragraph(f"{key}: {value}", styles['Justify']))
                            elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos do Youtube: {e}")

            if file_data_x:
                try:
                    file_data_by_url = defaultdict(list)
                    for data in file_data_x:
                        # Use uma URL padrão se não houver URL
                        urlvideo = data.get('urlvideo', 'URL não disponível')
                        file_data_by_url[urlvideo].append(data)
                    elements.append(
                        Paragraph("<b>ARQUIVOS DO X (ANTIGO TWITTER):</b>", styles['Bold']))

                    for urlvideo, files in file_data_by_url.items():
                        elements.append(
                            Paragraph(f"<b>URL:</b> {urlvideo}", styles['Bold']))
                        elements.append(Spacer(1, 12))  # Espaçamento após a URL

                        for data in files:
                            elements.append(
                                Paragraph(f"Arquivo: {data['nome_do_arquivo']}", styles['Bold']))
                            elements.append(Paragraph(HASHES_DO_ARQUIVO, styles['Bold']))
                            for algorithm, hash_value in data['hashes'].items():
                                elements.append(
                                    Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                            elements.append(Spacer(1, 12))

                            elements.append(
                                Paragraph(METADADOS_DO_ARQUIVO, styles['Bold']))
                            for key, value in data['metadata'].items():
                                elements.append(
                                    Paragraph(f"{key}: {value}", styles['Justify']))
                            elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos do X (antigo Twitter): {e}")

            if file_data_tiktok:
                try:
                    file_data_by_url = defaultdict(list)
                    for data in file_data_tiktok:
                        urlvideo = data['urlvideo']
                        file_data_by_url[urlvideo].append(data)

                    elements.append(
                        Paragraph("<b>ARQUIVOS DO TIKTOK:</b>", styles['Bold']))

                    for urlvideo, files in file_data_by_url.items():
                        elements.append(
                            Paragraph(f"<b>URL:</b> {urlvideo}", styles['Bold']))
                        elements.append(Spacer(1, 12))

                        for data in files:
                            elements.append(
                                Paragraph(f"Arquivo: {data['nome_do_arquivo']}", styles['Bold']))
                            elements.append(Paragraph("Hashes:", styles['Bold']))
                            for algorithm, hash_value in data['hashes'].items():
                                elements.append(
                                    Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                            elements.append(Spacer(1, 12))

                            elements.append(
                                Paragraph(METADADOS_DO_ARQUIVO, styles['Bold']))
                            for key, value in data['metadata'].items():
                                elements.append(
                                    Paragraph(f"{key}: {value}", styles['Justify']))
                            elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos do TikTok: {e}")

            if file_data_instagram:

                elements.append(
                    Paragraph("<b>ARQUIVOS DO INSTAGRAM:</b>", styles['Bold']))

                for data in file_data_instagram:
                    elements.append(
                        Paragraph(f"<b>Arquivo: {data['nome_do_arquivo']}</b>", styles['Bold']))
                    elements.append(Paragraph("Hashes:", styles['Bold']))
                    for algorithm, hash_value in data['hashes'].items():
                        elements.append(
                            Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                    elements.append(Spacer(1, 12))

                    elements.append(Paragraph("Metadados:", styles['Bold']))
                    for key, value in data['metadata'].items():
                        elements.append(
                            Paragraph(f"{key}: {value}", styles['Justify']))
                    elements.append(Spacer(1, 12))

            if videos_data:
                try:
                    
                    elements.append(
                        Paragraph("<b>ARQUIVOS DE GRAVAÇÃO DE VÍDEO:</b>", styles['Bold']))
                    elements.append(Spacer(1, 12))

                    for video_data in videos_data:
                        video_path = video_data["Caminho do Arquivo"]
                        video_file_metadata = video_data["Metadados"]
                        video_hash_results = video_data["Hashes"]

                        # Imprime o caminho do arquivo
                        elements.append(Paragraph(f"Video: {video_path}", styles['Bold']))
                        elements.append(Spacer(1, 6))

                        # Imprime os metadados do vídeo
                        elements.append(Paragraph("Metadados do Vídeo:", styles['Bold']))
                        for key, value in video_file_metadata.items():
                            elements.append(Paragraph(f"{key}: {value}", styles['Justify']))
                        elements.append(Spacer(1, 12))

                        # Imprime os hashes do vídeo
                        elements.append(Paragraph("Hashes do Vídeo:", styles['Bold']))
                        for algorithm, hash_value in video_hash_results.items():
                            elements.append(Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                        elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos de vídeo: {e}")

            if file_data_whatsapp:
                try:
                    # Código para imprimir em PDF...
                    elements.append(
                        Paragraph("<b>ARQUIVOS DO WHATSAPP:</b>", styles['Bold']))
                    elements.append(Spacer(1, 12))

                    for file_data in file_data_whatsapp:
                        file_path = file_data["nome_do_arquivo"]
                        file_metadata = file_data["metadata"]
                        file_hash_results = file_data["hashes"]

                        # Imprime o caminho do arquivo
                        elements.append(Paragraph(f"Arquivo: {file_path}", styles['Bold']))
                        elements.append(Spacer(1, 6))

                        # Imprime os metadados do arquivo
                        elements.append(Paragraph(METADADOS_DO_ARQUIVO, styles['Bold']))
                        for key, value in file_metadata.items():
                            elements.append(Paragraph(f"{key}: {value}", styles['Justify']))
                        elements.append(Spacer(1, 12))

                        # Imprime os hashes do arquivo
                        elements.append(Paragraph(HASHES_DO_ARQUIVO, styles['Bold']))
                        for algorithm, hash_value in file_hash_results.items():
                            elements.append(Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                        elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos do WhatsApp: {e}")

            if file_data_paginas:
                try:
                        
                    elements.append(Paragraph("<b>ARQUIVOS DE PÁGINAS CAPTURADAS:</b>", styles['Bold']))
                    elements.append(Spacer(1, 12))

                    for file_data in file_data_paginas:
                        file_path = file_data["nome_do_arquivo"]
                        file_metadata = file_data["metadata"]
                        file_hash_results = file_data["hashes"]

                        # Imprime o caminho do arquivo
                        elements.append(Paragraph(f"Arquivo: {file_path}", styles['Bold']))
                        elements.append(Spacer(1, 6))

                        # Imprime os metadados do arquivo
                        elements.append(Paragraph(METADADOS_DO_ARQUIVO, styles['Bold']))
                        for key, value in file_metadata.items():
                            elements.append(Paragraph(f"{key}: {value}", styles['Justify']))
                        elements.append(Spacer(1, 12))

                        # Imprime os hashes do arquivo
                        elements.append(Paragraph(HASHES_DO_ARQUIVO, styles['Bold']))
                        for algorithm, hash_value in file_hash_results.items():
                            elements.append(Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                        elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos de páginas capturadas: {e}")

            if metadados_total:
                try:
                        
                    elements.append(Paragraph("<b>ARQUIVOS AVULSOS</b>:", styles['Bold']))

                    for arquivo_metadados in metadados_total:
                        elements.append(Spacer(1, 12))
                        # Verifique se arquivo_metadados é um dicionário
                        if isinstance(arquivo_metadados, dict):
                            # Acessando os dados corretamente
                            nome_do_arquivo = arquivo_metadados.get('nome_do_arquivo', 'N/A')
                            elements.append(Paragraph(f"<b>Arquivo: {nome_do_arquivo}</b>", styles['Bold']))
                            
                            # Verifique se 'metadata' e 'hashes' são dicionários e se eles existem
                            if 'metadata' in arquivo_metadados and isinstance(arquivo_metadados['metadata'], dict):
                                elements.append(Paragraph(METADADOS_DO_ARQUIVO, styles['Bold']))
                                for key, value in arquivo_metadados['metadata'].items():
                                    elements.append(Paragraph(f"{key}: {value}", styles['Justify']))
                            elements.append(Spacer(1, 12))   
                                
                            if 'hashes' in arquivo_metadados and isinstance(arquivo_metadados['hashes'], dict):
                                elements.append(Paragraph(HASHES_DO_ARQUIVO, styles['Bold']))
                                for algorithm, hash_value in arquivo_metadados['hashes'].items():
                                    elements.append(Paragraph(f"{algorithm.upper()}: {hash_value}", styles['Justify']))
                            elements.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Erro ao adicionar os arquivos avulsos: {e}")
                    
            selected_value = combo_var.get()

            if selected_value == COLETA_PROBATORIA:  # Só adiciona o título se for uma coleta probatória
                
                elements.append(PageBreak())

                elements.append(Paragraph("Folha de Assinaturas", styles['Title']))

                operador_nome = dados_gerais.get('Nome do Operador', '')
                operador_matricula = dados_gerais.get('Matrícula do Operador', '')
                testemunha1_nome = dados_gerais.get('Nome da Testemunha 1', '')
                testemunha1_cpf = dados_gerais.get('CPF da Testemunha 1', '')
                testemunha2_nome = dados_gerais.get('Nome da Testemunha 2', '')
                testemunha2_cpf = dados_gerais.get('CPF da Testemunha 2', '')
                
                def formata_linha(lista_campos):
                    maior_texto = 0
                    for campo in lista_campos:
                        if len(campo) > maior_texto:
                            maior_texto = len(campo)
                    maior_texto += 10
                    if maior_texto > 73:
                        maior_texto = 73
                    linha = maior_texto*'_'
                    return linha

                linha_proporcional = formata_linha([operador_nome, testemunha1_nome, testemunha2_nome])

                elements.append(Spacer(1, 30))
                elements.append(Paragraph(f"{linha_proporcional}", styles['Center']))
                elements.append(Spacer(1, 3))
                elements.append(Paragraph(f"{operador_nome.upper()}", styles['Center']))
                elements.append(Paragraph(f"Mat. {operador_matricula}", styles['Center']))
                elements.append(Paragraph("Operador(a)", styles['Center']))

                if testemunha1_nome != '':
                    elements.append(Spacer(1, 30))
                    elements.append(Paragraph(f"{linha_proporcional}", styles['Center']))
                    elements.append(Spacer(1, 3))
                    elements.append(Paragraph(f"{testemunha1_nome.upper()}", styles['Center']))
                    elements.append(Paragraph(f"CPF {testemunha1_cpf}", styles['Center']))
                    elements.append(Paragraph("Testemunha", styles['Center']))
                
                if testemunha2_nome != '':
                    elements.append(Spacer(1, 30))
                    elements.append(Paragraph(f"{linha_proporcional}", styles['Center']))
                    elements.append(Spacer(1, 3))
                    elements.append(Paragraph(f"{testemunha2_nome.upper()}", styles['Center']))
                    elements.append(Paragraph(f"CPF {testemunha2_cpf}", styles['Center']))
                    elements.append(Paragraph("Testemunha", styles['Center']))

            try:
                # Adicionar páginas subsequentes com cabeçalho e numeração
                def capa_relatorio(canvas, doc):
                    gerar_capa_relatorio(canvas)

                def my_later_pages(canvas, doc):
                    cabecalho_relatorio(canvas, logo_path)
                    add_page_number(canvas, doc)

                doc.build(elements, onFirstPage=capa_relatorio,
                        onLaterPages=my_later_pages)

                chave_hash_pdf = str(os.urandom(24).hex())
                chaves = gerar_chaves_criptograficas(chave_hash_pdf)
                
                emissor = EMISSOR_RELATORIO
                hash_documento = gerar_hash_pdf(save_path)
                chave_privada = load_pem_private_key(chaves['chave_privada'], password=chave_hash_pdf.encode())
                assinatura = assinar_hash(hash_documento, chave_privada)
                chave_publica = chaves['chave_publica']

                # Dados para o QR Code
                dados_qr = {
                    "emissor": emissor,
                    "data_hora": data_hora_relatorio,
                    "hash": hash_documento,
                    "assinatura": assinatura,
                    "chave_publica": chave_publica
                }

                dados_qr = json.dumps(dados_qr, ensure_ascii=False, indent=0)
                
                qr_code_img = gerar_qr_code(dados_qr)

                # Adicionar a nova página ao PDF existente
                adicionar_pagina_ao_pdf(save_path, emissor, data_hora_relatorio, hash_documento, assinatura, chave_publica, qr_code_img, save_path, dados_gerais_style, styles, logo_path, chaves_style)
            except Exception as e:
                print(f"Erro ao salvar PDF: {e}")
    
        except Exception as e:
            print(f"Erro ao salvar PDF: {e}")

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        page_number_text = f"Página {doc.page}"
        # Ajustar a posição do número da página
        canvas.drawRightString(A4[0] - 1 * inch, 0.75 * inch, page_number_text)
        canvas.restoreState()

    def gerar_capa_relatorio(canvas):
        # Configurações para a capa
        page_width, page_height = A4
        title = "CUSTODIATECH"
        subtitle = "Registro Qualificado de Vestígio Digital"

        # Adiciona o título
        title_font_size = 36
        canvas.setFont("Helvetica-Bold", title_font_size)
        title_width = canvas.stringWidth(
            title, "Helvetica-Bold", title_font_size)
        title_x = (page_width - title_width) / 2
        title_y = (page_height + title_font_size) / 2
        canvas.drawString(title_x, title_y, title)

        # Adiciona o subtítulo
        subtitle_font_size = 24
        canvas.setFont("Helvetica", subtitle_font_size)
        subtitle_width = canvas.stringWidth(
            subtitle, "Helvetica", subtitle_font_size)
        subtitle_x = (page_width - subtitle_width) / 2
        # Ajuste a posição vertical conforme necessário
        subtitle_y = (page_height - title_font_size - 20) / 2
        canvas.drawString(subtitle_x, subtitle_y, subtitle)
        
    def clear_file_list():
        for widget in frame_atividades_caso.winfo_children():
            widget.destroy()

    def criar_novo_caso(case_name_entry, selecionar_caminho_button, combobox):
        global var_thread_atividades_caso
        
        progressbar['value'] = 0
        case_name = case_name_entry.get().strip()

        # Lista de caracteres inválidos
        invalid_chars = r'[<>:"/\\|?*]'

        # Verificar se o nome contém caracteres inválidos
        if re.search(invalid_chars, case_name):
            messagebox.showerror("Erro", "O nome do caso contém caracteres inválidos. "
                                 "Por favor, evite usar: <>:\"/\\|?*", parent=tk_custodia_tech)
            return

        if case_name:
            global case_directory, captured_screenshots, captured_screenshots_zip, videos_data, dados_gerais, metadados_total, file_data_youtube, file_data_x, file_data_instagram, file_data_tiktok, file_data_whatsapp, file_data_paginas
            # Caminho dinâmico para AppData\Local\CustodiaTech\Casos
            case_base_path = Path.home() / "AppData" / "Local" / "CustodiaTech" / "Casos"
            
            # Cria o diretório "Casos" se não existir
            case_base_path.mkdir(parents=True, exist_ok=True)
            
            # Cria a pasta do caso
            case_directory = case_base_path / case_name

            if os.path.exists(case_directory):
                # tk_custodia_tech.update_idletasks()
                # tk_login.update_idletasks()
                resposta = messagebox.askquestion("Caso Existente",
                                                  f"Verificamos que o caso '{
                                                      case_name}' já existe.\n"
                                                  "Deseja continuar o caso?",
                                                  icon='warning',
                                                  type='yesno',
                                                  parent=tk_custodia_tech)

                if resposta == 'yes':
                    var_thread_atividades_caso = True
                    print(var_thread_atividades_caso)
                    
                    thread_atividades_caso = Thread(target=itens_atividades_do_caso, daemon=True)
                    thread_atividades_caso.start()
                    # Continuar o caso existente
                    enable_buttons(True)

                    selected_value = combo_var.get()
                    
                    registrar_acao(
                        "Caso existente continuado", 
                        f"Caso existente '{case_name}' continuado com tipo de relatório {selected_value} pelo usuário {usuario} no diretório {case_directory}")
            
                    json_file_path = os.path.join(case_directory, "CustodiaTech.config")
                    if os.path.exists(json_file_path):
                        with open(json_file_path, "rb") as json_file:
                            encrypted_data = json_file.read()
                            # Descriptografar o arquivo JSON
                            decrypted_data = decrypt_AES_CBC(encrypted_data)
                            dados_coleta_probatoria = json.loads(decrypted_data)

                        # Popular os campos de entrada com os dados do JSON
                        numero_procedimento_entry.insert(0, dados_coleta_probatoria.get("numero_procedimento", ""))
                        
                        if operador_nome_entry.get() == '':
                            operador_nome_entry.insert(0, dados_coleta_probatoria.get("operador_nome", ""))
                        if operador_matricula_entry.get() == '':
                            operador_matricula_entry.insert(0, dados_coleta_probatoria.get("operador_matricula", ""))
                        if operador_orgao_entry.get() == '':
                            operador_orgao_entry.insert(0, dados_coleta_probatoria.get("operador_orgao", ""))
                                                
                        denunciante_nome_entry.insert(0, dados_coleta_probatoria.get("denunciante_nome", ""))
                        denunciante_cpf_entry.insert(0, dados_coleta_probatoria.get("denunciante_cpf", ""))
                        denunciante_endereco_entry.insert(0, dados_coleta_probatoria.get("denunciante_endereco", ""))
                        denunciante_telefone_entry.insert(0, dados_coleta_probatoria.get("denunciante_telefone", ""))
                        testemunha1_nome_entry.insert(0, dados_coleta_probatoria.get("testemunha1_nome", ""))
                        testemunha1_cpf_entry.insert(0, dados_coleta_probatoria.get("testemunha1_cpf", ""))
                        testemunha1_endereco_entry.insert(0, dados_coleta_probatoria.get("testemunha1_endereco", ""))
                        testemunha1_telefone_entry.insert(0, dados_coleta_probatoria.get("testemunha1_telefone", ""))
                        testemunha2_nome_entry.insert(0, dados_coleta_probatoria.get("testemunha2_nome", ""))
                        testemunha2_cpf_entry.insert(0, dados_coleta_probatoria.get("testemunha2_cpf", ""))
                        testemunha2_endereco_entry.insert(0, dados_coleta_probatoria.get("testemunha2_endereco", ""))
                        testemunha2_telefone_entry.insert(0, dados_coleta_probatoria.get("testemunha2_telefone", ""))

                        # Popular os dados adicionais que foram salvos
                        captured_screenshots = dados_coleta_probatoria.get("captured_screenshots", [])
                        captured_screenshots_zip = dados_coleta_probatoria.get("captured_screenshots_zip", [])
                        videos_data = dados_coleta_probatoria.get("videos_data", [])
                        dados_gerais = dados_coleta_probatoria.get("dados_gerais", {})
                        metadados_total = dados_coleta_probatoria.get("metadados_total", [])
                        file_data_youtube = dados_coleta_probatoria.get("file_data_youtube", [])
                        file_data_x = dados_coleta_probatoria.get("file_data_x", [])
                        file_data_instagram = dados_coleta_probatoria.get("file_data_instagram", [])
                        file_data_tiktok = dados_coleta_probatoria.get("file_data_tiktok", [])
                        file_data_whatsapp = dados_coleta_probatoria.get("file_data_whatsapp", [])
                        file_data_paginas = dados_coleta_probatoria.get("file_data_paginas", [])
                        
                        if numero_procedimento_entry.get() == '' or operador_nome_entry.get() == '' or operador_matricula_entry.get() == '' or operador_orgao_entry.get() == '':
                            notebook.select(tab2)
                        
                        # Deletar o arquivo JSON após carregar os dados
                        os.remove(json_file_path)
                    
                    # Desabilitar o botão e o campo de entrada
                    case_name_entry.config(state='disabled')
                    selecionar_caminho_button.config(state='disabled')
                    combobox.config(state='disabled')
                    
                    
                else:
                    # Cancelar a criação do caso
                    case_directory = ''
                    case_name_entry.delete(0, tk.END)
                    return
            else:
                # Criar novo caso
                var_thread_atividades_caso = True
                print(var_thread_atividades_caso)
                
                thread_atividades_caso = Thread(target=itens_atividades_do_caso, daemon=True)
                thread_atividades_caso.start()
                
                os.makedirs(case_directory, exist_ok=True)
                enable_buttons()

                selected_value = combo_var.get()
                
                notebook.select(tab2)
                tk_custodia_tech.after(0, numero_procedimento_entry.focus_set)
                
                registrar_acao(
                    "Novo caso criado",
                    f"Novo caso criado de nome {case_name} e tipo do relatório {selected_value} pelo usuário {usuario} no diretório {case_directory}"
                )
                
                # Reinicia o monitoramento
                restart_monitoring()
                
                # Desabilitar o botão e o campo de entrada
                case_name_entry.config(state='disabled')
                selecionar_caminho_button.config(state='disabled')
                combobox.config(state='disabled')
        else:
            messagebox.showerror(  
                "Erro", "O nome do caso não pode estar vazio. Por favor, insira um nome válido.", parent=tk_custodia_tech)
    
    def enable_buttons(caso_aberto=False):
        global usuario
        selected_value = combo_var.get()
        botao_fechar_caso.config(state=tk.NORMAL)
        botao_captura_tela.config(state=tk.NORMAL)
        botao_gravacao_tela.config(state=tk.NORMAL)
        botao_extrair_metadados.config(state=tk.NORMAL)
        # botao_instagram.config(state=tk.NORMAL)
        botao_youtube.config(state=tk.NORMAL)
        botao_x_twitter.config(state=tk.NORMAL)
        botao_tiktok.config(state=tk.NORMAL)
        botao_whatsapp.config(state=tk.NORMAL)
        botao_captura_paginas.config(state=tk.NORMAL)
        # facebook_button.config(state=tk.NORMAL)
        
        if selected_value == COLETA_PROBATORIA:

            notebook.tab(1, state="normal")
            tk_custodia_tech.after(0, numero_procedimento_entry.focus_set)

            # Carrega os dados do operador
            load_user_data(case_directory, usuario, operador_nome_entry, operador_matricula_entry, operador_orgao_entry)
        
    def restart_monitoring():
        global stop_monitoring
        global case_directory
        
        if case_directory and os.path.exists(case_directory):
            stop_monitoring = False
            clear_file_list()  # Clear the GUI list
        else:
            clear_file_list()  # Limpa a lista mesmo se não houver um caso válido
    
    # Função para atualizar a barra de progresso progressivamente
    def atualizar_progressbar(progressbar, valor, intervalo=10):
        global stop_monitoring
        if valor < 100:
            progressbar['value'] = valor
            progressbar.update_idletasks()  # Atualiza a interface gráfica
            progressbar.after(intervalo, atualizar_progressbar,
                              progressbar, valor + 1, intervalo)
        else:
            progressbar['value'] = 100
            
             # Ao finalizar a progressbar, libera os botões
            case_name_entry.config(state='normal')
            selecionar_caminho_button.config(state='normal')
            combobox.config(state='readonly')
            
            progressbar['value'] = 0
            botao_fechar_caso.config(state=tk.DISABLED)
            botao_captura_tela.config(state=tk.DISABLED)
            botao_gravacao_tela.config(state=tk.DISABLED)
            botao_extrair_metadados.config(state=tk.DISABLED)
            botao_instagram.config(state=tk.DISABLED)
            botao_youtube.config(state=tk.DISABLED)
            botao_x_twitter.config(state=tk.DISABLED)
            botao_tiktok.config(state=tk.DISABLED)
            botao_whatsapp.config(state=tk.DISABLED)
            botao_captura_paginas.config(state=tk.DISABLED)
            case_name_entry.delete(0, tk.END)
            stop_monitoring = True
            restart_monitoring()

    # Função para compactar a pasta
    def compactar_pasta():
        global case_directory
        
        if case_directory and os.path.exists(case_directory):
            
            # Procura pela pasta "Whatsapp" dentro de case_directory
            whatsapp_directory = os.path.join(case_directory, "Whatsapp")
            if os.path.exists(whatsapp_directory):
                # Caminho do arquivo a ser deletado
                contador_file_path = os.path.join(whatsapp_directory, "Contador_de_Capturas.txt")
                if os.path.exists(contador_file_path):
                    os.remove(contador_file_path)  # Deleta o arquivo
            
            # Procura pela pasta "Páginas Capturadas" dentro de case_directory
            paginas_capturadas_directory = os.path.join(case_directory, "Páginas Capturadas")
            if os.path.exists(paginas_capturadas_directory):
                # Caminho do arquivo a ser deletado
                contador_file_path = os.path.join(paginas_capturadas_directory, "Contador_de_Capturas.txt")
                if os.path.exists(contador_file_path):
                    os.remove(contador_file_path)  # Deleta o arquivo
            
            # Cria o arquivo zip no mesmo local
            zip_file_local = shutil.make_archive(case_directory, 'zip', case_directory)  # Compacta no mesmo local

            # Define o caminho para mover o zip para a área de trabalho
            desktop_path = Path.home() / "Desktop"
            zip_file_desktop = desktop_path / f"{os.path.basename(case_directory)}.zip"

            # Move o arquivo zip para a área de trabalho
            shutil.move(zip_file_local, zip_file_desktop)
            
            # Abre o PDF dentro do ZIP
            try:
                with zipfile.ZipFile(zip_file_desktop, 'r') as zip_ref:
                    # Extrai temporariamente o PDF
                    temp_dir = tempfile.gettempdir()
                    zip_ref.extract(nome_relatorio, temp_dir)
                    pdf_path = os.path.join(temp_dir, nome_relatorio)
                    
                    messagebox.showinfo("Relatório gerado",
                                "Relatório gerado com sucesso!\nOs arquivos do caso foram salvos na Área de Trabalho.", 
                                parent=tk_custodia_tech)
                    
                    # Abre o PDF com o visualizador padrão do sistema
                    os.startfile(pdf_path)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o PDF: {str(e)}", parent=tk_custodia_tech)
        
            shutil.rmtree(case_directory)
            case_directory = ""
            
        # Atualiza a lista de casos no combobox
        user_dir = str(Path.home())+'\\AppData\\Local\\CustodiaTech\\Casos'
        case_names_list = listar_casos_combobox(user_dir)
        case_names_list_sorted = sorted(case_names_list)
        case_name_entry['values'] = case_names_list_sorted
        case_name_entry.set('')  # Limpa a seleção atual

    def check_files():
        for filename in os.listdir(case_directory):
            if filename.startswith("Gravação"):
                file_path = os.path.join(case_directory, filename)

    def iniciar_progressbar():
        progressbar['value'] = 10

        thread = Thread(target=executar_compactacao)
        thread.start()

    def executar_compactacao():
        compactar_pasta()
        atualizar_progressbar(progressbar, 0)

        
    def fechar_caso():
        
        # Verifica a seleção do combobox
        if combo_var.get() == COLETA_PROBATORIA:
            
            if valida_campo_preenchido(numero_procedimento_entry, notebook, tab2, "CAMPO OBRIGATÓRIO"):
                return
            if valida_campo_preenchido(operador_nome_entry, notebook, tab2, "CAMPO OBRIGATÓRIO"):
                return
            if valida_campo_preenchido(operador_matricula_entry, notebook, tab2, "CAMPO OBRIGATÓRIO"):
                return
            if valida_campo_preenchido(operador_orgao_entry, notebook, tab2, "CAMPO OBRIGATÓRIO"):
                return

            if valida_campo_cpf(denunciante_nome_entry, denunciante_cpf_entry, notebook, tab2):
                return
            
            if valida_campo_cpf(testemunha1_nome_entry, testemunha1_cpf_entry, notebook, tab2):
                return
            
            if valida_campo_cpf(testemunha2_nome_entry, testemunha2_cpf_entry, notebook, tab2):
                return
    
        check_files()

        global case_directory, captured_screenshots, captured_screenshots_zip, videos_data, dados_gerais, metadados_total, file_data_youtube, file_data_x, file_data_instagram, file_data_tiktok, file_data_whatsapp, file_data_paginas
        
        if case_directory and (captured_screenshots or captured_screenshots_zip or videos_data or dados_gerais or metadados_total or file_data_youtube or file_data_x or file_data_instagram or file_data_tiktok or file_data_whatsapp or file_data_paginas):
            
            parar_thread_salvar_estado()

            # Deletar o arquivo JSON após no fechamento do caso
            json_file_path = os.path.join(case_directory, "CustodiaTech.config")
            if os.path.exists(json_file_path):
                os.remove(str(json_file_path))
            
            incluir_dados()

            adicionar_dados_no_relatorio(captured_screenshots, captured_screenshots_zip, videos_data, case_directory, dados_gerais, metadados_total,
                                             file_data_youtube, file_data_x, file_data_instagram, file_data_tiktok, file_data_whatsapp, file_data_paginas)
            iniciar_progressbar()
            
            # Remove os arquivos de captura de tela após gerar o PDF
            for screenshot_path in captured_screenshots:
                try:
                    os.remove(screenshot_path)
                    print(f"Imagem removida: {screenshot_path}")
                except Exception as e:
                    print(f"Erro ao remover a imagem {screenshot_path}: {e}")

            # Limpa as listas de evidências e campos do JSON
            videos_data = []
            captured_screenshots = []
            captured_screenshots_zip = []
            dados_gerais = {}
            file_data_youtube = []
            file_data_x = []
            file_data_instagram = []
            file_data_tiktok = []
            file_data_whatsapp = []
            metadados_total = []
            file_data_paginas = []

            # Limpa os dados gerais do operador e testemunhas
            numero_procedimento_entry.delete(0, tk.END)
            # operador_nome_entry.delete(0, tk.END)
            # operador_matricula_entry.delete(0, tk.END)
            # operador_orgao_entry.delete(0, tk.END)
            denunciante_nome_entry.delete(0, tk.END)
            denunciante_cpf_entry.delete(0, tk.END)
            denunciante_endereco_entry.delete(0, tk.END)
            denunciante_telefone_entry.delete(0, tk.END)
            testemunha1_nome_entry.delete(0, tk.END)
            testemunha1_cpf_entry.delete(0, tk.END)
            testemunha1_endereco_entry.delete(0, tk.END)
            testemunha1_telefone_entry.delete(0, tk.END)
            testemunha2_nome_entry.delete(0, tk.END)
            testemunha2_cpf_entry.delete(0, tk.END)
            testemunha2_endereco_entry.delete(0, tk.END)
            testemunha2_telefone_entry.delete(0, tk.END)

            botao_fechar_caso.config(state=tk.DISABLED)
            
            notebook.tab(1, state="disabled")
            tk_custodia_tech.after(0, case_name_entry.focus_set)
            
            registrar_acao(
                "Relatório criado",
                f"Novo relatório criado de nome {nome_relatorio} pelo usuário {usuario} no diretório {case_directory}"
            )
             
        else:
            messagebox.showinfo("Aviso", "Nenhum caso aberto para fechar ou nenhuma evidência capturada.", parent=tk_custodia_tech)

    def itens_atividades_do_caso():
        global case_directory, var_thread_atividades_caso, known_files

        var_thread_atividades_caso = True
        
        def is_file_ready(file_path, max_attempts=5, delay=0.2):
            """Verifica se o arquivo está pronto para ser acessado."""
            attempts = 0
            while attempts < max_attempts:
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return True
                time.sleep(delay)
                attempts += 1
            return False
        
        while var_thread_atividades_caso:
            if case_directory and os.path.exists(case_directory):
                try:
                    all_files = os.listdir(case_directory) # Pega todos os arquivos da pasta caso
                    files = set(f for f in all_files if f.endswith(".zip") or f.startswith(("Páginas", "Whatsapp")))
                    new_files = files - known_files  # Arquivos novos
                    removed_files = known_files - files  # Arquivos removidos

                    # Remover arquivos que não estão mais presentes
                    for file in removed_files:
                        for widget in frame_atividades_caso.winfo_children():
                            children = widget.winfo_children()
                            if len(children) > 1 and widget.winfo_children()[1].cget("text") == file:
                                widget.destroy()
                                break
                        known_files.discard(file)  # Atualiza o conjunto

                    # Adicionar arquivos novos
                    for file in new_files:
                        file_path = os.path.join(case_directory, file)
                        
                        # Obtém a data de criação do arquivo
                        creation_time = os.path.getctime(file_path)
                        current_time = datetime.fromtimestamp(creation_time).strftime('%d/%m/%Y %H:%M:%S')

                        if file not in known_files and is_file_ready(file_path):  # Verifica duplicatas
                            adicionar_item_atividades_do_caso(file, current_time)
                            known_files.add(file)  # Atualiza o conjunto

                except Exception as e:
                    print(f"Erro ao listar arquivos: {e}")

            time.sleep(1)  # Atualiza a cada 1 segundo

    # Função para excluir um arquivo
    def delete_file_or_directory(name):
        
        global ip_local
        global case_directory, captured_screenshots, captured_screenshots_zip, videos_data, dados_gerais, metadados_total, file_data_youtube, file_data_x, file_data_instagram, file_data_tiktok, file_data_whatsapp, file_data_paginas
        
        print(f"name: {name}")
        print(f"Captured Screenshot: {captured_screenshots}")
        print(f"Captured Screenshot Zip: {captured_screenshots_zip}")
        print(f"Videos Data: {videos_data}")
        print(f"Dados Gerais: {dados_gerais}")
        print(f"Metadados Total: {metadados_total}")
        print(f"File Data YouTube: {file_data_youtube}")
        print(f"File Data X: {file_data_x}")
        print(f"File Data Instagram: {file_data_instagram}")
        print(f"File Data TikTok: {file_data_tiktok}")
        print(f"File Data WhatsApp: {file_data_whatsapp}")
        print(f"File Data Paginas: {file_data_paginas}")
        
        path = os.path.join(case_directory, name)
        
        try:
            if os.path.isfile(path):
                os.remove(path)
                print(f"Arquivo {name} deletado com sucesso.")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Pasta {name} deletada com sucesso.")

            # Remover o widget correspondente da interface
            for widget in frame_atividades_caso.winfo_children():
                if widget.winfo_children()[1].cget("text") == name:
                    widget.destroy()
                    break
            
             # Remover o arquivo das listas, se presente
            full_path = os.path.abspath(path)  # Obtém o caminho absoluto do arquivo
            
            if full_path in captured_screenshots:
                captured_screenshots.remove(full_path)
                print(f"Arquivo {name} removido de captured_screenshots.")
            elif any(item[1]["Nome do Arquivo"] == name for item in captured_screenshots_zip):
                captured_screenshots_zip = [item for item in captured_screenshots_zip if item[1]["Nome do Arquivo"] != name]
                screenshot_name = name[:-4]  # Remove o ".zip"
                screenshot_path = os.path.join(case_directory, screenshot_name)
                if screenshot_path in captured_screenshots:
                    captured_screenshots.remove(screenshot_path)
                    print(f"Screenshot {screenshot_name} removido de captured_screenshots devido à exclusão do ZIP.")
                    print(f"Arquivo {name} removido de captured_screenshots_zip.")
            elif any(video["Caminho do Arquivo"] == full_path for video in videos_data):
                videos_data = [video for video in videos_data if video["Caminho do Arquivo"] != full_path]
                print(f"Arquivo {name} removido de videos_data.")
            elif name in dados_gerais:
                dados_gerais.pop(name, None)  # Remove a chave se existir
                print(f"Arquivo {name} removido de dados_gerais.")
            elif any(metadado.get("nome_do_arquivo") == name for metadado in metadados_total):
                metadados_total = [metadado for metadado in metadados_total if metadado.get("nome_do_arquivo") != name]
                print(f"Arquivo {name} removido de metadados_total.")
            elif any(file["nome_do_arquivo"] == name for file in file_data_youtube):
                file_data_youtube = [file for file in file_data_youtube if file["nome_do_arquivo"] != name]
                print(f"Arquivo {name} removido de file_data_youtube.")
            elif any(file["nome_do_arquivo"] == name for file in file_data_x):
                file_data_x = [file for file in file_data_x if file["nome_do_arquivo"] != name]
                print(f"Arquivo {name} removido de file_data_x.")
            elif any(file["nome_do_arquivo"] == name for file in file_data_instagram):
                file_data_instagram = [file for file in file_data_instagram if file["nome_do_arquivo"] != name]
                print(f"Arquivo {name} removido de file_data_instagram.")
            elif any(file["nome_do_arquivo"] == name for file in file_data_tiktok):
                file_data_tiktok = [file for file in file_data_tiktok if file["nome_do_arquivo"] != name]
                print(f"Arquivo {name} removido de file_data_tiktok.")
            elif any(file["nome_do_arquivo"] == name for file in file_data_whatsapp):
                file_data_whatsapp = [file for file in file_data_whatsapp if file["nome_do_arquivo"] != name]
                print(f"Arquivo {name} removido de file_data_whatsapp.")
            elif any(file["nome_do_arquivo"] == name for file in file_data_paginas):
                file_data_paginas = [file for file in file_data_paginas if file["nome_do_arquivo"] != name]
                print(f"Arquivo {name} removido de file_data_paginas.")

        except Exception as e:
            print(f"Erro ao deletar {name}: {e}")

    # Função para criar um item na lista de arquivos
    def adicionar_item_atividades_do_caso(file_name, current_time):
        frame = tk.Frame(frame_atividades_caso, borderwidth=1, relief='solid')

        fonte_base = 10  # Tamanho padrão da fonte
        tamanho_fonte = max(7, int(fonte_base * fator_escala))  # Evita fonte muito pequena
        
        if fator_escala < 0.9:
            ipadx = 10
        else:
            ipadx = 2
        
        frame.pack(fill='x', padx=5, pady=2, expand=True)

        time_label = tk.Label(frame, text=current_time, width=int(20*fator_escala), font=("Arial", tamanho_fonte), anchor='w')
        time_label.pack(side='left', fill='x', expand=True)

        file_label = tk.Label(frame, text=file_name, width=int(43*fator_escala), padx=int(ipadx * fator_escala), font=("Arial", tamanho_fonte), anchor='w')
        file_label.pack(side='left', fill='x', expand=True, ipadx=ipadx)

        delete_button = ttk.Button(
            frame, text="Excluir", command=lambda name=file_name: delete_file_or_directory(name))
        delete_button.pack(side='left', fill='x', expand=True, ipadx=2)
        
    def incluir_dados():

        global usuario

        # Capturar os valores dos campos de entrada
        numero_procedimento = numero_procedimento_entry.get()
        
        # Dados do Operador
        operador_nome = operador_nome_entry.get()
        operador_matricula = operador_matricula_entry.get()
        operador_orgao = operador_orgao_entry.get()
        
        # Dados do Denunciante
        denunciante_nome = denunciante_nome_entry.get()
        denunciante_cpf = denunciante_cpf_entry.get()
        denunciante_endereco = denunciante_endereco_entry.get()
        denunciante_telefone = denunciante_telefone_entry.get()
        
        # Dados da Testemunha 1
        testemunha1_nome = testemunha1_nome_entry.get()
        testemunha1_cpf = testemunha1_cpf_entry.get()
        testemunha1_endereco = testemunha1_endereco_entry.get()
        testemunha1_telefone = testemunha1_telefone_entry.get()

        # Dados da Testemunha 2
        testemunha2_nome = testemunha2_nome_entry.get()
        testemunha2_cpf = testemunha2_cpf_entry.get()
        testemunha2_endereco = testemunha2_endereco_entry.get()
        testemunha2_telefone = testemunha2_telefone_entry.get()

        # Criar o dicionário de dados gerais com apenas os campos preenchidos
        global dados_gerais 
        dados_gerais = {}


        if numero_procedimento:
            dados_gerais["Número do Procedimento"] = numero_procedimento
        
        if operador_nome:
            dados_gerais['Nome do Operador'] = operador_nome
        if operador_matricula:
            dados_gerais['Matrícula do Operador'] = operador_matricula
        if operador_orgao:
            dados_gerais['Orgão do Operador'] = operador_orgao

        if denunciante_nome:
            dados_gerais["Nome do Denunciante"] = denunciante_nome
        if denunciante_cpf:
            dados_gerais["CPF do Denunciante"] = denunciante_cpf
        if denunciante_endereco:
            dados_gerais["Endereço do Denunciante"] = denunciante_endereco
        if denunciante_telefone:
            dados_gerais["Telefone do Denunciante"] = denunciante_telefone

        if testemunha1_nome:
            dados_gerais["Nome da Testemunha 1"] = testemunha1_nome
        if testemunha1_cpf:
            dados_gerais["CPF da Testemunha 1"] = testemunha1_cpf
        if testemunha1_endereco:
            dados_gerais["Endereço da Testemunha 1"] = testemunha1_endereco
        if testemunha1_telefone:
            dados_gerais["Telefone da Testemunha 1"] = testemunha1_telefone

        if testemunha2_nome:
            dados_gerais["Nome da Testemunha 2"] = testemunha2_nome
        if testemunha2_cpf:
            dados_gerais["CPF da Testemunha 2"] = testemunha2_cpf
        if testemunha2_endereco:
            dados_gerais["Endereço da Testemunha 2"] = testemunha2_endereco
        if testemunha2_telefone:
            dados_gerais["Telefone da Testemunha 2"] = testemunha2_telefone

        #Grava os dados do operador
        selected_value = combo_var.get()
        if selected_value == COLETA_PROBATORIA:
            save_user_data(case_directory, usuario, dados_gerais)

    extrair_metadados_icon_path = get_resource_path("imagens\\metadados.png")
    facebook_icon_path = get_resource_path("imagens\\facebook.png")
    instagram_icon_path = get_resource_path("imagens\\instagram.png")
    logo_path = get_resource_path(CTLOGO)
    captura_tela_icon_path = get_resource_path("imagens\\captura_tela.png")
    tiktok_icon_path = get_resource_path("imagens\\tiktok.png")
    gravacao_icon_path = get_resource_path("imagens\\gravacao_tela.png")
    youtube_icon_path = get_resource_path("imagens\\youtube.png")
    x_icon_path = get_resource_path("imagens\\x.png")
    whatsapp_icon_path = get_resource_path("imagens\\whatsapp.png")
    captura_paginas_icon_path = get_resource_path("imagens\\captura_paginas.png")
    ajuda_icon_path = get_resource_path("imagens\\ajuda2.png")

    """ instagram_post_path = get_resource_path("imagens\\instagram_post.png")
    instagram_data_path = get_resource_path("imagens\\instagram_data.png")
    instagram_perfil_path = get_resource_path("imagens\\instagram_perfil.png")
    instagram_stories_path = get_resource_path("imagens\\instagram_stories.png")
    instagram_reels_path = get_resource_path("imagens\\instagram_reels.png") """

    def atualizar_tempo_sessao():
        global tempo_restante, var_thread_atividades_caso
        
        if tempo_restante > 1:
            
            minutos, segundos = divmod(tempo_restante, 60)
            tempo_restante_label.config(text=f'Tempo de Sessão: {
                                        minutos:02}:{segundos:02}')
            tempo_restante -= 1
            tk_custodia_tech.after(1000, atualizar_tempo_sessao)
        else:
            # Após a contagem zerar
            if not api_perdigueiro.autorizar():

                parar_thread_salvar_estado()
                
                messagebox.showinfo('Sessão expirada!',
                                    'É necessário refazer o logon.',  parent=tk_custodia_tech)
                
                dados_coleta_probatoria = {
                    "numero_procedimento": numero_procedimento_entry.get(),
                    "operador_nome": operador_nome_entry.get(),
                    "operador_matricula": operador_matricula_entry.get(),
                    "operador_orgao": operador_orgao_entry.get(),
                    "denunciante_nome": denunciante_nome_entry.get(),
                    "denunciante_cpf": denunciante_cpf_entry.get(),
                    "denunciante_endereco": denunciante_endereco_entry.get(),
                    "denunciante_telefone": denunciante_telefone_entry.get(),
                    "testemunha1_nome": testemunha1_nome_entry.get(),
                    "testemunha1_cpf": testemunha1_cpf_entry.get(),
                    "testemunha1_endereco": testemunha1_endereco_entry.get(),
                    "testemunha1_telefone": testemunha1_telefone_entry.get(),
                    "testemunha2_nome": testemunha2_nome_entry.get(),
                    "testemunha2_cpf": testemunha2_cpf_entry.get(),
                    "testemunha2_endereco": testemunha2_endereco_entry.get(),
                    "testemunha2_telefone": testemunha2_telefone_entry.get(),
                }

                # Criar o dicionário com os dados para salvar
                dados_para_salvar = {
                    "captured_screenshots": captured_screenshots,
                    "captured_screenshots_zip": captured_screenshots_zip,
                    "videos_data": videos_data,
                    "dados_gerais": dados_gerais,
                    "metadados_total": metadados_total,
                    "file_data_youtube": file_data_youtube,
                    "file_data_x": file_data_x,
                    "file_data_instagram": file_data_instagram,
                    "file_data_tiktok": file_data_tiktok,
                    "file_data_whatsapp": file_data_whatsapp,
                    "file_data_paginas": file_data_paginas
                }

                # Combinar os dois dicionários
                dados_completos = {**dados_coleta_probatoria, **dados_para_salvar}

                salvar_dados_json(dados_completos, case_directory)
            
                # Reinicializar known_files com os arquivos atuais na pasta
                known_files.clear()
                
                var_thread_atividades_caso = False
                
                tk_custodia_tech.destroy()
                tk_login.deiconify()

    #Salva estado da aplicação em um arquivo json
    def salvar_estado_aplicacao():
        
        try:
            # Criar o dicionário com os dados de coleta probatória
            dados_coleta_probatoria = {
                "numero_procedimento": numero_procedimento_entry.get(),
                "operador_nome": operador_nome_entry.get(),
                "operador_matricula": operador_matricula_entry.get(),
                "operador_orgao": operador_orgao_entry.get(),
                "denunciante_nome": denunciante_nome_entry.get(),
                "denunciante_cpf": denunciante_cpf_entry.get(),
                "denunciante_endereco": denunciante_endereco_entry.get(),
                "denunciante_telefone": denunciante_telefone_entry.get(),
                "testemunha1_nome": testemunha1_nome_entry.get(),
                "testemunha1_cpf": testemunha1_cpf_entry.get(),
                "testemunha1_endereco": testemunha1_endereco_entry.get(),
                "testemunha1_telefone": testemunha1_telefone_entry.get(),
                "testemunha2_nome": testemunha2_nome_entry.get(),
                "testemunha2_cpf": testemunha2_cpf_entry.get(),
                "testemunha2_endereco": testemunha2_endereco_entry.get(),
                "testemunha2_telefone": testemunha2_telefone_entry.get(),
            }

            # Criar o dicionário com os dados para salvar
            dados_para_salvar = {
                "captured_screenshots": captured_screenshots,
                "captured_screenshots_zip": captured_screenshots_zip,
                "videos_data": videos_data,
                "dados_gerais": dados_gerais,
                "metadados_total": metadados_total,
                "file_data_youtube": file_data_youtube,
                "file_data_x": file_data_x,
                "file_data_instagram": file_data_instagram,
                "file_data_tiktok": file_data_tiktok,
                "file_data_whatsapp": file_data_whatsapp,
                "file_data_paginas": file_data_paginas,
            }
            
            # Combinar os dois dicionários
            dados_completos = {**dados_coleta_probatoria, **dados_para_salvar}

            salvar_dados_json(dados_completos, case_directory)
            
            data_hora_local = datetime.now(fuso_local)
            timestamp_json = data_hora_local.strftime("%d/%m/%Y %H:%M:%S UTC %Z")
            print(f'Tentativa de salvamento do estado da aplicação em {timestamp_json}.')
            

        except Exception as e:
                print(f"Erro ao salvar estado da aplicação: {e}")

    # Função para salvar o estado periodicamente
    def salvar_estado_periodicamente():
        global thread_running_salvamento
        while thread_running_salvamento:
            try:
                salvar_estado_aplicacao()
            except Exception as e:
                print(f"Erro ao salvar estado da aplicação: {e}")

            # Aguarda 5 minutos (300 segundos), mas pode ser interrompido antes
            for _ in range(300):  
                if not thread_running_salvamento:
                    break
                time.sleep(1)

    # Iniciar a thread de salvamento automático
    def iniciar_thread_salvar_estado():
        global thread_running_salvamento
        thread_running_salvamento = True  # Garante que a thread possa ser iniciada novamente
        thread = threading.Thread(target=salvar_estado_periodicamente, daemon=True)
        thread.start()

    # Parar a thread de salvamento
    def parar_thread_salvar_estado():
        global thread_running_salvamento
        thread_running_salvamento = False
        print("Thread de salvamento interrompida.")

    def confirmar_fechamento():

        global var_thread_atividades_caso

        if messagebox.askokcancel("Sair", "Deseja realmente sair?", parent=tk_custodia_tech):
            try:
                parar_thread_salvar_estado()
                # Criar o dicionário com os dados de coleta probatória
                dados_coleta_probatoria = {
                    "numero_procedimento": numero_procedimento_entry.get(),
                    "operador_nome": operador_nome_entry.get(),
                    "operador_matricula": operador_matricula_entry.get(),
                    "operador_orgao": operador_orgao_entry.get(),
                    "denunciante_nome": denunciante_nome_entry.get(),
                    "denunciante_cpf": denunciante_cpf_entry.get(),
                    "denunciante_endereco": denunciante_endereco_entry.get(),
                    "denunciante_telefone": denunciante_telefone_entry.get(),
                    "testemunha1_nome": testemunha1_nome_entry.get(),
                    "testemunha1_cpf": testemunha1_cpf_entry.get(),
                    "testemunha1_endereco": testemunha1_endereco_entry.get(),
                    "testemunha1_telefone": testemunha1_telefone_entry.get(),
                    "testemunha2_nome": testemunha2_nome_entry.get(),
                    "testemunha2_cpf": testemunha2_cpf_entry.get(),
                    "testemunha2_endereco": testemunha2_endereco_entry.get(),
                    "testemunha2_telefone": testemunha2_telefone_entry.get(),
                }

                # Criar o dicionário com os dados para salvar
                dados_para_salvar = {
                    "captured_screenshots": captured_screenshots,
                    "captured_screenshots_zip": captured_screenshots_zip,
                    "videos_data": videos_data,
                    "dados_gerais": dados_gerais,
                    "metadados_total": metadados_total,
                    "file_data_youtube": file_data_youtube,
                    "file_data_x": file_data_x,
                    "file_data_instagram": file_data_instagram,
                    "file_data_tiktok": file_data_tiktok,
                    "file_data_whatsapp": file_data_whatsapp,
                    "file_data_paginas": file_data_paginas
                }
                
                # Combinar os dois dicionários
                dados_completos = {**dados_coleta_probatoria, **dados_para_salvar}

                salvar_dados_json(dados_completos, case_directory)

                var_thread_atividades_caso = False
                    
                if tk_custodia_tech.winfo_exists():
                    tk_custodia_tech.quit()
                    tk_custodia_tech.destroy()
                else:
                    print("A janela principal já foi destruída.")
            except Exception as e:
                print(f"Erro ao fechar a aplicação: {e}")
            finally:
                os._exit(0)  # Força o encerramento do programa

    tk_custodia_tech = tk.Toplevel()
    
    tk_custodia_tech.withdraw()
    
    tk_custodia_tech.iconbitmap(get_resource_path(icone_custodia))
    tk_custodia_tech.title("CustodiaTech – GAECO/MPRN")
    tk_custodia_tech.resizable(False, False)
    tk_custodia_tech.attributes('-fullscreen', False)
    
    tk_custodia_tech.attributes('-topmost', True)
    tk_custodia_tech.update()
    tk_custodia_tech.attributes('-topmost', False)
    tk_custodia_tech.update_idletasks()
    tk_custodia_tech.focus_force()
    
    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(tk_custodia_tech, "principal")
    
     # *** CÁLCULO DO FATOR DE ESCALA ***
    LARGURA_BASE = 585 
    fator_escala = LARGURA_CT / LARGURA_BASE
    print(f"Fator de Escala: {fator_escala}")

    global tema_configurado

    if not tema_configurado:
        Style(theme='simplex')
        tema_configurado = True


    #Logo
    LOGO_LARGURA_PERCENTUAL = 0.76
    LOGO_ALTURA_PERCENTUAL = 0.18
    
    #ComboBox
    COMBOBOX_LARGURA_BASE = 65
    # print(f"COMBOBOX_LARGURA_BASE: {COMBOBOX_LARGURA_BASE}")

    #Labels do Frame de Usuário e Tempo Restante
    LABEL_PADDING_X = 10
    LABEL_PADDING_Y = 1
    
    #Logo
    logo_image = PILImage.open(logo_path)
    logo_image = logo_image.resize((int(LARGURA_CT * LOGO_LARGURA_PERCENTUAL) , int(ALTURA_CT * LOGO_ALTURA_PERCENTUAL)), PILImage.BILINEAR)
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(tk_custodia_tech, image=logo_photo)
    logo_label.pack(pady=10)
    
    global tempo_restante, tempo_restante_label
    
    user_frame = tk.Frame(tk_custodia_tech, bg='#2C3E50')
    user_frame.pack(pady=1* fator_escala, padx=20 * fator_escala, fill='x', anchor='e')

    login_usuario = tk.Label(user_frame, text='Usuário: ' + usuario.upper(),
                             anchor='e', font=('Ivy', int(8), 'bold'), bg='#2C3E50', fg='#ECF0F1')
    login_usuario.pack(side='right', padx=LABEL_PADDING_X * fator_escala)

    session_time_frame = tk.Frame(tk_custodia_tech, bg='#2C3E50')
    session_time_frame.pack(pady=1* fator_escala, padx=20* fator_escala, fill='x', anchor='e')

    tempo_restante = 60 * 60
    tempo_restante_label = tk.Label(session_time_frame, text='Tempo de Sessão: 60:00', anchor='nw', font=(
        'Ivy 8 bold'), bg='#2C3E50', fg='#ECF0F1')
    tempo_restante_label.pack(side='right', padx=LABEL_PADDING_X, anchor='w')
    
     # *** AJUSTE DAS FONTES ***
    tamanho_fonte_base = 10 # Tamanho Base para as fontes
    captura_font = ('Arial', int(tamanho_fonte_base * fator_escala), 'bold')
    captura_font_entry = ('Arial', int((tamanho_fonte_base - 1) * fator_escala), 'bold') 
    
    #Notebook tab Captura
    notebook = ttk.Notebook(tk_custodia_tech)
    notebook.pack(padx=10 * fator_escala, expand=True)
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text='Captura')

    forms_frame = tk.Frame(tab1)
    forms_frame.pack(pady=5* fator_escala, padx=(20* fator_escala, 0), anchor='w')

    # Nome do caso
    case_name_label = tk.Label(
        forms_frame, text="Nome do Caso:", font=captura_font)
    case_name_label.grid(row=0, column=0, pady=5* fator_escala, sticky='e')
    
    case_name_entry_sv = tk.StringVar()
    case_name_entry_sv.trace_add("write", lambda *args: case_name_entry_sv.set(case_name_entry_sv.get().upper()))

    def listar_casos_combobox(pasta):
        # Verifica se a pasta existe, se não, cria a pasta
        if not os.path.exists(pasta):
            os.makedirs(pasta)  # Cria a pasta e quaisquer diretórios intermediários

        # Lista apenas os diretórios na pasta fornecida
        return [nome for nome in os.listdir(pasta) if os.path.isdir(os.path.join(pasta, nome))]

    # Dados da lista para o combo box
    user_dir = str(Path.home())+'\\AppData\\Local\\CustodiaTech\\Casos'
    case_names_list = listar_casos_combobox(user_dir)
    case_names_list_sorted = sorted(case_names_list)

    # Combobox nome do caso
    case_name_entry = ttk.Combobox(
        forms_frame,
        textvariable=case_name_entry_sv,
        bootstyle="dark",
        width=int(COMBOBOX_LARGURA_BASE),  # Largura ajustada
        font=captura_font_entry,
        values=case_names_list_sorted
    )
    case_name_entry.grid(row=0, column=1, padx=(0, 200 * fator_escala), sticky='w')
    
    def atualizar_texto_botao(*args):
        case_name = case_name_entry.get().strip()
        if case_name in case_names_list_sorted:
            selecionar_caminho_button.config(text="Abrir Caso Existente")
        else:
            selecionar_caminho_button.config(text="Criar Novo Caso")

    # Vincular a função ao evento de mudança no combobox
    case_name_entry_sv.trace_add("write", atualizar_texto_botao)
    case_name_entry.bind("<<ComboboxSelected>>", atualizar_texto_botao)
    
    # Função para sinalizar a seleção de texto após a escolha
    def on_selection(event):
        # Selecionar o texto no combobox
         case_name_entry.select_range(0, 'end')
        # Colocar o cursor no final do texto
         case_name_entry.icursor('end')
        # Garantir que o combobox esteja em foco para exibir o destaque
         case_name_entry.focus_set()
    
    # Adicionando evento ao combobox
    case_name_entry.bind("<<ComboboxSelected>>", on_selection)

    # Tipo do Relatório
    # Define o estilo CSS para o combobox
    style = ttk.Style()
    # Define a cor de fundo como branco
    style.configure("TCombobox", background="white")
    style.map("TCombobox", background=[("readonly", "white"), ("!readonly", "white")],
              fieldbackground=[("readonly", "white"), ("!readonly", "white")],
              foreground=[("readonly", "black"), ("!readonly", "black")],
              selectbackground=[("readonly", "f2f2f2"),
                                ("!readonly", "f2f2f2")],
              selectforeground=[("readonly", "black"), ("!readonly", "black")])
    style.configure("TButton", font=captura_font_entry)
    
    #Combobox Tipo de Relatório
    case_name_label = tk.Label(
        forms_frame, text="Tipo do Relatório:", font=captura_font)
    case_name_label.grid(row=1, column=0, padx=(10 * fator_escala, 0), pady=5* fator_escala, sticky='e')
    
    combo_var = tk.StringVar()
    combobox = ttk.Combobox(forms_frame, textvariable=combo_var, values=[
                            COLETA_PROBATORIA, "Procedimento Interno"], font=captura_font_entry, bootstyle="dark", width=int(COMBOBOX_LARGURA_BASE), state="readonly")
    combobox.grid(row=1, column=1, padx=(0, 200* fator_escala), sticky='w')
    combobox.current(0)
    
    def ajuda_messagebox():
        messagebox.showinfo('Tipo do Relatório',
                                    'Coleta Probatória: O material é coletado visando à destinação a um processo judicial. Para esse tipo de coleta, é obrigatório informar os dados do operador e do processo, sendo recomendável a inclusão de outros elementos, tais como: dados do denunciante e de duas testemunhas.\n\n'
                                    'Procedimento interno: O material coletado é voltado à atividade de inteligência, de modo que os dados gerais de identificação do operador e do processo encontram-se desabilitados para esse tipo de coleta.',  
                                    parent=tk_custodia_tech)
    
    style = Style()
    style.configure("Transparente.TButton", background="white", borderwidth=0, highlightthickness=0, activebackground="white", padding=(0,0))
    
    altura_combobox = combobox.winfo_reqheight()
    # print(f"Altura do Combobox: {altura_combobox}")

    # Carrega a imagem de ajuda
    ajuda_icon_image = PILImage.open(ajuda_icon_path).convert("RGBA")
    ajuda_icon_image = ajuda_icon_image.resize((int(altura_combobox/2), int(altura_combobox/2)), PILImage.BILINEAR)
    ajuda_icon_photo = ImageTk.PhotoImage(ajuda_icon_image)
    
    ajuda_button = ttk.Button(
        forms_frame,
        image=ajuda_icon_photo,
        command=lambda: ajuda_messagebox(),
        style="Transparente.TButton",
    )
    ajuda_button.image = ajuda_icon_photo  # Mantém uma referência
    ajuda_button.grid(row=1, column=0, padx=0 , sticky="w")
    
    #Botão "Criar novo caso"
    selecionar_caminho_button = ttk.Button(forms_frame, text="Criar Novo Caso", command=lambda: criar_novo_caso(case_name_entry, selecionar_caminho_button, combobox), width=int(COMBOBOX_LARGURA_BASE), bootstyle="primary", style="TButton")
    selecionar_caminho_button.grid(row=2, column=1, padx=(0, 200* fator_escala), pady=(0, 10* fator_escala))

    # Função para controlar cliques em botões
    def controle_cliques(botao, funcao):
        def wrapper():
            botao.config(state=tk.DISABLED)
            try:
                funcao()
            finally:
                tk_custodia_tech.after(2000, lambda: botao.config(state=tk.NORMAL))
        return wrapper
    
    
    buttons_frame = tk.Frame(tab1)
    buttons_frame.pack(pady=5 * fator_escala, padx=20 * fator_escala, fill="both", expand=True)

    # Configurar o grid para expansão uniforme
    buttons_frame.grid_columnconfigure(0, weight=1)
    buttons_frame.grid_columnconfigure(1, weight=1)
    buttons_frame.grid_columnconfigure(2, weight=1)
    buttons_frame.grid_columnconfigure(3, weight=1)
    buttons_frame.grid_columnconfigure(4, weight=1)
    buttons_frame.grid_rowconfigure(0, weight=1)
    buttons_frame.grid_rowconfigure(1, weight=1)

    # Limites mínimos e máximos dos botões
    BOTAO_LARGURA_MIN = 25
    BOTAO_LARGURA_MAX = 100
    BOTAO_ALTURA_MIN = 25
    BOTAO_ALTURA_MAX = 100

    BOTAO_LARGURA = max(BOTAO_LARGURA_MIN, min(int(65 * fator_escala), BOTAO_LARGURA_MAX))
    BOTAO_ALTURA = max(BOTAO_ALTURA_MIN, min(int(65 * fator_escala), BOTAO_ALTURA_MAX))
    
    print(f"BOTAO_LARGURA: {BOTAO_LARGURA}\nBOTAO_ALTURA: {BOTAO_ALTURA}")

    #Padding dos botões
    padx_botao = int(7 * fator_escala)
    pady_botao = int(5 * fator_escala)
    
    captura_tela_em_execucao = False
    
    def pressionar_botao_captura_tela():
        """Simula o clique no botão de captura de tela."""
        nonlocal captura_tela_em_execucao
        
        print(f"botao_captura_tela.state(): {botao_captura_tela.state()}")
        if "disabled" in botao_captura_tela.state():
            return
        
        if not captura_tela_em_execucao:
            captura_tela_em_execucao = True
            tk_custodia_tech.after(0, lambda: abrir_janela_captura_tela())

    def abrir_janela_captura_tela():
        """Abre a janela_captura_tela dentro do loop do tkinter"""
        nonlocal captura_tela_em_execucao
        
        if "disabled" in botao_captura_tela.state():
            captura_tela_em_execucao = False
            return
        
        try:
            # Abre a janela_captura_tela corretamente
            janela_captura_tela(
                tk_custodia_tech,
                case_directory,
                get_resource_path(icone_custodia),
                usuario,
                captured_screenshots,
                captured_screenshots_zip
            )
        finally:
             captura_tela_em_execucao = False

    captura_tela_icon_image = PILImage.open(captura_tela_icon_path)
    captura_tela_icon_image = captura_tela_icon_image.resize(
        (BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    captura_tela_icon_photo = ImageTk.PhotoImage(captura_tela_icon_image)

    botao_captura_tela = ttk.Button(
        buttons_frame, image=captura_tela_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    botao_captura_tela.grid(row=0, column=0, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_captura_tela.config(command=controle_cliques(
        botao_captura_tela, lambda: janela_captura_tela(
            tk_custodia_tech, 
            case_directory, 
            get_resource_path(icone_custodia),
            usuario, 
            captured_screenshots, 
            captured_screenshots_zip
        )))

    Hovertip(botao_captura_tela, 'Captura de Tela', 0)
    # Configurar a escuta do atalho "Alt + Print Screen"
    keyboard.add_hotkey("alt+print screen", pressionar_botao_captura_tela)

    # Botão de gravação de vídeo do navegador
    gravacao_icon_image = PILImage.open(gravacao_icon_path)
    gravacao_icon_image = gravacao_icon_image.resize(
        (BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    gravacao_icon_photo = ImageTk.PhotoImage(gravacao_icon_image)

    botao_gravacao_tela = ttk.Button(buttons_frame, image=gravacao_icon_photo,
                                 bootstyle="dark-outline", state=tk.DISABLED)
    botao_gravacao_tela.grid(row=0, column=1, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_gravacao_tela.config(command=controle_cliques(
        botao_gravacao_tela, lambda: iniciar_gravacao_tela(case_directory, videos_data)))

    Hovertip(botao_gravacao_tela, 'Captura de Vídeo do Navegador', 0)

    # Botão de extração de metadados
    extrair_metadados_icon_image = PILImage.open(extrair_metadados_icon_path)
    extrair_metadados_icon_image = extrair_metadados_icon_image.resize(
        (BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    extrair_metadados_icon_photo = ImageTk.PhotoImage(
        extrair_metadados_icon_image)

    botao_extrair_metadados = ttk.Button(
        buttons_frame, image=extrair_metadados_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    botao_extrair_metadados.grid(row=0, column=2, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_extrair_metadados.config(
        command=lambda: janela_extrair_metadados(
            tk_custodia_tech, 
            case_directory, 
            usuario, 
            get_resource_path(icone_custodia),
            metadados_total
        )
    )

    Hovertip(botao_extrair_metadados, 'Extração de Metadados', 0)

    # Botão de Captura de Página
    captura_paginas_icon_image = PILImage.open(captura_paginas_icon_path)
    captura_paginas_icon_image = captura_paginas_icon_image.resize((BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    captura_paginas_icon_photo = ImageTk.PhotoImage(captura_paginas_icon_image)

    botao_captura_paginas = ttk.Button(
        buttons_frame, image=captura_paginas_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    botao_captura_paginas.grid(row=0, column=3, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_captura_paginas.config(command=lambda: iniciar_tela_captura_paginas(
        tk_custodia_tech, 
        case_directory, 
        usuario, 
        file_data_paginas, 
        get_resource_path(icone_custodia),
        botao_captura_paginas  # Passa o botão como parâmetro
    ))

    Hovertip(botao_captura_paginas, 'Captura de Múltiplas Páginas Web', 0)

    # Botão do Instagram
    instagram_icon_image = PILImage.open(instagram_icon_path)
    instagram_icon_image = instagram_icon_image.resize(
        (BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    instagram_icon_photo = ImageTk.PhotoImage(instagram_icon_image)

    botao_instagram = ttk.Button(
        buttons_frame, image=instagram_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    botao_instagram.grid(row=0, column=4, padx=padx_botao, pady=pady_botao, sticky="nsew")
    # botao_instagram.config(command=controle_cliques(
    #     botao_instagram, instaloader_janela))

    Hovertip(botao_instagram, 'Captura de Instagram [Desabilitado]', 0)

    # Botão do Youtube
    youtube_icon_image = PILImage.open(youtube_icon_path)
    youtube_icon_image = youtube_icon_image.resize((BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    youtube_icon_photo = ImageTk.PhotoImage(youtube_icon_image)

    botao_youtube = ttk.Button(
        buttons_frame, image=youtube_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    botao_youtube.grid(row=1, column=0, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_youtube.config(command=controle_cliques(
        botao_youtube, lambda: Thread(
            target=janela_youtube, 
            args=(
                tk_custodia_tech, 
                case_directory, 
                usuario, 
                file_data_youtube, 
                get_resource_path(icone_custodia))).start()))

    Hovertip(botao_youtube, 'Captura de Youtube [Download de Vídeos]', 0)

    # Botão do Tiktok
    tiktok_icon_image = PILImage.open(tiktok_icon_path)
    tiktok_icon_image = tiktok_icon_image.resize((BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    tiktok_icon_photo = ImageTk.PhotoImage(tiktok_icon_image)

    botao_tiktok = ttk.Button(
        buttons_frame, image=tiktok_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    botao_tiktok.grid(row=1, column=1, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_tiktok.config(command=controle_cliques(
        botao_tiktok, lambda: Thread(
            target=janela_tiktok, 
            args=(
                tk_custodia_tech, 
                case_directory, 
                usuario, 
                file_data_tiktok, 
                get_resource_path(icone_custodia))).start()))

    Hovertip(botao_tiktok, 'Captura de Tiktok', 0)

    # Botão do X (Twitter)
    x_icon_image = PILImage.open(x_icon_path)
    x_icon_image = x_icon_image.resize((BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    x_icon_photo = ImageTk.PhotoImage(x_icon_image)

    botao_x_twitter = ttk.Button(buttons_frame, image=x_icon_photo,
                          bootstyle="dark-outline", state=tk.DISABLED)
    botao_x_twitter.grid(row=1, column=2, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_x_twitter.config(command=controle_cliques(
        botao_x_twitter, lambda: janela_x_twitter(
            tk_custodia_tech, 
            case_directory, 
            file_data_x, 
            usuario,
            get_resource_path(icone_custodia))))

    Hovertip(botao_x_twitter, 'Captura de X (Antigo Twitter)', 0)

    # Botão do Whatsapp
    whatsapp_icon_image = PILImage.open(whatsapp_icon_path)
    whatsapp_icon_image = whatsapp_icon_image.resize(
        (BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    whatsapp_icon_photo = ImageTk.PhotoImage(whatsapp_icon_image)

    botao_whatsapp = ttk.Button(
        buttons_frame, image=whatsapp_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    botao_whatsapp.grid(row=1, column=3, padx=padx_botao, pady=pady_botao, sticky="nsew")
    botao_whatsapp.config(command=lambda: janela_whatsapp(
            tk_custodia_tech, 
            case_directory, 
            usuario, 
            file_data_whatsapp,
            botao_whatsapp, 
            get_resource_path(icone_custodia)))

    Hovertip(botao_whatsapp,
             'Captura de Whatsapp [Captura de Perfil, Conversa, Interlocutor e Lista de Contatos]', 0)

    # Botão do Facebook
    facebook_icon_image = PILImage.open(facebook_icon_path)
    facebook_icon_image = facebook_icon_image.resize(
        (BOTAO_LARGURA, BOTAO_ALTURA), PILImage.BILINEAR)
    facebook_icon_photo = ImageTk.PhotoImage(facebook_icon_image)

    facebook_button = ttk.Button(
        buttons_frame, image=facebook_icon_photo, bootstyle="dark-outline", state=tk.DISABLED)
    facebook_button.grid(row=1, column=4, padx=padx_botao, pady=pady_botao, sticky="nsew")
    facebook_button.config(state=tk.DISABLED)

    Hovertip(facebook_button, 'Captura de Facebook [Desabilitado]', 0)
    
    LENGTH_PROGRESSBAR = int(LARGURA_CT * 0.68)

    if ALTURA_CT > 700:
        pady_gerar_relatorio_frame = 5
    else:
        pady_gerar_relatorio_frame = 1

    gerar_relatorio_frame = tk.Frame(tab1)
    gerar_relatorio_frame.pack(pady=pady_gerar_relatorio_frame * fator_escala, expand=True, fill='x')
    
    botao_fechar_caso = ttk.Button(gerar_relatorio_frame, text="Fechar Caso e Gerar Relatório",
                                   command=fechar_caso, width=int(LARGURA_CT * 0.1 * fator_escala), bootstyle="primary-outline")
    botao_fechar_caso.pack(pady=pady_gerar_relatorio_frame * fator_escala)  # Usa pack
    botao_fechar_caso.config(state=tk.DISABLED)

    progressbar = ttk.Progressbar(gerar_relatorio_frame, orient='horizontal',
                                  length=LENGTH_PROGRESSBAR, mode='determinate', bootstyle="warning-striped")
    progressbar.pack(pady=pady_gerar_relatorio_frame * fator_escala)  # Usa pack

   # Lista de atividades do caso
    lista_atividade_frame = ttk.LabelFrame(
        tab1, text="Atividades do caso", bootstyle="dark")
    lista_atividade_frame.pack(pady=(0,int(5 * fator_escala)), padx=int(5 * fator_escala), fill='both', expand=True)

    # Criar canvas
    canvas_atividades_frame = tk.Canvas(lista_atividade_frame)
    canvas_atividades_frame.pack(side='left', fill='both', expand=True)

    # Criar barra de rolagem
    scrollbar = tk.Scrollbar(lista_atividade_frame,
                             orient='vertical', command=canvas_atividades_frame.yview)
    scrollbar.pack(side='right', fill='y')

    # Configurar o canvas
    canvas_atividades_frame.configure(yscrollcommand=scrollbar.set)
    canvas_atividades_frame.bind('<Configure>', lambda e: canvas_atividades_frame.configure(
        scrollregion=canvas_atividades_frame.bbox('all')))
    
    if fator_escala < 0.8:
        # Definir uma altura máxima para o canvas
        canvas_atividades_frame.config(height=70)
    else:
        canvas_atividades_frame.config(height=160)

    # Criar frame interno
    frame_atividades_caso = tk.Frame(canvas_atividades_frame)
    canvas_atividades_frame.create_window((0, 0), window=frame_atividades_caso, anchor='nw')
    
    # Configurar o frame interno
    frame_atividades_caso.bind("<Configure>", lambda e: canvas_atividades_frame.configure(
        scrollregion=canvas_atividades_frame.bbox("all")))
    
    # Adicionando a label abaixo do lista_atividade_frame
    copyright_label = tk.Label(tk_custodia_tech, text="© 2025 CUSTODIATECH. Ministério Público do Rio Grande do Norte.\nTodos os direitos reservados.", font=captura_font, anchor='center')
    copyright_label.pack(pady=0) 

    # Função para lidar com o evento de rolagem do mouse
    def _on_mousewheel(event):
        canvas_atividades_frame.yview_scroll(int(-1*(event.delta/120)), "units")

    # Função para lidar com o evento de entrada do mouse
    def _bound_to_mousewheel(event):
        canvas_atividades_frame.bind_all("<MouseWheel>", _on_mousewheel)

    # Função para lidar com o evento de saída do mouse
    def _unbound_to_mousewheel(event):
        canvas_atividades_frame.unbind_all("<MouseWheel>")

    # Vincular eventos de rolagem apenas ao canvas_atividades_frame
    canvas_atividades_frame.bind("<Enter>", _bound_to_mousewheel)
    canvas_atividades_frame.bind("<Leave>", _unbound_to_mousewheel)

    # Para sistemas baseados em Unix (Linux, macOS)
    canvas_atividades_frame.bind("<Button-4>", lambda e: canvas_atividades_frame.yview_scroll(-1, "units"))
    canvas_atividades_frame.bind("<Button-5>", lambda e: canvas_atividades_frame.yview_scroll(1, "units"))
    
    # Crie um estilo para o campo de entrada com texto vermelho
    style.configure('Red.TEntry', foreground='red')

    # Verificação do CPF do Denunciante ao sair do campo
    def verificar_cpf_denunciante(event):
        verificar_cpf(denunciante_cpf_entry)

    # Verificação do CPF da Testemunha 1 ao sair do campo
    def verificar_cpf_testemunha1(event):
        verificar_cpf(testemunha1_cpf_entry)

    # Verificação do CPF da Testemunha 2 ao sair do campo
    def verificar_cpf_testemunha2(event):
        verificar_cpf(testemunha2_cpf_entry)
    
    # Dados Gerais
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text='Dados Gerais')

    notebook.tab(1, state="disabled")

    # Cria um Canvas para permitir a rolagem
    canvas = tk.Canvas(tab2)
    scroll_y = ttk.Scrollbar(tab2, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Configura o scrollable_frame para se ajustar ao tamanho do canvas
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Adiciona o scrollable_frame ao canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Adiciona a barra de rolagem ao canvas
    canvas.configure(yscrollcommand=scroll_y.set)

    # Organiza o canvas e a barra de rolagem
    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    # Define a largura máxima do frame
    criminal_frame = tk.Frame(scrollable_frame)
    criminal_frame.pack(anchor='w', padx=0, pady=0)

    # Define a largura máxima do frame
    criminal_frame.config(width=1)  # Defina a largura máxima desejada
    criminal_frame.pack_propagate(False)  # Impede que o frame ajuste seu tamanho automaticamente
    
    def toggle_scroll():
        if ALTURA_CT > 700:
            scroll_y.pack_forget()  # Oculta a barra de rolagem
            canvas.unbind_all("<MouseWheel>")  # Desvincula a rolagem do mouse
        else:
            scroll_y.pack(side="right", fill="y")  # Exibe a barra de rolagem
            canvas.bind_all("<MouseWheel>", on_mouse_wheel)


    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Vincula o evento de rolagem do mouse ao canvas
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Para Windows
    # canvas.bind_all("<Button-4>", on_mouse_wheel)  # Para Linux
    # canvas.bind_all("<Button-5>", on_mouse_wheel)  # Para Linux
    
    # Chama a função de toggle_scroll ao iniciar
    toggle_scroll()

    # Adiciona um evento para verificar a altura da janela quando ela for redimensionada
    tab2.bind("<Configure>", lambda e: toggle_scroll())

    # Bloco: Dados gerais do Processo
    width_entry = int(LARGURA_CT * 0.1)
    print(f"width_entry: {width_entry}")

    if ALTURA_CT > 700:
        label_font = ('Arial', 10, 'bold')
        entry_font = ('Arial', 8)
    else:
        label_font = ('Arial', 8, 'bold')
        entry_font = ('Arial', 7)
        
    def next_entry(event):
        """Move o foco para o próximo campo de entrada."""
        widget = event.widget
        next_widget = widget.tk_focusNext()
        
        # Se o proximo campo não for um Entry e for um Combobox, pula para o próximo
        if next_widget.winfo_class() != 'TEntry':
            next_widget = next_widget.tk_focusNext()
        
        next_widget.focus_set()
    
    def voltar_tab1(event):
        """Volta para a tab1 ao pressionar a tecla Enter."""
        notebook.select(0)
        
    # Cria uma StringVar e associa a função de rastreamento
    numero_procedimento_entry_sv = tk.StringVar()
    numero_procedimento_entry_sv.trace_add("write", lambda *args: numero_procedimento_entry_sv.set(numero_procedimento_entry_sv.get().upper()))
    operador_nome_entry_sv = tk.StringVar()
    operador_nome_entry_sv.trace_add("write", lambda *args: operador_nome_entry_sv.set(operador_nome_entry_sv.get().upper()))
    operador_orgao_entry_sv = tk.StringVar()
    operador_orgao_entry_sv.trace_add("write", lambda *args: operador_orgao_entry_sv.set(operador_orgao_entry_sv.get().upper()))
    denunciante_nome_entry_sv = tk.StringVar()
    denunciante_nome_entry_sv.trace_add("write", lambda *args: denunciante_nome_entry_sv.set(denunciante_nome_entry_sv.get().upper()))
    testemunha1_nome_entry_sv = tk.StringVar()
    testemunha1_nome_entry_sv.trace_add("write", lambda *args:  testemunha1_nome_entry_sv.set( testemunha1_nome_entry_sv.get().upper()))
    testemunha2_nome_entry_sv = tk.StringVar()
    testemunha2_nome_entry_sv.trace_add("write", lambda *args: testemunha2_nome_entry_sv.set(testemunha2_nome_entry_sv.get().upper()))

    numero_procedimento_label = tk.Label(criminal_frame, text="Número do Procedimento *", state='normal', font=label_font)
    numero_procedimento_label.grid(row=1, column=0, sticky='e')  # Ajuste no pady

    numero_procedimento_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal', font=entry_font, textvariable= numero_procedimento_entry_sv)
    numero_procedimento_entry.grid(row=1, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    # Definir o foco em um Label ou no próprio notebook
    tab2.bind("<Visibility>", lambda event: notebook.focus_set())
    
    # Bloco: Dados do Operador
    operador_nome_label = tk.Label(criminal_frame, text="Nome do Operador *", state='normal', font=label_font)
    operador_nome_label.grid(row=2, column=0, pady=2, sticky='e')  # Ajuste no pady

    operador_nome_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font, textvariable=operador_nome_entry_sv)
    operador_nome_entry.grid(row=2, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    operador_matricula_label = tk.Label(criminal_frame, text="Matrícula do Operador *", state='normal', font=label_font)
    operador_matricula_label.grid(row=3, column=0, pady=2, sticky='e')  # Ajuste no pady

    operador_matricula_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    operador_matricula_entry.grid(row=3, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    operador_orgao_label = tk.Label(criminal_frame, text="Órgão do Operador *", state='normal', font=label_font)
    operador_orgao_label.grid(row=4, column=0, pady=2, sticky='e')  # Ajuste no pady

    operador_orgao_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font, textvariable=operador_orgao_entry_sv)
    operador_orgao_entry.grid(row=4, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    # Bloco: Denunciante
    denunciante_nome_label = tk.Label(criminal_frame, text="Nome do Denunciante", state='normal', font=label_font)
    denunciante_nome_label.grid(row=5, column=0, pady=2, sticky='e')  # Ajuste no pady

    denunciante_nome_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font, textvariable=denunciante_nome_entry_sv)
    denunciante_nome_entry.grid(row=5, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    denunciante_cpf_label = tk.Label(criminal_frame, text="CPF do Denunciante", state='normal', font=label_font)
    denunciante_cpf_label.grid(row=6, column=0, pady=2, sticky='e')  # Ajuste no pady

    denunciante_cpf_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    denunciante_cpf_entry.grid(row=6, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady
    
    denunciante_cpf_entry.bind("<FocusOut>", verificar_cpf_denunciante)

    denunciante_endereco_label = tk.Label(criminal_frame, text="Endereço do Denunciante", state='normal', font=label_font)
    denunciante_endereco_label.grid(row=7, column=0, pady=2, sticky='e')  # Ajuste no pady

    denunciante_endereco_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    denunciante_endereco_entry.grid(row=7, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    denunciante_telefone_label = tk.Label(criminal_frame, text="Telefone do Denunciante", state='normal', font=label_font)
    denunciante_telefone_label.grid(row=8, column=0, pady=2, sticky='e')  # Ajuste no pady

    denunciante_telefone_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    denunciante_telefone_entry.grid(row=8, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    # Bloco: Testemunha 1
    testemunha1_nome_label = tk.Label(criminal_frame, text="Nome da Testemunha 1", state='normal', font=label_font)
    testemunha1_nome_label.grid(row=9, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha1_nome_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font, textvariable=testemunha1_nome_entry_sv)
    testemunha1_nome_entry.grid(row=9, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    testemunha1_cpf_label = tk.Label(criminal_frame, text="CPF da Testemunha 1", state='normal', font=label_font)
    testemunha1_cpf_label.grid(row=10, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha1_cpf_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    testemunha1_cpf_entry.grid(row=10, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady
    
    testemunha1_cpf_entry.bind("<FocusOut>", verificar_cpf_testemunha1)

    testemunha1_endereco_label = tk.Label(criminal_frame, text="Endereço da Testemunha 1", state='normal', font=label_font)
    testemunha1_endereco_label.grid(row=11, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha1_endereco_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    testemunha1_endereco_entry.grid(row=11, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    testemunha1_telefone_label = tk.Label(criminal_frame, text="Telefone da Testemunha 1", state='normal', font=label_font)
    testemunha1_telefone_label.grid(row=12, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha1_telefone_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    testemunha1_telefone_entry.grid(row=12, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    # Bloco: Testemunha 2
    testemunha2_nome_label = tk.Label(criminal_frame, text="Nome da Testemunha 2", state='normal', font=label_font)
    testemunha2_nome_label.grid(row=13, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha2_nome_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font, textvariable=testemunha2_nome_entry_sv)
    testemunha2_nome_entry.grid(row=13, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    testemunha2_cpf_label = tk.Label(criminal_frame, text="CPF da Testemunha 2", state='normal', font=label_font)
    testemunha2_cpf_label.grid(row=14, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha2_cpf_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    testemunha2_cpf_entry.grid(row=14, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    testemunha2_endereco_label = tk.Label(criminal_frame, text="Endereço da Testemunha 2", state='normal', font=label_font)
    testemunha2_endereco_label.grid(row=15, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha2_endereco_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    testemunha2_endereco_entry.grid(row=15, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    testemunha2_telefone_label = tk.Label(criminal_frame, text="Telefone da Testemunha 2", state='normal', font=label_font)
    testemunha2_telefone_label.grid(row=16, column=0, pady=2, sticky='e')  # Ajuste no pady

    testemunha2_telefone_entry = ttk.Entry(criminal_frame, bootstyle="dark", width=width_entry, state='normal',  font=entry_font)
    testemunha2_telefone_entry.grid(row=16, column=1, padx=(5, 0), pady=2, sticky='w')  # Ajuste no padx e pady

    testemunha2_cpf_entry.bind("<FocusOut>", verificar_cpf_testemunha2)
    
    numero_procedimento_entry.bind("<Return>", next_entry)
    operador_nome_entry.bind("<Return>", next_entry)
    operador_matricula_entry.bind("<Return>", next_entry)
    operador_orgao_entry.bind("<Return>", next_entry)
    denunciante_nome_entry.bind("<Return>", next_entry)
    denunciante_cpf_entry.bind("<Return>", next_entry)
    denunciante_endereco_entry.bind("<Return>", next_entry)
    denunciante_telefone_entry.bind("<Return>", next_entry)
    testemunha1_nome_entry.bind("<Return>", next_entry)
    testemunha1_cpf_entry.bind("<Return>", next_entry)
    testemunha1_endereco_entry.bind("<Return>", next_entry)
    testemunha1_telefone_entry.bind("<Return>", next_entry)
    testemunha2_nome_entry.bind("<Return>", next_entry)
    testemunha2_cpf_entry.bind("<Return>", next_entry)
    testemunha2_endereco_entry.bind("<Return>", next_entry)
    testemunha2_telefone_entry.bind("<Return>", voltar_tab1)
    
    def mostrar_notas(frame_notas):
        """
        Carrega e exibe as notas de atualização no frame fornecido.
        """
        try:
            import modulos.notas_atualizacao.interface_notas_atualizacao as notas
            notas.preencher_frame_notas(frame_notas, versao_atual, LARGURA_CT, ALTURA_CT, fator_escala, notebook, tab1)

        except ImportError:
            print("Erro ao importar módulo de notas de atualização.")
            label_erro = tk.Label(
                frame_notas,
                text="Erro ao carregar as notas de atualização",
                font=("Arial", int(10 * fator_escala))
            )
            label_erro.pack()
    
    # Aba Sobre - Notas de Versão
    tab_sobre = ttk.Frame(notebook)
    notebook.add(tab_sobre, text='Sobre')
    
    frame_notas = tk.Frame(tab_sobre)
    frame_notas.pack(pady=10, padx=0, fill='both', expand=True)
    
    mostrar_notas(frame_notas)
    
    # Verificação se é o primeiro login
    if PRIMEIRO_LOGIN == 'True':
        notebook.select(tab_sobre)  # Troca para a aba 'Sobre'
        env.atualizar_env("PRIMEIRO_LOGIN", "False") # Altera o valor para false no env

    
    tk_custodia_tech.after(0, limpar_relatorios_temp)
    tk_custodia_tech.deiconify()
    atualizar_tempo_sessao()
    tk_custodia_tech.protocol("WM_DELETE_WINDOW", confirmar_fechamento)

    # Iniciar salvamento automático ao iniciar a interface
    tk_custodia_tech.after(2000, iniciar_thread_salvar_estado)

    tk_custodia_tech.after(0, case_name_entry.focus_set)

    tk_custodia_tech.mainloop()

interface_login()
