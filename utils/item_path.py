import os
import sys


def get_resource_path(relative_path):
    """
    Obtém o caminho absoluto de um recurso, considerando o ambiente de execução.

    Parâmetros:
    relative_path (str): O caminho relativo do recurso a ser localizado.

    Retorna:
    str: O caminho absoluto do recurso.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)