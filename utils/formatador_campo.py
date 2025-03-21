import tkinter as tk 

def validar_cpf(cpf):
    """
    Valida um CPF.

    Parâmetros:
    cpf (str): O CPF a ser validado.

    Retorna:
    bool: True se o CPF for válido, False caso contrário.
    """
    cpf = ''.join(filter(str.isdigit, cpf))  # Remove caracteres não numéricos
    if len(cpf) != 11 or cpf == cpf[0] * 11:  # Verifica se tem 11 dígitos e não é uma sequência de números iguais
        return False

    # Validação dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(0, i))
        digito = 11 - (soma % 11)
        digito = digito if digito < 10 else 0
        if digito != int(cpf[i]):
            return False
    return True

def formatar_cpf(cpf):
    """
    Formata um CPF.

    Parâmetros:
    cpf (str): O CPF a ser formatado.

    Retorna:
    str: O CPF formatado no padrão "XXX.XXX.XXX-XX" ou o CPF original se não tiver 11 dígitos.
    """
    cpf = ''.join(filter(str.isdigit, cpf))  # Remove caracteres não numéricos
    if len(cpf) != 11:
        return cpf  # Retorna o CPF original se não tiver 11 dígitos
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"  # Formata o CPF

def limpar_placeholder(entry):
    """
    Limpa o campo de entrada se a mensagem de erro "CPF inválido" estiver presente.

    Parâmetros:
    entry (tk.Entry): O campo de entrada a ser limpo.
    """
    if entry.get() == "CPF INVÁLIDO":  # Verifica se a mensagem de erro está presente
        entry.delete(0, tk.END)  # Limpa o campo
        entry.config(style='')  # Restaura o estilo padrão
        
def limpar_placeholder_obrigatorio(entry):
    """
    Limpa o campo de entrada se a mensagem de erro "Campo obrigatório" estiver presente.

    Parâmetros:
    entry (tk.Entry): O campo de entrada a ser limpo.
    """
    if entry.get() == "CAMPO OBRIGATÓRIO" or entry.get() == "CPF INVÁLIDO":  # Verifica se a mensagem de erro está presente
        entry.delete(0, tk.END)  # Limpa o campo
        entry.config(bootstyle="dark")  # Restaura o estilo padrão
    elif entry.get().strip() != "":  # Se o campo não estiver vazio
        entry.config(bootstyle="dark")  # Restaura o estilo padrão
        
def verificar_cpf(entry):
    """
    Verifica e valida o CPF inserido em um campo de entrada.

    Parâmetros:
    entry (tk.Entry): O campo de entrada que contém o CPF a ser verificado.
    """
    cpf = entry.get()
    if cpf == "":  # Verifica se o campo está vazio
        return  # Não faz nada se o campo estiver vazio
    if not validar_cpf(cpf):
        entry.delete(0, tk.END)  # Limpa o campo
        entry.insert(0, "CPF INVÁLIDO")  # Insere a mensagem de erro
        entry.config(style='Red.TEntry')  # Muda o estilo para vermelho
        entry.bind("<FocusIn>", lambda e: limpar_placeholder(entry))  # Limpa ao focar
    else:
        cpf_formatado = formatar_cpf(cpf)
        entry.delete(0, tk.END)  # Limpa o campo
        entry.insert(0, cpf_formatado)  # Insere o CPF formatado
        entry.config(bootstyle="dark")  # Restaura o estilo padrão
