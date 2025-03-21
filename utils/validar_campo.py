from utils.formatador_campo import limpar_placeholder_obrigatorio
import tkinter as tk


def valida_campo_preenchido(entry, notebook, tab, error_message):
    """
    Valida se um campo de entrada está vazio ou contém uma mensagem de erro,
    e reporta o erro alternando para a aba especificada e aplicando
    feedback visual ao campo de entrada.

    Args:
        entry: O campo de entrada a ser validado.
        notebook: O widget Tkinter Notebook que contém as abas.
        tab: O objeto da aba (ex: tab2) para a qual mudar quando um erro for encontrado.
        error_message: A mensagem de erro a ser exibida no campo de entrada.

    Returns:
        True se um erro foi encontrado, False caso contrário.
    """
    if not entry.get().strip() or entry.get().strip() == 'CAMPO OBRIGATÓRIO' or entry.get().strip() == 'CPF INVÁLIDO':
        notebook.select(tab)
        entry.delete(0, tk.END)
        entry.insert(0, error_message)
        entry.config(style='Red.TEntry')

        def limpar_e_remover_bind(event):
            limpar_placeholder_obrigatorio(entry)
            entry.unbind("<FocusIn>")

        entry.bind("<FocusIn>", limpar_e_remover_bind)
        return True  # Campo não foi preenchido corretamente

    return False  # Campo preenchido corretamente

def valida_campo_cpf(nome_entry, cpf_entry, notebook, tab):
    """Valida os campos nome e cpf e reporta erros."""
    nome = nome_entry.get().strip()
    cpf = cpf_entry.get().strip()
    
    if (nome and not cpf) or cpf == 'CPF INVÁLIDO':
        return valida_campo_preenchido(cpf_entry, notebook, tab, "CPF INVÁLIDO")
    
    if (not nome and cpf) or nome == 'CAMPO OBRIGATÓRIO':
        return valida_campo_preenchido(nome_entry, notebook, tab, "CAMPO OBRIGATÓRIO")

    return False