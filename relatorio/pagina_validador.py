import os

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import (PageBreak, PageTemplate, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

from relatorio.cabecalho_relatorio import cabecalho_relatorio
from utils.env_manager import SITE_VALIDACAO



def criar_pagina_adicional(temp_pdf, emissor, data_hora_relatorio, hash_documento, assinatura, chave_publica, qr_code_img, dados_gerais_style,styles, logo_path, chaves_style):
    """
    Cria uma página adicional com o conteúdo especificado e salva em um arquivo PDF temporário.
    """
    
    def my_later_pages_qrcode(canvas, doc):
        cabecalho_relatorio(canvas, logo_path)
    
    doc = SimpleDocTemplate(temp_pdf, pagesize=A4, topMargin=2.0 * inch)
    
    elements = []

    # Conteúdo da nova página
    elements.append(Paragraph("Autenticidade e Integridade do Relatório", styles['Title']))
    elements.append(Spacer(1, 9))
    elements.append(Paragraph(f"Emissor: {emissor}", dados_gerais_style))
    elements.append(Spacer(1, 9))
    elements.append(Paragraph(f"Data/Hora da Geração do Relatório: {data_hora_relatorio}", dados_gerais_style))
    elements.append(Spacer(1, 9))
    elements.append(Paragraph("Hash:", dados_gerais_style))
    elements.append(Spacer(1, 1))
    elements.append(Paragraph(f"{hash_documento}", chaves_style))
    elements.append(Spacer(1, 9))
    elements.append(Paragraph("Assinatura:", dados_gerais_style))
    elements.append(Spacer(1, 1))
    elements.append(Paragraph(f"{assinatura}", chaves_style))
    elements.append(Spacer(1, 9))
    elements.append(Paragraph("Chave Pública:", dados_gerais_style))
    elements.append(Spacer(1, 1))
    elements.append(Paragraph("-----BEGIN PUBLIC KEY-----", chaves_style))
    elements.append(Spacer(1, 1))
    elements.append(Paragraph(f"{chave_publica.replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '')}", chaves_style))
    elements.append(Spacer(1, 1))
    elements.append(Paragraph("-----END PUBLIC KEY-----", chaves_style))
    elements.append(Spacer(1, 18))

    # Adicionando a imagem centralizada
    img = RLImage(qr_code_img, width=3 * inch, height=3 * inch)  # Definindo tamanho da imagem
    img.hAlign = 'CENTER'
    elements.append(img)

    elements.append(Spacer(1, 18))
    elements.append(Paragraph(f"Valide este relatório em {SITE_VALIDACAO}.", styles['Center']))
    elements.append(Spacer(1, 9))

    # Construindo o PDF
    doc.build(elements, onFirstPage=my_later_pages_qrcode)

    # Remover o arquivo temporário
    if os.path.exists(qr_code_img):
        os.remove(qr_code_img)

def adicionar_pagina_ao_pdf(original_pdf, emissor, data_hora_relatorio, hash_documento, assinatura, chave_publica, qr_code_img, pdf_saida, dados_gerais_style, styles, logo_path, chaves_style):
    """
    Adiciona uma nova página ao final de um PDF existente e salva o resultado em um novo arquivo.
    """
    # Caminho para o PDF temporário da nova página
    temp_pdf = "pagina_adicional.pdf"

    # Criar a nova página
    criar_pagina_adicional(temp_pdf, emissor, data_hora_relatorio, hash_documento, assinatura, chave_publica, qr_code_img, dados_gerais_style, styles, logo_path, chaves_style)

    # Ler o PDF original e o PDF da nova página
    leitor_original = PdfReader(original_pdf)
    leitor_nova_pagina = PdfReader(temp_pdf)
    escritor = PdfWriter()

    # Adicionar todas as páginas do PDF original
    for pagina in leitor_original.pages:
        escritor.add_page(pagina)

    # Adicionar a nova página ao final
    escritor.add_page(leitor_nova_pagina.pages[0])

    # Escrever o PDF combinado em um arquivo temporário
    temp_saida = "temp_pdf_saida.pdf"
    with open(temp_saida, "wb") as arquivo_saida:
        escritor.write(arquivo_saida)

    # Substituir o arquivo original pelo arquivo final
    os.replace(temp_saida, pdf_saida)
    # Remover o arquivo temporário da nova página
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)
