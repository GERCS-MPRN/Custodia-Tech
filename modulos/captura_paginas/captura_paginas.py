import base64
import html
import io
import os
import shutil
import threading
import time
import warnings
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import urllib.parse
from urllib.parse import urljoin

import keyboard
import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from urllib3.util.retry import Retry
import magic #python-magic-bin
import mimetypes

warnings.filterwarnings('ignore')

icone_custodia = 'imagens\\iconecustodiatech.ico'

Image.MAX_IMAGE_PIXELS = None

global sair
sair = 0

global stop
stop = False

# Define flags globais para controlar as threads
global stop_thred_interrupcao
stop_thread_interrupcao = False
global stop_thred_continuacao
stop_thread_continuacao = False

# Define as threads de atalho
global thread_atalho_interrupcao
thread_atalho_interrupcao = None
global thread_atalho_continuacao
thread_atalho_continuacao = None

global conta_arquivos
conta_arquivos = 0

global js_visible_elements

# Identifica e isola mídias
js_visible_elements =   """
                        return Array.from(document.querySelectorAll("img, video, image, svg, i, div, source")).flatMap(function(elem) {
                            var rect = elem.getBoundingClientRect();
                            var style = window.getComputedStyle(elem);

                            //Função para verificar se o valor do atributo começa com os prefixos desejados
                            function isRelevantValue(value) {
                                return value && (value.startsWith("http") || value.startsWith("/") || value.startsWith("//") || 
                                                value.startsWith("blob:") || value.startsWith("data:") || value.includes("url(") || value.includes("url ("));
                            }

                            //Filtra apenas elementos visíveis e com atributos relevantes que atendem aos critérios
                            if (rect.width > 0 && rect.height > 0 && style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0") {
                                // Extrai e processa os valores dos atributos
                                return [
                                    elem.getAttribute("src"),
                                    elem.getAttribute("style"),
                                    elem.getAttribute("poster"),
                                    elem.getAttribute("xlink:href"),
                                    elem.getAttribute("data-src"),
                                    elem.getAttribute("data-curl"),
                                    elem.getAttribute("data-surl")
                                ]
                                .filter(isRelevantValue) // Filtra apenas os valores que passam no filtro
                                .concat(
                                    // Para o srcset, divide os valores separados por vírgula e aplica o filtro
                                    (elem.getAttribute("srcset") || "")
                                        .split(",")
                                        .map(item => item.trim().split(" ")[0]) // Pega apenas o URL antes do tamanho (se houver)
                                        .filter(isRelevantValue)
                                );
                            } else {
                                return [];
                            }
                        });
                        """

global js_remove_elements

# JavaScript para remover elementos de sites específicos
js_remove_elements = """
(function() {
    var currentURL = window.location.href;

    // Facebook
    if (currentURL.includes("facebook.com")) {
        var fbElements = [
            '.x9f619.x1ja2u2z.x1xzczws.x7wzq59', // Pop-up
            'div[data-pagelet="ProfileTilesFeed_0"]', // Apresentação
            'div[data-pagelet="ProfileTilesFeed_1"]', // Fotos
            'div[data-pagelet^="ProfileTilesFeed_"]', // Amigos
            'footer[aria-label="Facebook"][role="contentinfo"]' // Footer
        ];
        fbElements.forEach(selector => {
            var element = document.querySelector(selector);
            if (element) element.remove();
        });
    }

    // Twitter (X)
    if (currentURL.includes("twitter.com") || currentURL.includes("x.com")) {
        var popupElement = document.querySelector('div[class="css-175oi2r r-aqfbo4 r-gtdqiz r-1gn8etr r-1g40b8q"]');
        if (popupElement) popupElement.remove();
    }

    // Kwai
    if (currentURL.includes("kwai.com")) {
        var kwaiElements = [
            'div[class="top-bar"][data-v-79aaa428=""][data-v-34574b58=""]', // Topbar
            'div[class="sideContainer slide"][data-v-4e151dd5=""][data-v-277622c8=""]' // Barra lateral
        ];
        kwaiElements.forEach(selector => {
            var element = document.querySelector(selector);
            if (element) element.remove();
        });
    }

    // YouTube
    if (currentURL.includes("youtube.com")) {
        var sidebarElement = document.querySelector("#guide");
        if (sidebarElement) sidebarElement.remove();
    }
})();
"""

