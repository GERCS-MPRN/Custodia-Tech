import os
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread

from ttkbootstrap import Style

from modulos.captura_paginas.captura_paginas import iniciar_captura_de_paginas
from utils.metadata import calculate_hash, get_file_metadata
from utils.monitor import centraliza_janela_no_monitor_ativo


def trata_urls(conteudo):
    links = []
    for link in conteudo.split("\n"):
        if link != "":
            if not link.startswith("http:") and not link.startswith("https:"):
                links.append("https://" + link)
            else:
                links.append(link)
    return links


def iniciar_tela_captura_paginas(
    tk_custodia_tech,
    case_directory,
    usuario,
    file_data_paginas,
    icone_custodia,
    captura_paginas_button,
):
    urls = []

    def abrir_arquivo():
        arquivo = filedialog.askopenfilename(
            title="Selecione um arquivo .txt",
            filetypes=[("Arquivos de Texto", "*.txt")],
        )
        if arquivo:
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                    texto_saida.delete("1.0", tk.END)
                    texto_saida.insert(tk.END, conteudo)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{e}")
        else:
            messagebox.showinfo("Informação", "Nenhum arquivo foi selecionado.")

    def carregar_conteudo_thread(file_data_paginas):
        try:
            captura_paginas_button.config(state="disabled")
            conteudo = texto_saida.get("1.0", tk.END).strip()
            links = trata_urls(conteudo)
            if len(links) > 20:
                messagebox.showwarning(
                    "Aviso", "O limite de captura é de 20 (vinte) páginas por vez!"
                )
            elif not conteudo:
                messagebox.showwarning(
                    "Aviso", "A caixa de texto está vazia. Nada foi carregado."
                )
            else:
                tk_captura_paginas.destroy()
                zip_files = iniciar_captura_de_paginas(case_directory, links)

                for zip_file_path in zip_files:
                    hashes = calculate_hash(
                        zip_file_path, algorithms=["md5", "sha1", "sha256"]
                    )
                    metadata = get_file_metadata(zip_file_path)
                    file_data_paginas.append(
                        {
                            "nome_do_arquivo": os.path.basename(zip_file_path),
                            "hashes": hashes,
                            "metadata": metadata,
                        }
                    )
                    print(f"Arquivo: {zip_file_path}")
                    print(f"Hashes: {hashes}")
                    print(f"Metadados: {metadata}")
                    print("-" * 40)
        finally:
            captura_paginas_button.config(state="normal")

    def ignorar_conteudo_thread(file_data_paginas):
        try:
            captura_paginas_button.config(state="disabled")
            tk_captura_paginas.destroy()
            links = ["https://www.google.com"]
            zip_files = iniciar_captura_de_paginas(case_directory, links)

            for zip_file_path in zip_files:
                hashes = calculate_hash(
                    zip_file_path, algorithms=["md5", "sha1", "sha256"]
                )
                metadata = get_file_metadata(zip_file_path)
                file_data_paginas.append(
                    {
                        "nome_do_arquivo": os.path.basename(zip_file_path),
                        "hashes": hashes,
                        "metadata": metadata,
                    }
                )
                print(f"Arquivo: {zip_file_path}")
                print(f"Hashes: {hashes}")
                print(f"Metadados: {metadata}")
                print("-" * 40)
        finally:
            captura_paginas_button.config(state="normal")

    tk_captura_paginas = tk.Toplevel(tk_custodia_tech)
    tk_captura_paginas.withdraw()
    tk_captura_paginas.iconbitmap(icone_custodia)
    tk_captura_paginas.title("Captura Dinâmica de Páginas")
    tk_captura_paginas.resizable(False, False)
    tk_captura_paginas.attributes("-fullscreen", False)

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(
        tk_captura_paginas, "captura_paginas"
    )

    # Calcular fator de escala com base na largura original (480) da tela de captura de páginas
    LARGURA_ORIGINAL = 480  # Largura base da tela de captura de páginas
    fator_escala = LARGURA_CT / LARGURA_ORIGINAL

    # Definir tamanhos de fonte
    TAMANHO_FONTE_PADRAO_BASE = 12  # Tamanho base para a fonte padrão
    TAMANHO_FONTE_INSTRUCOES_BASE = 10  # Tamanho base para a fonte das instruções

    tamanho_fonte_padrao = int(TAMANHO_FONTE_PADRAO_BASE * fator_escala)
    tamanho_fonte_instrucoes = int(TAMANHO_FONTE_INSTRUCOES_BASE * fator_escala)

    # Texto de instruções
    instrucoes = [
        "INSTRUÇÕES",
        "1. Carregue as páginas a serem capturadas (max. 20):",
        "   a) Leia os links a partir de um arquivo texto (.txt).",
        "   b) Copie e cole links na caixa de texto.",
        "   c) Pule a carga e digite links no navegador de captura.",
        "2. Efetue os logins eventualmente necessários.",
        "3. É recomendável salvar as senhas no navegador para uso futuro.",
        "4. Quando todas as páginas estiverem prontas, pressione:",
        "   a) 'ctrl+alt+F7' (MODO VISUAL COM AJUSTES).",
        "   b) 'ctrl+alt+F8' (MODO OCULTO COM AJUSTES).",
        "   c) 'ctrl+alt+F9' (MODO OCULTO SEM AJUSTES - RECOMENDADO).",
        "5. Caso deseje interromper a rolagem automática, pressione:",
        "   a) 'ctrl+alt+F5' (INTERROMPER ROLAGEM).",
        "   b) 'ctrl+alt+F6' (CONTINUAR ROLAGEM).",
        "6. Aguarde o término do processo de captura.",
        "7. Ao final, clique em OK na mensagem de status exibida.",
    ]

    # Criar Labels para cada instrução
    for i, linha in enumerate(instrucoes):
        label_instrucao = tk.Label(
            tk_captura_paginas,
            text=linha,
            justify="left",
            font=("Arial", tamanho_fonte_instrucoes),
        )
        label_instrucao.grid(
            row=i,
            column=0,
            columnspan=3,
            padx=int(20 * fator_escala),
            pady=int(1 * fator_escala),
            sticky="w",
        )

    # Frame para o quadro de texto
    frame_texto = tk.Frame(tk_captura_paginas)
    frame_texto.grid(
        row=len(instrucoes),
        column=0,
        columnspan=3,
        padx=int(20 * fator_escala),
        pady=int(10 * fator_escala),
        sticky="nsew",
    )  # Ajuste aqui

    # Barra de rolagem
    scrollbar = tk.Scrollbar(frame_texto)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Área de texto
    altura_texto = int(6 * fator_escala)  # Altura base * fator de escala
    texto_saida = tk.Text(
        frame_texto,
        wrap=tk.WORD,
        yscrollcommand=scrollbar.set,
        font=("Arial", tamanho_fonte_padrao),
        bg="white",
        relief="solid",
        borderwidth=1,
        height=altura_texto,
    )
    texto_saida.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=texto_saida.yview)

    # Frame para os botões
    frame_botoes = tk.Frame(tk_captura_paginas)
    frame_botoes.grid(
        row=len(instrucoes) + 1,
        column=0,
        columnspan=3,
        padx=int(10 * fator_escala),
        pady=int(10 * fator_escala),
        sticky="ew",
    )  # Ajuste aqui

    # Calcular largura dos botões
    LARGURA_BOTAO_BASE = 15
    largura_botao = int(LARGURA_BOTAO_BASE * fator_escala)
    LARGURA_MAXIMA_BOTAO = 20  # Limite máximo para a largura do botão
    largura_botao = min(largura_botao, LARGURA_MAXIMA_BOTAO)

    # Botão para abrir arquivo
    botao_abrir = tk.Button(
        frame_botoes,
        text="Importar do Arquivo",
        command=abrir_arquivo,
        font=("Arial", tamanho_fonte_padrao),
    )
    botao_abrir.grid(
        row=0,
        column=0,
        padx=int(10 * fator_escala),
        ipadx=int(20 * fator_escala),
        ipady=int(5 * fator_escala),
        sticky="ew",
    )

    # Botões de decisão
    botao_carregar = tk.Button(
        frame_botoes,
        text="Capturar Links",
        command=lambda: Thread(
            target=carregar_conteudo_thread, args=(file_data_paginas,)
        ).start(),
        font=("Arial", tamanho_fonte_padrao),
        bg="#DC3545",
        fg="white",
        width=largura_botao,
    )
    botao_carregar.grid(
        row=0,
        column=1,
        padx=int(10 * fator_escala),
        ipadx=int(10 * fator_escala),
        ipady=int(5 * fator_escala),
        sticky="ew",
    )

    # Botão Pular
    botao_pular = tk.Button(
        frame_botoes,
        text="Pular Etapa",
        command=lambda: Thread(
            target=ignorar_conteudo_thread, args=(file_data_paginas,)
        ).start(),
        font=("Arial", tamanho_fonte_padrao),
        bg="#DC3545",
        fg="white",
        width=largura_botao,
    )
    botao_pular.grid(
        row=0,
        column=2,
        padx=int(10 * fator_escala),
        ipadx=int(10 * fator_escala),
        ipady=int(5 * fator_escala),
        sticky="ew",
    )

    # Configurar o peso das linhas e colunas para permitir redimensionamento
    tk_captura_paginas.grid_rowconfigure(
        len(instrucoes), weight=1
    )  # Onde frame_texto está
    tk_captura_paginas.grid_rowconfigure(
        len(instrucoes) + 1, weight=0
    )  # Onde frame_botoes está. Use 0 para manter a altura.
    tk_captura_paginas.grid_columnconfigure(0, weight=1)

    # Configurar pesos para as colunas dos botões
    frame_botoes.grid_columnconfigure(0, weight=1)
    frame_botoes.grid_columnconfigure(1, weight=1)
    frame_botoes.grid_columnconfigure(2, weight=1)

    tk_captura_paginas.deiconify()
    tk_captura_paginas.transient(tk_custodia_tech)
    tk_captura_paginas.after(0, texto_saida.focus_set)
    tk_custodia_tech.wait_window(tk_captura_paginas)
