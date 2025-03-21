import os
import shutil
import threading
import time
import warnings
import zipfile
from io import BytesIO
from pathlib import Path

import keyboard
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options

warnings.filterwarnings('ignore')

Image.MAX_IMAGE_PIXELS = None

global status
status = 0

global destino
destino = ''

global diretorio
diretorio = ''

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

def status_message_conversas(driver, diretorio_base):

    status = driver.execute_script("""
        
        return new Promise((resolve) => {

            //Cria uma caixa de diálogo personalizada com duas opções
            function showCustomAlert(message, diretorio) {
                // Criar um contêiner de diálogo
                const dialogContainer = document.createElement("div");
                dialogContainer.style.position = "fixed";
                dialogContainer.style.top = "0";
                dialogContainer.style.left = "0";
                dialogContainer.style.width = "100%";
                dialogContainer.style.height = "100%";
                dialogContainer.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
                dialogContainer.style.display = "flex";
                dialogContainer.style.alignItems = "center";
                dialogContainer.style.justifyContent = "center";
                dialogContainer.style.zIndex = "1000";

                //Caixa de diálogo
                const dialogBox = document.createElement("div");
                dialogBox.style.backgroundColor = "#fff";
                dialogBox.style.padding = "20px";
                dialogBox.style.borderRadius = "8px";
                dialogBox.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
                dialogBox.style.textAlign = "center";
                dialogBox.style.width = "560px";

                //Mensagem do diálogo
                const dialogMessage = document.createElement("p");
                dialogMessage.style.color = "#262626";  //Cinza escuro
                dialogMessage.style.fontFamily = "Helvetica Neue, Arial, sans-serif";  //Fonte parecida com a do WhatsApp
                dialogMessage.style.fontSize = "16px";
                dialogMessage.style.lineHeight = "1.6";  // Espaçamento entre linhas
                dialogMessage.style.overflowWrap = "break-word";  // Garante que palavras longas quebrem corretamente
                dialogMessage.style.wordBreak = "break-all";  // Força quebra em palavras contínuas sem espaços
                dialogMessage.textContent = `${message}\n\nOs arquivos foram gravados em: ${diretorio}`;
                dialogBox.appendChild(dialogMessage);

                //Botão de opção 1
                const okButton = document.createElement("button");
                okButton.textContent = "Capturar Outra Conversa";
                okButton.style.margin = "10px";
                okButton.style.backgroundColor = "#25D366";  // Cor verde do WhatsApp
                okButton.style.color = "#fff";  // Texto branco
                okButton.style.border = "none";
                okButton.style.padding = "10px 20px";
                okButton.style.borderRadius = "5px";
                okButton.style.cursor = "pointer";
                okButton.onclick = function () {
                    console.log("Usuário clicou em continuar.");
                    document.body.removeChild(dialogContainer); // Remove o diálogo
                    resolve(1);  // Retorna 1 ao clicar em OK
                };

                //Botão de opção 2
                const cancelButton = document.createElement("button");
                cancelButton.textContent = "Encerrar Captura";
                cancelButton.style.margin = "10px";
                cancelButton.style.backgroundColor = "#25D366";  // Cor verde do WhatsApp
                cancelButton.style.color = "#fff";  // Texto branco
                cancelButton.style.border = "none";
                cancelButton.style.padding = "10px 20px";
                cancelButton.style.borderRadius = "5px";
                cancelButton.style.cursor = "pointer";
                cancelButton.onclick = function () {
                    console.log("Usuário clicou em encerrar.");
                    document.body.removeChild(dialogContainer); // Remove o diálogo
                    resolve(2);  // Retorna 2 ao clicar em Cancelar
                };

                //Adiciona botões ao diálogo
                dialogBox.appendChild(okButton);
                dialogBox.appendChild(cancelButton);
                dialogContainer.appendChild(dialogBox);

                //Adiciona o contêiner de diálogo ao body do documento
                document.body.appendChild(dialogContainer);
                                   
                //Define um evento que retorne 0 caso o diálogo seja removido
                window.addEventListener("beforeunload", () => resolve(0));
            }

            //Chama função para exibir o diálogo
            showCustomAlert("Processo de captura finalizado com sucesso!", arguments[0]);
        });
    """, diretorio_base)

    return status