# Oculta elementos que flutuam na tela e interferem na captura
def hide_floating_elements(driver, selectors):
    for selector in selectors:
        driver.execute_script(
            """
            var elements = document.querySelectorAll(arguments[0]);
            for (var i = 0; i < elements.length; i++) {
                elements[i].style.display = 'none';
            }
            """, selector
        )

    driver.execute_script("""
        var elements = document.querySelectorAll('*');
        for (var i = 0; i < elements.length; i++) {
            var style = window.getComputedStyle(elements[i]);
            if (style.position === 'fixed') {
                var rect = elements[i].getBoundingClientRect();
                var elementArea = rect.width * rect.height;
                var viewportArea = window.innerWidth * window.innerHeight;
                
                // Verifica se o elemento ocupa uma proporção significativa do viewport
                if (
                    rect.bottom > 0 && rect.top < window.innerHeight &&
                    rect.right > 0 && rect.left < window.innerWidth &&
                    elementArea / viewportArea < 0.2 // Oculta se ocupar menos de 20% do viewport
                ) {
                    elements[i].style.display = 'none';
                }
            }
        }
    """)

# Identifica o maior elemento rolável da página 
def get_largest_scrollable_element(driver):
    
    largest_element = driver.execute_script(
        """
        const elements = [document.documentElement, document.body].concat(
            Array.from(document.querySelectorAll("*")).filter(function(elem) {
                const style = window.getComputedStyle(elem);
                return style.overflowY === 'scroll' || style.overflowY === 'auto';
            })
        );

        let maxScrollArea = 0;
        let largestScrollable = null;

        elements.forEach(element => {
            const scrollArea = element.scrollHeight * element.scrollWidth;
            if (scrollArea > maxScrollArea) {
                maxScrollArea = scrollArea;
                largestScrollable = element;
            }
        });

        return largestScrollable;
        """
    )
    return largest_element  

# Função que será chamada quando o atalho ctrl+alt+F5 for detectado.
def interrompe_rolagem():
    global stop
    stop = True

# Função da thread que aguarda pelo atalho.
def aguarda_atalho_interrupcao():
    global stop_thread_interrupcao
    while stop_thread_interrupcao == False:
        if keyboard.is_pressed('ctrl+alt+F5'):
            interrompe_rolagem()
            time.sleep(0.3)
        time.sleep(0.1)

# Função que será chamada quando o atalhoctrl+alt+F6 for detectado.
def marca_rolagem():
    global stop
    stop = False

# Função da thread que aguarda pelo atalho.
def aguarda_atalho_continuacao():
    global stop_thread_continuacao
    while stop_thread_continuacao == False:
       if keyboard.is_pressed('ctrl+alt+F6'):
            marca_rolagem()
            time.sleep(0.3)
       time.sleep(0.1)

# Converte PNG em PDF
def converte_para_pdf(input_file, output_file):
    image = Image.open(input_file)
    largura_pagina, altura_pagina = image.width, 3508 #3508 = Formato A4
    paginas = []
    for topo in range(0, image.height, altura_pagina):
        caixa = (0, topo, largura_pagina, min(topo + altura_pagina, image.height))
        pagina = image.crop(caixa)
        paginas.append(pagina)
    paginas[0].save(output_file, save_all=True, append_images=paginas[1:], format='PDF', resolution=100.0)

