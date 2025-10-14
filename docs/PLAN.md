# PLANO DE CRIAÇÃO DO BOILERPLATE WEB APP

**Objetivo**: Transformar a aplicação de loja virtual em um boilerplate genérico e reutilizável para aplicações web com FastAPI, que sirva de base para projetos de alunos.

**Stack**: Python + FastAPI + Jinja2 + Pydantic + Bootstrap 5.3.8 + SQLite

---

## TAREFA 1: Limpeza e Preparação Inicial

### Objetivos
- Remover todo código específico da loja virtual
- Manter apenas estrutura de usuários e autenticação
- Preparar base limpa para o boilerplate

### Arquivos a REMOVER
- `dtos/categoria_dto.py`
- `model/categoria_model.py`, `model/cliente_model.py`, `model/forma_pagamento_model.py`, `model/produto_model.py`, `model/admin_model.py`
- `repo/categoria_repo.py`, `repo/cliente_repo.py`, `repo/forma_pagamento_repo.py`, `repo/produto_repo.py`, `repo/admin_repo.py`
- `sql/categoria_sql.py`, `sql/cliente_sql.py`, `sql/forma_pagamento_sql.py`, `sql/produto_sql.py`, `sql/admin_sql.py`
- `routes/admin_categorias_routes.py`, `routes/admin_produtos_routes.py`, `routes/admin_clientes_routes.py`, `routes/admin_formas_routes.py`
- `data/insert_*.sql` (todos)
- Templates relacionados a produtos, categorias, etc.

### Arquivos a MODIFICAR
- `main.py` - remover imports e rotas de produtos/categorias/clientes/formas
- `util/criar_admin.py` - simplificar para criar apenas admin padrão

### Checklist
- [ ] Remover todos os arquivos específicos da loja
- [ ] Limpar imports no main.py
- [ ] Remover criação de tabelas desnecessárias
- [ ] Testar se aplicação inicia sem erros

---

## TAREFA 2: Sistema de Perfis Centralizado (Enum)

### Objetivos
- Centralizar definição de perfis em um enum
- Facilitar adição de novos perfis
- Evitar strings hardcoded

### Arquivos a CRIAR
**`util/perfis.py`**
```python
from enum import Enum

class Perfil(str, Enum):
    ADMIN = "admin"
    CLIENTE = "cliente"

    @classmethod
    def valores(cls):
        """Retorna lista de todos os valores de perfis"""
        return [perfil.value for perfil in cls]

    @classmethod
    def existe(cls, valor: str) -> bool:
        """Verifica se um perfil existe"""
        return valor in cls.valores()
```

### Arquivos a MODIFICAR
- `util/auth_decorator.py` - usar `Perfil.ADMIN.value` ao invés de `"admin"`
- `routes/auth_routes.py` - usar enum para definir perfil padrão
- `routes/admin_usuarios_routes.py` - usar enum
- Todos os lugares que usam strings hardcoded para perfis

### Checklist
- [ ] Criar arquivo util/perfis.py com enum
- [ ] Refatorar auth_decorator.py para usar enum
- [ ] Refatorar todas as rotas para usar enum
- [ ] Atualizar documentação sobre como adicionar perfis

---

## TAREFA 3: Sistema de Logger

### Objetivos
- Configurar sistema de logs profissional
- Logs em arquivo com rotação automática
- Níveis configuráveis via ambiente

### Arquivos a CRIAR
**`util/logger_config.py`**
```python
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

def configurar_logger():
    # Criar pasta de logs se não existir
    Path("logs").mkdir(exist_ok=True)

    # Configurar formato
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formato)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)

    # Configurar logger raiz
    logger = logging.getLogger()
    nivel = os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, nivel))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Logger global para importação
logger = configurar_logger()
```

**`.env.example`** (adicionar)
```
LOG_LEVEL=INFO
```

### Arquivos a MODIFICAR
- `main.py` - adicionar `from util.logger_config import logger` e logar início da aplicação
- `routes/auth_routes.py` - adicionar logs de login/logout
- `util/auth_decorator.py` - logar tentativas de acesso não autorizado

### Exemplos de Uso
```python
from util.logger_config import logger

logger.info("Aplicação iniciada")
logger.warning("Tentativa de acesso não autorizado")
logger.error(f"Erro ao processar: {e}")
logger.debug("Dados de debug")
```

### Checklist
- [ ] Criar util/logger_config.py
- [ ] Criar pasta logs/
- [ ] Adicionar LOG_LEVEL ao .env.example
- [ ] Implementar logs em main.py
- [ ] Implementar logs em rotas de autenticação
- [ ] Testar rotação de logs

---

## TAREFA 4: Sistema de E-mail (MailerSend)

### Objetivos
- Integrar MailerSend para envio de e-mails
- Templates para recuperação de senha, boas-vindas
- Configuração via variáveis de ambiente