def status_message_contatos(driver, diretorio_base):

    status = driver.execute_script("""
        
        return new Promise((resolve) => {

            //Cria uma caixa de diálogo personalizada com confirmação
            function showCustomAlert(message, diretorio) {
                // Criar um contêiner de diálogo
                const dialogContainer = document.createElement("div");
                dialogContainer.style.position = "fixed";
                dialogContainer.style.top = "0";
                dialogContainer.style.left = "0";
                dialogContainer.style.width = "100%";
                dialogContainer.style.height = "100%";
                dialogContainer.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
                dialogContainer.style.display = "flex";
                dialogContainer.style.alignItems = "center";
                dialogContainer.style.justifyContent = "center";
                dialogContainer.style.zIndex = "1000";

                //Caixa de diálogo
                const dialogBox = document.createElement("div");
                dialogBox.style.backgroundColor = "#fff";
                dialogBox.style.padding = "20px";
                dialogBox.style.borderRadius = "8px";
                dialogBox.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
                dialogBox.style.textAlign = "center";
                dialogBox.style.width = "560px";

                //Mensagem do diálogo
                const dialogMessage = document.createElement("p");
                dialogMessage.style.color = "#262626";  //Cinza escuro
                dialogMessage.style.fontFamily = "Helvetica Neue, Arial, sans-serif";  //Fonte parecida com a do WhatsApp
                dialogMessage.style.fontSize = "16px";
                dialogMessage.style.lineHeight = "1.6";  // Espaçamento entre linhas
                dialogMessage.style.overflowWrap = "break-word";  // Garante que palavras longas quebrem corretamente
                dialogMessage.style.wordBreak = "break-all";  // Força quebra em palavras contínuas sem espaços
                dialogMessage.textContent = `${message}\n\nOs arquivos foram gravados em: ${diretorio}`;
                dialogBox.appendChild(dialogMessage);

                //Botão de confirmação
                const okButton = document.createElement("button");
                okButton.textContent = "OK";
                okButton.style.margin = "10px";
                okButton.style.backgroundColor = "#25D366";  // Cor verde do WhatsApp
                okButton.style.color = "#fff";  // Texto branco
                okButton.style.border = "none";
                okButton.style.padding = "10px 20px";
                okButton.style.borderRadius = "5px";
                okButton.style.cursor = "pointer";
                okButton.onclick = function () {
                    console.log("Usuário clicou em continuar.");
                    document.body.removeChild(dialogContainer); // Remove o diálogo
                    resolve(3);  // Retorna 3 ao clicar em OK
                };

                //Adiciona botão ao diálogo
                dialogBox.appendChild(okButton);
                dialogContainer.appendChild(dialogBox);

                //Adiciona o contêiner de diálogo ao body do documento
                document.body.appendChild(dialogContainer);
                                   
                //Define um evento que retorne 0 caso o diálogo seja removido
                window.addEventListener("beforeunload", () => resolve(0));
            }

            //Chama função para exibir o diálogo
            showCustomAlert("Processo de captura finalizado com sucesso!", arguments[0]);
        });
    """, diretorio_base)

    return status

#Função que será chamada quando o atalho ctrl+alt+F2 for detectado.
def interrompe_rolagem():
    global stop
    stop = True

# Função da thread que aguarda pelo atalho.
def aguarda_atalho_interrupcao():
    global stop_thread_interrupcao
    while stop_thread_interrupcao == False:
        if keyboard.is_pressed('ctrl+alt+F2'):
            interrompe_rolagem()
            time.sleep(0.3)
        time.sleep(0.1)