# Identifica o maior elemento rolável e captura as tags das mídias da página, além de capturar imagens das telas
def rolagem_captura(driver, caminho, nome_arquivo, ponto_interrupcao, rolagem_interrompida):

    global js_visible_elements
    global js_remove_elements
    global stop
    global thread_atalho_interrupcao
    global thread_atalho_continuacao
    global stop_thread_interrupcao
    global stop_thread_continuacao
    
    # Executa o JavaScript para remover os elementos indesejados
    driver.execute_script(js_remove_elements)

    # Define os seletores CSS dos elementos flutuantes a serem ocultados
    floating_elements_selectors = [
        "nav",              # Barra de navegação fixa
        ".floating-banner", # Banner flutuante
        ".cookie-banner",   # Banner de cookies
        ".sticky-footer",   # Rodapé flutuante
        ".privacy-banner",  # Banner de privacidade
        "#modal",           # Pop-up modal
    ]

    # Oculta elementos flutuantes durante a rolagem
    hide_floating_elements(driver, floating_elements_selectors)

    element = get_largest_scrollable_element(driver)

    driver.execute_script("arguments[0].scrollTo(0, 0);", element)

    time.sleep(0.5)

    # Espera que a página esteja completamente carregada (HTML)
    while (d := driver.execute_script("return document.readyState")) != "complete":
        time.sleep(0.5)
    
    img_li = []
    visible_html_array = []
            
    height = 0
    offset = 0
    height = driver.execute_script("return Math.min(" "arguments[0].clientHeight, arguments[0].offsetHeight);", element)
    if height == 0 and driver.execute_script("return window.innerHeight") != None:
        height = driver.execute_script("return window.innerHeight")
    total_height = driver.execute_script("return arguments[0].scrollHeight;", element)
    img_height = 0

    while(offset < ponto_interrupcao):

        # Executa o JavaScript para remover os elementos indesejados
        driver.execute_script(js_remove_elements)

        # Oculta elementos flutuantes durante a rolagem
        hide_floating_elements(driver, floating_elements_selectors)
    
        visible_elements = driver.execute_script(js_visible_elements)
        for ve in visible_elements:
            if ve not in visible_html_array:
                visible_html_array.append(ve)
        
        # Captura a tela usando Chrome DevTools Protocol (CDP)
        screenshot = driver.execute_cdp_cmd("Page.captureScreenshot", {})
        image_data = screenshot["data"]
        image = Image.open(io.BytesIO(base64.b64decode(image_data))) # Converte o base64 para imagem
        img_height += image.size[1]
        img_li.append(image)

        # Obtém as coordenadas do elemento, limitando ao viewport
        rect = driver.execute_script("""
            var rect = arguments[0].getBoundingClientRect();
            var viewportHeight = window.innerHeight;  // Obtém a altura do viewport
            
            // Se qualquer um dos valores for zero, pega o outro; caso contrário, usa o menor
            var final_height = (rect.height && viewportHeight) ? Math.min(rect.height, viewportHeight) : Math.max(rect.height, viewportHeight);
               
            return {
                x: rect.x, 
                y: rect.y, 
                width: rect.width, 
                height: final_height  // Limita a altura ao viewport
            };
        """, element)

        diff = height - rect["height"]

        print('---------------------')
        print(f'height: {height}')
        print(f'rect: {rect["height"]}')
        print(f'diff: {diff}')
        print(f'ponto_interrupcao: {ponto_interrupcao}')

        if diff > 0:
            last_image = img_li[-1]
            box = (0, 0, rect["width"], rect["height"])
            img_li[-1] = last_image.crop(box)
            
        offset += height
        
        driver.execute_script("arguments[0].scrollTo(0, "+str(offset)+");", element)
        time.sleep(3)

    extra_height = offset - driver.execute_script("return arguments[0].scrollHeight;", element)
    pixel_ratio = driver.execute_script("return window.devicePixelRatio;")
    if extra_height > 0 and len(img_li) > 1:
        extra_height *= pixel_ratio
        last_image = img_li[-1]
        width, height = last_image.size
        box = (0, extra_height, width, height)
        img_li[-1] = last_image.crop(box)

    img_frame_height = sum([img_frag.size[1] for img_frag in img_li])
    img_frame = Image.new("RGB", (img_li[0].size[0], img_frame_height))
    offset = 0
    for img_frag in img_li:
        img_frame.paste(img_frag, (0, offset))
        offset += img_frag.size[1]
    img_frame.save(Path(caminho+'\\'+nome_arquivo+'.png'))

    if rolagem_interrompida != 1:
        img_frame.save(Path(caminho+'\\'+nome_arquivo+'.png'))
    else:
        width, height = img_frame.size
        box = (0, 0, width, (ponto_interrupcao * pixel_ratio))
        cropped_img_frame = Image.new("RGB", (width, (ponto_interrupcao * pixel_ratio)))
        cropped_img_frame.paste(img_frame.crop(box))                                      
        cropped_img_frame.save(Path(caminho+'\\'+nome_arquivo+'.png'))
    
    visible_elements = driver.execute_script(js_visible_elements)
    for ve in visible_elements:
        if ve not in visible_html_array:
            visible_html_array.append(ve)

    return visible_html_array

# Decodifica o conteúdo em base64 e salva como arquivo com a extensão apropriada
def processa_base64(link_tratado, conta_arquivos, midias_dir):

    link_split = link_tratado.split('base64,')[0].split(':')[1].split(';')[0].split('/')
    extensao = link_split[1].lower()
    cadeia = link_tratado.split('base64,')[1]

    file_data = base64.b64decode(cadeia)

    file_name = f"{str(conta_arquivos).zfill(5)}_Media_File.{extensao}"

    with open(midias_dir+'\\'+file_name, "wb") as file:
        file.write(file_data)

# Trata links de mídias
def get_midias(midias_dir, visible_html_array, base_url):

    global conta_arquivos

    resultado = []

    # Analisa resultados e manipulação de dados
    for link_tratado in visible_html_array:

        while r'\/' in link_tratado:

            link_tratado = link_tratado.replace(r'\/','/')

        link_tratado = html.unescape(link_tratado)

        if link_tratado.startswith('//'):

            link_tratado = urljoin('https:', link_tratado)

            resultado.append(link_tratado)
        
        elif link_tratado.startswith('/'):

            link_tratado = urljoin(base_url, link_tratado)

            resultado.append(link_tratado)

        elif link_tratado.startswith('data:') and 'base64' in link_tratado:

            conta_arquivos += 1

            try:
                processa_base64(link_tratado, conta_arquivos, midias_dir)
            except:
                continue

        elif link_tratado.startswith('blob:'):

            link_tratado = link_tratado.split('blob:')[1]

            resultado.append(link_tratado)

        elif 'url(' in link_tratado or 'url (' in link_tratado:

            link_tratado = link_tratado.replace('url (', 'url(')

            link_split = link_tratado.split('url(')[1].split(')')[0].replace('"', '').replace("'",'')

            if link_split.startswith('data:') and 'base64' in link_split:

                conta_arquivos += 1

                try:
                    processa_base64(link_split, conta_arquivos, midias_dir)
                except:
                    continue
            elif link_split.startswith('http'):
                resultado.append(link_split)
        
        elif link_tratado.startswith('http'):

            resultado.append(link_tratado)

    return resultado

