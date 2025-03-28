import os
import shutil
import time
import tkinter as tk
import zipfile
from datetime import datetime
from threading import Thread
from tkinter import messagebox, ttk

import yt_dlp
from googleapiclient.discovery import build
from tzlocal import get_localzone

from utils.api_perdigueiro import registrar_acao
from utils.env_manager import YOUTUBE_API_KEY
from utils.metadata import calculate_hash, get_file_metadata
from utils.monitor import centraliza_janela_no_monitor_ativo
from utils.renomear_zip import renomear_zip


def janela_youtube(
    tk_custodia_tech, case_directory, usuario, file_data_youtube, icone_custodia
):

    def get_youtube_comments(video_id):
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        comments = []
        next_page_token = None
        max_comments = 1000  # Limitar a quantidade de comentários

        while len(comments) < max_comments:
            try:
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    textFormat="plainText",
                    maxResults=100,
                    pageToken=next_page_token,
                )
                response = request.execute()

                if "items" not in response:
                    break

                for item in response["items"]:
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    author_name = snippet.get(
                        "authorDisplayName", "Autor não disponível"
                    )
                    author_channel_id = snippet.get("authorChannelId", {}).get(
                        "value", "ID do canal não disponível"
                    )
                    comment_text = snippet.get(
                        "textDisplay", "Comentário não disponível"
                    )
                    comments.append(
                        f"Autor: {author_name} (Channel ID: {author_channel_id})\nComentário: {comment_text}\n"
                    )

                    if len(comments) >= max_comments:
                        break

                next_page_token = response.get("nextPageToken")
                if not next_page_token or len(comments) >= max_comments:
                    break

                time.sleep(1)  # Atraso de 1 segundo entre as requisições

            except Exception as e:
                print(f"Erro ao obter comentários: {e}")
                break

        return comments

    def download_youtube_videos():
        button.config(state=tk.DISABLED)
        urls = [
            entry_url1.get(),
            entry_url2.get(),
            entry_url3.get(),
            entry_url4.get(),
            entry_url5.get(),
        ]

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

                # Verifica se o URL é válido do YouTube
                if not (
                    url_limpo.startswith("youtube.com/watch?v=")
                    or url_limpo.startswith("youtu.be/")
                ):
                    messagebox.showerror(
                        "URL Inválido",
                        f"O link {url} não pode ser processado!\nPor favor, insira apenas URLs válidos do YouTube",
                        parent=tk_youtube,
                    )
                    button.config(state=tk.NORMAL)
                    return

        # Conta o número de URLs válidas
        num_urls = sum(1 for url in urls if url.strip())
        completed_downloads = 0  # Contador para downloads concluídos

        for i, urlvideo in enumerate(urls, start=1):
            if not urlvideo.strip():
                continue  # Ignora URLs vazias

            fuso_local = get_localzone()
            timestamp = datetime.now(fuso_local).strftime("%d-%m-%Y_%H-%M-%S_UTC%Z")
            nome_caputura_video = f"youtube_video_{i}_{timestamp}"
            video_directory = os.path.join(case_directory, nome_caputura_video)

            # Cria a pasta se não existir
            os.makedirs(video_directory, exist_ok=True)

            def progress_hook(d):
                if d["status"] == "downloading":
                    percent = d["downloaded_bytes"] / d["total_bytes"] * 100
                    progress_b["value"] = (
                        (completed_downloads + percent / 100) / num_urls * 100
                    )
                    tk_youtube.update_idletasks()  # Atualiza a interface gráfica

            ydl_opts = {
                "format": "best",
                "outtmpl": os.path.join(
                    video_directory, nome_caputura_video + ".%(ext)s"
                ),
                "progress_hooks": [progress_hook],
                "writeinfojson": True,
                "postprocessors": [],
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
                    print(f"Título do vídeo {i}: {title}")
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
                    video_id = info_dict.get("id", "")

                    # Obtém os comentários
                    comments = get_youtube_comments(video_id)
                    comments_text = (
                        "\n".join(comments)
                        if comments
                        else "Comentários não disponíveis"
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
                        f.write(f"Comentários:\n{comments_text}\n")

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
                        zip_file_path, metadata, f"youtube_video_{i}_"
                    )

                    file_data_youtube.append(
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
                    tk_youtube.update_idletasks()

                    registrar_acao(
                        f"Download do vídeo {i} do YouTube concluído",
                        f"Download do vídeo {i} do YouTube {urlvideo} feito pelo usuário {usuario} no diretório {video_directory}",
                    )

            except Exception as e:
                print(f"Erro ao baixar o vídeo {i}: {e}")
                shutil.rmtree(video_directory)
                messagebox.showerror(
                    "Erro",
                    f"Erro ao baixar o vídeo {i}: Verifique sua conexão com a Internet ou o link inserido.",
                    parent=tk_youtube,
                )
                button.config(state=tk.NORMAL)

        # Exibe a mensagem de conclusão após todos os downloads
        if completed_downloads > 0:
            messagebox.showinfo(
                "Concluído",
                f"Download de {completed_downloads} vídeo(s) concluído(s) com sucesso!",
                parent=tk_youtube,
            )
        else:
            messagebox.showinfo(
                "Concluído", "Nenhum vídeo foi baixado.", parent=tk_youtube
            )

        # Limpa os campos de entrada
        entry_url1.delete(0, tk.END)
        entry_url2.delete(0, tk.END)
        entry_url3.delete(0, tk.END)
        entry_url4.delete(0, tk.END)
        entry_url5.delete(0, tk.END)
        progress_b["value"] = 0

        button.config(state=tk.NORMAL)

    # Código para criar a janela do YouTube e os elementos da interface
    tk_youtube = tk.Toplevel(tk_custodia_tech)

    tk_youtube.withdraw()

    tk_youtube.iconbitmap(icone_custodia)
    tk_youtube.title("Baixar Vídeos do YouTube")
    tk_youtube.resizable(False, False)
    tk_youtube.attributes("-fullscreen", False)

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(tk_youtube, "youtube")

    # Fator de escala baseado na largura original (400)
    LARGURA_ORIGINAL = 400
    fator_escala = LARGURA_CT / LARGURA_ORIGINAL

    # Tamanhos ajustados
    tamanho_fonte = int(12 * fator_escala)
    pady = int(5 * fator_escala)
    padx = int(5 * fator_escala)

    # Estilo da fonte
    fonte = ("Arial", tamanho_fonte)

    # Criar um estilo para o botão
    style = ttk.Style()
    style.configure("Custom.TButton", font=fonte, padding=(5, int(5 * fator_escala)))

    label_link = tk.Label(
        tk_youtube, text="URLs dos vídeos do YouTube (máximo 5):", font=fonte
    )
    label_link.grid(row=0, column=0, sticky="w", padx=padx, pady=pady)

    entry_url1 = ttk.Entry(tk_youtube, bootstyle="dark", font=fonte)
    entry_url1.grid(row=1, column=0, sticky="ew", padx=padx, pady=pady)

    entry_url2 = ttk.Entry(tk_youtube, bootstyle="dark", font=fonte)
    entry_url2.grid(row=2, column=0, sticky="ew", padx=padx, pady=pady)

    entry_url3 = ttk.Entry(tk_youtube, bootstyle="dark", font=fonte)
    entry_url3.grid(row=3, column=0, sticky="ew", padx=padx, pady=pady)

    entry_url4 = ttk.Entry(tk_youtube, bootstyle="dark", font=fonte)
    entry_url4.grid(row=4, column=0, sticky="ew", padx=padx, pady=pady)

    entry_url5 = ttk.Entry(tk_youtube, bootstyle="dark", font=fonte)
    entry_url5.grid(row=5, column=0, sticky="ew", padx=padx, pady=pady)

    progress_b = ttk.Progressbar(
        tk_youtube, orient="horizontal", mode="determinate", bootstyle="warning-striped"
    )
    progress_b.grid(row=6, column=0, sticky="ew", padx=padx, pady=pady)

    # Usar o estilo personalizado no botão
    button = ttk.Button(
        tk_youtube,
        text="Baixar Vídeo(s)",
        style="Custom.TButton",
        command=lambda: Thread(target=download_youtube_videos).start(),
    )
    button.grid(
        row=7, column=0, sticky="ew", padx=padx, pady=pady, ipady=int(5 * fator_escala)
    )

    # Configurar o peso da coluna para expandir os widgets
    tk_youtube.grid_columnconfigure(0, weight=1)

    # Configurar o peso das linhas para distribuir o espaço vertical
    for i in range(8):  # 8 linhas no total
        tk_youtube.grid_rowconfigure(i, weight=1)

    tk_youtube.deiconify()

    tk_youtube.transient(tk_custodia_tech)
    tk_youtube.grab_set()
    tk_youtube.after(0, entry_url1.focus_set)
    tk_custodia_tech.wait_window(tk_youtube)
