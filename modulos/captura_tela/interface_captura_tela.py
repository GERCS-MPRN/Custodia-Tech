import tkinter as tk
from tkinter import ttk
from threading import Thread

from modulos.captura_tela.captura_tela import capture_and_process_screenshot, select_area
from utils.monitor import centraliza_janela_no_monitor_ativo

def janela_captura_tela(tk_custodia_tech, case_directory, icone_custodia, usuario, captured_screenshots, captured_screenshots_zip):
    
    def fechar_janela():
        """Função para fechar a janela e destruir o objeto"""
        try:
            tk_captura_tela.destroy()
        except Exception as e:
            print(f"Erro ao fechar a janela captura tela {e}")
    
    tk_captura_tela = tk.Toplevel(tk_custodia_tech)

    # tk_captura_tela.withdraw()

    tk_captura_tela.iconbitmap(icone_custodia)
    tk_captura_tela.title("Captura de Tela")
    tk_captura_tela.resizable(False, False)
    tk_captura_tela.attributes('-fullscreen', False)
    
    tk_captura_tela.attributes('-topmost', True)
    tk_captura_tela.update()
    tk_captura_tela.attributes('-topmost', False)
    tk_captura_tela.update_idletasks()
    tk_captura_tela.focus_force()

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(tk_captura_tela, "captura_tela")

    # Fator de escala baseado na largura original (300)
    LARGURA_ORIGINAL = 300
    fator_escala = LARGURA_CT / LARGURA_ORIGINAL

    # Tamanhos base
    TAMANHO_FONTE_BASE = 12
    LARGURA_TEXT_BASE = 40  # Ajuste conforme necessário
    ALTURA_TEXT_BASE = 4   # Ajuste conforme necessário
    PAD_BASE = 10

    # Tamanhos ajustados
    tamanho_fonte = int(TAMANHO_FONTE_BASE * fator_escala)
    largura_texto = int(LARGURA_TEXT_BASE * fator_escala)
    altura_texto = int(ALTURA_TEXT_BASE * fator_escala)
    pad = int(PAD_BASE * fator_escala)

    # Estilo da fonte
    fonte = ("Arial", tamanho_fonte)

    label = tk.Label(tk_captura_tela, text="Informe o motivo da captura:", font=fonte)
    label.grid(row=0, column=0, padx=pad, pady=pad, sticky="ew")
    
    def format_text(event):
        reason_entry.edit_modified(False)  # Reseta o estado de modificação
        text = reason_entry.get("1.0", "end-1c")  # Obtém o texto sem o caractere extra de nova linha
        if text:
            formatted_text = text.capitalize()  # Apenas a primeira letra maiúscula
            if text != formatted_text:  # Evita loop infinito ao modificar o texto
                reason_entry.delete("1.0", "end")
                reason_entry.insert("1.0", formatted_text)
                reason_entry.edit_modified(False)  # Reseta o estado de modificação novamente


    reason_entry = tk.Text(tk_captura_tela, width=largura_texto, height=altura_texto, font=fonte)
    reason_entry.grid(row=1, column=0, padx=pad, pady=pad, sticky="nsew")  # 'nsew' para expandir
    
    reason_entry.bind("<<Modified>>", format_text)

    def capture_and_hide():
        tk_captura_tela.withdraw()
        # Abre o overlay para seleção da área
        bounding_box = select_area(tk_custodia_tech)
        print(f"Bounding box capture_and_hide: {bounding_box}")
        # Captura a screenshot utilizando a região selecionada
        capture_and_process_screenshot(
            case_directory, 
            ['md5', 'sha1', 'sha256'], 
            reason_entry.get("1.0", tk.END), 
            usuario, 
            tk_custodia_tech, 
            captured_screenshots, 
            captured_screenshots_zip, 
            tk_captura_tela,
            bounding_box  # Novo parâmetro
        )
        fechar_janela()

    save_button = ttk.Button(
        tk_captura_tela, text="Capturar Tela", command=capture_and_hide, style='TButton')
    save_button.grid(row=2, column=0, padx=pad, pady=pad, sticky="ew")

    # Configurar o peso das linhas e colunas para permitir redimensionamento
    tk_captura_tela.grid_rowconfigure(1, weight=1)  # A linha do Text expande
    tk_captura_tela.grid_columnconfigure(0, weight=1)  # A coluna expande

    # Remove 'transient' e 'grab_set'
    # tk_captura_tela.transient(tk_custodia_tech)
    # tk_captura_tela.grab_set()
    tk_captura_tela.after(0, reason_entry.focus_set)
    
    tk_captura_tela.update_idletasks()
    tk_captura_tela.deiconify() # Mostrar a janela
    # tk_custodia_tech.wait_window(tk_captura_tela) # Remover o wait_window