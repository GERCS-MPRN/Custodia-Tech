from threading import Thread
import webbrowser
from modulos.gravacao_tela.monitor_downloads_folder import monitor_downloads_folder
from pathlib import Path

def iniciar_gravacao_tela(case_directory, videos_data):
    
    user_dir = str(Path.home())
    user_dir_custodiatech = user_dir+'\\AppData\\Local\\CustodiaTech'
    modulo_gravacao_dir = user_dir_custodiatech+'\\_internal\\modulos\\gravacao_tela'

    path_to_html = modulo_gravacao_dir.replace('\\','/') + '/pagina_gravacao.html'

    webbrowser.open(f"file:///{path_to_html}")

    thread_monitoramento_pasta_download = Thread(
        target=monitor_downloads_folder,
        args=(case_directory, videos_data),
        daemon=True
    )
    thread_monitoramento_pasta_download.start()