# Rola automaticamente as páginas
def rolagem_automatica_paginas(driver, ajuste_pagina):

    global sair
    global conta_arquivos

    global js_visible_elements
    global js_remove_elements
    global stop
    global thread_atalho_interrupcao
    global thread_atalho_continuacao
    global stop_thread_interrupcao
    global stop_thread_continuacao

    if ajuste_pagina == 0:
        stop_thread_interrupcao = True
        stop_thread_continuacao = True
        stop = False

    abas = driver.window_handles
    
    dict_captura = []

    # Processa as abas do navegador
    for aba in abas:

        rolagem_interrompida = 0
        ponto_interrupcao = 0

        stop = False
        
        driver.switch_to.window(aba)

        # Executa o JavaScript para remover os elementos indesejados
        driver.execute_script(js_remove_elements)

        # Define os seletores CSS dos elementos flutuantes a serem ocultados
        floating_elements_selectors = [
            "nav",              # Barra de navegação fixa
            ".floating-banner", # Banner flutuante
            ".cookie-banner",   # Banner de cookies
            ".sticky-footer",   # Rodapé flutuante
            ".privacy-banner",  # Banner de privacidade
            "#modal",           # Pop-up modal
        ]

        #Oculta elementos flutuantes durante a rolagem
        hide_floating_elements(driver, floating_elements_selectors)

        element = get_largest_scrollable_element(driver)

        driver.execute_script("arguments[0].scrollTo(0, 0);", element)
        
        time.sleep(0.5)

        # Espera que a página esteja completamente carregada (HTML)
        while (d := driver.execute_script("return document.readyState")) != "complete":
            time.sleep(0.5)

        height = 0
        offset = 0
        height = driver.execute_script("return Math.min(" "arguments[0].clientHeight, arguments[0].offsetHeight);", element)
        if height == 0 and driver.execute_script("return window.innerHeight") != None:
            height = driver.execute_script("return window.innerHeight")
        total_height = driver.execute_script("return arguments[0].scrollHeight;", element)

        tentativas = 0

        while(True):

            # Executa o JavaScript para remover os elementos indesejados
            driver.execute_script(js_remove_elements)

            # Oculta elementos flutuantes durante a rolagem
            hide_floating_elements(driver, floating_elements_selectors)
        
            if stop == True:
                
                rolagem_interrompida = 1
                driver.execute_script("window.alert('A rolagem com captura automática foi interrompida para essa página! Após selecionar o ponto de captura (fundo da página visível), pressione ctrl+alt+F6 para continuar.');")
                break

            offset += height
            driver.execute_script("arguments[0].scrollTo(0, arguments[1]);", element, offset)
            
            total_height = driver.execute_script("return arguments[0].scrollHeight;", element)

            if offset > total_height:
                offset = total_height
                tentativas += 1
                time.sleep(0.4)
            else:
                tentativas = 0

            if tentativas == 10:
                break
        
        while stop == True:
            continue

        ponto_interrupcao = driver.execute_script("return arguments[0].scrollTop;", element) + height

        dict_captura.append({"url" : driver.current_url, "rolagem_interrompida" : rolagem_interrompida, "ponto_interrupcao" : ponto_interrupcao})

    stop_thread_interrupcao = True
    stop_thread_continuacao = True
    stop = False

    return dict_captura

# Exibe a barra de progresso
def mostra_barra_progresso(driver, headless):

    # Define o caminho para o arquivo HTML local da barra de progresso
    base_dir = os.path.dirname(os.path.abspath(__file__))
    barra_progresso_path = f"file://{os.path.join(base_dir, 'Progresso.html')}"

    if headless == 0:
        driver.switch_to.window(driver.window_handles[-1]) 
        driver.switch_to.new_window('tab')
    driver.get(barra_progresso_path)  #Abre o arquivo HTML da barra de progresso
    time.sleep(0.5)
    barra = driver.window_handles[-1]

    while len(driver.find_elements(By.XPATH, '//html/body/input')) < 1:
        continue

    element = driver.find_element(By.XPATH, '//html/body/input')

    # Inicia a barra de progresso a partir de um botão oculto no HTML
    driver.execute_script("""
                            
                                let elemento = document.querySelector('#invisibleButtonInc');
                                if (elemento) {
                                    elemento.click();
                                }
                            
                            """)
    return barra

