from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from utils.env_manager import (ENDERECO_TELEFONE, NUCLEO, ORGAO, UNIDADE,
                               reload_env)


def cabecalho_relatorio(canvas, logo_path):
    """
    Adiciona um cabeçalho ao relatório PDF.

    Args:
        canvas (Canvas): O objeto canvas do ReportLab onde o cabeçalho será desenhado.
        logo_path (str): O caminho para o arquivo de imagem do logotipo.

    """
    reload_env()  
    
    logo_width = 3.24 * inch
    logo_height = 1.04 * inch
    page_width = A4[0]
    logo_x = (page_width - logo_width) / 2
    canvas.drawImage(logo_path, logo_x, 750,
                        width=logo_width, height=logo_height,
                        mask='auto')

    header_text = [
        ORGAO,
        UNIDADE,
        NUCLEO,
        ENDERECO_TELEFONE
    ]
    
    header_text = [line for line in header_text if line] # Filtra as linhas vazias

    y_position = 740
    font_size = 8
    canvas.setFont("Times-Roman", font_size)

    for line in header_text:
        text_width = canvas.stringWidth(line, "Times-Roman", font_size)
        text_x = (page_width - text_width) / 2
        canvas.drawString(text_x, y_position, line)
        y_position -= 12