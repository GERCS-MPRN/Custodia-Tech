import ctypes


def obter_proporcao(monitor_width, monitor_height):
    print(f"monitor_width: {monitor_width}, monitor_height: {monitor_height}")
    return round(monitor_width / monitor_height, 3)

def definir_percentuais(monitor_width, monitor_height, tela="principal"):
    # Usamos os seguintes baselines (já considerando a área de trabalho):
    # 16:9 -> 1920 x 1032
    # 16:10 -> 1680 x 1002
    # 4:3 -> 1280 x 912
    
    if tela == "principal":  # Tamanho desejado: 585x800
        proporcoes = {
            1.777: (0.3046, 0.7407),  # Para 16:9
            1.6:   (0.3482, 0.7619),  # Para 16:10
            1.333: (0.4178, 0.7619),  # Para 4:3
        }
    elif tela == "login":  # Tamanho desejado: 310x340
        proporcoes = {
            1.777: (0.1615, 0.3148),  # Para 16:9
            1.6:   (0.1845, 0.3238),  # Para 16:10
            1.333: (0.2214, 0.3238),  # Para 4:3
        }
    elif tela == "captura_tela":  # Tamanho desejado: 300x360
        proporcoes = {
            1.777: (0.1563, 0.3333),  # Para 16:9
            1.6:   (0.1563, 0.3),     # Para 16:10
            1.333: (0.2930, 0.4688),  # Para 4:3
        }
    elif tela in ("youtube", "tiktok"):  # Tamanho desejado: 400x320
        proporcoes = {
            1.777: (0.2083, 0.2963),  # Para 16:9
            1.6:   (0.2083, 0.2667),  # Para 16:10
            1.333: (0.3906, 0.4167),  # Para 4:3
        }
    elif tela == "x_twitter":  # Tamanho desejado: 400x200
        proporcoes = {
            1.777: (0.2083, 0.1852),  # Para 16:9
            1.6:   (0.2083, 0.1667),  # Para 16:10
            1.333: (0.3906, 0.2604),  # Para 4:3
        }
    elif tela == "whatsapp":  # Tamanho desejado: 300x200
        proporcoes = {
            1.777: (0.1563, 0.1852),  # Para 16:9
            1.6:   (0.1563, 0.1667),  # Para 16:10
            1.333: (0.2930, 0.2604),  # Para 4:3
        }
    elif tela == "extrair_metadados":  # Tamanho desejado: 450x410
        proporcoes = {
            1.777: (0.2344, 0.3796),  # Para 16:9
            1.6:   (0.2344, 0.3417),  # Para 16:10
            1.333: (0.4395, 0.5339),  # Para 4:3
        }
    elif tela == "captura_paginas":  # Tamanho desejado: 480x600
        proporcoes = {
            1.777: (0.2500, 0.5556),  # Para 16:9
            1.6:   (0.2500, 0.5000),  # Para 16:10
            1.333: (0.4688, 0.7813),  # Para 4:3
        }
    else:
        raise ValueError(f"Tela '{tela}' não reconhecida.")
    
    # Obtém a proporção atual do monitor (ou área de trabalho)
    proporcao_atual = obter_proporcao(monitor_width, monitor_height)
    print(f"proporcao_atual: {proporcao_atual}")
    
    # Seleciona a configuração cuja proporção é a mais próxima da atual
    proporcao_mais_proxima = min(proporcoes.keys(), key=lambda p: abs(p - proporcao_atual))
    print(f"proporcao_mais_proxima: {proporcao_mais_proxima}")
    
    return proporcoes[proporcao_mais_proxima]

def obter_monitor_ativo():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()

    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

    ponto = POINT()
    user32.GetCursorPos(ctypes.byref(ponto))
    monitor = user32.MonitorFromPoint(ponto, 1)

    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                    ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_long), ("rcMonitor", RECT),
                    ("rcWork", RECT), ("dwFlags", ctypes.c_long)]

    monitor_info = MONITORINFO()
    monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info))

    # Retorna os limites da área de trabalho excluindo a barra de tarefas
    return monitor_info.rcWork.left, monitor_info.rcWork.top, \
           monitor_info.rcWork.right, monitor_info.rcWork.bottom
           
def centraliza_janela_no_monitor_ativo(janela, tela):
    # Obtém as dimensões da área de trabalho ativa (exclui barra de tarefas)
    monitor_left, monitor_top, monitor_right, monitor_bottom = obter_monitor_ativo()
    
    monitor_width = monitor_right - monitor_left
    monitor_height = monitor_bottom - monitor_top
    
    # Define as proporções desejadas
    LARGURA_PERCENTUAL, ALTURA_PERCENTUAL = definir_percentuais(monitor_width, monitor_height, tela)
    print(f"Tela {tela} -> LARGURA_PERCENTUAL: {LARGURA_PERCENTUAL}, ALTURA_PERCENTUAL: {ALTURA_PERCENTUAL}")

    # Calcula as dimensões da janela com base nos percentuais fornecidos
    LARGURA_CT = int(monitor_width * LARGURA_PERCENTUAL)
    
    if tela == "principal":
        ALTURA_CT = int(monitor_height * ALTURA_PERCENTUAL) + 60
    else:
        ALTURA_CT = int(monitor_height * ALTURA_PERCENTUAL)
    print(f"Tela {tela} -> LARGURA_CT: {LARGURA_CT}, ALTURA_CT: {ALTURA_CT}")

    # Calcula a posição para centralizar a janela na área de trabalho disponível
    pos_x = monitor_left + (monitor_width - LARGURA_CT) // 2
    pos_y = monitor_top + (monitor_height - ALTURA_CT) // 2

    # Define a geometria da janela
    janela.geometry(f"{LARGURA_CT}x{ALTURA_CT}+{pos_x}+{pos_y}")
    
    return LARGURA_CT, ALTURA_CT