import tkinter as tk
from threading import Thread
from tkinter import messagebox, ttk

from utils.monitor import centraliza_janela_no_monitor_ativo

from .captura_whatsapp import iniciar_captura_whatsapp
from .metadados_whatsapp import metadados_whatsapp


def janela_whatsapp(tk_custodia_tech, case_directory, usuario, file_data_whatsapp, botao_whatsapp, icone_custodia):
    def captura_whatsapp(file_data_whatsapp):
        # Obtém o valor selecionado e chama a função de captura
        selecao = var.get()
        
        thread_captura_whatsapp = Thread(target=captura_thread, args=(selecao,file_data_whatsapp))
        thread_captura_whatsapp.start()
    
    def captura_thread(selecao, file_data_whatsapp):
        try:
            botao_whatsapp.config(state='disabled')

            if selecao == 1:
                messagebox.showinfo('Captura de Lista de Contatos de Whatsapp\n\n', 
                                    '1. Efetue o login no Whatsapp com o QRCode.\n'
                                    '2. Aguarde a rolagem automática da lista de contatos.\n'
                                    '3. Ao final, uma mensagem de status será exibida.\n\n'
                                    'OBS.: A qualquer momento, a rolagem automática de uma lista de contatos poderá ser interrompida (ctrl+alt+F2) e continuada (ctrl+alt+F3), de modo que a captura será realizada até o fundo da lista visível respectiva.\n\n',
                                    parent=tk_whatsapp)
                tk_whatsapp.destroy()
                iniciar_captura_whatsapp(case_directory, 1)
                file_data_whatsapp = metadados_whatsapp(case_directory, file_data_whatsapp)
                
            if selecao == 2:
                messagebox.showinfo('Captura Conversas de Whatsapp\n\n', 
                                    '1. Efetue o login no Whatsapp com o QRCode.\n'
                                    '2. Selecione a conversa que deseja capturar.\n'
                                    '3. Aguarde o término do processo.\n'
                                    '4. Ao final, uma mensagem de status será exibida e será facultada a captura de uma nova conversa.\n\n'                             
                                    'OBS.: A qualquer momento, a rolagem automática de uma conversa poderá ser interrompida (ctrl+alt+F2) e continuada (ctrl+alt+F3), de modo que a captura será realizada a partir do topo da conversa visível respectiva.\n\n',
                                    parent=tk_whatsapp)
                tk_whatsapp.destroy()
                iniciar_captura_whatsapp(case_directory, 2)
                file_data_whatsapp = metadados_whatsapp(case_directory,file_data_whatsapp)
        
        finally:
            botao_whatsapp.config(state='normal')

    tk_whatsapp = tk.Toplevel(tk_custodia_tech)

    tk_whatsapp.withdraw()

    tk_whatsapp.iconbitmap(icone_custodia)
    tk_whatsapp.title("Captura Dinâmica de Whatsapp")
    tk_whatsapp.resizable(False, False)
    tk_whatsapp.attributes('-fullscreen', False)

    LARGURA_CT, ALTURA_CT = centraliza_janela_no_monitor_ativo(tk_whatsapp, "whatsapp")

    # Fator de escala baseado na largura original (300)
    LARGURA_ORIGINAL = 300
    fator_escala = LARGURA_CT / LARGURA_ORIGINAL

    # Tamanhos base
    TAMANHO_FONTE_TITULO_BASE = 14
    TAMANHO_FONTE_PADRAO_BASE = 12
    PAD_Y_BASE = 5
    PADX_BASE = 10

    # Tamanhos ajustados
    tamanho_fonte_titulo = int(TAMANHO_FONTE_TITULO_BASE * fator_escala)
    tamanho_fonte_padrao = int(TAMANHO_FONTE_PADRAO_BASE * fator_escala)
    pady = int(PAD_Y_BASE * fator_escala)
    padx = int(PADX_BASE * fator_escala)

    # Estilos de fonte
    fonte_titulo = ("Arial", tamanho_fonte_titulo)
    fonte_padrao = ("Arial", tamanho_fonte_padrao)

    # Define estilo para botões
    style = ttk.Style()
    style.configure("Iniciar.TButton", foreground="white",
                    background="green", font=("Helvetica", tamanho_fonte_padrao))

    # Cria label de instruções
    label_instrucoes = tk.Label(tk_whatsapp, text="Selecione o tipo de captura",
                                justify="center", font=fonte_titulo)
    label_instrucoes.grid(row=0, column=0, sticky="ew", padx=padx, pady=pady)

    var = tk.IntVar(value=1)

    # Cria radio buttons com espaçamento
    radio_contatos = tk.Radiobutton(tk_whatsapp, text="Capturar Lista de Contatos",
                                     variable=var, value=1, font=fonte_padrao)
    radio_contatos.grid(row=1, column=0, sticky="w", padx=padx, pady=pady)

    radio_conversas = tk.Radiobutton(tk_whatsapp, text="Capturar Conversas",
                                      variable=var, value=2, font=fonte_padrao)
    radio_conversas.grid(row=2, column=0, sticky="w", padx=padx, pady=pady)

    # Cria botão "Iniciar" com estilo
    iniciar_button = ttk.Button(
         tk_whatsapp, text="Iniciar", command=lambda: captura_whatsapp(file_data_whatsapp), style="Iniciar.TButton")
    iniciar_button.grid(row=3, column=0, sticky="ew", padx=padx, pady=pady)

    # Configurar o peso da coluna para expandir os widgets
    tk_whatsapp.grid_columnconfigure(0, weight=1)

    # Configurar o peso das linhas para distribuir o espaço vertical
    for i in range(4):
        tk_whatsapp.grid_rowconfigure(i, weight=1)

    tk_whatsapp.deiconify()

    tk_whatsapp.transient(tk_custodia_tech) 
    tk_whatsapp.grab_set()
    tk_custodia_tech.wait_window(tk_whatsapp)