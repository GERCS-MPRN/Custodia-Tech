import os
import shutil
import time
import tkinter as tk
import zipfile
from datetime import datetime
from pathlib import Path
from threading import Thread
from tkinter import messagebox, ttk

import yt_dlp
from tzlocal import get_localzone

from modulos.tiktok.login_tiktok import login_tiktok
from utils.api_perdigueiro import registrar_acao
from utils.metadata import calculate_hash, get_file_metadata
from utils.monitor import centraliza_janela_no_monitor_ativo
from utils.renomear_zip import renomear_zip


def janela_tiktok(
    tk_custodia_tech, case_directory, usuario, file_data_tiktok, icone_custodia
):
    """
    Cria a janela para baixar vídeos do TikTok.
    """

    user_dir = str(Path.home())
    custodiatech_dir = user_dir + "\\AppData\\Local\\CustodiaTech"
    cookies_file = f"{custodiatech_dir}\\tiktok_cookies.txt"
    captura_paginas_profile = custodiatech_dir + "\\Captura_Paginas_Profile"

    def download_tiktok_videos():
        """
        Função para baixar vídeos do TikTok.
        """

        if not os.path.exists(cookies_file):
            messagebox.showerror(
                "Erro",
                "Por favor, realize o login no TikTok antes de baixar os vídeos.",
                parent=tk_tiktok,
            )
            return

        urls = [
            entry_url1.get(),
            entry_url2.get(),
            entry_url3.get(),
            entry_url4.get(),
            entry_url5.get(),
        ]

        if not urls:
            messagebox.showerror(
                "Erro",
                "Por favor, insira pelo menos um URL do TikTok.",
                parent=tk_tiktok,
            )
            return

        # Validação dos URLs
        for url in urls:
            if url.strip():  # Verifica apenas URLs não vazios
                # Remove possíveis @ no início do URL
                url_limpo = url.strip().lstrip("@").lower()  # Converte para minúsculas

                # Normaliza o URL para permitir diferentes formatos
                if url_limpo.startswith("https://"):
                    url_limpo = url_limpo[8:]  # Remove 'https://'
                if url_limpo.startswith("http://"):
                    url_limpo = url_limpo[7:]  # Remove 'http://'
                if url_limpo.startswith("www."):
                    url_limpo = url_limpo[4:]  # Remove 'www.'

                # Verifica se o URL é válido do TikTok
                if not (
                    url_limpo.startswith("tiktok.com/")
                    or url_limpo.startswith("vm.tiktok.com/")
                ):
                    messagebox.showerror(
                        "URL Inválido",
                        f"O link {url} não pode ser processado!\nPor favor, insira apenas URLs válidos do Tiktok",
                        parent=tk_tiktok,
                    )
                    return

        # Conta o número de URLs válidas
        num_urls = sum(1 for url in urls if url.strip())
        completed_downloads = 0  # Contador para downloads concluídos

        for i, urlvideo in enumerate(urls, start=1):
            if not urlvideo.strip():
                continue  # Ignora URLs vazias

            casedirectory = case_directory
            fuso_local = get_localzone()
            timestamp = datetime.now(fuso_local).strftime("%d-%m-%Y_%H-%M-%S_UTC%Z")
            nome_caputura_video = f"tiktok_video_{i}_{timestamp}"
            video_directory = os.path.join(casedirectory, nome_caputura_video)

            # Cria a pasta se não existir
            os.makedirs(video_directory, exist_ok=True)

            def progress_hook(d):
                if d["status"] == "downloading":
                    percent = d["downloaded_bytes"] / d["total_bytes"] * 100
                    progress_b["value"] = (
                        (completed_downloads + percent / 100) / num_urls * 100
                    )
                    tk_tiktok.update_idletasks()  # Atualiza a interface gráfica

            ydl_opts = {
                "format": "best",
                "outtmpl": os.path.join(
                    video_directory, nome_caputura_video + ".%(ext)s"
                ),
                "progress_hooks": [progress_hook],
                "writeinfojson": True,
                "postprocessors": [],
                "cookiefile": cookies_file,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Medir o tempo para extrair informações do vídeo
                    start_extract_time = time.time()
                    info_dict = ydl.extract_info(urlvideo, download=True)
                    end_extract_time = time.time()
                    print(
                        f"Extração de informações do vídeo {i} levou {end_extract_time - start_extract_time:.4f} segundos."
                    )

                    # Informações sobre o vídeo
                    title = info_dict.get("title", "Título não disponível")
                    description = info_dict.get(
                        "description", "Descrição não disponível"
                    )
                    view_count = info_dict.get(
                        "view_count", "Número de visualizações não disponível"
                    )
                    like_count = info_dict.get(
                        "like_count", "Número de curtidas não disponível"
                    )
                    dislike_count = info_dict.get(
                        "dislike_count", "Número de descurtidas não disponível"
                    )

                    # Cria e escreve no arquivo .txt
                    info_file_path = os.path.join(
                        video_directory, f"{nome_caputura_video}_info.txt"
                    )
                    with open(info_file_path, "w", encoding="utf-8") as f:
                        f.write(f"Título: {title}\n")
                        f.write(f"Descrição: {description}\n")
                        f.write(f"Visualizações: {view_count}\n")
                        f.write(f"Curtidas: {like_count}\n")
                        f.write(f"Descurtidas: {dislike_count}\n")

                    # Compacta a pasta video_directory
                    zip_file_path = video_directory + ".zip"
                    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
                        for foldername, subfolders, filenames in os.walk(
                            video_directory
                        ):
                            for filename in filenames:
                                file_path = os.path.join(foldername, filename)
                                zip_file.write(
                                    file_path,
                                    os.path.relpath(file_path, video_directory),
                                )

                    shutil.rmtree(video_directory)

                    # Calcula o hash e os metadados do arquivo compactado
                    hashes = calculate_hash(
                        zip_file_path, algorithms=["md5", "sha1", "sha256"]
                    )
                    metadata = get_file_metadata(zip_file_path)

                    metadata, nome_final_zip = renomear_zip(
                        zip_file_path, metadata, f"tiktok_video_{i}_"
                    )

                    file_data_tiktok.append(
                        {
                            "nome_do_arquivo": nome_final_zip,
                            "hashes": hashes,
                            "metadata": metadata,
                            "urlvideo": urlvideo,
                        }
                    )

                    completed_downloads += (
                        1  # Incrementa o contador de downloads concluídos
                    )

                    # Atualiza a barra de progresso com o avanço do download
                    progress_b["value"] = (completed_downloads / num_urls) * 100
                    tk_tiktok.update_idletasks()

                    registrar_acao(
                        f"Download do vídeo {i} do TikTok concluído",
                        f"Download do vídeo {i} do TikTok {urlvideo} feito pelo usuário {usuario} no diretório {video_directory}",
                    )

            except Exception as e:
                print(f"Erro ao baixar o vídeo {i}: {e}")
                messagebox.showerror(
                    "Erro no download do vídeo",
                    f"Erro ao baixar o vídeo {i}. Tente novamente mais tarde.",
                    parent=tk_tiktok,
                )
                shutil.rmtree(video_directory)

        # Exibe a mensagem de conclusão após todos os downloads
        if completed_downloads > 0:
            messagebox.showinfo(
                "Concluído",
                f"Download de {completed_downloads} vídeo(s) concluído(s) com sucesso!",
                parent=tk_tiktok,
            )
        else:
            messagebox.showinfo(
                "Concluído", "Nenhum vídeo foi baixado.", parent=tk_tiktok
            )

        tk_tiktok.destroy()

    # Código para criar a janela do TikTok e os elementos da interface
    tk_tiktok = tk.Toplevel(tk_custodia_tech)
    tk_tiktok.withdraw()

    tk_tiktok.iconbitmap(icone_custodia)
    tk_tiktok.title("Baixar Vídeos do TikTok")
    tk_tiktok.resizable(False, False)
    tk_tiktok.attributes("-fullscreen", False)

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(tk_tiktok, "tiktok")

    # Fator de escala baseado na largura original (400)
    LARGURA_ORIGINAL = 400
    fator_escala = LARGURA_CT / LARGURA_ORIGINAL

    # Tamanhos base
    TAMANHO_FONTE_BASE = 12
    PAD_Y_BASE = 5  # espaçamento vertical
    PADX_BASE = 5  # espaçamento horizontal

    # Tamanhos ajustados
    tamanho_fonte = int(TAMANHO_FONTE_BASE * fator_escala)
    pady = int(PAD_Y_BASE * fator_escala)
    padx = int(PADX_BASE * fator_escala)

    # Estilo da fonte
    fonte = ("Arial", tamanho_fonte)

    # Criar um estilo para o botão
    style = ttk.Style()
    style.configure("Custom.TButton", font=fonte, padding=(5, int(5 * fator_escala)))

    label_link = tk.Label(
        tk_tiktok, text="URLs dos vídeos do TikTok (máximo 5):", font=fonte
    )
    label_link.grid(row=0, column=0, columnspan=2, sticky="ew", padx=padx, pady=pady)

    entry_url1 = ttk.Entry(tk_tiktok, bootstyle="dark", font=fonte)
    entry_url1.grid(row=1, column=0, columnspan=2, sticky="ew", padx=padx, pady=pady)

    entry_url2 = ttk.Entry(tk_tiktok, bootstyle="dark", font=fonte)
    entry_url2.grid(row=2, column=0, columnspan=2, sticky="ew", padx=padx, pady=pady)

    entry_url3 = ttk.Entry(tk_tiktok, bootstyle="dark", font=fonte)
    entry_url3.grid(row=3, column=0, columnspan=2, sticky="ew", padx=padx, pady=pady)

    entry_url4 = ttk.Entry(tk_tiktok, bootstyle="dark", font=fonte)
    entry_url4.grid(row=4, column=0, columnspan=2, sticky="ew", padx=padx, pady=pady)

    entry_url5 = ttk.Entry(tk_tiktok, bootstyle="dark", font=fonte)
    entry_url5.grid(row=5, column=0, columnspan=2, sticky="ew", padx=padx, pady=pady)

    progress_b = ttk.Progressbar(
        tk_tiktok, orient="horizontal", mode="determinate", bootstyle="warning-striped"
    )
    progress_b.grid(row=6, column=0, columnspan=2, sticky="ew", padx=padx, pady=pady)

    button_login = ttk.Button(
        tk_tiktok,
        text="Login no TikTok",
        style="Custom.TButton",
        command=lambda: Thread(
            target=login_tiktok,
            args=(captura_paginas_profile, cookies_file, button_login, button_download),
        ).start(),
    )
    button_login.grid(
        row=7, column=0, sticky="ew", padx=padx, pady=pady, ipady=int(5 * fator_escala)
    )

    button_download = ttk.Button(
        tk_tiktok,
        text="Baixar Vídeo(s)",
        style="Custom.TButton",
        command=lambda: Thread(target=download_tiktok_videos).start(),
    )  # removeu parâmetros não usados
    button_download.grid(
        row=7, column=1, sticky="ew", padx=padx, pady=pady, ipady=int(5 * fator_escala)
    )

    if os.path.exists(cookies_file):
        button_login.config(state=tk.DISABLED)

    if not os.path.exists(cookies_file):
        button_download.config(state=tk.DISABLED)

    # Configurar o peso da coluna para expandir os widgets
    tk_tiktok.grid_columnconfigure(0, weight=1)
    tk_tiktok.grid_columnconfigure(1, weight=1)

    # Configurar o peso das linhas para distribuir o espaço vertical
    for i in range(8):  # 8 linhas no total
        tk_tiktok.grid_rowconfigure(i, weight=1)

    tk_tiktok.deiconify()

    tk_tiktok.transient(tk_custodia_tech)
    tk_tiktok.grab_set()
    tk_tiktok.after(0, entry_url1.focus_set)
    tk_custodia_tech.wait_window(tk_tiktok)