### Arquivos a CRIAR
**`util/email_service.py`**
```python
import os
import requests
from typing import Optional
from util.logger_config import logger

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('MAILERSEND_API_KEY')
        self.from_email = os.getenv('MAILERSEND_FROM_EMAIL', 'noreply@seudominio.com')
        self.from_name = os.getenv('MAILERSEND_FROM_NAME', 'Sistema')
        self.base_url = "https://api.mailersend.com/v1/email"

    def enviar_email(
        self,
        para_email: str,
        para_nome: str,
        assunto: str,
        html: str,
        texto: Optional[str] = None
    ) -> bool:
        """Envia e-mail via MailerSend"""
        if not self.api_key:
            logger.warning("MAILERSEND_API_KEY não configurada")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": {
                "email": self.from_email,
                "name": self.from_name
            },
            "to": [
                {
                    "email": para_email,
                    "name": para_nome
                }
            ],
            "subject": assunto,
            "html": html,
            "text": texto or assunto
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"E-mail enviado para {para_email}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    def enviar_recuperacao_senha(self, para_email: str, para_nome: str, token: str) -> bool:
        """Envia e-mail de recuperação de senha"""
        url_recuperacao = f"{os.getenv('BASE_URL', 'http://localhost:8000')}/redefinir-senha?token={token}"

        html = f"""
        <html>
        <body>
            <h2>Recuperação de Senha</h2>
            <p>Olá {para_nome},</p>
            <p>Você solicitou a recuperação de senha.</p>
            <p>Clique no link abaixo para redefinir sua senha:</p>
            <a href="{url_recuperacao}">Redefinir Senha</a>
            <p>Este link expira em 1 hora.</p>
            <p>Se você não solicitou esta recuperação, ignore este e-mail.</p>
        </body>
        </html>
        """

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto="Recuperação de Senha",
            html=html
        )

    def enviar_boas_vindas(self, para_email: str, para_nome: str) -> bool:
        """Envia e-mail de boas-vindas"""
        html = f"""
        <html>
        <body>
            <h2>Bem-vindo(a)!</h2>
            <p>Olá {para_nome},</p>
            <p>Seu cadastro foi realizado com sucesso!</p>
            <p>Agora você pode acessar o sistema com seu e-mail e senha.</p>
        </body>
        </html>
        """

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto="Bem-vindo ao Sistema",
            html=html
        )

# Instância global
email_service = EmailService()
```

**`.env.example`** (adicionar)
```
MAILERSEND_API_KEY=seu_api_key_aqui
MAILERSEND_FROM_EMAIL=noreply@seudominio.com
MAILERSEND_FROM_NAME=Sistema
BASE_URL=http://localhost:8000
```

### Arquivos a MODIFICAR
- `routes/auth_routes.py` - enviar e-mail de boas-vindas no cadastro
- Adicionar rota de recuperação de senha usando email_service

### Checklist
- [ ] Criar util/email_service.py
- [ ] Adicionar variáveis MAILERSEND ao .env.example
- [ ] Integrar envio de boas-vindas no cadastro
- [ ] Criar fluxo de recuperação de senha
- [ ] Testar envio de e-mails

---

## TAREFA 5: Sistema de Configurações do Sistema

### Objetivos
- Permitir configurar parâmetros do sistema via interface admin
- Armazenar em banco de dados
- Cache para performance

### Arquivos a CRIAR
**`model/configuracao_model.py`**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Configuracao:
    id: int
    chave: str
    valor: str
    descricao: Optional[str] = None
