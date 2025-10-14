# DefaultWebApp - Boilerplate FastAPI

> Boilerplate completo para desenvolvimento de aplicações web modernas com Python, FastAPI, Jinja2 e Bootstrap 5.

## Características Principais

- ✅ **Python 3.10+** com FastAPI para alta performance
- ✅ **Templates Jinja2** + Bootstrap 5.3.8 para interface responsiva
- ✅ **Autenticação completa** com sistema de perfis (roles)
- ✅ **Sistema de Logger** profissional com rotação de arquivos
- ✅ **Envio de e-mails** integrado (Resend.com)
- ✅ **Flash messages e Toasts** para feedback ao usuário
- ✅ **Validação com Pydantic DTOs** para segurança de dados
- ✅ **SQLite sem ORM** - SQL puro para máximo controle
- ✅ **Configurações do sistema** editáveis via interface admin
- ✅ **CRUD de exemplo** (Tarefas) como template
- ✅ **Sistema de seeds** para dados iniciais em JSON
- ✅ **Rate limiting** para proteção contra ataques
- ✅ **Security headers** configurados

## Instalação Rápida

### Pré-requisitos
- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/maroquio/DefaultWebApp
   cd DefaultWebApp
   ```

2. **Crie um ambiente virtual**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env

   # Edite o arquivo .env com suas configurações
   ```

5. **Execute a aplicação**
   ```bash
   python main.py
   ```

6. **Acesse no navegador**
   ```
   http://localhost:8000
   ```

## Usuários Padrão

O sistema vem com usuários pré-cadastrados para facilitar os testes:

| Perfil | E-mail | Senha | Descrição |
|--------|--------|-------|-----------|
| **Admin** | admin@sistema.com | Admin@123 | Acesso administrativo completo |
| **Cliente** | joao@email.com | Joao@123 | Usuário comum |
| **Cliente** | maria@email.com | Maria@123 | Usuário comum |

> **Importante**: Altere essas senhas em ambiente de produção!

## Estrutura do Projeto

```
DefaultWebApp/
├── data/                    # Dados seed em JSON
│   └── usuarios_seed.json   # Usuários iniciais
│
├── docs/                    # Documentação do projeto
│   ├── CRIAR_CRUD.md       # Tutorial para criar CRUDs
│   ├── PERFIS.md           # Como adicionar perfis
│   └── QUICK_START.md      # Início rápido para alunos
│
├── dtos/                    # DTOs Pydantic para validação
│   ├── tarefa_dto.py       # DTOs de tarefas
│   ├── usuario_dto.py      # DTOs de usuários
│   └── login_dto.py        # DTOs de autenticação
│
├── model/                   # Modelos de entidades (dataclasses)
│   ├── usuario_model.py    # Modelo de usuário
│   ├── tarefa_model.py     # Modelo de tarefa
│   └── configuracao_model.py # Modelo de configuração
│
├── repo/                    # Repositórios de acesso a dados
│   ├── usuario_repo.py     # Repositório de usuários
│   ├── tarefa_repo.py      # Repositório de tarefas
│   └── configuracao_repo.py # Repositório de configurações
│
├── routes/                  # Rotas organizadas por módulo
│   ├── auth_routes.py      # Rotas de autenticação
│   ├── tarefas_routes.py   # Rotas de tarefas
│   ├── admin_usuarios_routes.py      # Admin de usuários
│   └── admin_configuracoes_routes.py # Admin de configurações
│
├── sql/                     # Comandos SQL
│   ├── usuario_sql.py      # SQLs de usuários
│   ├── tarefa_sql.py       # SQLs de tarefas
│   └── configuracao_sql.py # SQLs de configurações
│
├── static/                  # Arquivos estáticos
│   ├── css/                # Folhas de estilo
│   ├── js/                 # Scripts JavaScript
│   └── img/                # Imagens
│
├── templates/               # Templates Jinja2
│   ├── auth/               # Templates de autenticação
│   ├── tarefas/            # Templates de tarefas
│   ├── admin/              # Templates administrativos
│   └── perfil/             # Templates de perfil
│
├── util/                    # Utilitários
│   ├── auth_decorator.py   # Decorator de autenticação
│   ├── db_util.py          # Utilitários de banco de dados
│   ├── email_service.py    # Serviço de e-mail
│   ├── flash_messages.py   # Sistema de mensagens flash
│   ├── logger_config.py    # Configuração de logs
│   ├── perfis.py           # Enum de perfis
│   ├── security.py         # Funções de segurança
│   ├── senha_util.py       # Validação de senhas
│   ├── seed_data.py        # Carregamento de dados seed
│   └── template_util.py    # Utilitários de templates
│
├── tests/                   # Testes automatizados
│
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo Git
├── main.py                  # Arquivo principal da aplicação
├── requirements.txt         # Dependências Python
└── README.md                # Este arquivo
```

## Como Executar

### Modo Desenvolvimento (com hot reload)
```bash
python main.py
```

### Modo Produção
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Executar Testes
```bash
pytest
```

