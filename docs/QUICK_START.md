# Guia de Início Rápido - DefaultWebApp

Bem-vindo! Este guia foi criado especialmente para **alunos** que estão começando a trabalhar com o DefaultWebApp. Aqui você encontrará tudo que precisa para começar rapidamente.

## Índice
1. [Instalação e Primeiro Acesso](#instalação-e-primeiro-acesso)
2. [Entendendo a Estrutura](#entendendo-a-estrutura)
3. [Seu Primeiro CRUD em 30 Minutos](#seu-primeiro-crud-em-30-minutos)
4. [Dicas para Iniciantes](#dicas-para-iniciantes)
5. [Problemas Comuns](#problemas-comuns)
6. [Próximos Passos](#próximos-passos)

---

## Instalação e Primeiro Acesso

### 1. Instalar Python

Você precisa do Python 3.10 ou superior. Verifique se já tem instalado:

```bash
python --version
# ou
python3 --version
```

Se não tiver, baixe em: https://www.python.org/downloads/

**Importante no Windows**: marque a opção "Add Python to PATH" durante a instalação!

### 2. Baixar o Projeto

Se você recebeu o projeto em um arquivo ZIP:
```bash
# Extraia o ZIP em uma pasta de sua escolha
# Exemplo: C:\MeusProjetos\DefaultWebApp
```

Se está usando Git:
```bash
git clone <url-do-repositorio>
cd DefaultWebApp
```

### 3. Criar Ambiente Virtual

O ambiente virtual isola as dependências do projeto:

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Você verá `(.venv)` no início da linha do terminal quando o ambiente estiver ativado.

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

Aguarde alguns minutos enquanto tudo é instalado.

### 5. Executar a Aplicação

```bash
python main.py
```

Você verá algo assim:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 6. Acessar no Navegador

Abra seu navegador e acesse:
```
http://localhost:8000
```

### 7. Fazer Login

Use um dos usuários padrão:

**Administrador:**
- E-mail: `admin@sistema.com`
- Senha: `Admin@123`

**Cliente:**
- E-mail: `joao@email.com`
- Senha: `Joao@123`

---

## Entendendo a Estrutura

### Arquitetura Simples

O projeto segue uma arquitetura em camadas bem simples:

```
Usuário faz requisição
    ↓
Route (recebe requisição)
    ↓
DTO (valida dados)
    ↓
Repository (acessa banco)
    ↓
SQL (executa query)
    ↓
Banco de Dados SQLite
```

### Pastas Importantes

```
DefaultWebApp/
├── main.py              ← Arquivo principal (inicia tudo)
├── requirements.txt     ← Lista de dependências
│
├── model/              ← Modelos (representam entidades)
│   └── tarefa_model.py
│
├── repo/               ← Repositórios (acessam banco)
│   └── tarefa_repo.py
│
├── routes/             ← Rotas (URLs da aplicação)
│   └── tarefas_routes.py
│
├── templates/          ← HTMLs (interface)
│   └── tarefas/
│       └── listar.html
│
├── static/             ← CSS, JS, imagens
│   ├── css/
│   ├── js/
│   └── img/
│
└── util/               ← Utilitários (funções auxiliares)
    └── auth_decorator.py
```

### Fluxo de Dados

**Exemplo: Listar Tarefas**

1. Usuário acessa `http://localhost:8000/tarefas`
2. Route `tarefas_routes.py` recebe a requisição
3. Repository `tarefa_repo.py` busca no banco
4. Template `tarefas/listar.html` mostra os dados
5. HTML é enviado de volta ao usuário

---

## Seu Primeiro CRUD em 30 Minutos

Vamos criar um CRUD de **Livros** do zero!

### Passo 1: Criar o Model (3 min)

Crie o arquivo `model/livro_model.py`:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Livro:
    id: int
    titulo: str
    autor: str
    ano: int
    disponivel: bool = True
    data_cadastro: Optional[str] = None
```

### Passo 2: Criar os SQLs (5 min)

Crie o arquivo `sql/livro_sql.py`:

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS livro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    ano INTEGER NOT NULL,
    disponivel INTEGER DEFAULT 1,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO livro (titulo, autor, ano, disponivel)
VALUES (?, ?, ?, ?)
"""

OBTER_TODOS = "SELECT * FROM livro ORDER BY titulo"

OBTER_POR_ID = "SELECT * FROM livro WHERE id = ?"

ATUALIZAR = """
UPDATE livro
SET titulo = ?, autor = ?, ano = ?, disponivel = ?
WHERE id = ?
"""

EXCLUIR = "DELETE FROM livro WHERE id = ?"
```

### Passo 3: Criar o Repository (7 min)

Crie o arquivo `repo/livro_repo.py`:

```python
from typing import Optional, List
from model.livro_model import Livro
from sql.livro_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(livro: Livro) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            livro.titulo,
            livro.autor,
            livro.ano,
            1 if livro.disponivel else 0
        ))
        return cursor.lastrowid

def obter_todos() -> List[Livro]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_livro(row) for row in rows]

def obter_por_id(id: int) -> Optional[Livro]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_livro(row) if row else None

def excluir(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0

def _row_to_livro(row) -> Livro:
    return Livro(
        id=row["id"],
        titulo=row["titulo"],
        autor=row["autor"],
        ano=row["ano"],
        disponivel=bool(row["disponivel"]),
        data_cadastro=row["data_cadastro"]
    )
```

### Passo 4: Criar as Rotas (10 min)

Crie o arquivo `routes/livros_routes.py`:

```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

from model.livro_model import Livro
from repo import livro_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro

router = APIRouter(prefix="/livros")
templates = criar_templates("templates/livros")

@router.get("/")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: dict = None):
    livros = livro_repo.obter_todos()
    return templates.TemplateResponse(
        "listar.html",
        {"request": request, "livros": livros}
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
    autor: str = Form(...),
    ano: int = Form(...),
    usuario_logado: dict = None
):
    livro = Livro(
        id=0,
        titulo=titulo,
        autor=autor,
        ano=ano,
        disponivel=True
    )

    livro_repo.inserir(livro)
    informar_sucesso(request, "Livro cadastrado com sucesso!")
    return RedirectResponse("/livros", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/{id}/excluir")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: dict = None):
    livro_repo.excluir(id)
    informar_sucesso(request, "Livro excluído!")
    return RedirectResponse("/livros", status_code=status.HTTP_303_SEE_OTHER)
```

### Passo 5: Criar Templates (5 min)

Crie a pasta `templates/livros/` e os arquivos:

**`templates/livros/listar.html`:**
```html
{% extends "base.html" %}

{% block title %}Livros{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between mb-4">
        <h1>Livros</h1>
        <a href="/livros/cadastrar" class="btn btn-primary">Novo Livro</a>
    </div>

    {% if livros %}
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Título</th>
                <th>Autor</th>
                <th>Ano</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for livro in livros %}
            <tr>
                <td>{{ livro.titulo }}</td>
                <td>{{ livro.autor }}</td>
                <td>{{ livro.ano }}</td>
                <td>
                    <form method="POST" action="/livros/{{ livro.id }}/excluir"
                          style="display: inline;">
                        <button type="submit" class="btn btn-sm btn-danger">
                            Excluir
                        </button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <div class="alert alert-info">Nenhum livro cadastrado.</div>
    {% endif %}
</div>
{% endblock %}
```

**`templates/livros/cadastrar.html`:**
```html
{% extends "base.html" %}

{% block title %}Cadastrar Livro{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Cadastrar Livro</h1>

    <form method="POST" action="/livros/cadastrar" class="mt-4">
        <div class="mb-3">
            <label for="titulo" class="form-label">Título *</label>
            <input type="text" class="form-control" id="titulo"
                   name="titulo" required>
        </div>

        <div class="mb-3">
            <label for="autor" class="form-label">Autor *</label>
            <input type="text" class="form-control" id="autor"
                   name="autor" required>
        </div>

        <div class="mb-3">
            <label for="ano" class="form-label">Ano *</label>
            <input type="number" class="form-control" id="ano"
                   name="ano" required>
        </div>

        <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary">Cadastrar</button>
            <a href="/livros" class="btn btn-secondary">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

### Passo 6: Registrar no main.py (2 min)

Edite `main.py` e adicione:

```python
# No início, com os outros imports
from repo import livro_repo
from routes.livros_routes import router as livros_router

# Após criar outras tabelas
livro_repo.criar_tabela()
logger.info("Tabela 'livro' criada/verificada")

# Após incluir outros routers
app.include_router(livros_router, tags=["Livros"])
logger.info("Router de livros incluído")
```

### Passo 7: Testar! (3 min)

1. Pare o servidor (Ctrl+C)
2. Execute novamente: `python main.py`
3. Acesse: `http://localhost:8000/livros`
4. Cadastre alguns livros
5. Teste a exclusão

**Pronto! Você criou seu primeiro CRUD completo!** 🎉

---

## Dicas para Iniciantes

### 1. Use o VS Code

É o melhor editor para este projeto:
- Download: https://code.microsoft.com/
- Instale a extensão "Python"
- Abra a pasta do projeto no VS Code

### 2. Aprenda os Atalhos

**VS Code:**
- `Ctrl + P` → Buscar arquivo
- `Ctrl + Shift + F` → Buscar no projeto todo
- `Ctrl + ` → Abrir terminal
- `F5` → Debug

**Terminal:**
- `Ctrl + C` → Parar servidor
- `↑` → Comando anterior
- `Tab` → Autocompletar

### 3. Consulte os Exemplos

Sempre que tiver dúvida, olhe o código de Tarefas:
- `model/tarefa_model.py`
- `repo/tarefa_repo.py`
- `routes/tarefas_routes.py`
- `templates/tarefas/`

### 4. Use o Logger

Para debugar, adicione logs:

```python
from util.logger_config import logger

logger.debug(f"Variável x = {x}")
logger.info("Operação realizada")
logger.warning("Atenção!")
logger.error(f"Erro: {e}")
```

Logs ficam em `logs/app.log`

### 5. Leia as Mensagens de Erro

Erros Python são amigáveis! Leia de baixo para cima:

```
Traceback (most recent call last):
  File "main.py", line 10
    print("Olá"
         ^
SyntaxError: invalid syntax
```

Diz exatamente onde está o erro (linha 10).

### 6. Teste Aos Poucos

Não escreva muito código de uma vez. Teste frequentemente:

1. Escreve uma função → Testa
2. Adiciona uma rota → Testa
3. Cria um template → Testa

### 7. Commit Frequentemente (Se usar Git)

```bash
git add .
git commit -m "Adiciona CRUD de livros"
git push
```

### 8. Consulte a Documentação

- [CRIAR_CRUD.md](CRIAR_CRUD.md) → Tutorial detalhado
- [PERFIS.md](PERFIS.md) → Sistema de perfis
- README.md → Visão geral

---

## Problemas Comuns

### 1. "Python não é reconhecido"

**Problema:** Python não está no PATH

**Solução Windows:**
1. Procure "Variáveis de Ambiente" no Windows
2. Adicione `C:\Python310` (ou onde instalou)
3. Adicione `C:\Python310\Scripts`

**Solução Linux/Mac:**
```bash
# Use python3 ao invés de python
python3 main.py
```

### 2. "pip: command not found"

**Solução:**
```bash
python -m pip install -r requirements.txt
```

### 3. "Address already in use"

**Problema:** Porta 8000 já está em uso

**Solução 1 - Mudar porta:**
Edite `main.py`:
```python
port = int(os.getenv("PORT", "8001"))  # Mudou para 8001
```

**Solução 2 - Matar processo:**

Windows:
```bash
netstat -ano | findstr :8000
taskkill /PID <numero> /F
```

Linux/Mac:
```bash
lsof -i :8000
kill -9 <PID>
```

### 4. "Template not found"

**Problema:** Template não está no lugar certo

**Solução:**
Verifique estrutura de pastas:
```
templates/
└── livros/
    ├── listar.html
    └── cadastrar.html
```

E no código:
```python
templates = criar_templates("templates/livros")  # Caminho correto
```

### 5. "ModuleNotFoundError"

**Problema:** Esqueceu de ativar ambiente virtual

**Solução:**
```bash
# Ative o ambiente
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale novamente
pip install -r requirements.txt
```

### 6. Senha não funciona

**Problema:** Senhas são case-sensitive!

**Solução:** Use exatamente como documentado:
- `Admin@123` (não `admin@123`)
- `Joao@123` (não `joao@123`)

### 7. "Operational Error: no such table"

**Problema:** Tabela não foi criada

**Solução:**
1. Verifique se chamou `criar_tabela()` no `main.py`
2. Pare e reinicie o servidor
3. Ou delete o arquivo `database.db` e reinicie

### 8. Flash messages não aparecem

**Problema:** Esqueceu de incluir no template

**Solução:** Seu template deve usar `{% extends "base.html" %}`

---

## Próximos Passos

### Iniciante

1. ✅ Complete o CRUD de Livros
2. ✅ Adicione campo "descrição" aos livros
3. ✅ Adicione botão de "Alterar" (além de Excluir)
4. ✅ Crie página de confirmação antes de excluir
5. ✅ Adicione validação: ano não pode ser maior que 2024

### Intermediário

1. ✅ Adicione busca por título
2. ✅ Adicione paginação (10 livros por página)
3. ✅ Adicione campo de upload de capa
4. ✅ Crie relacionamento: livro pertence a categoria
5. ✅ Adicione ordenação (por título, autor, ano)

### Avançado

1. ✅ Crie API REST para livros
2. ✅ Adicione testes automatizados
3. ✅ Implemente sistema de avaliações (1-5 estrelas)
4. ✅ Adicione empréstimos de livros
5. ✅ Crie relatório de livros mais populares

---

## Recursos de Aprendizado

### Documentação Oficial

- **FastAPI**: https://fastapi.tiangolo.com/
- **Jinja2**: https://jinja.palletsprojects.com/
- **Bootstrap**: https://getbootstrap.com/docs/5.3/
- **Python**: https://docs.python.org/3/

### Tutoriais Recomendados

- FastAPI Tutorial (oficial)
- Python para Iniciantes (python.org)
- Bootstrap 5 Crash Course (YouTube)

### Ferramentas Úteis

- **DB Browser for SQLite** → Visualizar banco de dados
  - Download: https://sqlitebrowser.org/
- **Postman** → Testar APIs
  - Download: https://www.postman.com/
- **Git** → Controle de versão
  - Download: https://git-scm.com/

---

## Comandos Úteis

### Executar aplicação
```bash
python main.py
```

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Executar testes
```bash
pytest
```

### Ver banco de dados
```bash
sqlite3 database.db
.tables
SELECT * FROM livro;
.quit
```

### Limpar cache Python
```bash
# Windows
rmdir /s /q __pycache__

# Linux/Mac
find . -type d -name __pycache__ -exec rm -r {} +
```

### Atualizar dependência
```bash
pip install --upgrade fastapi
```

### Ver logs em tempo real
```bash
# Windows
type logs\app.log

# Linux/Mac
tail -f logs/app.log
```

---

## Glossário

**API** - Interface de Programação de Aplicações

**CRUD** - Create, Read, Update, Delete (operações básicas)

**DTO** - Data Transfer Object (objeto de transferência de dados)

**Endpoint** - URL que responde a uma requisição

**Model** - Representação de uma entidade do sistema

**Repository** - Camada que acessa o banco de dados

**Route** - Caminho/URL da aplicação

**Template** - Arquivo HTML com lógica

**Virtual Environment** - Ambiente isolado para Python

---

## Ajuda e Suporte

### Durante as Aulas

- Pergunte ao instrutor
- Discuta com os colegas
- Consulte a documentação

### Fora das Aulas

- Releia esta documentação
- Consulte os exemplos no código
- Pesquise o erro no Google
- Verifique a documentação oficial

---

## Checklist do Iniciante

Antes de começar seu projeto, certifique-se:

- [ ] Python 3.10+ instalado
- [ ] VS Code instalado e configurado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Aplicação rodando em `localhost:8000`
- [ ] Conseguiu fazer login
- [ ] Explorou o CRUD de Tarefas
- [ ] Criou seu primeiro CRUD (Livros)
- [ ] Leu a documentação de CRUD
- [ ] Entendeu a estrutura de pastas

---

**Parabéns por chegar até aqui! 🎉**

Agora você tem tudo para criar aplicações web incríveis com FastAPI!

Bons estudos e bom código! 💻✨

---

**Dúvidas?** Entre em contato com seu instrutor ou consulte a documentação completa.
