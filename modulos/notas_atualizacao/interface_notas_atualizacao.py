import os
import tkinter as tk
from tkinter import ttk

from PIL import Image as PILImage
from PIL import ImageTk

from utils.item_path import get_resource_path
from utils.monitor import centraliza_janela_no_monitor_ativo

def formatar_texto_markdown(texto, font_size_base):
    """
    Formata o texto Markdown para ser exibido em Labels do Tkinter.

    Args:
        texto (str): O texto em formato Markdown.
        font_size_base (int): Tamanho base da fonte para os textos.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa um 
              parágrafo formatado com a formatação necessária (negrito, tamanho) 
              e o texto.
    """
    paragrafos = []
    linhas = texto.split('\n')
    
    for linha in linhas:
        linha = linha.strip()
        if linha.startswith('#'):
            # É um cabeçalho
            level = linha.count('#', 0, linha.find(' ') + 1)  # Conta o número de '#' até o primeiro espaço
            texto = linha.lstrip('#').strip()
            font_size = int(font_size_base + 4 - level)  # Ajusta o tamanho da fonte baseado no nível do cabeçalho
            font_weight = "bold"
        else:
            # É um parágrafo normal
            texto = linha
            font_size = font_size_base
            font_weight = "normal"
        if texto:
            paragrafos.append({
                'text': texto,
                'font_size': font_size,
                'font_weight': font_weight
            })
    return paragrafos

def preencher_frame_notas(frame_notas, versao_atual, LARGURA_CT, ALTURA_CT, fator_escala, notebook, tab1):
    
    print(f"largura: {LARGURA_CT}, altura: {ALTURA_CT}, fator: {fator_escala}")
    
    LARGURA_BARRA_ROLAGEM = int(50 * fator_escala) # Largura padrão da barra de rolagem (aproximadamente 20 pixels)

    # Título
    titulo_label = tk.Label(frame_notas, text=f"Notas de Versão {versao_atual}", font=("Arial", int(16 * fator_escala), "bold"))
    titulo_label.pack(pady=int(10 * fator_escala))

    # Frame para os parágrafos formatados
    frame_paragrafos = tk.Frame(frame_notas)
    frame_paragrafos.pack(padx=int(20 * fator_escala), pady=int(1 * fator_escala), fill="both", expand=True)

    # Barra de rolagem
    scrollbar = tk.Scrollbar(frame_paragrafos)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Canvas para o frame dos parágrafos
    canvas_paragrafos = tk.Canvas(frame_paragrafos, yscrollcommand=scrollbar.set)
    canvas_paragrafos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configurar a scrollbar para o canvas
    scrollbar.config(command=canvas_paragrafos.yview)

    # Frame para conter os parágrafos dentro do Canvas
    frame_conteudo = tk.Frame(canvas_paragrafos)
    canvas_paragrafos.create_window((0, 0), window=frame_conteudo, anchor="nw")

    # Carregar o conteúdo do arquivo .md
    try:
        # versao_atual = "1.5.1" teste
        versao_doc = versao_atual.replace(".", "_")
        atualizacao_path = get_resource_path(f"docs/Atualização_{versao_doc}.md")
        with open(atualizacao_path, "r", encoding="utf-8") as f:
            conteudo_md = f.read()

            # Formatar o texto Markdown
            paragrafos_formatados = formatar_texto_markdown(conteudo_md, int(10 * fator_escala))

            # Adicionar Labels formatadas ao frame
            for paragrafo in paragrafos_formatados:
                label = tk.Label(
                    frame_conteudo,
                    text=paragrafo['text'],
                    font=("Arial", paragrafo['font_size'], paragrafo['font_weight']),
                    justify='left',
                    wraplength=int(LARGURA_CT - 40 * fator_escala - LARGURA_BARRA_ROLAGEM),  # Ajustar largura do texto com base na largura da janela
                    anchor="w"
                )
                label.pack(fill="x", pady=int(1 * fator_escala))

            # Atualizar a região de rolagem do canvas após adicionar os widgets
            frame_conteudo.update_idletasks()
            canvas_paragrafos.config(scrollregion=canvas_paragrafos.bbox("all"))

    except Exception as e:
        label_erro = tk.Label(
            frame_conteudo,
            text=f"Erro ao carregar o arquivo de atualização: {e}",
            font=("Arial", int(10 * fator_escala))
        )
        label_erro.pack()

    # Configurar a função para lidar com o redimensionamento da região de rolagem
    frame_conteudo.bind("<Configure>", lambda e: canvas_paragrafos.config(scrollregion=canvas_paragrafos.bbox("all")))
    
    def _on_mousewheel(event):
        """Lida com o evento de rolagem do mouse."""
        canvas_paragrafos.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bound_to_mousewheel(event):
        """Vincula o evento de rolagem do mouse ao canvas."""
        canvas_paragrafos.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbound_to_mousewheel(event):
        """Desvincula o evento de rolagem do mouse do canvas."""
        canvas_paragrafos.unbind_all("<MouseWheel>")

    # Vincular eventos de rolagem tanto ao canvas quanto ao frame_conteudo
    canvas_paragrafos.bind("<Enter>", _bound_to_mousewheel)
    canvas_paragrafos.bind("<Leave>", _unbound_to_mousewheel)

    frame_conteudo.bind("<Enter>", _bound_to_mousewheel)
    frame_conteudo.bind("<Leave>", _unbound_to_mousewheel)

    # Para sistemas baseados em Unix (Linux, macOS)
    canvas_paragrafos.bind("<Button-4>", lambda e: canvas_paragrafos.yview_scroll(-1, "units"))
    canvas_paragrafos.bind("<Button-5>", lambda e: canvas_paragrafos.yview_scroll(1, "units"))
    
    frame_conteudo.bind("<Button-4>", lambda e: canvas_paragrafos.yview_scroll(-1, "units"))
    frame_conteudo.bind("<Button-5>", lambda e: canvas_paragrafos.yview_scroll(1, "units"))
    
    # Botão Voltar
    def voltar_para_captura():
        notebook.select(tab1)

    voltar_button = ttk.Button(frame_conteudo, text="Voltar", command=voltar_para_captura)
    voltar_button.pack(pady=10)