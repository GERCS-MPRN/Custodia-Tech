import tkinter as tk
from threading import Thread
from tkinter import messagebox, ttk

from utils.monitor import centraliza_janela_no_monitor_ativo

from .captura_twitter import download_twitter_videos


def janela_x_twitter(
    tk_custodia_tech, case_directory, file_data_x, usuario, icone_custodia
):
    def download_x_video():
        url = entry_url.get()

        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira uma URL.")
            return

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

            # Verifica se o URL é válido do X (Twitter)
            if not (
                url_limpo.startswith("twitter.com/") or url_limpo.startswith("x.com/")
            ):
                messagebox.showerror(
                    "URL Inválido",
                    f"O link {url} não pode ser processado!\nPor favor, insira apenas URLs válidos do X (Twitter)",
                    parent=tk_x_twittter,
                )
                botao_download_twitter.config(state=tk.NORMAL)
                return
        try:
            download_twitter_videos(
                url,
                case_directory,
                progress_b,
                label_status,
                botao_download_twitter,
                file_data_x,
                tk_x_twittter,
                entry_url,
                usuario,
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar o vídeo: {e}")

    tk_x_twittter = tk.Toplevel(tk_custodia_tech)
    tk_x_twittter.withdraw()

    tk_x_twittter.iconbitmap(icone_custodia)
    tk_x_twittter.title("Baixar Vídeo do X (Twitter)")
    tk_x_twittter.resizable(False, False)
    tk_x_twittter.attributes("-fullscreen", False)

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(
        tk_x_twittter, "x_twitter"
    )

    label_link = tk.Label(tk_x_twittter, text="URL do vídeo do X (Twitter):")
    label_link.pack(pady=int(ALTURA_CT * 0.0156))

    entry_url = ttk.Entry(
        tk_x_twittter, bootstyle="dark", width=int(LARGURA_CT * 0.125)
    )
    entry_url.pack(pady=int(ALTURA_CT * 0.0156))

    progress_b = ttk.Progressbar(
        tk_x_twittter,
        orient="horizontal",
        mode="determinate",
        length=int(LARGURA_CT * 0.875),
        bootstyle="warning-striped",
    )
    progress_b.pack(pady=int(ALTURA_CT * 0.03))

    botao_download_twitter = ttk.Button(
        tk_x_twittter,
        text="Baixar Vídeo",
        command=lambda: Thread(target=download_x_video).start(),
    )
    botao_download_twitter.pack(pady=int(ALTURA_CT * 0.01))

    label_status = tk.Label(tk_x_twittter, text="")
    label_status.pack(pady=int(ALTURA_CT * 0.03))

    tk_x_twittter.deiconify()

    tk_x_twittter.transient(tk_custodia_tech)
    tk_x_twittter.grab_set()
    tk_x_twittter.after(0, entry_url.focus_set)
    tk_custodia_tech.wait_window(tk_x_twittter)
