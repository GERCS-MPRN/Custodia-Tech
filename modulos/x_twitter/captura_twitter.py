import os
import shutil
import zipfile
from datetime import datetime

import yt_dlp
from tzlocal import get_localzone

from utils.api_perdigueiro import registrar_acao
from utils.metadata import calculate_hash, get_file_metadata
from utils.renomear_zip import renomear_zip


def download_twitter_videos(
    urlvideo,
    casedirectory,
    progress_b,
    label_status,
    botao_download_twitter,
    file_data_x,
    x_window,
    entry_url,
    usuario,
):
    if urlvideo == "":
        raise ValueError("Nenhuma URL fornecida.")

    # Atualiza a barra de progresso com base no total de vídeos
    progress_b["maximum"] = 1
    progress_b["value"] = 0

    def progress_hook(d):
        if d["status"] == "downloading":
            downloaded_bytes = d.get("downloaded_bytes", 0) or 0
            total_bytes = d.get("total_bytes", 0) or 0
            percent = d.get("percent", 0)  # Adiciona verificação para 'percent'

            if total_bytes > 0:  # Evita divisão por zero
                progress_b["value"] = downloaded_bytes / total_bytes * 100
                print(
                    f"Baixando: {d['filename']} - {downloaded_bytes / 1024 / 1024:.2f} MB de {total_bytes / 1024 / 1024:.2f} MB ({percent:.2f}%)"
                )

                x_window.update_idletasks()  # Atualiza a barra de progresso

        if d["status"] == "finished":
            label_status.config(text="Seu vídeo foi baixado com sucesso!")
            entry_url.delete(0, "end")

    fuso_local = get_localzone()
    timestamp = datetime.now(fuso_local).strftime("%d-%m-%Y_%H-%M-%S_UTC%Z")
    nome_caputura_video = f"twitter_video_{timestamp}"
    video_twitter_directory = os.path.join(casedirectory, nome_caputura_video)

    # Cria a pasta se não existir
    os.makedirs(video_twitter_directory, exist_ok=True)

    ydl_opts = {
        "format": "best",
        "outtmpl": os.path.join(
            video_twitter_directory, nome_caputura_video + ".%(ext)s"
        ),
        "progress_hooks": [progress_hook],
    }

    try:
        # Desativa o botão durante o download
        botao_download_twitter.config(state="disabled")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(urlvideo, download=True)
            video_file_path = os.path.join(
                video_twitter_directory, nome_caputura_video + ".mp4"
            )

            if os.path.exists(video_file_path):
                # Salva informações em um arquivo .txt
                info_file_path = os.path.join(
                    video_twitter_directory, nome_caputura_video + "_info.txt"
                )
                with open(info_file_path, "w") as info_file:
                    info_file.write(f"URL do vídeo: {urlvideo}\n")
                    info_file.write(f"Likes: {info_dict.get('like_count', 'N/A')}\n")
                    info_file.write(
                        f"Retweets: {info_dict.get('repost_count', 'N/A')}\n"
                    )
                    info_file.write(f"Replies: {info_dict.get('reply_count', 'N/A')}\n")
                    info_file.write(f"Views: {info_dict.get('view_count', 'N/A')}\n")

                zip_file_path = video_twitter_directory + ".zip"
                with zipfile.ZipFile(zip_file_path, "w") as zip_file:
                    for foldername, subfolders, filenames in os.walk(
                        video_twitter_directory
                    ):
                        for filename in filenames:
                            file_path = os.path.join(foldername, filename)
                            zip_file.write(
                                file_path,
                                os.path.relpath(file_path, video_twitter_directory),
                            )

                shutil.rmtree(video_twitter_directory)

                hashes = calculate_hash(
                    zip_file_path, algorithms=["md5", "sha1", "sha256"]
                )
                metadata = get_file_metadata(zip_file_path)

                metadata, nome_final_zip = renomear_zip(
                    zip_file_path, metadata, "twitter_video_"
                )

                file_data_x.append(
                    {
                        "nome_do_arquivo": nome_final_zip,
                        "hashes": hashes,
                        "metadata": metadata,
                        "urlvideo": urlvideo,
                    }
                )

                registrar_acao(
                    f"Download do vídeo {nome_final_zip} do Twitter concluído",
                    f"Download do vídeo {nome_final_zip} do Twitter {urlvideo} feito pelo usuário {usuario} no diretório {video_twitter_directory}",
                )

                # Ativa o botão novamente após o download bem-sucedido
                if x_window.winfo_exists():  # Verifica se a janela ainda está aberta
                    botao_download_twitter.config(state="normal")
                return

    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        # Verifica se a pasta está vazia ou não contém arquivos que começam com "twitter_video"
        if not any(
            f.startswith("twitter_video") for f in os.listdir(video_twitter_directory)
        ):
            shutil.rmtree(
                video_twitter_directory, ignore_errors=True
            )  # Remove a pasta e seu conteúdo
        else:
            print(
                "A pasta contém arquivos que começam com 'twitter_video', não será removida."
            )
        countdown(
            15,
            label_status,
            x_window,
            urlvideo,
            casedirectory,
            progress_b,
            botao_download_twitter,
            file_data_x,
            entry_url,
            usuario,
        )  # Passa os parâmetros necessários


def countdown(
    seconds,
    label_status,
    x_window,
    urlvideo,
    casedirectory,
    progress_b,
    botao_download_twitter,
    file_data_x,
    entry_url,
    usuario,
):
    if seconds > 0:
        if x_window.winfo_exists():  # Verifica se a janela ainda está aberta
            label_status.config(
                text=f"Erro ao baixar o vídeo.\n Tentando novamente em {seconds} segundos..."
            )
            x_window.after(
                1000,
                countdown,
                seconds - 1,
                label_status,
                x_window,
                urlvideo,
                casedirectory,
                progress_b,
                botao_download_twitter,
                file_data_x,
                entry_url,
                usuario,
            )  # Chama a função novamente após 1 segundo
        else:
            return  # Sai se a janela foi fechada
    else:
        if x_window.winfo_exists():  # Verifica se a janela ainda está aberta
            label_status.config(text="Tentando baixar o vídeo novamente")
            download_twitter_videos(
                urlvideo,
                casedirectory,
                progress_b,
                label_status,
                botao_download_twitter,
                file_data_x,
                x_window,
                entry_url,
                usuario,
            )  # Tenta o download novamente após a contagem