```

**`sql/configuracao_sql.py`**
```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descricao TEXT
)
"""

INSERIR = "INSERT INTO configuracao (chave, valor, descricao) VALUES (?, ?, ?)"
OBTER_POR_CHAVE = "SELECT * FROM configuracao WHERE chave = ?"
OBTER_TODOS = "SELECT * FROM configuracao ORDER BY chave"
ATUALIZAR = "UPDATE configuracao SET valor = ? WHERE chave = ?"
```

**`repo/configuracao_repo.py`**
```python
from typing import Optional
from model.configuracao_model import Configuracao
from sql.configuracao_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def obter_por_chave(chave: str) -> Optional[Configuracao]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CHAVE, (chave,))
        row = cursor.fetchone()
        if row:
            return Configuracao(
                id=row["id"],
                chave=row["chave"],
                valor=row["valor"],
                descricao=row["descricao"]
            )
        return None

def obter_todos() -> list[Configuracao]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [
            Configuracao(
                id=row["id"],
                chave=row["chave"],
                valor=row["valor"],
                descricao=row["descricao"]
            )
            for row in rows
        ]

def atualizar(chave: str, valor: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (valor, chave))
        return cursor.rowcount > 0

def inserir_padrao() -> None:
    """Insere configurações padrão se não existirem"""
    configs_padrao = [
        ("nome_sistema", "Sistema Web", "Nome do sistema"),
        ("email_contato", "contato@sistema.com", "E-mail de contato"),
        ("tema_padrao", "claro", "Tema padrão (claro/escuro)"),
    ]

    with get_connection() as conn:
        cursor = conn.cursor()
        for chave, valor, descricao in configs_padrao:
            try:
                cursor.execute(INSERIR, (chave, valor, descricao))
            except:
                pass  # Já existe
        conn.commit()
```

**`util/config_cache.py`**
```python
from typing import Optional
from repo import configuracao_repo

class ConfigCache:
    _cache = {}

    @classmethod
    def obter(cls, chave: str, padrao: str = "") -> str:
        """Obtém configuração com cache"""
        if chave not in cls._cache:
            config = configuracao_repo.obter_por_chave(chave)
            cls._cache[chave] = config.valor if config else padrao
        return cls._cache[chave]

    @classmethod
    def limpar(cls):
        """Limpa o cache"""
        cls._cache = {}

config = ConfigCache()
```

**`routes/admin_configuracoes_routes.py`**
```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from repo import configuracao_repo
from util.config_cache import config
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates

router = APIRouter(prefix="/admin/configuracoes")
templates = criar_templates("templates/admin/configuracoes")

@router.get("/")
@requer_autenticacao(["admin"])
async def get_configuracoes(request: Request, usuario_logado: dict = None):
    configuracoes = configuracao_repo.obter_todos()
    return templates.TemplateResponse(
        "listar.html",
        {"request": request, "configuracoes": configuracoes}
    )

@router.post("/atualizar")
@requer_autenticacao(["admin"])
async def post_atualizar(
    request: Request,
    chave: str = Form(...),
    valor: str = Form(...),
    usuario_logado: dict = None
):
    configuracao_repo.atualizar(chave, valor)
    config.limpar()  # Limpa cache
    return RedirectResponse("/admin/configuracoes", status.HTTP_303_SEE_OTHER)
```

**Templates**: `templates/admin/configuracoes/listar.html`

### Arquivos a MODIFICAR
- `main.py` - adicionar `configuracao_repo.criar_tabela()` e `configuracao_repo.inserir_padrao()`
- `main.py` - incluir router de configurações

### Checklist
- [ ] Criar model, sql e repo de configurações
- [ ] Criar util/config_cache.py
- [ ] Criar rotas admin de configurações
- [ ] Criar templates de configurações
- [ ] Testar CRUD de configurações
- [ ] Documentar como adicionar novas configs

---

## TAREFA 6: Sistema de Toasts Aprimorado

### Objetivos
- Melhorar sistema de flash messages
- Integração com Bootstrap 5 toasts
- Suporte a múltiplos tipos e posições

### Arquivos a MODIFICAR
**`util/flash_messages.py`**
```python
from fastapi import Request
from typing import Literal

TipoMensagem = Literal["sucesso", "erro", "aviso", "info"]

def adicionar_mensagem(
    request: Request,
    mensagem: str,
    tipo: TipoMensagem = "info"
):
    """Adiciona mensagem flash à sessão"""
    if "mensagens" not in request.session:
        request.session["mensagens"] = []

    request.session["mensagens"].append({
        "texto": mensagem,
        "tipo": tipo
    })

def informar_sucesso(request: Request, mensagem: str):
    adicionar_mensagem(request, mensagem, "sucesso")

def informar_erro(request: Request, mensagem: str):
    adicionar_mensagem(request, mensagem, "erro")

def informar_aviso(request: Request, mensagem: str):
    adicionar_mensagem(request, mensagem, "aviso")

def informar_info(request: Request, mensagem: str):
    adicionar_mensagem(request, mensagem, "info")

def obter_mensagens(request: Request) -> list:
    """Obtém e limpa mensagens da sessão"""
    mensagens = request.session.pop("mensagens", [])
    return mensagens
```

**`util/template_util.py`** (modificar)
```python
from jinja2 import Environment, FileSystemLoader
from util.flash_messages import obter_mensagens

def criar_templates(pasta: str):
    env = Environment(loader=FileSystemLoader(pasta))

    # Adicionar função global para obter mensagens
    env.globals['obter_mensagens'] = obter_mensagens

    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory=pasta, env=env)
    return templates
```

**`static/js/toasts.js`** (criar)
```javascript
// Sistema de Toasts Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    const mensagens = JSON.parse(document.getElementById('mensagens-data')?.textContent || '[]');

    const tipoMap = {
        'sucesso': 'success',
        'erro': 'danger',
        'aviso': 'warning',
        'info': 'info'
    };

    mensagens.forEach(msg => {
        mostrarToast(msg.texto, tipoMap[msg.tipo] || 'info');
    });
});

function mostrarToast(mensagem, tipo = 'info') {
    const container = document.getElementById('toast-container');
    const id = 'toast-' + Date.now();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${tipo} border-0`;
    toast.setAttribute('role', 'alert');
    toast.id = id;

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${mensagem}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}
```

**`templates/base.html`** (adicionar)
```html
<!-- Container para toasts -->
<div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3"></div>

<!-- Dados de mensagens (hidden) -->
<script id="mensagens-data" type="application/json">
    {{ obter_mensagens(request) | tojson }}
</script>

<!-- Script de toasts -->
<script src="/static/js/toasts.js"></script>
```

### Checklist
- [ ] Atualizar util/flash_messages.py
- [ ] Modificar util/template_util.py
- [ ] Criar static/js/toasts.js
- [ ] Atualizar templates/base.html
- [ ] Testar todos os tipos de toast
- [ ] Documentar uso do sistema de toasts

---

## TAREFA 7: Autenticação Completa

### Objetivos
- Implementar recuperação de senha completa
- Validação de força de senha
- Melhorar segurança do login

### Arquivos a CRIAR
**`util/senha_util.py`**
```python
import re
from typing import Tuple

def validar_forca_senha(senha: str) -> Tuple[bool, str]:
    """
    Valida força da senha
    Retorna: (é_válida, mensagem)
    """
    if len(senha) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"

    if not re.search(r"[A-Z]", senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"

    if not re.search(r"[a-z]", senha):
        return False, "Senha deve conter pelo menos uma letra minúscula"

    if not re.search(r"\d", senha):
        return False, "Senha deve conter pelo menos um número"

    return True, "Senha válida"

def calcular_nivel_senha(senha: str) -> str:
    """Retorna: fraca, média, forte"""
    pontos = 0

    if len(senha) >= 8: pontos += 1
    if len(senha) >= 12: pontos += 1
    if re.search(r"[A-Z]", senha): pontos += 1
    if re.search(r"[a-z]", senha): pontos += 1
    if re.search(r"\d", senha): pontos += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha): pontos += 1

    if pontos <= 2: return "fraca"
    if pontos <= 4: return "média"
    return "forte"
```

### Arquivos a MODIFICAR
**`routes/auth_routes.py`** - Adicionar rotas de recuperação
```python
from util.email_service import email_service
from util.senha_util import validar_forca_senha
from util.security import gerar_token_redefinicao, obter_data_expiracao_token
from datetime import datetime

@router.get("/esqueci-senha")
async def get_esqueci_senha(request: Request):
    return templates.TemplateResponse("esqueci_senha.html", {"request": request})

@router.post("/esqueci-senha")
async def post_esqueci_senha(
    request: Request,
    email: str = Form(...)
):
    usuario = usuario_repo.obter_por_email(email)

    if usuario:
        # Gerar token
        token = gerar_token_redefinicao()
        data_expiracao = obter_data_expiracao_token(horas=1)

        # Salvar token no banco
        usuario_repo.atualizar_token(email, token, data_expiracao)

        # Enviar e-mail
        email_service.enviar_recuperacao_senha(email, usuario.nome, token)

    # Sempre mostrar mesma mensagem (segurança)
    informar_sucesso(request, "Se o e-mail existir, você receberá instruções de recuperação")
    return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)

@router.get("/redefinir-senha")
async def get_redefinir_senha(request: Request, token: str):
    # Validar token
    usuario = usuario_repo.obter_por_token(token)

    if not usuario or not usuario.data_token:
        informar_erro(request, "Token inválido ou expirado")
        return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)

    # Verificar expiração
    data_token = datetime.fromisoformat(usuario.data_token)
    if datetime.now() > data_token:
        informar_erro(request, "Token expirado")
        return RedirectResponse("/esqueci-senha", status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "redefinir_senha.html",
        {"request": request, "token": token}
    )

@router.post("/redefinir-senha")
async def post_redefinir_senha(
    request: Request,
    token: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...)
):
    # Validar senhas
    if senha != confirmar_senha:
        informar_erro(request, "Senhas não coincidem")
        return RedirectResponse(f"/redefinir-senha?token={token}", status.HTTP_303_SEE_OTHER)

    # Validar força
    valida, msg = validar_forca_senha(senha)
    if not valida:
        informar_erro(request, msg)
        return RedirectResponse(f"/redefinir-senha?token={token}", status.HTTP_303_SEE_OTHER)

    # Validar token
    usuario = usuario_repo.obter_por_token(token)
    if not usuario:
        informar_erro(request, "Token inválido")
        return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)

    # Atualizar senha
    senha_hash = criar_hash_senha(senha)
    usuario_repo.atualizar_senha(usuario.id, senha_hash)
    usuario_repo.limpar_token(usuario.id)

    informar_sucesso(request, "Senha redefinida com sucesso!")
    return RedirectResponse("/login", status.HTTP_303_SEE_OTHER)
```

**Templates a criar**:
- `templates/auth/esqueci_senha.html`
- `templates/auth/redefinir_senha.html`

### Checklist
- [ ] Criar util/senha_util.py
- [ ] Adicionar rotas de recuperação de senha
- [ ] Criar templates de recuperação
- [ ] Testar fluxo completo de recuperação
- [ ] Adicionar rate limiting no login (opcional)

---

## TAREFA 8: Páginas de Perfil do Usuário

### Objetivos
- Edição de dados pessoais
- Upload de foto de perfil
- Alteração de senha
- Interface amigável

### Arquivos a VERIFICAR/MELHORAR
**`routes/perfil_routes.py`** - já existe, melhorar
**`util/foto_util.py`** - adaptar para fotos de usuário

**`routes/perfil_routes.py`** (melhorias)
```python
from util.senha_util import validar_forca_senha
from util.flash_messages import informar_sucesso, informar_erro

@router.post("/alterar-senha")
@requer_autenticacao()
async def post_alterar_senha(
    request: Request,
    senha_atual: str = Form(...),
    senha_nova: str = Form(...),
    confirmar_senha: str = Form(...),
    usuario_logado: dict = None
):
    # Validar senha atual
    usuario = usuario_repo.obter_por_id(usuario_logado["id"])
    if not verificar_senha(senha_atual, usuario.senha):
        informar_erro(request, "Senha atual incorreta")
        return RedirectResponse("/perfil", status.HTTP_303_SEE_OTHER)

    # Validar novas senhas
    if senha_nova != confirmar_senha:
        informar_erro(request, "Senhas não coincidem")
        return RedirectResponse("/perfil", status.HTTP_303_SEE_OTHER)

    # Validar força
    valida, msg = validar_forca_senha(senha_nova)
    if not valida:
        informar_erro(request, msg)
        return RedirectResponse("/perfil", status.HTTP_303_SEE_OTHER)

    # Atualizar
    senha_hash = criar_hash_senha(senha_nova)
    usuario_repo.atualizar_senha(usuario.id, senha_hash)

    informar_sucesso(request, "Senha alterada com sucesso!")
    return RedirectResponse("/perfil", status.HTTP_303_SEE_OTHER)
```

**Templates a criar/melhorar**:
- `templates/perfil/index.html` - visão geral do perfil
- `templates/perfil/editar.html` - edição de dados
- `templates/perfil/senha.html` - alteração de senha
- `templates/perfil/foto.html` - upload de foto

### Checklist
- [ ] Melhorar rotas de perfil
- [ ] Criar/atualizar templates de perfil
- [ ] Integrar validação de senha forte
- [ ] Testar upload de foto
- [ ] Adicionar preview de imagem

---

## TAREFA 9: Dados Seed e Inicialização

### Objetivos
- Migrar dados SQL para JSON
- Scripts automáticos de inicialização
- Dados de exemplo para desenvolvimento

### Arquivos a CRIAR
**`data/usuarios_seed.json`**
```json
{
  "usuarios": [
    {
      "nome": "Administrador",
      "email": "admin@sistema.com",
      "senha": "Admin@123",
      "perfil": "admin"
    },
    {
      "nome": "João Silva",
      "email": "joao@email.com",
      "senha": "Joao@123",
      "perfil": "cliente"
    },
    {
      "nome": "Maria Santos",
      "email": "maria@email.com",
      "senha": "Maria@123",
      "perfil": "cliente"
    }
  ]
}
```

**`util/seed_data.py`**
```python
import json
from pathlib import Path
from repo import usuario_repo
from model.usuario_model import Usuario
from util.security import criar_hash_senha
from util.logger_config import logger

def carregar_usuarios_seed():
    """Carrega usuários do arquivo JSON seed"""
    arquivo = Path("data/usuarios_seed.json")

    if not arquivo.exists():
        logger.warning("Arquivo de seed não encontrado")
        return

    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    for user_data in dados.get("usuarios", []):
        # Verificar se já existe
        if usuario_repo.obter_por_email(user_data["email"]):
            logger.info(f"Usuário {user_data['email']} já existe")
            continue

        # Criar usuário
        usuario = Usuario(
            id=0,
            nome=user_data["nome"],
            email=user_data["email"],
            senha=criar_hash_senha(user_data["senha"]),
            perfil=user_data["perfil"]
        )

        usuario_repo.inserir(usuario)
        logger.info(f"Usuário {user_data['email']} criado")

def inicializar_dados():
    """Inicializa todos os dados seed"""
    logger.info("Iniciando carga de dados seed...")
    carregar_usuarios_seed()
    logger.info("Dados seed carregados com sucesso!")
```

### Arquivos a MODIFICAR
**`main.py`**
```python
from util.seed_data import inicializar_dados

# Após criar tabelas
usuario_repo.criar_tabela()
configuracao_repo.criar_tabela()

# Inicializar dados
inicializar_dados()
```

### Checklist
- [ ] Criar pasta data/
- [ ] Criar usuarios_seed.json
- [ ] Criar util/seed_data.py
- [ ] Integrar no main.py
- [ ] Testar carga de dados
- [ ] Documentar como adicionar seeds

---

## TAREFA 10: Entidade CRUD de Exemplo

### Objetivos
- Criar entidade exemplo completa (ex: "Tarefa")
- Servir como template para alunos
- Demonstrar todos os padrões do boilerplate

### Arquivos a CRIAR

**`model/tarefa_model.py`**
```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Tarefa:
    id: int
    titulo: str
    descricao: str
    concluida: bool
    usuario_id: int
    data_criacao: Optional[str] = None
    data_conclusao: Optional[str] = None
```

**`sql/tarefa_sql.py`**
```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS tarefa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    concluida INTEGER DEFAULT 0,
    usuario_id INTEGER NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_conclusao DATETIME,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO tarefa (titulo, descricao, usuario_id)
VALUES (?, ?, ?)
"""