#Função que será chamada quando o atalho ctrl+alt+F3 for detectado.
def marca_rolagem():
    global stop
    stop = False

#Função da thread que aguarda pelo atalho.
def aguarda_atalho_continuacao():
    global stop_thread_continuacao
    while stop_thread_continuacao == False:
       if keyboard.is_pressed('ctrl+alt+F3'):
            marca_rolagem()
            time.sleep(0.3)
       time.sleep(0.1)

#Converte PNG em PDF
def converte_para_pdf(input_file, output_file):
    image = Image.open(input_file)
    largura_pagina, altura_pagina = image.width, 3508 #3508 = Formato A4
    paginas = []
    for topo in range(0, image.height, altura_pagina):
        caixa = (0, topo, largura_pagina, min(topo + altura_pagina, image.height))
        pagina = image.crop(caixa)
        paginas.append(pagina)
    paginas[0].save(output_file, save_all=True, append_images=paginas[1:], format='PDF', resolution=100.0)

def full_screenshot_wpp_contatos(driver, save_path:Path):

    global destino
    global diretorio
    global stop
    global thread_atalho_interrupcao
    global thread_atalho_continuacao
    global stop_thread_interrupcao
    global stop_thread_continuacao
    rolagem_interrompida = 0
    ponto_interrupcao = 0

    #Idenificar e clicar no botão que fecha notificação janela de contatos
    while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[3]/div/span/div/div/div[3]/button")) < 1:
        time.sleep(1)
    time.sleep(1)
    
    button_contatos = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[3]/div/span/div/div/div[3]/button")
    
    button_contatos.click()
    
    while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[3]/div/span/div/div/div[3]/button")) > 0:
        time.sleep(1)
    time.sleep(1)
    
    while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[3]/div/div[3]")) < 1:
        time.sleep(1)
    time.sleep(1)

    elemento_contatos = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[3]/div/div[3]")

    driver.execute_script("arguments[0].scrollTo(0, 0);", elemento_contatos)
    time.sleep(0.5)

    img_li = []

    offset = 0
    height = driver.execute_script("return Math.min(" "arguments[0].clientHeight, arguments[0].offsetHeight);", elemento_contatos)

    while(offset < driver.execute_script("return arguments[0].scrollTop;", elemento_contatos) + height):
       
        img = Image.open(BytesIO((elemento_contatos.screenshot_as_png)))
        img_li.append(img)

        if stop == True:
            
            rolagem_interrompida = 1
            driver.execute_script("window.alert('A rolagem com captura automática foi interrompida! Após selecionar o ponto de captura (fundo da lista de contatos visível), pressione ctrl+alt+F3 para continuar.');")
            break

        offset += height

        driver.execute_script("arguments[0].scrollTo(0, "+str(offset)+");", elemento_contatos)
        time.sleep(3)

    while stop == True:
        continue
    
    stop_thread_interrupcao = True
    stop_thread_continuacao = True
    stop = False

    if rolagem_interrompida == 1:

        ponto_interrupcao = driver.execute_script("return arguments[0].scrollTop;", elemento_contatos) + height
    
        driver.execute_script("arguments[0].scrollTo(0, 0);", elemento_contatos)

        time.sleep(3)

        img_li = []
        
        offset = 0
        height = driver.execute_script("return Math.min(" "arguments[0].clientHeight, arguments[0].offsetHeight);", elemento_contatos)

        while(offset < ponto_interrupcao):
        
            img = Image.open(BytesIO((elemento_contatos.screenshot_as_png)))
            img_li.append(img)

            offset += height

            driver.execute_script("arguments[0].scrollTo(0, "+str(offset)+");", elemento_contatos)
            time.sleep(3)
    
    extra_height = offset - driver.execute_script("return arguments[0].scrollHeight;", elemento_contatos)
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
    
    if rolagem_interrompida != 1:
        img_frame.save(save_path)
    else:
        width, height = img_frame.size
        box = (0, 0, width, (ponto_interrupcao * pixel_ratio))
        cropped_img_frame = Image.new("RGB", (width, (ponto_interrupcao * pixel_ratio)))
        cropped_img_frame.paste(img_frame.crop(box))                                      
        cropped_img_frame.save(save_path)

    with open(diretorio+'\\'+'Código_HTML_Contatos.txt', 'wb') as file:
        file.write(driver.page_source.encode('utf-8'))

    buffer = ''
    for c in driver.get_cookies():
        buffer += str(c)+'\n'
    with open(diretorio+'\\'+'Cookies_Contatos.txt', 'w') as cookie:
        cookie.write(buffer)