def get_mime_extension():
    
    mime_to_extension = {
            
            # Imagens
            "image/avif": "avif",
            "image/heic": "heic",
            "image/heif": "heif",
            "image/jp2": "jp2",
            "image/jpx": "jpe2",
            "image/jpeg": "jpeg",
            "image/jpg": "jpg",
            "image/pjpeg": "jpe",
            "image/tiff": "tiff",
            "image/x-tiff": "tif",
            "image/webp": "webp",
            "image/x-canon-cr2": "cr2",
            "image/bmp": "bmp",
            "image/x-sony-arw": "arw",
            "image/x-adobe-dng": "dng",
            "image/gif": "gif",
            "image/vnd.microsoft.icon": "ico",
            "image/x-jxr": "jxr",
            "image/x-wdp": "wdp",
            "image/png": "png",
            "image/svg+xml": "svg",
            "image/x-icon": "ico",
            "image/jfif": "jfif",

            # Vídeos
            "video/avi": "avi",
            "video/divx": "divx",
            "video/mpeg": "mpeg",
            "video/webm": "webm",
            "video/mp4": "mp4",
            "video/ogg": "ogv",
            "video/x-ms-asf": "asf",
            "video/x-ms-wmv": "wmv",
            "video/x-msvideo": "avi",
            "video/x-flv": "flv",
            "video/x-matroska": "mkv",
            "video/quicktime": "mov",
            "application/x-shockwave-flash": "swf",
            "video/x-f4v": "f4v",
            "video/x-m4v": "m4v",
            "video/mp2": "mpe",
            "video/mpg": "mpg",
            "video/av1": "av1",
            "video/x-ogm+ogg": "ogm",
            "video/x-ms-asx": "asx",
            "video/x-ms-vob": "vob",
            "video/quicktime": "qt",
            "audio/vnd.rn-realaudio": "ram",
            "video/vnd.rn-realvideo": "rv",

            # Áudios
            "audio/flac": "flac",
            "audio/midi": "midi",
            "audio/mid": "mid",
            "audio/opus": "opus",
            "audio/aac": "aac",
            "audio/x-ape": "ape",
            "audio/mpeg": "mp3",
            "audio/ogg": "ogg",
            "audio/wav": "wav",
            "audio/x-ms-wma": "wma",
            "audio/x-pn-realaudio": "ra",
            "audio/x-m4a": "m4a",
            "audio/x-matroska": "mka",
            "audio/oga": "oga",
            "audio/x-realaudio": "rm",

            # Documentos
            "application/pdf": "pdf",
            "application/vnd.ms-excel": "xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.ms-powerpoint": "ppt",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
            "application/vnd.oasis.opendocument.text": "odt",
            "application/vnd.oasis.opendocument.spreadsheet": "ods",
            "application/vnd.oasis.opendocument.presentation": "odp",

            # Arquivos compactados e executáveis
            "application/zip": "zip",
            "application/x-rar-compressed": "rar",
            "application/x-msdownload": "exe",

        }
    return mime_to_extension

# Completa a barra de progresso.
def completa_barra_progresso(driver):
    driver.execute_script("if (typeof NProgress !== 'undefined') { NProgress.done(); }")
    driver.execute_script("""
                    
                        let elemento = document.querySelector('body > h1.blink');
                        if (elemento) {
                            elemento.classList.remove('blink');
                            elemento.innerText="Captura de página(s) finalizada!";
                        }
                    
                    """)

    time.sleep(0.5)
    
    driver.execute_script("window.alert('Processamento concluído! Página(s) capturada(s) com sucesso!');")

    # Aguarda o usuário dar OK na mensagem, para seguir com o encerramento do programa.
    while(True):
        try:
            d = driver.switch_to.alert.text
        except:
            break

