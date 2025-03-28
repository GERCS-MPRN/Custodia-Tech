import time
import tkinter as tk

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def login_tiktok(captura_paginas_profile, cookies_file, button_login, button_download):
    """
    Realiza o login no TikTok e salva os cookies em txt
    """
    
    button_login.config(state=tk.DISABLED)
    
    options = ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--nogpu')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--enable-javascript')
    options.add_argument(r"user-data-dir={}".format(captura_paginas_profile))
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--log-level=3")
    options.add_argument("--enable-unsafe-swiftshader")
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiktok.com/login")
    
    # URLs válidas após o login
    valid_urls = [
        "https://www.tiktok.com/foryou?lang=pt-BR",
        "https://www.tiktok.com/foryou",
        "https://www.tiktok.com/"
    ]
    
    # Loop de espera: monitora a URL até que ela corresponda a uma das URLs desejadas
    while True:
        current_url = driver.current_url
        # print("Current URL:", current_url)
        if current_url in valid_urls:
            break
        time.sleep(2)

    # Obtém os cookies
    cookies = driver.get_cookies()
    driver.quit()

    # Salva os cookies em um arquivo no formato Netscape
    with open(cookies_file, 'w', encoding='utf-8') as f:
        f.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            domain = cookie.get("domain")
            # Define a flag como TRUE se o domínio começar com ponto (domínios abrangentes)
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = cookie.get("path", "/")
            secure = "TRUE" if cookie.get("secure", False) else "FALSE"
            # Caso não haja expiração, usa 0
            expiry = str(cookie.get("expiry", 0))
            name = cookie.get("name")
            value = cookie.get("value")
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
            
    button_download.config(state=tk.NORMAL)