OBTER_TODOS_POR_USUARIO = """
SELECT * FROM tarefa
WHERE usuario_id = ?
ORDER BY concluida ASC, data_criacao DESC
"""

OBTER_POR_ID = "SELECT * FROM tarefa WHERE id = ?"

ATUALIZAR = """
UPDATE tarefa
SET titulo = ?, descricao = ?, concluida = ?
WHERE id = ?
"""

MARCAR_CONCLUIDA = """
UPDATE tarefa
SET concluida = 1, data_conclusao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = "DELETE FROM tarefa WHERE id = ?"
```

**`repo/tarefa_repo.py`**
```python
from typing import Optional
from model.tarefa_model import Tarefa
from sql.tarefa_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(tarefa: Tarefa) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            tarefa.titulo,
            tarefa.descricao,
            tarefa.usuario_id
        ))
        return cursor.lastrowid

def obter_todos_por_usuario(usuario_id: int) -> list[Tarefa]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_POR_USUARIO, (usuario_id,))
        rows = cursor.fetchall()
        return [
            Tarefa(
                id=row["id"],
                titulo=row["titulo"],
                descricao=row["descricao"],
                concluida=bool(row["concluida"]),
                usuario_id=row["usuario_id"],
                data_criacao=row["data_criacao"],
                data_conclusao=row["data_conclusao"]
            )
            for row in rows
        ]

def obter_por_id(id: int) -> Optional[Tarefa]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return Tarefa(
                id=row["id"],
                titulo=row["titulo"],
                descricao=row["descricao"],
                concluida=bool(row["concluida"]),
                usuario_id=row["usuario_id"],
                data_criacao=row["data_criacao"],
                data_conclusao=row["data_conclusao"]
            )
        return None

def atualizar(tarefa: Tarefa) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            tarefa.titulo,
            tarefa.descricao,
            tarefa.concluida,
            tarefa.id
        ))
        return cursor.rowcount > 0

def marcar_concluida(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_CONCLUIDA, (id,))
        return cursor.rowcount > 0

def excluir(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0
```

**`dtos/tarefa_dto.py`**
```python
from pydantic import BaseModel, Field, field_validator

class CriarTarefaDTO(BaseModel):
    titulo: str = Field(..., tamanho_minimo=3, tamanho_maximo=100)
    descricao: str = Field(default="", tamanho_maximo=500)

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v):
        if not v or not v.strip():
            raise ValueError('Título é obrigatório')
        return v.strip()

class AlterarTarefaDTO(BaseModel):
    id: int = Field(..., gt=0)
    titulo: str = Field(..., tamanho_minimo=3, tamanho_maximo=100)
    descricao: str = Field(default="", tamanho_maximo=500)
    concluida: bool = False

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v):
        if not v or not v.strip():
            raise ValueError('Título é obrigatório')
        return v.strip()
```

**`routes/tarefas_routes.py`**
```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.tarefa_dto import CriarTarefaDTO, AlterarTarefaDTO
from model.tarefa_model import Tarefa
from repo import tarefa_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger

router = APIRouter(prefix="/tarefas")
templates = criar_templates("templates/tarefas")

@router.get("/")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: dict = None):
    tarefas = tarefa_repo.obter_todos_por_usuario(usuario_logado["id"])
    return templates.TemplateResponse(
        "listar.html",
        {"request": request, "tarefas": tarefas}
    )

@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar(request: Request, usuario_logado: dict = None):
    return templates.TemplateResponse("cadastrar.html", {"request": request})

@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(""),
    usuario_logado: dict = None
):
    try:
        # Validar com DTO
        dto = CriarTarefaDTO(titulo=titulo, descricao=descricao)

        # Criar tarefa
        tarefa = Tarefa(
            id=0,
            titulo=dto.titulo,
            descricao=dto.descricao,
            concluida=False,
            usuario_id=usuario_logado["id"]
        )

        tarefa_repo.inserir(tarefa)
        logger.info(f"Tarefa criada por usuário {usuario_logado['id']}")

        informar_sucesso(request, "Tarefa criada com sucesso!")
        return RedirectResponse("/tarefas", status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        return templates.TemplateResponse(
            "cadastrar.html",
            {"request": request, "dados": {"titulo": titulo, "descricao": descricao}}
        )

@router.post("/{id}/concluir")
@requer_autenticacao()
async def concluir(request: Request, id: int, usuario_logado: dict = None):
    tarefa = tarefa_repo.obter_por_id(id)

    # Verificar se pertence ao usuário
    if not tarefa or tarefa.usuario_id != usuario_logado["id"]:
        informar_erro(request, "Tarefa não encontrada")
        return RedirectResponse("/tarefas", status.HTTP_303_SEE_OTHER)

    tarefa_repo.marcar_concluida(id)
    informar_sucesso(request, "Tarefa concluída!")
    return RedirectResponse("/tarefas", status.HTTP_303_SEE_OTHER)

@router.get("/{id}/excluir")
@requer_autenticacao()
async def get_excluir(request: Request, id: int, usuario_logado: dict = None):
    tarefa = tarefa_repo.obter_por_id(id)

    if not tarefa or tarefa.usuario_id != usuario_logado["id"]:
        return RedirectResponse("/tarefas", status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "excluir.html",
        {"request": request, "tarefa": tarefa}
    )

@router.post("/{id}/excluir")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: dict = None):
    tarefa = tarefa_repo.obter_por_id(id)

    if tarefa and tarefa.usuario_id == usuario_logado["id"]:
        tarefa_repo.excluir(id)
        informar_sucesso(request, "Tarefa excluída!")

    return RedirectResponse("/tarefas", status.HTTP_303_SEE_OTHER)
```

**Templates**: criar pasta `templates/tarefas/` com:
- `listar.html`
- `cadastrar.html`
- `excluir.html`

### Arquivos a MODIFICAR
**`main.py`**
```python
from repo import tarefa_repo
from routes.tarefas_routes import router as tarefas_router

# Criar tabela
tarefa_repo.criar_tabela()

# Incluir router
app.include_router(tarefas_router)
```

### Checklist
- [ ] Criar model/tarefa_model.py
- [ ] Criar sql/tarefa_sql.py
- [ ] Criar repo/tarefa_repo.py
- [ ] Criar dtos/tarefa_dto.py
- [ ] Criar routes/tarefas_routes.py
- [ ] Criar templates de tarefas
- [ ] Integrar no main.py
- [ ] Testar CRUD completo
- [ ] Documentar como template

---

## TAREFA 11: Documentação Completa

### Objetivos
- README profissional
- Guias para alunos
- Documentação da arquitetura
- Exemplos práticos

### Arquivos a CRIAR

**`README.md`**
```markdown
# Boilerplate Web App - FastAPI

Boilerplate completo para desenvolvimento de aplicações web com Python, FastAPI, Jinja2 e Bootstrap.

## Características

- ✅ Python 3.10+ com FastAPI
- ✅ Templates Jinja2 + Bootstrap 5.3.8
- ✅ Autenticação e Autorização por perfil
- ✅ Sistema de Logger profissional
- ✅ Envio de e-mails (MailerSend)
- ✅ Flash messages e Toasts
- ✅ Validação com Pydantic DTOs
- ✅ SQLite sem ORM
- ✅ Configurações do sistema via admin
- ✅ Exemplo CRUD completo

## Instalação Rápida

1. Clone o repositório
2. Crie ambiente virtual: `python -m venv .venv`
3. Ative: `.venv\Scripts\activate` (Windows) ou `source .venv/bin/activate` (Linux/Mac)
4. Instale dependências: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e configure
6. Execute: `python main.py`
7. Acesse: http://localhost:8000

## Usuários Padrão

- Admin: admin@sistema.com / Admin@123
- Cliente: joao@email.com / Joao@123

## Estrutura do Projeto

```
├── data/              # Dados seed em JSON
├── docs/              # Documentação
├── dtos/              # DTOs Pydantic para validação
├── model/             # Modelos de entidades
├── repo/              # Repositórios de acesso a dados
├── routes/            # Rotas organizadas por módulo
├── sql/               # Comandos SQL
├── static/            # CSS, JS, imagens
├── templates/         # Templates Jinja2
├── util/              # Utilitários
└── tests/             # Testes
```

## Guias

- [Criando um novo CRUD](docs/CRIAR_CRUD.md)
- [Adicionando perfis](docs/PERFIS.md)
- [Sistema de validações](docs/VALIDACOES.md)
- [Envio de e-mails](docs/EMAILS.md)

## Tecnologias

- FastAPI 0.115+
- Jinja2
- Pydantic 2.0+
- Bootstrap 5.3.8
- SQLite3
```

**`docs/CRIAR_CRUD.md`**
```markdown
# Como Criar um CRUD Completo

Este guia mostra como criar um CRUD completo seguindo os padrões do boilerplate.

## Passo 1: Criar o Model

Arquivo: `model/entidade_model.py`

```python
from dataclasses import dataclass

@dataclass
class MinhaEntidade:
    id: int
    nome: str
    # outros campos...
```

## Passo 2: Criar os comandos SQL

Arquivo: `sql/entidade_sql.py`

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS minha_entidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
"""