# Processa captura de páginas
def captura_paginas(driver, driver_monitoramento, destino_captura, zip_files, config_captura, modo_captura):

    global sair
    global conta_arquivos

    conta_capturas = 0

    if os.path.exists(destino_captura) == False:
        os.makedirs(destino_captura)
        with open(destino_captura+'\\Contador_de_Capturas.txt', 'w') as cap:
            cap.write('Total de Capturas: 0')
    else:
        with open(destino_captura+'\\Contador_de_Capturas.txt', 'r') as cap:
            conta_capturas = int(cap.readline().split(': ')[1])

    abas = driver.window_handles

    for aba in list(abas):
        # Alterna para a aba
        driver.switch_to.window(aba)
        # Verifica se a aba não possui URL carregada
        if driver.current_url in ['', 'about:blank', 'chrome://new-tab-page/']:
            # Fecha a aba
            driver.close()
            # Atualiza lista de abas após fechamento
            try:
                abas = driver.window_handles
            except:
                sair = 1
                return
    
    # Calcula incremento de cada passo a partir do número de abas abertas
    n_abas = len(abas)
    incremento = str((100 / n_abas) / 100)
    
    if modo_captura == 0:
        barra = mostra_barra_progresso(driver, headless=0)
    
    ponto_interrupcao = 0
    rolagem_interrompida = 0

    # Processa as abas do navegador
    for aba in abas:

        conta_arquivos = 0
        
        driver.switch_to.window(aba)

        time.sleep(0.5)

        # Espera que a página esteja completamente carregada (HTML)
        while (d := driver.execute_script("return document.readyState")) != "complete":
            time.sleep(0.5)

        for cfg in config_captura:
            if cfg["url"] == driver.current_url:
                ponto_interrupcao = cfg["ponto_interrupcao"]
                rolagem_interrompida = cfg["rolagem_interrompida"]
        
        midias_dir = 'Mídias'
        
        if os.path.exists(midias_dir) == False:
            os.makedirs(midias_dir)

        conta_capturas += 1

        # Identifica o domínio da URL base
        base_url = driver.execute_script('return window.location.origin;')
        
        nome_arquivo = (driver.title+' - '+base_url).strip().replace('http://','').replace('https://','').replace('\\','').replace('//','-').replace('/','-').replace(':','').replace('*','').replace('?','').replace('<','').replace('>','').replace('|','').replace('"','').replace('  ', ' ')

        caminho = destino_captura+'\\'+str(conta_capturas).zfill(3)+' - '+nome_arquivo

        if os.path.exists(caminho) == False:
            os.makedirs(caminho)
        
        # Retorna elementos visíveis na página para geração de mídias e salva as capturas de tela da rolagem em um único arquivo PNG
        visible_html_array = rolagem_captura(driver, caminho, nome_arquivo, ponto_interrupcao, rolagem_interrompida)
        
        html = driver.page_source.encode('utf-8')
        buffer_cookie = ''
        for c in driver.get_cookies():
            buffer_cookie += str(c)+'\n'

        if modo_captura == 0:
            #Mostra e incrementa a barra de progresso durante o processamento
            driver.switch_to.window(barra)
        
        lista_midias = get_midias(midias_dir, visible_html_array, base_url)

        #M apeia tipos MIME para extensões
        mime_to_extension = get_mime_extension()
        
        session = requests.Session()
        retry_strategy = Retry(
            total=5,                                # Número total de tentativas
            backoff_factor=30,                      # Espera de 30 segundos em erros temporários
            status_forcelist=[500, 502, 503, 504],  # Repetir em erros temporários
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        #Verifica se a URL é mídia com base no cabeçalho Content-Type visando à obtenção da extensão
        def get_media_info(url):
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "Referer": base_url,        #URL da página de referência (domínio)
                    "Range": "bytes=0-1024",    #Solicita apenas os primeiros 1024 bytes
                    "Accept": "*/*",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                }
                response = requests.get(url, headers=headers, allow_redirects=True, timeout=5, verify=False)
                content_type = response.headers.get("Content-Type", "")
                #print(f"URL: {url}, Content-Type: {content_type}, Status Code: {response.status_code}") #Print apenas para debug.
                if response.status_code in [200, 206] and any(ct in content_type for ct in mime_to_extension):
                    #Obtém a extensão correspondente ao tipo MIME
                    extension = mime_to_extension.get(content_type, "unknown")
                    return url, extension
                return None
            #except requests.RequestException as r:
            except:
                return None

        def download_media(session, media_url):
            try:
                # Define cabeçalhos com 'range' para baixar o conteúdo em partes
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "Referer": base_url,  #URL da página de referência (domínio)
                    "Range": "bytes=0-",  #Solicita o conteúdo em partes
                    "Accept": "*/*",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                }
                response = session.get(media_url, headers=headers, verify=False, stream=True, timeout=5)
                response.raise_for_status()
                return response.content
            #except requests.exceptions.RequestException as e:
            except:
                return None
            
        # Filtra apenas URLs de mídia e obtém suas extensões, removendo None
        media_info = [info for info in (get_media_info(url) for url in lista_midias) if info is not None]

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_info = {executor.submit(download_media, session, media_url): (media_url, extension) for media_url, extension in media_info}

            for future in as_completed(future_to_info):
                url, extension = future_to_info[future]
                tentativa = 0
                while tentativa < 3:
                    try:
                        media_data = future.result()
                        if media_data:
                            
                            conta_arquivos += 1
                            
                            # Obtém o nome original do arquivo a partir da URL
                            parsed_url = urllib.parse.urlparse(url)
                            file_name = os.path.basename(parsed_url.path)  # Obtém o nome do arquivo
                            
                            # Se não houver nome de arquivo, usa "Media_File"
                            if not file_name or "." not in file_name:
                                final_file_name = f"{str(conta_arquivos).zfill(5)}_Media_File.{extension}"
                            else:
                                final_file_name = f"{str(conta_arquivos).zfill(5)}_{file_name}.{extension}"

                            safe_file_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in final_file_name)  # Evita caracteres inválidos
                            
                            # Salva a mídia em um arquivo.
                            with open(os.path.join(midias_dir, safe_file_name), 'wb') as handler:
                                handler.write(media_data)
                            
                            break # Sai do loop se o download for bem-sucedido
        
                        else:
                            print(f"Falha ao baixar {url}. Tentando novamente em 10 segundos...")
                            time.sleep(10)  # Excepcionalmente, aguarda 10 segundos antes de tentar novamente
                            tentativa += 1
                    except:
                        print(f"Falha ao baixar {url}. Tentando novamente em 10 segundos...")
                        time.sleep(10)  # Excepcionalmente, aguarda 10 segundos antes de tentar novamente
                        tentativa += 1

        shutil.move(midias_dir, caminho)

        with open(caminho+'\\'+nome_arquivo+'_HTML.txt', 'wb') as file:
            file.write(html)

        with open(caminho+'\\'+nome_arquivo+'_COOKIE.txt', 'w') as cookie:
            cookie.write(buffer_cookie)

        converte_para_pdf(caminho+'\\'+nome_arquivo+'.png', caminho+'\\'+nome_arquivo+'.pdf')

        # Zipa a pasta criada
        zip_path = f"{caminho}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for file_path in Path(caminho).rglob('*'):
                if file_path.is_file():
                    zip_file.write(str(file_path), str(file_path.relative_to(caminho)))

        # Deleta a pasta após criar o zip
        shutil.rmtree(caminho)
        
        # Adiciona o caminho do arquivo zip à lista
        zip_files.append(zip_path)
        
        if modo_captura == 1:
            #Incrementa a barra de progresso na conclusão do processamento da aba
            driver_monitoramento.execute_script("if (typeof NProgress !== 'undefined') { NProgress.inc("+incremento+"); }")
        else:
            driver.execute_script("if (typeof NProgress !== 'undefined') { NProgress.inc("+incremento+"); }")

    with open(destino_captura+'\\Contador_de_Capturas.txt', 'w') as cap:
            cap.write('Total de Capturas: '+str(conta_capturas))
    
    if modo_captura == 1:
        completa_barra_progresso(driver_monitoramento)
    else:
        completa_barra_progresso(driver)

    sair = 1

