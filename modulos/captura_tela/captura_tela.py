import os
import time
import tkinter as tk
import zipfile
from datetime import datetime
from tkinter import Image

import mss
from PIL import Image
from screeninfo import get_monitors
from tzlocal import get_localzone

from utils.api_perdigueiro import registrar_acao
from utils.metadata import calculate_hash, get_file_metadata
from utils.renomear_zip import renomear_zip


def select_area(tk_custodia_tech):
    """Abre um overlay para seleção da área e retorna um dicionário com as coordenadas."""
    bbox = {}
    start_x = start_y = 0
    rect = None

    tk_custodia_tech.withdraw()
    # Obter informações de todos os monitores
    monitors = get_monitors()

    # Calcular a área total combinada de todos os monitores
    min_x = min(monitor.x for monitor in monitors)
    min_y = min(monitor.y for monitor in monitors)
    max_x = max(monitor.x + monitor.width for monitor in monitors)
    max_y = max(monitor.y + monitor.height for monitor in monitors)
    total_width = max_x - min_x
    total_height = max_y - min_y

    overlay = tk.Toplevel(tk_custodia_tech)
    # Definir a geometria para cobrir todos os monitores
    overlay.geometry(f"{total_width}x{total_height}+{min_x}+{min_y}")
    overlay.attributes("-alpha", 0.3)  # Define a transparência
    overlay.config(bg="black")
    overlay.overrideredirect(True)  # Remove bordas e controles

    canvas = tk.Canvas(
        overlay, cursor="cross", bg="gray", width=total_width, height=total_height
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    def on_button_press(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(
            start_x, start_y, start_x, start_y, outline="red", width=2
        )

    def on_move_press(event):
        nonlocal rect
        cur_x, cur_y = event.x, event.y
        canvas.coords(rect, start_x, start_y, cur_x, cur_y)

    def on_button_release(event):
        nonlocal bbox
        end_x, end_y = event.x, event.y
        bbox = {
            "left": min(start_x, end_x) + min_x,  # Adicionado o min_x
            "top": min(start_y, end_y) + min_y,  # Adicionado o min_y
            "width": abs(end_x - start_x),
            "height": abs(end_y - start_y),
        }
        overlay.destroy()
        tk_custodia_tech.deiconify()

    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)

    tk_custodia_tech.wait_window(overlay)

    print(f"Bounding box: {bbox}")
    return bbox


def capture_screenshot(
    case_directory, usuario, tk_custodia_tech, tk_captura_tela, bounding_box=None
):
    """
    Captura uma screenshot da tela

    Args:
        case_directory (str): Diretório do caso
        usuario (str): Nome do usuário que está fazendo a captura

    Returns:
        str: Caminho do arquivo de screenshot ou None se houver erro
    """
    try:
        tk_custodia_tech.withdraw()
        time.sleep(0.5)

        if bounding_box is None:
            # Mantém a lógica original para capturar o monitor completo
            x = tk_captura_tela.winfo_rootx()
            y = tk_captura_tela.winfo_rooty()
            for monitor in get_monitors():
                if (
                    monitor.x <= x < monitor.x + monitor.width
                    and monitor.y <= y < monitor.y + monitor.height
                ):
                    with mss.mss() as sct:
                        bbox = {
                            "top": monitor.y,
                            "left": monitor.x,
                            "width": monitor.width,
                            "height": monitor.height,
                        }
                        screenshot = sct.grab(bbox)
                        img = Image.frombuffer(
                            "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX", 0, 1
                        )
                        break
        else:
            # Utiliza a região selecionada
            with mss.mss() as sct:
                screenshot = sct.grab(bounding_box)
                img = Image.frombuffer(
                    "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX", 0, 1
                )

        fuso_local = get_localzone()
        timestamp = datetime.now(fuso_local).strftime("%d-%m-%Y_%H-%M-%S_UTC%Z")
        nome_captura = f"screenshot_{timestamp}.png"
        screenshot_path = os.path.join(case_directory, nome_captura)
        img.save(screenshot_path)

        registrar_acao(
            "Captura realizada",
            f"Captura realizada de nome {nome_captura} pelo usuario {usuario} e salva em {case_directory}",
        )

        tk_custodia_tech.deiconify()
        return screenshot_path
    except Exception as e:
        print(f"Erro ao capturar a screenshot: {e}")
        # Erro ao capturar a screenshot: Expecting value: line 1 column 1 (char 0)
        return None


def capture_and_process_screenshot(
    case_directory,
    algorithms,
    reason,
    usuario,
    tk_custodia_tech,
    captured_screenshots,
    captured_screenshots_zip,
    tk_captura_tela,
    bounding_box,
):
    """
    Captura e processa uma screenshot, incluindo compactação, cálculo de hashes,
    e renomeação do arquivo zip com o timestamp atualizado.

    Args:
        case_directory (str): Diretório do caso
        algorithms (list): Lista de algoritmos de hash a serem calculados
        reason (str): Motivo da captura
        usuario (str): Nome do usuário que está fazendo a captura
        tk_custodia_tech (tk.Tk): Janela principal do tkinter
        captured_screenshots (list): Lista para armazenar os caminhos das screenshots
        captured_screenshots_zip (list): Lista para armazenar os dados dos zips
        tk_captura_tela (tk.Toplevel): Janela de captura da tela
        bounding_box (dict): Área selecionada para captura

    Returns:
        tuple: Tupla contendo (hash_results, file_metadata, reason) ou None se houver erro
    """

    # Verifica se a string reason não está vazia e se o primeiro caractere é minúsculo
    if reason and reason[0].islower():
        reason = (
            reason[0].upper() + reason[1:]
        )  # Converte o primeiro caractere para maiúsculo

    screenshot_path = capture_screenshot(
        case_directory, usuario, tk_custodia_tech, tk_captura_tela, bounding_box
    )
    if screenshot_path:
        captured_screenshots.append(screenshot_path)
        # Compacta a imagem em um .zip usando o nome original com timestamp
        zip_file_path = f"{screenshot_path}.zip"
        with zipfile.ZipFile(zip_file_path, "w") as zip_file:
            zip_file.write(screenshot_path, os.path.basename(screenshot_path))
        print(f"Imagem compactada em {zip_file_path}")

        # Calcula o hash e obtém os metadados do arquivo
        hashes = calculate_hash(zip_file_path, algorithms)
        metadata = get_file_metadata(zip_file_path)

        metadata, _ = renomear_zip(zip_file_path, metadata, "screenshot_")

        captured_screenshots_zip.append((hashes, metadata, reason))
        return hashes, metadata, reason
    return None
