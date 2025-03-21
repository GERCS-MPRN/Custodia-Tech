# Comandos para compilar o projeto

## Setup do Projeto

Crie o ambiente virtual do Custodia e ative ele no terminal

```bash
python -m venv venv
venv\Scripts\activate
```

Faça upgrade do PIP e instale as bibliotecas do Custodia

```bash
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```

Quando instalar novas bibliotecas, atualize o requirements.txt

```bash
pip freeze > requirements.txt
```

## Gerar o programa executável

Para gerar o aquivo executável do Custodiatech, execute o comando abaixo:

```bash
pyinstaller --onedir --windowed --icon "imagens/iconecustodiatech.ico" --add-data "imagens;imagens" --add-data "docs;docs" --add-data "utils;utils" --add-data "modulos;modulos" --add-data "_internal/Profile_Whatsapp;Profile_Whatsapp" --add-data "_internal/ExifToolPackage;ExifToolPackage" --add-data ".env;." interface_projeto_captura.py --noconfirm
```

## Gerar o Instalador

Para gerar o arquivo de instalação do Custodia Tech, siga os passos a seguir:

1. Baixe e instale a versão mais recente do [Inno Setup](https://jrsoftware.org/isdl.php).
2. Gere o programa executável do CT usando o comando do PyInstaller. O comando criará a pasta **dist** no diretório do projeto.
3. No Inno Setup escolha a opção de abrir um script pronto. Na pasta docs nós disponibilizamos o arquivo script_inno_setup.iss.
4. Atualize os campos `MyAppPublisher` e `MyAppURL` com a unidade e página da unidade do MP de vocês.
5. Atualize a variável `SetupIconFile` com o local do ícone do CT.
6. Atualize o caminho do diretório da pasta dist gerada no passo 2 nas duas linhas `Source` de [Files].
7. Clique no botão de Compile (Ctrl + F9) para gerar o intalador. O arquivo de instalação do CT estará na pasta Output dentro da pasta docs do diretório do projeto.

## Editar os dados do Relatório

Para editar os dados do cabeçalho e validador basta editar os campos
> CTLOGO, ORGAO, UNIDADE, NUCLEO, ENDERECO_TELEFONE, SITE_VALIDACAO , EMISSOR_RELATORIO

É importante se atentar para somente editar os campos SITE_VALIDACAO e EMISSOR_RELATORIO quando tiver feito a implementação do validador próprio. Na validação é checado se o EMISSOR_RELATORIO é `CustodiaTech - MPRN`. Quando implementarem o validador, basta modificar na função `valida_relatorio()` para que o valor seja o mesmo do .env.
# Custodia-Tech