def iniciar_captura_de_paginas(case_directory, urls):

    global destino
    global sair
    global stop
    global thread_atalho_interrupcao
    global thread_atalho_continuacao
    global stop_thread_interrupcao
    global stop_thread_continuacao

    modo_captura = 0
    ajuste_pagina = 0
    modo_ajuste = ""

    # Inicia as threads de atallho
    stop_thread_interrupcao = False
    stop_thread_continuacao = False
    stop = False
    thread_atalho_interrupcao = threading.Thread(target=aguarda_atalho_interrupcao, daemon=True)
    thread_atalho_interrupcao.start()
    thread_atalho_continuacao = threading.Thread(target=aguarda_atalho_continuacao, daemon=True)
    thread_atalho_continuacao.start()

    destino = str(Path(case_directory))
    destino_captura = destino + '\\Páginas Capturadas'
    
    user_dir = str(Path.home())
    custodiatech_dir = user_dir+'\\AppData\\Local\\CustodiaTech'
    chromeprofile_dir = custodiatech_dir+'\\Captura_Paginas_Profile'
    
    options = ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--nogpu')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--enable-javascript')
    options.add_argument(r"user-data-dir={}".format(chromeprofile_dir))
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--log-level=3")
    options.add_experimental_option("prefs", {
    "download.default_directory": destino_captura,
    "download.prompt_for_download": False,
    "download.manager.showWhenStarting": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.notifications": 2
    })
    options.add_argument("--enable-unsafe-swiftshader")

    zip_files = []

    try:
        
        driver = webdriver.Chrome(options=options)
        size = driver.get_window_size()

        if len(urls) > 0:
            
            # Carrega páginas
            primeira_pagina = True
            
            for url in urls:
                
                if primeira_pagina:
                    # Carrega a URL na primeira aba
                    driver.get(url)
                    primeira_pagina = False
                else:
                    # Abrir uma nova aba
                    driver.execute_script("window.open('');")
                    # Mudar para a nova aba
                    driver.switch_to.window(driver.window_handles[-1])
                    # Acessar a URL na nova aba
                    driver.get(url)

                time.sleep(0.5)

                # Espera que a página esteja completamente carregada (HTML)
                while (d := driver.execute_script("return document.readyState")) != "complete":
                    time.sleep(0.5)    
        
        else:

            driver.get('https://www.google.com')

            time.sleep(0.5)

            # Espera que a página esteja completamente carregada (HTML)
            while (d := driver.execute_script("return document.readyState")) != "complete":
                time.sleep(0.5)    

        # Solicita a confirmação do modo de captura escolhido
        while True:

            while True:

                if len(driver.window_handles) == 0:
                    break

                if keyboard.is_pressed('ctrl+alt+F7'):
                    modo_captura = 0
                    ajuste_pagina = 1
                    modo_ajuste = "Modo Visual com Ajustes"
                    break

                elif keyboard.is_pressed('ctrl+alt+F8'):
                    modo_captura = 1
                    ajuste_pagina = 1
                    modo_ajuste = "Modo Oculto com Ajustes Prévios"
                    break

                elif keyboard.is_pressed('ctrl+alt+F9'):
                    modo_captura = 1
                    ajuste_pagina = 0
                    modo_ajuste = "Modo Totalmente Oculto sem Ajustes Prévios"
                    break
            
            if len(driver.window_handles) == 0:
                break
            else:
                driver.switch_to.window(driver.window_handles[0]) 
                driver.execute_script("window.focus();")
                driver.execute_script(f"""window.alertResult = confirm("Deseja capturar as páginas no modo abaixo?\\n\\nMODO DE CAPTURA: {modo_ajuste}.");""")
        
                while(True):
                    try:
                        d = driver.switch_to.alert.text
                    except:
                        break

                retorno = driver.execute_script("return window.alertResult;")

                if retorno:
                    break
                else:
                    continue

        if modo_captura == 0 or (modo_captura == 1 and ajuste_pagina == 1):

            config_captura = rolagem_automatica_paginas(driver, ajuste_pagina)

        if modo_captura == 0:
        
            captura_paginas(driver, None, destino_captura, zip_files, config_captura, modo_captura)
        
        elif modo_captura == 1:

            # Usa o comando CDP para listar todas as páginas abertas
            targets = driver.execute_cdp_cmd("Target.getTargets", {})

            # Armazena os cookies de cada URL
            cookies_by_url = {}

            for target in targets["targetInfos"]:
                if target["type"] == "page" and target["url"].startswith("http"):
                    target_id = target["targetId"]  # Obtém o ID da aba/target

                    # Anexa ao target da aba
                    session = driver.execute_cdp_cmd("Target.attachToTarget", {"targetId": target_id, "flatten": True})

                    # Obtém os cookies do target
                    cookies = driver.execute_cdp_cmd("Storage.getCookies", {})["cookies"]
                    cookies_by_url[target["url"]] = cookies

                    # Detacha do target
                    driver.execute_cdp_cmd("Target.detachFromTarget", {"sessionId": session["sessionId"]})

            driver.quit()

            options_monitoramento = ChromeOptions()
            options_monitoramento.add_argument('--start-maximized')
            options_monitoramento.add_experimental_option('excludeSwitches', ['enable-automation'])
            options_monitoramento.add_experimental_option('useAutomationExtension', False)
            options_monitoramento.add_argument('--disable-blink-features=AutomationControlled')
            options_monitoramento.add_argument("--disable-notifications")
            options_monitoramento.add_argument("--disable-infobars")
            options_monitoramento.add_argument("--log-level=3")

            driver_monitoramento = webdriver.Chrome(options=options_monitoramento)

            barra = mostra_barra_progresso(driver_monitoramento, headless=1)

            options.add_argument('--headless=new')
            driver_headless = webdriver.Chrome(options=options)
            driver_headless.set_window_size(size["width"], size["height"])

            # Adiciona os cookies coletados no navegador headless
            primeira_pagina = True
            for url, cookies in cookies_by_url.items():
                if primeira_pagina:
                    # Carrega a URL na primeira aba
                    driver_headless.get(url)
                    primeira_pagina = False
                else:
                    # Abrir uma nova aba
                    driver_headless.execute_script("window.open('');")
                    # Mudar para a nova aba
                    driver_headless.switch_to.window(driver_headless.window_handles[-1])
                    # Acessar a URL na nova aba
                    driver_headless.get(url)

                time.sleep(0.5)

                # Espera que a página esteja completamente carregada (HTML)
                while (d := driver_headless.execute_script("return document.readyState")) != "complete":
                    time.sleep(0.5)    
                
                # Adiciona apenas cookies válidos para o domínio atual
                for cookie in cookies:
                    # Verifica se o domínio do cookie corresponde ao domínio carregado
                    if cookie.get("domain") in driver_headless.current_url:
                        driver_headless.add_cookie(cookie)
                        driver_headless.refresh()

            if ajuste_pagina == 0:
                config_captura = rolagem_automatica_paginas(driver_headless, ajuste_pagina)

            captura_paginas(driver_headless, driver_monitoramento, destino_captura, zip_files, config_captura, modo_captura)
            
        # Aguarda a confirmação de encerramento.
        while (True):
            if sair == 1:
                break

        if modo_captura == 0:
            driver.quit()
        else:
            driver_headless.quit()
            driver_monitoramento.quit()

        time.sleep(1)

    except:
        print('O navegador foi fechado de modo manual pelo usuário ou ocorreu um erro interno na aplicação.')

    stop_thread_interrupcao = True
    stop_thread_continuacao = True
    stop = False

    # Aguarda as threads terminarem
    thread_atalho_interrupcao.join()
    thread_atalho_continuacao.join()

    return zip_files