INSERIR = "INSERT INTO minha_entidade (nome) VALUES (?)"
OBTER_TODOS = "SELECT * FROM minha_entidade ORDER BY nome"
OBTER_POR_ID = "SELECT * FROM minha_entidade WHERE id = ?"
ATUALIZAR = "UPDATE minha_entidade SET nome = ? WHERE id = ?"
EXCLUIR = "DELETE FROM minha_entidade WHERE id = ?"
```

## Passo 3: Criar o Repositório

Arquivo: `repo/entidade_repo.py`

[código exemplo completo]

## Passo 4: Criar DTOs de Validação

Arquivo: `dtos/entidade_dto.py`

[código exemplo]

## Passo 5: Criar as Rotas

Arquivo: `routes/entidade_routes.py`

[código exemplo]

## Passo 6: Criar Templates

Pasta: `templates/entidades/`
- `listar.html`
- `cadastrar.html`
- `alterar.html`
- `excluir.html`

## Passo 7: Registrar no main.py

```python
from repo import entidade_repo
from routes.entidade_routes import router as entidade_router

# Criar tabela
entidade_repo.criar_tabela()

# Registrar rotas
app.include_router(entidade_router)
```

## Exemplo Completo

Veja o CRUD de Tarefas para um exemplo completo funcionando.
```