def full_screenshot_wpp_conversa(driver, save_path:Path, tipo_perfil, opcao_captura):

    global stop
    global destino
    global diretorio
    global thread_atalho_interrupcao
    global thread_atalho_continuacao
    global stop_thread_interrupcao
    global stop_thread_continuacao
    rolagem_interrompida = 0
    ponto_interrupcao = 0

    #Janela de conversa de contato ou grupo
    elemento_conversa = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]")

    while(True):

        if stop == True:
            
            rolagem_interrompida = 1
            driver.execute_script("window.alert('A rolagem automática foi interrompida! Após selecionar o ponto de captura (topo da conversa visível), pressione ctrl+alt+F3 para continuar.');")
            break

        driver.execute_script("arguments[0].scrollTo(0, 0);", elemento_conversa)
        
        texto = ''
        elemento = None

        try:
        
            if len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/button/div/div")) > 0:
                
                elemento = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/button/div/div")
                texto = elemento.text.strip()

            elif len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[1]/div[2]")) > 0:
                    
                elemento = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[1]/div[2]")
                texto = elemento.text.strip()

            elif len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/div/div/div")) > 0:
                
                elemento = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/div/div/div")
                texto = elemento.text.strip()
                
            elif len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[1]/span/span")) > 0:

                elemento = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[1]/span/span")
                texto = elemento.text.strip()

            if texto in ["Sincronizando mensagens mais antigas. Clique para ver o progresso.", "Clique neste aviso para carregar mensagens mais antigas do seu celular.", "Não foi possível carregar as mensagens mais antigas. Abra o WhatsApp no seu celular e clique neste aviso para tentar novamente."]:
                
                elemento.click()

                if texto == "Sincronizando mensagens mais antigas. Clique para ver o progresso.":
        
                    while driver.find_element(By.XPATH, "//html/body/div[1]/div/div/span[2]/div/div/div/div/div/div/div[1]/div[2]").text != '100%':
                        time.sleep(0.5)
                    driver.find_element(By.XPATH, "//html/body/div[1]/div/div/span[2]/div/div/div/div/div/div/div[2]/div/button[2]").click()

                continue

            elif texto in ["As mensagens são protegidas com a criptografia de ponta a ponta e ficam somente entre você e os participantes desta conversa. Nem mesmo o WhatsApp pode lê-las ou ouvi-las. Clique para saber mais.", "As mensagens e as ligações são protegidas com a criptografia de ponta a ponta e ficam somente entre você e os participantes desta conversa. Nem mesmo o WhatsApp pode ler ou ouvi-las. Toque para saber mais.", "Use o WhatsApp no seu celular para abrir mensagens mais antigas."]:
        
                break

            else:

                continue
        
        except:
            continue
    
    while stop == True:
        continue

    stop_thread_interrupcao = True
    stop_thread_continuacao = True
    stop = False
    
    #Janela de contatos
    while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[3]/div/div[3]")) < 1:
        time.sleep(1)
    time.sleep(1)
    
    driver.execute_script("""
                        
                            let contatos = document.querySelector('#pane-side');
                            if (contatos) {
                                contatos.inneHTML = '';
                                contatos.remove();
                            }
                        
                        """)
    
    time.sleep(1)

    if rolagem_interrompida == 1:
        ponto_interrupcao = driver.execute_script("return arguments[0].scrollTop;", elemento_conversa)
    else:
        driver.execute_script("arguments[0].scrollTo(0, 0);", elemento_conversa)
    
    full_screenshot_wpp_perfil_titular(driver, Path(diretorio+'\\'+'Perfil_Titular.png'), opcao_captura)
    full_screenshot_wpp_perfil_interlocutor(driver, Path(diretorio+'\\'+'Perfil_Contato.png'), tipo_perfil)

    with open(diretorio+'\\'+'Código_HTML_Conversa_Titular_Interlocutor.txt', 'wb') as file:
        file.write(driver.page_source.encode('utf-8'))

    buffer = ''
    for c in driver.get_cookies():
        buffer += str(c)+'\n'
    with open(diretorio+'\\'+'Cookies_Conversa_Titular_Interlocutor.txt', 'w') as cookie:
        cookie.write(buffer)

    #Fechar contato interlocutor
    if tipo_perfil == 1:
        driver.find_element(By.XPATH, '//html/body/div[1]/div/div/div[3]/div/div[5]/span/div/span/div/header/div/div[1]/div').click()
    #Fechar grupo interlocutor
    elif tipo_perfil == 2:
        driver.find_element(By.XPATH, '//html/body/div[1]/div/div/div[3]/div/div[5]/span/div/span/div/div/header/div/div[1]/div').click()

    time.sleep(1)

    if rolagem_interrompida != 1:
        driver.execute_script("arguments[0].scrollTo(0, 0);", elemento_conversa)

    #Elimina balão de data repetitivo/flutuante
    driver.execute_script("""
                          
                            let date_popup = document.querySelector('.xnpuxes > span:nth-child(1)');
                            if (date_popup) {
                                date_popup.inneHTML = '';
                                date_popup.remove();
                            }
                          
                          """)
    
    #Elimina botão de rolagem
    driver.execute_script("""
                          
                            let date_popup = document.querySelector('#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div.x10l6tqk.x1epdt8v.x1qs2g4o.xa1v5g2.x3nfvp2.xdt5ytf');
                            if (date_popup) {
                                date_popup.inneHTML = '';
                                date_popup.remove();
                            }
                          
                          """)
    
    time.sleep(1)
   
    img_li = []
    
    offset = 0
    
    height = driver.execute_script("return Math.min(" "arguments[0].clientHeight, arguments[0].offsetHeight);", elemento_conversa)

    while(offset < driver.execute_script("return arguments[0].scrollTop;", elemento_conversa) + height):
    
        img = Image.open(BytesIO((elemento_conversa.screenshot_as_png)))
        img_li.append(img)

        offset += height

        driver.execute_script("arguments[0].scrollTo(0, "+str(offset)+")", elemento_conversa)
    
    extra_height = offset - driver.execute_script("return arguments[0].scrollHeight;", elemento_conversa)
    pixel_ratio = driver.execute_script("return window.devicePixelRatio;")
    if extra_height > 0 and len(img_li) > 1:
        extra_height *= pixel_ratio
        last_image = img_li[-1]
        width, height = last_image.size
        box = (0, extra_height, width, height)
        img_li[-1] = last_image.crop(box)

    #Header do contato ou do grupo
    elemento_header = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/header")
    img_header = Image.open(BytesIO((elemento_header.screenshot_as_png)))
    img_li.insert(0, img_header)
    
    img_frame_height = sum([img_frag.size[1] for img_frag in img_li])
    img_frame = Image.new("RGB", (img_li[0].size[0], img_frame_height))
    offset = 0
    for img_frag in img_li:
        img_frame.paste(img_frag, (0, offset))
        offset += img_frag.size[1]
    
    if rolagem_interrompida != 1:
        img_frame.save(save_path)
    else:
        width, height = img_frame.size
        box = (0, (ponto_interrupcao * pixel_ratio) + img_header.size[1], width, height)
        cropped_img_frame = Image.new("RGB", (width, height - (ponto_interrupcao * pixel_ratio)))
        cropped_img_frame.paste(img_header) 
        cropped_img_frame.paste(img_frame.crop(box), (0, img_header.size[1]))                                      
        cropped_img_frame.save(save_path)

