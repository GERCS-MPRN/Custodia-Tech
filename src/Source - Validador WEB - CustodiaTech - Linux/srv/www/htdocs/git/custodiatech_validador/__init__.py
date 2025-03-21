from flask import Flask, render_template, request, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from redis import Redis
import io
import fitz #pymupdf
from pyzbar.pyzbar import decode
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from PIL import Image
import json
import hashlib
import magic
from PyPDF2 import PdfReader, PdfWriter
import requests

global sitekey
sitekey = os.getenv("TURNSTILE_SITEKEY")

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Gera uma chave de 24 bytes aleatórios. É necessário para mensagens "flash".
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024  # Limite de 150 MB

# Configuração do Redis
redis_client = Redis(host='127.0.0.1', port=6379, ssl=True, decode_responses=True)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"],  # Limite global de 100 requisições por hora por IP
    strategy="fixed-window",  # Usa a estratégia de janela fixa para a rota onde o limiter é definido
    storage_uri="redis://127.0.0.1:6379"
)

ALLOWED_EXTENSIONS = {'pdf'}

# Função auxiliar para verificar se o arquivo tem extensão permitida
def allowed_file_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_type(file_content):
    mime = magic.from_buffer(file_content.read(2048), mime=True)  # Detecta o MIME
    file_content.seek(0)  # Retorna o cursor do arquivo para o início
    return mime.lower() == "application/pdf"

def custom_get_remote_address():
    return request.remote_addr

def validar_turnstile(response_token):
    secret_key = os.getenv("TURNSTILE_SECRET_KEY")
    if not secret_key:
        return False
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": secret_key,
        "response": response_token,
    }
    resultado = requests.post(url, data=data).json()
    return resultado.get("success", False)

# Verifica o QRCode do PDF e extrai os dados nele contidos
def extrair_dados_qr_code_pdf(conteudo_pdf):
    
    pdf_documento = fitz.open(stream=conteudo_pdf, filetype="pdf")

    # Processa apenas a última página
    ultima_pagina = pdf_documento[-1]
    imagens = ultima_pagina.get_images(full=True)

    for img_index, img in enumerate(imagens):
        xref = img[0]
        base_image = pdf_documento.extract_image(xref)
        image_bytes = base_image["image"]

        # Converte os bytes em uma imagem PIL
        img_pil = Image.open(io.BytesIO(image_bytes))

        # Tenta decodificar o QR Code
        resultado = decode(img_pil)
        for res in resultado:
            dados = res.data.decode()
            try:
                return json.loads(dados)  # Decodifica diretamente como JSON
            except json.JSONDecodeError:
                flash("Documento inválido. Erro ao decodificar JSON.")
                return None
    flash("Nenhum QR Code encontrado na última página do documento.")
    return None

# Verifica a assinatura digital
def verificar_assinatura(hash_documento, assinatura, chave_publica_pem):
    try:
        # Carrega a chave pública a partir do formato PEM
        chave_publica = load_pem_public_key(chave_publica_pem.encode())
        chave_publica.verify(
            bytes.fromhex(assinatura),
            hash_documento.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        flash("Erro na verificação da assinatura.")
        return False

# Calcula o hash do arquivo PDF anexado pelo usuário
def calcular_hash_pdf(conteudo_pdf):
    try:
        # Converte os bytes em um objeto de arquivo
        pdf_file = io.BytesIO(conteudo_pdf)

        # Usa PdfReader para ler o arquivo em memória
        leitor = PdfReader(pdf_file)
        escritor = PdfWriter()

        # Cria um buffer para armazenar o novo PDF
        buffer = io.BytesIO()

        # Adiciona páginas, exceto a última, que contém o QR Code
        for pagina in leitor.pages[:-1]:
            escritor.add_page(pagina)

        # Escreve o PDF no buffer
        escritor.write(buffer)
        buffer.seek(0)

        # Calcula o hash diretamente do conteúdo binário do buffer
        return hashlib.sha256(buffer.read()).hexdigest()

    except Exception:
        flash("Erro no cálculo do hash.")
        return None

# Valida a integridade e autenticidade do relatório
def valida_relatorio(conteudo_pdf):
    
    hash_calculado = calcular_hash_pdf(conteudo_pdf)

    dados_qr = extrair_dados_qr_code_pdf(conteudo_pdf)

    if dados_qr:
        try:
            if hash_calculado == dados_qr["hash"] and verificar_assinatura(hash_calculado, dados_qr["assinatura"], dados_qr["chave_publica"]) and dados_qr["emissor"] == 'CustodiaTech - MPRN':
                flash("O relatório submetido é íntegro e autêntico!")
            else:
                flash("O relatório submetido NÃO é íntegro ou autêntico!")
        except json.JSONDecodeError:
            flash("Documento inválido. Erro ao decodificar o JSON do QR Code.")
    else:
        flash("Não foi possível ler o QR Code.")

# Rotas
@app.errorhandler(413)  # Payload Too Large
def request_entity_too_large(error):
    global sitekey
    flash("O arquivo enviado é muito grande. Limite de tamanho excedido!")
    return render_template('index.html', sitekey=sitekey)

@app.errorhandler(429)  # Too Many Requests
def too_many_requests(error):
    global sitekey
    flash(f"Você enviou muitas requisições em um curto período a partir do IP {custom_get_remote_address()}. Tente novamente mais tarde.")
    return render_template('index.html', sitekey=sitekey)

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def index():
    
    global sitekey

    if request.method == 'POST':

        # Obtém o token do Turnstile enviado pelo formulário
        response_token = request.form.get('cf-turnstile-response')
        
        # Obtém a referência ao arquivo anexado pelo usuário
        arquivo_pdf = request.files['relatorio']
        
        def verifica_campos():
            
            status = False

            # Verifica se o captch foi preenchido
            if not response_token:
                flash('O CAPTCHA não foi preenchido. Tente novamente.')
            # Verifica se o captcha foi validado
            elif not validar_turnstile(response_token):
                flash('Falha na validação do CAPTCHA. Confirme que você é humano.')
            # Verifica se o arquivo foi enviado
            elif 'relatorio' not in request.files:
                flash('Nenhum arquivo foi enviado.')
            # Verifica se o arquivo é válido
            elif arquivo_pdf.filename == '':
                flash('Nenhum arquivo selecionado.')
            # Verifica se a extensão do arquivo anexado é "pdf"
            elif not allowed_file_extension(arquivo_pdf.filename):
                flash('Formato de arquivo inválido. Apenas PDFs são permitidos.')
            # Verifica se o mimetype do arquivo anexado é "application/pdf"
            elif not allowed_file_type(arquivo_pdf):
                flash('Formato de arquivo inválido. Apenas PDFs são permitidos.')
            else:
                status = True

            return status

        if not verifica_campos():
            return render_template('index.html', sitekey=sitekey)
        
        # Lê todo o conteúdo do arquivo diretamente em memória
        conteudo_pdf = arquivo_pdf.read()

        # Valida a integridade e a autenticidade do relatório
        valida_relatorio(conteudo_pdf)

    return render_template('index.html', sitekey=sitekey)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