**`docs/PERFIS.md`**
```markdown
# Sistema de Perfis

## Perfis Existentes

- **ADMIN**: Acesso administrativo total
- **CLIENTE**: Usuário comum

## Adicionando Novo Perfil

1. Edite `util/perfis.py`:
```python
class Perfil(str, Enum):
    ADMIN = "admin"
    CLIENTE = "cliente"
    VENDEDOR = "vendedor"  # NOVO
```

2. Use em rotas:
```python
@requer_autenticacao([Perfil.VENDEDOR.value])
async def rota_vendedor(request: Request, usuario_logado: dict = None):
    ...
```

## Verificação de Perfil

```python
from util.perfis import Perfil

if usuario_logado["perfil"] == Perfil.ADMIN.value:
    # código admin
```
```

**`docs/VALIDACOES.md`**, **`docs/EMAILS.md`**, etc.

**`.env.example`** (completo)
```
# Database
DATABASE_PATH=database.db

# Logging
LOG_LEVEL=INFO

# Email (MailerSend)
MAILERSEND_API_KEY=seu_api_key_aqui
MAILERSEND_FROM_EMAIL=noreply@seudominio.com
MAILERSEND_FROM_NAME=Sistema

# App
BASE_URL=http://localhost:8000
SECRET_KEY=sua_chave_secreta_aqui
```