def full_screenshot_wpp_perfil_titular(driver, save_path:Path, opcao_captura):

    global destino
    global diretorio
    
    conta_capturas = 0

    if os.path.exists(destino) == False:
        os.makedirs(destino)
        with open(destino+'\\Contador_de_Capturas.txt', 'w') as cap:
            cap.write('Total de Capturas: 0')
    else:
        with open(destino+'\\Contador_de_Capturas.txt', 'r') as cap:
            conta_capturas = int(cap.readline().split(': ')[1])
    
    while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/header/div/div/div/div/span/div/div[2]/div[2]/button")) < 1:
        time.sleep(1)
    time.sleep(1)
    
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div/header/div/div/div/div/span/div/div[2]/div[2]/button").click()

    time.sleep(1)
    
    while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[2]/div[1]")) < 1:
        time.sleep(1)
    time.sleep(1)
    elemento_perfil = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[2]/div[1]")
    elemento_perfil.click()

    time.sleep(3)
    
    if opcao_captura != 1:
        img_perfil = Image.open(BytesIO((elemento_perfil.screenshot_as_png)))
        img_perfil.save(save_path)
    else:
        
        conta_capturas += 1
        
        nome_titular = driver.find_element(By.XPATH, '//html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/span/div/div/span/div/div/div[2]/div[2]/div/div/span/span').text
        nome_titular = nome_titular.strip().replace('\\','-').replace('/','-').replace(':','-').replace('*','-').replace('?','-').replace('<','-').replace('>','-').replace('|','-').replace('"','').replace('  ', ' ')
        
        diretorio = destino+'\\'+str(conta_capturas).zfill(3)+'_Whatsapp_Contatos_de_'+nome_titular
        
        if os.path.exists(diretorio) == False:
            os.makedirs(diretorio)

        with open(destino+'\\Contador_de_Capturas.txt', 'w') as cap:
            cap.write('Total de Capturas: '+str(conta_capturas))

        save_path = Path(diretorio+'\\'+'Perfil_Titular.png')
        img_perfil = Image.open(BytesIO((elemento_perfil.screenshot_as_png)))
        img_perfil.save(save_path)
        time.sleep(1)

        with open(diretorio+'\\'+'Código_HTML_Perfil_Titular.txt', 'wb') as file:
            file.write(driver.page_source.encode('utf-8'))

        #Não há diferença entre os cookies de Perfil_Titular e Lista_Contatos
        buffer = ''
        for c in driver.get_cookies():
            buffer += str(c)+'\n'
        with open(diretorio+'\\'+'Cookies_Perfil_Titular.txt', 'w') as cookie:
            cookie.write(buffer)

        time.sleep(1)

        #Abre lista de contatos
        driver.find_element(By.XPATH, '//html/body/div[1]/div/div/div[3]/div/header/div/div/div/div/span/div/div[1]/div[1]').click()
        
        full_screenshot_wpp_contatos(driver, Path(diretorio+'\\'+'Lista_de_Contatos.png'))

