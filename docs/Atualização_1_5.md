# Lista de Atualizações da Versão 1.5

## Novos Recursos

### Fluxo de Atualização de Versão

- Verificação da versão atual do software
- Download da nova versão
- Instalação automática da nova versão

### Autenticação do Relatório

- Adicionada uma folha ao final do relatório para fins de autenticação
- Verificação de integridade via QRCODE
- custodiatech.mprn.mp.br

### Captura Whatsapp

- Implementada a tela de captura do Whatsapp
- O usuário pode capturar a lista de contatos, uma conversa específica ou ambos
- Otimização do código para melhor performance
- Uso do Firefox portátil ao invés do profile

### Coleta Probatória

- O relatório só pode ser criado caso o usuário tenha preenchido os campos obrigatórios:
  - Dados do processo
  - Dados do operador
  - Denunciante
  - Testemunha 1
  - CPF Testemunha 1
  - Testemunha 2
  - CPF Testemunha 2
- Verifica se o CPF é válido
- Formata automaticamente o CPF caso seja escrito de forma errada ou somente números
- Quando é inserido o nome do Denunciante e testemunha, é obrigatório inserir o CPF dos mesmos

### Limitações e Controle

- Limite de download de comentários do Youtube para 1000
- Controle de acesso à API do Twitter: Caso o download não seja realizado, uma nova tentativa será feita em 15 segundos

### Captura de Tela

- A captura de tela agora suporta multiplos monitores.

## Melhorias de Interface

### Resizer

- A tela do Custódia abre de acordo com o monitor ativo
- O tamanho da tela do CT é relativo ao tamanho do monitor do usuário (anteriormente o CT não era compatível com monitor de notebook)
- As janelas abrem de acordo com o monitor em que estiver a interface do CT

### Metadados avulsos

- Nome da pasta com limitação de caracteres
- Não é mais necessário escolher entre mover ou copiar. Copiar arquivos ficou como padrão.

### Qualidade de vida

- Novo ícone do CustodiaTech
- Os botões não podem ser clicados mais de uma vez, impedindo múltiplas instâncias de um mesmo módulo
- Quando um caso é fechado sem ser finalizado, é criado um arquivo contendo os dados da coleta probatória
- Ao abrir um caso em andamento, os dados da coleta probatória são populados automaticamente
- Os casos abertos não ficam mais no Desktop
- Código modularizado para melhor organização e manutenção
- Campo de login com foco
- Corrigido bug onde as janelas apareciam por trás das demais abertas
- Documentação de muitas funções diretamente no código
- Adicionado hovertip nos botões dos módulos
- Criada lista suspensa para seleção de casos existentes, com possibilidade de digitação facilitada do nome do caso
- Padronização nos nomes de funções

- © 2025 CUSTODIATECH. Ministério Público do Rio Grande do Norte. Todos os direitos reservados.