### Checklist
- [ ] Criar README.md principal
- [ ] Criar docs/CRIAR_CRUD.md
- [ ] Criar docs/PERFIS.md
- [ ] Criar docs/VALIDACOES.md
- [ ] Criar docs/EMAILS.md
- [ ] Criar .env.example completo
- [ ] Adicionar comentários no código
- [ ] Criar CONTRIBUTING.md

---

## TAREFA 12: Testes e Segurança

### Objetivos
- Estrutura de testes com pytest
- Exemplos de testes
- Melhorias de segurança
- Rate limiting

### Arquivos a CRIAR

**`tests/conftest.py`**
```python
import pytest
from fastapi.testclient import TestClient
from main import app
import os

@pytest.fixture
def client():
    """Cliente de teste FastAPI"""
    return TestClient(app)

@pytest.fixture
def db_test():
    """Banco de dados de teste"""
    # Configurar DB de teste
    os.environ['DATABASE_PATH'] = ':memory:'
    yield
    # Limpar
```

**`tests/test_auth.py`**
```python
def test_login_sucesso(client):
    response = client.post("/login", data={
        "email": "admin@sistema.com",
        "senha": "Admin@123"
    })
    assert response.status_code == 303  # Redirect

def test_login_falha(client):
    response = client.post("/login", data={
        "email": "invalido@email.com",
        "senha": "senhaerrada"
    })
    assert "Credenciais inválidas" in response.text

def test_acesso_sem_autenticacao(client):
    response = client.get("/admin/configuracoes")
    assert response.status_code == 303  # Redirect para login
```