def full_screenshot_wpp_perfil_interlocutor(driver, save_path:Path, tipo_perfil):

    global destino
    global diretorio

    while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/header/div[2]/div/div")) < 1:
        time.sleep(1)
    time.sleep(1)

    barra_interlocutor = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/header/div[2]/div/div")
    barra_interlocutor.click()
    time.sleep(1)
    
    img_li = []
    
    #Contato interlocutor
    if tipo_perfil == 1:
        while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[5]/span/div/span/div/div")) < 1:
            time.sleep(1)
        time.sleep(1)
        elemento_perfil = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[5]/span/div/span/div/div")
    
    #Grupo interlocutor
    elif tipo_perfil == 2:
        while len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[5]/span/div/span/div/div/div")) < 1:
            time.sleep(1)
        elemento_perfil = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[5]/span/div/span/div/div/div")
        
    time.sleep(3)

    offset = 0
    height = driver.execute_script("return Math.min(" "arguments[0].clientHeight, arguments[0].offsetHeight);", elemento_perfil)

    while(offset < driver.execute_script("return arguments[0].scrollTop;", elemento_perfil) + height):
       
        img = Image.open(BytesIO((elemento_perfil.screenshot_as_png)))
        img_li.append(img)

        offset += height

        driver.execute_script("arguments[0].scrollTo(0, "+str(offset)+");", elemento_perfil)

    extra_height = offset - driver.execute_script("return arguments[0].scrollHeight;", elemento_perfil)
    if extra_height > 0 and len(img_li) > 1:
        pixel_ratio = driver.execute_script("return window.devicePixelRatio;")
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
    img_frame.save(save_path)

