# Bibliotecas usadas

## Manipulação Assíncrona e Web

- aiofiles: Fornece suporte para operações de arquivos assíncronas. Útil para evitar bloqueios de IO em aplicações assíncronas.
- aiohappyeyeballs: Implementa o algoritmo Happy Eyeballs para conexões mais rápidas em ambientes com múltiplas rotas de rede.
- aiohttp: Um cliente/servidor HTTP assíncrono para Python, essencial para aplicações que realizam requisições web de forma não bloqueante.
- aiosignal: Uma biblioteca para gerenciamento de sinais assíncronos, usada internamente por outras bibliotecas assíncronas.
- h11: Implementação de baixo nível do protocolo HTTP/1.1, geralmente usada por bibliotecas assíncronas HTTP.
- multidict: Um dicionário otimizado para trabalhar com múltiplas chaves, frequentemente usado em contextos de requisição web.
- sniffio: Uma biblioteca para detectar qual biblioteca assíncrona está em uso.
- trio: Uma biblioteca para programação concorrente e assíncrona.
- trio-websocket: Permite comunicação via WebSocket assíncrona usando o Trio.
- websockets: Fornece implementação do protocolo WebSocket para Python, útil para comunicação - bidirecional em tempo real.
- wsproto: Uma implementação puramente Python do protocolo WebSocket.
- yarl: Uma biblioteca para manipulação de URLs.

## Requisições HTTP e Outros Protocolos

- httplib2: Cliente HTTP abrangente que suporta vários recursos.
- requests: Uma das bibliotecas mais populares para fazer requisições HTTP em Python.
- urllib3: Uma biblioteca de baixo nível para fazer requisições HTTP, frequentemente usada como base para outras bibliotecas como requests.
- PySocks: Uma biblioteca para usar proxies SOCKS.
- websocket-clien: Cliente WebSocket para conectar a um servidor WebSocket.

## Manipulação de Dados e Texto

- beautifulsoup4: Uma biblioteca para fazer parsing de HTML e XML, essencial para web scraping.
- Brotli: Compressão de dados Brotli, para reduzir o tamanho de dados transmitidos.
- chardet: Detecção de codificação de caracteres.
- charset-normalizer: Detecção e normalização de codificação de caracteres.
- lxml: Uma biblioteca para processamento XML e HTML, conhecida por sua velocidade e flexibilidade.
- packaging: Ferramentas para manipulação de versões de pacotes Python.
- pyparsing: Uma biblioteca para criar gramáticas e realizar parsing.
- six: Utilitários de compatibilidade para Python 2 e 3.
- sortedcontainers: Implementações de estruturas de dados para conjuntos e mapas ordenados.

## Manipulação de Imagens e Vídeos

- imageio: Uma biblioteca para leitura e escrita de uma variedade de formatos de imagem.
- imageio-ffmpeg: Fornece suporte para manipulação de vídeos usando a biblioteca ffmpeg através do imageio.
- img2pdf: Converte imagens para arquivos PDF.
- moviepy: Biblioteca para edição de vídeo, incluindo cortar, unir e adicionar texto ou elementos visuais.
- numpy: Biblioteca fundamental para computação científica em Python, especialmente para computação numérica.
- opencv-python: Biblioteca para visão computacional, essencial para processamento de imagem e vídeo.
- Pillow: Biblioteca de manipulação de imagens para Python.

## Automação e Interação com o Sistema

- keyboard: Uma biblioteca para capturar e simular eventos de teclado.
- MouseInfo: Informações sobre mouse.
- PyAutoGUI: Biblioteca para automatizar interações com a GUI, como clicar em botões e digitar texto.
- PyGetWindow: Obtém informações de janelas.
- PyMsgBox: Cria caixas de mensagem.
- pynput: Biblioteca para capturar e simular eventos de teclado e mouse.
- PyRect: Uma biblioteca para manipular retângulos no espaço da tela.
- PyScreeze: Uma biblioteca para tirar screenshots e manipular imagens na tela.
- psutil: Informações sobre processos em execução e utilização de recursos do sistema.
- pytweening: Funções de interpolação para criação de animações e transições suaves.
- watchdog: Monitoramento de mudanças no sistema de arquivos.
- webdriver-manager: Gerenciamento de drivers do Selenium.