**`tests/test_tarefas.py`**
```python
def test_criar_tarefa(client):
    # Login primeiro
    client.post("/login", data={
        "email": "joao@email.com",
        "senha": "Joao@123"
    })

    # Criar tarefa
    response = client.post("/tarefas/cadastrar", data={
        "titulo": "Teste",
        "descricao": "Descrição teste"
    })

    assert response.status_code == 303

def test_validacao_tarefa(client):
    client.post("/login", data={
        "email": "joao@email.com",
        "senha": "Joao@123"
    })

    # Título muito curto
    response = client.post("/tarefas/cadastrar", data={
        "titulo": "AB",
        "descricao": ""
    })

    assert "Título" in response.text
```

**`util/rate_limit.py`**
```python
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)

    def verificar(self, identificador: str):
        """Verifica se request está dentro do limite"""
        agora = datetime.now()

        # Limpar requests antigos
        self.requests[identificador] = [
            req_time for req_time in self.requests[identificador]
            if agora - req_time < self.window
        ]

        # Verificar limite
        if len(self.requests[identificador]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas requisições. Tente novamente mais tarde."
            )

        # Adicionar request atual
        self.requests[identificador].append(agora)

# Limiter para login
login_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 por 5min
```

**Modificar `routes/auth_routes.py`**
```python
from util.rate_limit import login_limiter

@router.post("/login")
async def post_login(request: Request, email: str = Form(), senha: str = Form()):
    # Rate limiting
    ip = request.client.host
    login_limiter.verificar(ip)

    # resto do código...
```

**`util/security_headers.py`**
```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
```

**Modificar `main.py`**
```python
from util.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

**`pytest.ini`**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**`requirements.txt`** (adicionar)
```
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.24.1
```

### Checklist
- [ ] Criar estrutura de testes
- [ ] Implementar testes de autenticação
- [ ] Implementar testes de CRUD
- [ ] Adicionar rate limiting no login
- [ ] Adicionar security headers
- [ ] Configurar pytest
- [ ] Documentar como rodar testes
- [ ] Adicionar CSRF protection (se necessário)

---

## ORDEM DE EXECUÇÃO

1. ✅ Tarefa 1: Limpeza
2. ✅ Tarefa 2: Perfis Enum
3. ✅ Tarefa 3: Logger
4. ✅ Tarefa 4: E-mail
5. ✅ Tarefa 5: Configurações
6. ✅ Tarefa 6: Toasts
7. ✅ Tarefa 7: Autenticação
8. ✅ Tarefa 8: Perfil
9. ✅ Tarefa 9: Seeds
10. ✅ Tarefa 10: CRUD Exemplo
11. ✅ Tarefa 11: Documentação
12. ✅ Tarefa 12: Testes e Segurança

---

## VALIDAÇÃO FINAL

Após concluir todas as tarefas, verificar:

- [ ] Aplicação inicia sem erros
- [ ] Login/Logout funcionando
- [ ] Perfis funcionando corretamente
- [ ] Logger gerando logs
- [ ] E-mails sendo enviados (testar com conta real)
- [ ] Toasts aparecendo corretamente
- [ ] Configurações sendo salvas
- [ ] Perfil de usuário completo
- [ ] CRUD de exemplo funcionando
- [ ] Testes passando: `pytest`
- [ ] Rate limiting no login
- [ ] Security headers presentes
- [ ] Documentação completa e clara
- [ ] .env.example atualizado
- [ ] Código limpo e comentado

## PRÓXIMOS PASSOS (Opcional)

- [ ] Docker/docker-compose
- [ ] CI/CD básico
- [ ] Deploy (Heroku/Railway/etc)
- [ ] Internacionalização (i18n)
- [ ] Theme switcher (claro/escuro)
- [ ] API REST endpoints
- [ ] WebSockets para notificações real-time