def captura_whatsapp(opcao_captura, driver, zip_files):

    global destino
    global diretorio
    global stop
    global status
    global thread_atalho_interrupcao
    global thread_atalho_continuacao
    global stop_thread_interrupcao
    global stop_thread_continuacao
    
    conta_capturas = 0

    if os.path.exists(destino) == False:
        os.makedirs(destino)
        with open(destino+'\\Contador_de_Capturas.txt', 'w') as cap:
            cap.write('Total de Capturas: 0')
    else:
        with open(destino+'\\Contador_de_Capturas.txt', 'r') as cap:
            conta_capturas = int(cap.readline().split(': ')[1])

    #Inicia as threads de atallho
    stop_thread_interrupcao = False
    stop_thread_continuacao = False
    stop = False
    thread_atalho_interrupcao = threading.Thread(target=aguarda_atalho_interrupcao, daemon=True)
    thread_atalho_interrupcao.start()
    thread_atalho_continuacao = threading.Thread(target=aguarda_atalho_continuacao, daemon=True)
    thread_atalho_continuacao.start()

    url = "https://web.whatsapp.com/"
        
    driver.get(url)
    driver.maximize_window()

    if opcao_captura == 1:

        full_screenshot_wpp_perfil_titular(driver, None, opcao_captura)
        converte_para_pdf(diretorio+'\\'+'Lista_de_Contatos.png', diretorio+'\\'+'Lista_de_Contatos.pdf')
        converte_para_pdf(diretorio+'\\'+'Perfil_Titular.png', diretorio+'\\'+'Perfil_Titular.pdf')

        # Zipa a pasta criada
        zip_path = str(Path(diretorio).with_suffix('.zip'))  # Convertendo para string
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for file_path in Path(diretorio).rglob('*'):
                if file_path.is_file():
                    zip_file.write(str(file_path), str(file_path.relative_to(diretorio)))

        # Deletar a pasta após criar o zip
        shutil.rmtree(diretorio)
        
        # Adiciona o caminho do arquivo zip à lista
        zip_files.append(zip_path)
        
        while True:
            try:
                status = status_message_contatos(driver, diretorio)
                if status:
                    break
            #except TimeoutException:
            except:
                continue
    
    else:

        contato = grupo = 0
        conta_capturas += 1
        
        #Verifica a presença do header de contato ou de grupo
        while (contato := len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/header/div[2]/div/div/div"))) < 1 and (grupo := len(driver.find_elements(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/header/div[2]/div[1]/div"))) < 1:
            time.sleep(1)
        time.sleep(1)

        interlocutor = ''
        if contato == 1:
            interlocutor = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/header/div[2]/div/div/div").text
            tipo_perfil = 1
        elif grupo == 1:
            interlocutor = driver.find_element(By.XPATH, "//html/body/div[1]/div/div/div[3]/div/div[4]/div/header/div[2]/div[1]/div").text
            tipo_perfil = 2
    
        interlocutor = interlocutor.strip().replace('\\','-').replace('/','-').replace(':','-').replace('*','-').replace('?','-').replace('<','-').replace('>','-').replace('|','-').replace('"','').replace('  ', ' ')
        
        diretorio = destino+'\\'+str(conta_capturas).zfill(3)+'_Whatsapp_Conversa_com_'+interlocutor
               
        if os.path.exists(diretorio) == False:
            os.makedirs(diretorio)

        with open(destino+'\\Contador_de_Capturas.txt', 'w') as cap:
            cap.write('Total de Capturas: '+str(conta_capturas))

        full_screenshot_wpp_conversa(driver, Path(diretorio+'\\'+'Conversa.png'), tipo_perfil, opcao_captura)
        converte_para_pdf(diretorio+'\\'+'Conversa.png', diretorio+'\\'+'Conversa.pdf')
        converte_para_pdf(diretorio+'\\'+'Perfil_Contato.png', diretorio+'\\'+'Perfil_Contato.pdf')
        converte_para_pdf(diretorio+'\\'+'Perfil_Titular.png', diretorio+'\\'+'Perfil_Titular.pdf')

        # Zipa a pasta criada
        zip_path = str(Path(diretorio).with_suffix('.zip'))  # Convertendo para string
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for file_path in Path(diretorio).rglob('*'):
                if file_path.is_file():
                    zip_file.write(str(file_path), str(file_path.relative_to(diretorio)))

        # Deletar a pasta após criar o zip
        shutil.rmtree(diretorio)
        
        # Adiciona o caminho do arquivo zip à lista
        zip_files.append(zip_path)
        
        while True:
            try:
                status = status_message_conversas(driver, diretorio)
                if status:
                    break
            #except TimeoutException:
            except:
                continue