## Manipulação de Documentos

- pikepdf: Uma biblioteca para ler, editar e criar arquivos PDF.
- PyMuPDF: Uma biblioteca para ler, modificar e criar arquivos PDF, além de outros formatos de documentos.
- python-docx: Uma biblioteca para criar e manipular documentos Word (.docx).
- reportlab: Uma biblioteca para criar documentos PDF complexos, útil para geração de relatórios.
- qrcode: Uma biblioteca para gerar códigos QR de forma simples e rápida.
- PyPDF2: Uma biblioteca para manipulação de arquivos PDF, permitindo leitura, edição e criação de PDFs.

## Ferramentas de Desenvolvimento e Empacotamento

- altgraph: Biblioteca usada internamente pelo PyInstaller.
- pefile: Biblioteca para trabalhar com arquivos PE (Portable Executable).
- pyinstaller: Empacota aplicações Python em executáveis standalone.
- pyinstaller-hooks-contrib: Hooks adicionais para o PyInstaller.
- setuptools: Ferramenta para criação e distribuição de pacotes Python.

## Segurança e Criptografia

- cffi: Interface para código C a partir do Python, usada por outras bibliotecas.
- cryptography: Uma biblioteca para criptografia, fornecendo diversas operações.
- pycryptodomex: Uma biblioteca para criptografia, usada em várias aplicações que exigem segurança.
- rsa: Biblioteca para lidar com criptografia RSA.

## Outras Ferramentas

- arsenic: Uma ferramenta para usar o Selenium WebDriver.
- attrs: Biblioteca para criar classes Python com atributos.
- cachetools: Ferramentas para implementar caches.
- certifi: Fornece um conjunto de certificados de autoridades de certificação (CAs) para verificar a segurança de conexões TLS/SSL.
- colorama: Adiciona suporte a cores para terminais.
- decorator: Permite uso de decoradores para adicionar funcionalidades a funções.
- Deprecated: Biblioteca para marcar funções e classes como deprecated.
- frozenlist: Versão congelada de listas.
- getmac: Obtém o endereço MAC de interfaces de rede.
- google-api-core: Biblioteca core do google api python client.
- google-api-python-client: Biblioteca para usar as APIs do Google.
- google-auth: Biblioteca de autenticação do Google.
- google-auth-httplib20: Adapter http para biblioteca de autenticação google.
- googleapis-common-protos: Google common protos.
- idna: Para codificação e decodificação de nomes de domínio internacionalizados.
- instaloader: Uma biblioteca para baixar fotos e outros conteúdos do Instagram.
- mutagen: Biblioteca para manipular metadados de arquivos de áudio.
- outcome: Resultados de operações.
- proglog10: Biblioteca para exibir progresso durante operações.
- propcache0: Biblioteca para cache de propriedades.
- proto-plus: Uma biblioteca para trabalhar com protobufs.
- protobuf: Biblioteca para serialização de dados usando o formato Protocol Buffers do Google.
- pyasn1: Biblioteca para trabalhar com ASN.1.
- pyasn1_modules: Módulos para trabalhar com ASN.1.
- pycparser: Parser de linguagem C escrito em Python.
- pyperclip: Biblioteca para copiar e colar texto do clipboard.
- python-dotenv: Carregar variáveis de ambiente de arquivos .env.
- selenium: Ferramenta para automatizar navegadores web para teste e web scraping.
- Selenium-Screenshot0: Tirar screenshots no Selenium.
- soupsieve: Seletor CSS implementado em Python.
- structlog: Ferramenta para logs estruturados.
- tqdm: Biblioteca para exibir barras de progresso em linha de comando.
- ttkbootstrap: Temas para Tkinter.
- ttkthemes: Temas adicionais para Tkinter.
- typing_extensions: Extensões para o sistema de tipos do Python.
- uritemplate: Uma biblioteca para manipular modelos de URI.
- wrapt: Uma biblioteca para criar wrappers e decorar funções dinamicamente.
- yt-dlp: Biblioteca para baixar vídeos de várias plataformas, incluindo YouTube e Vimeo.
