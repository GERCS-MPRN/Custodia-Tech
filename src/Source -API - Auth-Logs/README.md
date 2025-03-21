# CustodiaTech API - Serviço de Gerenciamento de Acesso e Auditoria ao app CustodiaTech

Projeto de Gerenciamento de Acesso e Auditoria ao app CustodiaTech

## Sumário

- [Tecnologias](#tecnologias)
- [Dependências](#dependências)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Modelo de Domínio](#modelo-de-domínio)
- [Classes](#classes)
- [Modelo de Componentes](#modelo-de-componentes)
- [Endpoints](#endpoints)
- [Informações Gerais](#informações-gerais)


## Tecnologias

- **♨️ Java 21**
- **🔐 JWT**
- **🍃 Spring Boot 3.2.3**
- **Ⓜ️ Maven**
- **🌶️ Lombok**
- **🗜️ Micrometer**
- **🗄️ Microsoft SQL Server**
- **🔥 Prometheus**

## Dependências

- **AUTH_LDAP_API**: API responsável por gerenciar as credenciais de acesso dos usuários aos sistemas do GAECO

## Variáveis de Ambiente

* [DB_AUDIT_NAME] - Nome da base de dados de auditoria
* [DB_AUDIT_USERNAME] - Nome do usuário do banco de dados de auditoria
* [DB_AUDIT_PASSWORD] - Senha de acesso à base de dados de auditoria
* [DB_AUDIT_PORT] - Porta de acesso à base de dados de auditoria
* [DB_AUDIT_SERVER] - Host do banco de dados de auditoria
* [DB_AUDIT_SGDB] - SGBD do banco de dados de auditoria. Ex: sqlserver
* [DB_AUTH_NAME] - Nome da base de dados de autenticação
* [DB_AUTH_USERNAME] - Nome do usuário do banco de dados de autenticação
* [DB_AUTH_PASSWORD] - Senha de acesso à base de dados de autenticação
* [DB_AUTH_PORT] - Porta de acesso à base de dados de autenticação
* [DB_AUTH_SERVER] - Host do banco de dados de autenticação
* [DB_AUTH_SGDB] - SGBD do banco de dados de autenticação. Ex: sqlserver
* [ENCRYPT]- Flag que indica se há ou não criptografia a comunicação com a base de dados. Ex: true
* [JWT_SECRET] - Padrão de chave para criptografar o token JWT
* [JWT_EXPIRATION_TIME] - Tempo de expiração (em milissegundos) do token de acesso
* [LOG_LEVEL_ROOT] - Atribuição do tipo de log raiz. Ex.: error
* [LOG_LEVEL_SQL] - Atribuição do tipo de log sql. Ex.: error
* [LOG_LEVEL_WEB] - Atribuição do tipo de log web. Ex.: error
* [LOG_PATH_FILE] - Caminho para inclusão dos logs
* [PORTA] - Porta da aplicação
* [TRUST_SERVER_CERTIFICATE] - Chave para aceitar o certificado do servidor de banco. Ex: true
* [URL_SERVICO_AD] - URL do serviço de Active Directory para consulta no catálogo de usuários
* [GRUPO_ACESSO] - Nome do perfil de usuário no sistema de autenticação que tem acesso ao app Custodia Tech


## Modelo de Domínio


## Classes
- **CustodiaTechAuditLog**
    - Registro dos logs do CustodiaTech
- **Perfil**
  - Registro dos perfis de usuário
- **Usuario**
  - Registro dos usuários na base de dados
- **UsuarioPerfil**
  - Registro das associações entre perfil e usuário
- **AceiteTermo**
  - Registro dos aceites de termo de uso do app

## Modelo de Componentes


## Endpoints

- **/logar - POST**
  - Recebe login e senha e retorna se o usuário possui acesso 
- **/autorizacao - GET**
  - Recebe o Token de usuário e verifica se ele possui acesso ao app
- **/log - POST**
  - Realiza o registro de novo log no sistema
- **/aceite - POST**
  - Realiza o aceite de uso do termo
- **/aceite - GET**
  - Verifica se o usuário aceitou o termo de uso
- **/download - GET**
  - Realiza o download do app

### Informações Gerais

Em caso de dúvida sobre
este projeto, favor entrar contato com:

    - Rivaldo Xavier: rivaldo.xavier@mprn.mp.br
    - Elainy M H A Lima: elainy.lima@mprn.mp.br
    - Maria Emília Eidelwein: maria.emilia@mprn.mp.br

Todos os projetos descritos nesse repositório são de posse do Ministério Público do Rio Grande do Norte e não devem ser
utilizado para outros fins além dos dessa instituição.