def iniciar_captura_whatsapp(case_directory, parametro):
    
    global destino 
    global stop_thread_interrupcao
    global stop_thread_continuacao
    global stop
    
    user_dir = str(Path.home())
    user_dir_custodiatech = user_dir+'\\AppData\\Local\\CustodiaTech\\_internal'
    profile_dir = user_dir_custodiatech+'\\Profile_Whatsapp'
    
    destino = str(Path(case_directory))+'\\Whatsapp'

    # Configuração das opções do Firefox
    firefox_options = Options()
    
    # Gera um profile temporário a partir de um profile fixo (Profile_Whatsapp)
    firefox_profile = FirefoxProfile(profile_dir)
    firefox_profile.update_preferences()
    firefox_options.profile = firefox_profile

    zip_files = []
    
    try:

        # Instancia o WebDriver
        driver = webdriver.Firefox(options=firefox_options)

        split_dir = '\\'+firefox_profile.path.split('\\')[7]
        temp_profile_path_selenium = firefox_profile.path.replace(split_dir, '')
        temp_profile_path_mozilla = driver.capabilities['moz:profile']
            
        while(True):
            #Função que chama a captura. 
            captura_whatsapp(parametro, driver, zip_files)
            if status != 1:
                break

        driver.quit()
    
        time.sleep(3)

        # Exclui os dados do perfil temporário criado pelo Selenium
        if os.path.exists(temp_profile_path_selenium):
            shutil.rmtree(temp_profile_path_selenium)

        if os.path.exists(temp_profile_path_mozilla):
            shutil.rmtree(temp_profile_path_mozilla)
    
    except:
        print('O navegador foi fechado de modo manual pelo usuário ou ocorreu um erro interno na aplicação.')

    stop_thread_interrupcao = True
    stop_thread_continuacao = True
    stop = False

    # Aguarda as threads terminarem
    thread_atalho_interrupcao.join()
    thread_atalho_continuacao.join()

    return zip_files