## Guias e Tutoriais

- **[Criar um novo CRUD](docs/CRIAR_CRUD.md)** - Tutorial completo para criar operações CRUD
- **[Adicionar novos perfis](docs/PERFIS.md)** - Como gerenciar perfis de usuário
- **[Início Rápido](docs/QUICK_START.md)** - Guia para alunos iniciarem rapidamente

## Tecnologias Utilizadas

### Backend
- **FastAPI 0.115+** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic 2.0+** - Validação de dados com type hints

### Frontend
- **Jinja2** - Engine de templates
- **Bootstrap 5.3.8** - Framework CSS responsivo
- **JavaScript vanilla** - Sem dependências frontend

### Banco de Dados
- **SQLite3** - Banco de dados embutido
- **SQL Puro** - Sem ORM para máximo controle

### Segurança
- **Passlib + Bcrypt** - Hash de senhas
- **SessionMiddleware** - Gerenciamento de sessões
- **Rate Limiting** - Proteção contra ataques

### Comunicação
- **Resend** - Envio de e-mails transacionais
- **Requests** - Cliente HTTP

### Desenvolvimento
- **Python-dotenv** - Gerenciamento de variáveis de ambiente
- **Pytest** - Framework de testes
- **Logging** - Sistema de logs profissional

## Funcionalidades

### Autenticação e Autorização
- Login e logout com sessões
- Cadastro de novos usuários
- Recuperação de senha por e-mail
- Sistema de perfis (admin, cliente, etc.)
- Proteção de rotas por perfil

### Gerenciamento de Usuários (Admin)
- Listar todos os usuários
- Criar novos usuários
- Editar dados de usuários
- Excluir usuários
- Alterar perfis

### Sistema de Configurações (Admin)
- Configurações editáveis via interface
- Cache para performance
- Valores padrão

### CRUD de Tarefas (Exemplo)
- Criar tarefas
- Listar tarefas por usuário
- Marcar como concluída
- Excluir tarefas
- Validação com DTOs

### Sistema de Logger
- Logs em arquivo com rotação automática
- Níveis configuráveis (DEBUG, INFO, WARNING, ERROR)
- Logs de todas as operações importantes

### Sistema de E-mails
- E-mail de boas-vindas
- Recuperação de senha
- Templates HTML personalizáveis

## Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```env
# Banco de Dados
DATABASE_PATH=database.db

# Logging
LOG_LEVEL=INFO

# E-mail (Resend.com)
RESEND_API_KEY=seu_api_key_aqui
RESEND_FROM_EMAIL=noreply@seudominio.com
RESEND_FROM_NAME=Sistema

# Aplicação
BASE_URL=http://localhost:8000
SECRET_KEY=sua_chave_secreta_super_segura_aqui

# Servidor
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

## Padrões de Desenvolvimento

### Arquitetura
O projeto segue uma arquitetura em camadas:

1. **Routes** → Recebem requisições HTTP
2. **DTOs** → Validam dados de entrada
3. **Models** → Representam entidades
4. **Repositories** → Acessam banco de dados
5. **SQL** → Comandos SQL isolados

### Fluxo de uma Requisição
```
Cliente → Route → DTO (validação) → Repository → SQL → Database
                    ↓
              Template ← Flash Message
```

### Boas Práticas
- Use DTOs para validar todas as entradas
- Use o decorator `@requer_autenticacao()` em rotas protegidas
- Use flash messages para feedback ao usuário
- Use logger para registrar operações importantes
- Mantenha SQL separado em arquivos `*_sql.py`
- Use dataclasses para models
- Documente funções com docstrings

## Segurança

### Implementações
- ✅ Senhas com hash bcrypt
- ✅ Sessões com chave secreta
- ✅ Rate limiting no login
- ✅ Validação de força de senha
- ✅ Security headers (X-Frame-Options, etc.)
- ✅ Proteção contra SQL injection (prepared statements)
- ✅ Validação de dados com Pydantic

### Recomendações para Produção
- [ ] Alterar SECRET_KEY para valor único e seguro
- [ ] Alterar senhas padrão dos usuários
- [ ] Configurar HTTPS/SSL
- [ ] Configurar firewall
- [ ] Backup regular do banco de dados
- [ ] Monitoramento de logs
- [ ] Limitar tentativas de login por IP

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto é um boilerplate educacional livre para uso.

## Suporte

Para dúvidas e suporte:
- Consulte a documentação em `/docs`
- Verifique os exemplos no código
- Entre em contato com o instrutor

## Roadmap

### Futuras Melhorias
- [ ] Docker e docker-compose
- [ ] CI/CD com GitHub Actions
- [ ] API REST endpoints
- [ ] Testes de integração completos
- [ ] Documentação automática (Swagger)
- [ ] Internacionalização (i18n)
- [ ] Theme switcher (claro/escuro)
- [ ] WebSockets para notificações real-time
- [ ] Upload de arquivos
- [ ] Paginação de listagens

---

**Desenvolvido com 💙 para ensino de desenvolvimento web com Python e FastAPI**
