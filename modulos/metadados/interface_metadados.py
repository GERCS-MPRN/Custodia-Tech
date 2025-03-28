import os
import tkinter as tk
from threading import Thread
from tkinter import filedialog, messagebox, ttk

from modulos.metadados.metadados import extracao_metadados
from utils.monitor import centraliza_janela_no_monitor_ativo


def janela_extrair_metadados(
    tk_custodia_tech, case_directory, usuario, icone_custodia, metadados_total
):

    def extrair_e_fechar():
        if any(var.get() for _, var in checkboxes):
            # Iniciar a barra de progresso
            progress_bar.start()

            extrair_button.config(state=tk.DISABLED)

            # Executar a extração em uma thread separada para não bloquear a interface
            Thread(target=extrair_metadados_com_progresso, daemon=True).start()
        else:
            tk.messagebox.showwarning(
                "Aviso",
                "Por favor, selecione pelo menos um arquivo antes de extrair os metadados.",
                parent=tk_extrair_metadados,
            )
            tk_extrair_metadados.deiconify()
            tk_extrair_metadados.focus_set()

    def extrair_metadados_com_progresso():
        total_arquivos = sum(1 for _, var in checkboxes if var.get())
        progresso_por_arquivo = 100 / total_arquivos if total_arquivos > 0 else 0
        progresso_atual = 0

        for arquivo, var in checkboxes:
            if var.get():  # Se o checkbox está marcado
                extracao_metadados(arquivo, case_directory, usuario, metadados_total)

                # Atualizar a barra de progresso
                progresso_atual += progresso_por_arquivo
                progress_bar["value"] = progresso_atual
                tk_extrair_metadados.update_idletasks()

        # Finalizar a barra de progresso
        progress_bar.stop()
        tk_extrair_metadados.destroy()

    tk_custodia_tech.update_idletasks()
    pasta = filedialog.askdirectory(
        parent=tk_custodia_tech, title="Selecione uma pasta..."
    )
    if not pasta:
        return

    tk_extrair_metadados = tk.Toplevel(tk_custodia_tech)
    tk_extrair_metadados.withdraw()

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(
        tk_extrair_metadados, "extrair_metadados"
    )
    tk_extrair_metadados.iconbitmap(icone_custodia)
    tk_extrair_metadados.title("Extração de Metadados")
    tk_extrair_metadados.resizable(False, False)

    # Criar um frame para conter todos os elementos
    frame_container = ttk.LabelFrame(tk_extrair_metadados, text="Selecione os arquivos")

    # Função para limitar o título
    def limitar_titulo(titulo, limite=60):
        return titulo if len(titulo) <= limite else titulo[: limite - 3] + "..."

    # Calcular tamanho proporcional da fonte
    tamanho_fonte = max(10, int(LARGURA_CT / 30))

    # Adicionar o título fora do frame_container
    titulo_texto = limitar_titulo(f"Arquivos da pasta:\n{pasta}")
    titulo_label = tk.Label(
        tk_extrair_metadados, text=titulo_texto, font=("Arial", tamanho_fonte, "bold")
    )
    titulo_label.grid(row=0, column=0, pady=(10, 5), sticky="n")

    # Criar um LabelFrame para a área de arquivos
    frame_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    # Adicionar um Canvas e uma Scrollbar para rolagem
    canvas = tk.Canvas(frame_container)
    scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
    files_frame = ttk.Frame(canvas)

    # Configurar o canvas
    canvas.configure(yscrollcommand=scrollbar.set)

    # Empacotar os widgets
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Criar uma janela no canvas para o frame
    canvas_frame = canvas.create_window((0, 0), window=files_frame, anchor="nw")

    # Função para ajustar o tamanho do scrollregion
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Função para ajustar a largura do frame interno
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_frame, width=event.width)

    # Vincular eventos
    files_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Vincular o scroll do mouse ao canvas
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)  # Para Windows e macOS
    canvas.bind_all(
        "<Button-4>", lambda e: canvas.yview_scroll(-1, "units")
    )  # Para Linux (scroll up)
    canvas.bind_all(
        "<Button-5>", lambda e: canvas.yview_scroll(1, "units")
    )  # Para Linux (scroll down)

    # Lista para armazenar as checkboxes
    checkboxes = []

    def selecionar_todos():
        selecionar = selecionar_todos_var.get()
        for _, var in checkboxes:
            var.set(selecionar)

    selecionar_todos_var = tk.BooleanVar(value=False)
    selecionar_todos_checkbox = ttk.Checkbutton(
        files_frame,
        text="Selecionar Todos",
        variable=selecionar_todos_var,
        command=selecionar_todos,
    )
    selecionar_todos_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    arquivos_com_data = []
    for arquivo in os.listdir(pasta):
        caminho_completo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_completo):
            data_modificacao = os.path.getmtime(caminho_completo)
            arquivos_com_data.append((caminho_completo, data_modificacao))

    # Ordenar os arquivos pela data de modificação (mais recente primeiro)
    arquivos_com_data.sort(key=lambda x: x[1], reverse=True)

    for i, (caminho_completo, _) in enumerate(arquivos_com_data):
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(
            files_frame, text=os.path.basename(caminho_completo), variable=var
        )
        checkbox.grid(row=i + 1, column=0, padx=5, pady=2, sticky="w")
        checkboxes.append((caminho_completo, var))

    # Adicionar a barra de progresso
    progress_bar = ttk.Progressbar(
        tk_extrair_metadados, orient="horizontal", length=300, mode="determinate"
    )
    progress_bar.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    # Adicionar um botão "Extrair metadados" na parte inferior
    extrair_button = ttk.Button(
        tk_extrair_metadados,
        text="Extrair Metadados",
        command=extrair_e_fechar,
        bootstyle="info",
        style="TButton",
    )
    extrair_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    # Configurar o grid para expandir corretamente
    tk_extrair_metadados.grid_rowconfigure(1, weight=1)
    tk_extrair_metadados.grid_columnconfigure(0, weight=1)

    tk_extrair_metadados.deiconify()

    tk_extrair_metadados.transient(tk_custodia_tech)
    tk_extrair_metadados.grab_set()
    tk_custodia_tech.wait_window(tk_extrair_metadados)
