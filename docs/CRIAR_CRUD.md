# Tutorial: Como Criar um CRUD Completo

Este guia mostra passo a passo como criar um CRUD completo seguindo os padrões do boilerplate DefaultWebApp.

## Sumário
1. [Visão Geral](#visão-geral)
2. [Passo 1: Criar o Model](#passo-1-criar-o-model)
3. [Passo 2: Criar os Comandos SQL](#passo-2-criar-os-comandos-sql)
4. [Passo 3: Criar o Repositório](#passo-3-criar-o-repositório)
5. [Passo 4: Criar DTOs de Validação](#passo-4-criar-dtos-de-validação)
6. [Passo 5: Criar as Rotas](#passo-5-criar-as-rotas)
7. [Passo 6: Criar Templates](#passo-6-criar-templates)
8. [Passo 7: Registrar no main.py](#passo-7-registrar-no-mainpy)
9. [Passo 8: Testar](#passo-8-testar)
10. [Exemplo Completo](#exemplo-completo)

---

## Visão Geral

Neste tutorial, vamos criar um CRUD de **Produtos** como exemplo. A estrutura será:

```
model/produto_model.py          → Define a entidade Produto
sql/produto_sql.py              → Comandos SQL
repo/produto_repo.py            → Operações no banco
dtos/produto_dto.py             → Validação de dados
routes/produtos_routes.py       → Rotas HTTP
templates/produtos/             → Interface HTML
```

---

## Passo 1: Criar o Model

**Arquivo**: `model/produto_model.py`

O model é uma dataclass que representa a entidade no sistema.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Produto:
    """Modelo de produto"""
    id: int
    nome: str
    descricao: str
    preco: float
    estoque: int
    ativo: bool = True
    data_cadastro: Optional[str] = None
```

### Boas Práticas
- Use `@dataclass` para menos código boilerplate
- Use type hints para clareza
- Use `Optional` para campos que podem ser None
- Adicione valores padrão quando apropriado
- Documente a classe

---

## Passo 2: Criar os Comandos SQL

**Arquivo**: `sql/produto_sql.py`

Todos os comandos SQL ficam isolados neste arquivo.

```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS produto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL NOT NULL,
    estoque INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO produto (nome, descricao, preco, estoque, ativo)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT * FROM produto
ORDER BY nome
"""

OBTER_ATIVOS = """
SELECT * FROM produto
WHERE ativo = 1
ORDER BY nome
"""

OBTER_POR_ID = """
SELECT * FROM produto
WHERE id = ?
"""

ATUALIZAR = """
UPDATE produto
SET nome = ?, descricao = ?, preco = ?, estoque = ?, ativo = ?
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM produto
WHERE id = ?
"""

DESATIVAR = """
UPDATE produto
SET ativo = 0
WHERE id = ?
"""

BUSCAR_POR_NOME = """
SELECT * FROM produto
WHERE nome LIKE ?
ORDER BY nome
"""
```

### Boas Práticas
- Use nomes de constantes em MAIÚSCULAS
- Use `?` para parâmetros (prepared statements)
- Nunca concatene strings SQL (evita SQL injection)
- Organize queries por funcionalidade
- Adicione índices se necessário

---

## Passo 3: Criar o Repositório

**Arquivo**: `repo/produto_repo.py`

O repositório encapsula todas as operações de banco de dados.

```python
from typing import Optional, List
from model.produto_model import Produto
from sql.produto_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    """Cria a tabela de produtos se não existir"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(produto: Produto) -> Optional[int]:
    """
    Insere um novo produto no banco
    Retorna: ID do produto inserido ou None
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            produto.nome,
            produto.descricao,
            produto.preco,
            produto.estoque,
            1 if produto.ativo else 0
        ))
        return cursor.lastrowid

def obter_todos() -> List[Produto]:
    """Retorna todos os produtos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_produto(row) for row in rows]

def obter_ativos() -> List[Produto]:
    """Retorna apenas produtos ativos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ATIVOS)
        rows = cursor.fetchall()
        return [_row_to_produto(row) for row in rows]

def obter_por_id(id: int) -> Optional[Produto]:
    """
    Busca produto por ID
    Retorna: Produto ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_produto(row) if row else None

def atualizar(produto: Produto) -> bool:
    """
    Atualiza dados do produto
    Retorna: True se atualizou, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            produto.nome,
            produto.descricao,
            produto.preco,
            produto.estoque,
            1 if produto.ativo else 0,
            produto.id
        ))
        return cursor.rowcount > 0

def excluir(id: int) -> bool:
    """
    Exclui produto do banco
    Retorna: True se excluiu, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0

def desativar(id: int) -> bool:
    """
    Desativa produto (soft delete)
    Retorna: True se desativou, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(DESATIVAR, (id,))
        return cursor.rowcount > 0

def buscar_por_nome(termo: str) -> List[Produto]:
    """Busca produtos por nome (parcial)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(BUSCAR_POR_NOME, (f"%{termo}%",))
        rows = cursor.fetchall()
        return [_row_to_produto(row) for row in rows]

def _row_to_produto(row) -> Produto:
    """Converte row do banco para objeto Produto"""
    return Produto(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        preco=row["preco"],
        estoque=row["estoque"],
        ativo=bool(row["ativo"]),
        data_cadastro=row["data_cadastro"]
    )
```

### Boas Práticas
- Use `with get_connection()` para garantir fechamento da conexão
- Documente funções com docstrings
- Use type hints para clareza
- Retorne tipos apropriados (Optional, List, bool, etc.)
- Crie função auxiliar `_row_to_*` para conversão
- Use nomes descritivos

---

## Passo 4: Criar DTOs de Validação

**Arquivo**: `dtos/produto_dto.py`

DTOs validam dados de entrada usando Pydantic.

```python
from pydantic import BaseModel, Field, field_validator

class CriarProdutoDTO(BaseModel):
    """DTO para criação de produto"""
    nome: str = Field(..., tamanho_minimo=3, tamanho_maximo=100)
    descricao: str = Field(default="", tamanho_maximo=500)
    preco: float = Field(..., gt=0)
    estoque: int = Field(default=0, ge=0)

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v: str) -> str:
        """Valida e limpa o nome do produto"""
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()

    @field_validator('preco')
    @classmethod
    def validar_preco(cls, v: float) -> float:
        """Valida o preço do produto"""
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        if v > 999999.99:
            raise ValueError('Preço muito alto')
        # Arredondar para 2 casas decimais
        return round(v, 2)

    @field_validator('estoque')
    @classmethod
    def validar_estoque(cls, v: int) -> int:
        """Valida o estoque"""
        if v < 0:
            raise ValueError('Estoque não pode ser negativo')
        return v

class AlterarProdutoDTO(BaseModel):
    """DTO para alteração de produto"""
    id: int = Field(..., gt=0)
    nome: str = Field(..., tamanho_minimo=3, tamanho_maximo=100)
    descricao: str = Field(default="", tamanho_maximo=500)
    preco: float = Field(..., gt=0)
    estoque: int = Field(default=0, ge=0)
    ativo: bool = True

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()

    @field_validator('preco')
    @classmethod
    def validar_preco(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Preço deve ser maior que zero')
        if v > 999999.99:
            raise ValueError('Preço muito alto')
        return round(v, 2)
```

### Boas Práticas
- Use `Field()` para definir constraints
- Use `field_validator` para validações customizadas
- Separe DTOs de criação e alteração
- Retorne mensagens de erro claras
- Limpe dados (trim, lowercase, etc.)

---

## Passo 5: Criar as Rotas

**Arquivo**: `routes/produtos_routes.py`

As rotas gerenciam requisições HTTP.

```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.produto_dto import CriarProdutoDTO, AlterarProdutoDTO
from model.produto_model import Produto
from repo import produto_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil

router = APIRouter(prefix="/produtos")
templates = criar_templates("templates/produtos")

@router.get("/")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: dict = None):
    """Lista todos os produtos"""
    produtos = produto_repo.obter_todos()
    return templates.TemplateResponse(
        "listar.html",
        {"request": request, "produtos": produtos}
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: dict = None):
    """Exibe formulário de cadastro de produto"""
    return templates.TemplateResponse("cadastrar.html", {"request": request})

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(""),
    preco: float = Form(...),
    estoque: int = Form(0),
    usuario_logado: dict = None
):
    """Cadastra um novo produto"""
    try:
        # Validar com DTO
        dto = CriarProdutoDTO(
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque
        )

        # Criar produto
        produto = Produto(
            id=0,
            nome=dto.nome,
            descricao=dto.descricao,
            preco=dto.preco,
            estoque=dto.estoque,
            ativo=True
        )

        produto_id = produto_repo.inserir(produto)
        logger.info(f"Produto '{dto.nome}' cadastrado por usuário {usuario_logado['id']}")

        informar_sucesso(request, f"Produto '{dto.nome}' cadastrado com sucesso!")
        return RedirectResponse("/produtos", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        return templates.TemplateResponse(
            "cadastrar.html",
            {
                "request": request,
                "dados": {
                    "nome": nome,
                    "descricao": descricao,
                    "preco": preco,
                    "estoque": estoque
                }
            }
        )

@router.get("/{id}/alterar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_alterar(request: Request, id: int, usuario_logado: dict = None):
    """Exibe formulário de alteração de produto"""
    produto = produto_repo.obter_por_id(id)

    if not produto:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/produtos", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "alterar.html",
        {"request": request, "produto": produto}
    )

@router.post("/{id}/alterar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_alterar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(""),
    preco: float = Form(...),
    estoque: int = Form(0),
    ativo: bool = Form(True),
    usuario_logado: dict = None
):
    """Altera dados do produto"""
    try:
        # Validar com DTO
        dto = AlterarProdutoDTO(
            id=id,
            nome=nome,
            descricao=descricao,
            preco=preco,
            estoque=estoque,
            ativo=ativo
        )

        # Atualizar produto
        produto = Produto(
            id=dto.id,
            nome=dto.nome,
            descricao=dto.descricao,
            preco=dto.preco,
            estoque=dto.estoque,
            ativo=dto.ativo
        )

        if produto_repo.atualizar(produto):
            logger.info(f"Produto {id} alterado por usuário {usuario_logado['id']}")
            informar_sucesso(request, "Produto alterado com sucesso!")
        else:
            informar_erro(request, "Erro ao alterar produto")

        return RedirectResponse("/produtos", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        produto = produto_repo.obter_por_id(id)
        return templates.TemplateResponse(
            "alterar.html",
            {"request": request, "produto": produto}
        )

@router.get("/{id}/excluir")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_excluir(request: Request, id: int, usuario_logado: dict = None):
    """Exibe confirmação de exclusão"""
    produto = produto_repo.obter_por_id(id)

    if not produto:
        informar_erro(request, "Produto não encontrado")
        return RedirectResponse("/produtos", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "excluir.html",
        {"request": request, "produto": produto}
    )

@router.post("/{id}/excluir")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: dict = None):
    """Exclui produto"""
    produto = produto_repo.obter_por_id(id)

    if produto:
        if produto_repo.excluir(id):
            logger.info(f"Produto {id} excluído por usuário {usuario_logado['id']}")
            informar_sucesso(request, "Produto excluído com sucesso!")
        else:
            informar_erro(request, "Erro ao excluir produto")
    else:
        informar_erro(request, "Produto não encontrado")

    return RedirectResponse("/produtos", status_code=status.HTTP_303_SEE_OTHER)
```

### Boas Práticas
- Use prefixo no router (`/produtos`)
- Separe GET e POST
- Use `@requer_autenticacao()` para proteção
- Valide com DTOs
- Use flash messages para feedback
- Use logger para auditoria
- Retorne redirect após POST (PRG pattern)

---

## Passo 6: Criar Templates

**Pasta**: `templates/produtos/`

### 6.1 - listar.html

```html
{% extends "base.html" %}

{% block title %}Produtos{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Produtos</h1>
        <a href="/produtos/cadastrar" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Novo Produto
        </a>
    </div>

    {% if produtos %}
    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>Descrição</th>
                    <th>Preço</th>
                    <th>Estoque</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for produto in produtos %}
                <tr>
                    <td>{{ produto.id }}</td>
                    <td>{{ produto.nome }}</td>
                    <td>{{ produto.descricao }}</td>
                    <td>R$ {{ "%.2f"|format(produto.preco) }}</td>
                    <td>{{ produto.estoque }}</td>
                    <td>
                        {% if produto.ativo %}
                        <span class="badge bg-success">Ativo</span>
                        {% else %}
                        <span class="badge bg-secondary">Inativo</span>
                        {% endif %}
                    </td>
                    <td>
                        <a href="/produtos/{{ produto.id }}/alterar"
                           class="btn btn-sm btn-warning">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <a href="/produtos/{{ produto.id }}/excluir"
                           class="btn btn-sm btn-danger">
                            <i class="bi bi-trash"></i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="alert alert-info">
        Nenhum produto cadastrado.
    </div>
    {% endif %}
</div>
{% endblock %}
```

### 6.2 - cadastrar.html

```html
{% extends "base.html" %}

{% block title %}Cadastrar Produto{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Cadastrar Produto</h1>

    <form method="POST" action="/produtos/cadastrar" class="mt-4">
        <div class="mb-3">
            <label for="nome" class="form-label">Nome *</label>
            <input type="text" class="form-control" id="nome" name="nome"
                   value="{{ dados.nome if dados else '' }}" required>
        </div>

        <div class="mb-3">
            <label for="descricao" class="form-label">Descrição</label>
            <textarea class="form-control" id="descricao" name="descricao"
                      rows="3">{{ dados.descricao if dados else '' }}</textarea>
        </div>

        <div class="row">
            <div class="col-md-6 mb-3">
                <label for="preco" class="form-label">Preço *</label>
                <input type="number" step="0.01" class="form-control" id="preco"
                       name="preco" value="{{ dados.preco if dados else '' }}" required>
            </div>

            <div class="col-md-6 mb-3">
                <label for="estoque" class="form-label">Estoque</label>
                <input type="number" class="form-control" id="estoque" name="estoque"
                       value="{{ dados.estoque if dados else 0 }}">
            </div>
        </div>

        <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary">Cadastrar</button>
            <a href="/produtos" class="btn btn-secondary">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

### 6.3 - alterar.html

Similar ao cadastrar.html, mas com valores preenchidos.

### 6.4 - excluir.html

```html
{% extends "base.html" %}

{% block title %}Excluir Produto{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1>Excluir Produto</h1>

    <div class="alert alert-danger mt-4">
        <h5>Tem certeza que deseja excluir este produto?</h5>
        <p class="mb-0">Esta ação não pode ser desfeita.</p>
    </div>

    <div class="card">
        <div class="card-body">
            <p><strong>Nome:</strong> {{ produto.nome }}</p>
            <p><strong>Descrição:</strong> {{ produto.descricao }}</p>
            <p><strong>Preço:</strong> R$ {{ "%.2f"|format(produto.preco) }}</p>
            <p><strong>Estoque:</strong> {{ produto.estoque }}</p>
        </div>
    </div>

    <form method="POST" action="/produtos/{{ produto.id }}/excluir" class="mt-4">
        <div class="d-flex gap-2">
            <button type="submit" class="btn btn-danger">Sim, excluir</button>
            <a href="/produtos" class="btn btn-secondary">Cancelar</a>
        </div>
    </form>
</div>
{% endblock %}
```

---

## Passo 7: Registrar no main.py

**Arquivo**: `main.py`

Adicione as importações e registre o router:

```python
# Importar repositório
from repo import produto_repo

# Importar router
from routes.produtos_routes import router as produtos_router

# Criar tabela (após outras tabelas)
produto_repo.criar_tabela()
logger.info("Tabela 'produto' criada/verificada")

# Incluir router (após outros routers)
app.include_router(produtos_router, tags=["Produtos"])
logger.info("Router de produtos incluído")
```

---

## Passo 8: Testar

### 8.1 - Executar aplicação
```bash
python main.py
```

### 8.2 - Testar funcionalidades
1. Acesse `http://localhost:8000/produtos`
2. Teste cadastro de produto
3. Teste alteração
4. Teste exclusão
5. Teste validações (dados inválidos)
6. Verifique logs em `logs/app.log`

### 8.3 - Verificar banco de dados
```bash
sqlite3 database.db
.tables
SELECT * FROM produto;
```

---

## Exemplo Completo

Para um exemplo completo funcionando, veja o CRUD de **Tarefas** incluído no projeto:

- `model/tarefa_model.py`
- `sql/tarefa_sql.py`
- `repo/tarefa_repo.py`
- `dtos/tarefa_dto.py`
- `routes/tarefas_routes.py`
- `templates/tarefas/`

---

## Checklist Final

- [ ] Model criado com dataclass e type hints
- [ ] Comandos SQL isolados em arquivo próprio
- [ ] Repositório com todas as operações CRUD
- [ ] DTOs para validação de entrada
- [ ] Rotas GET e POST implementadas
- [ ] Templates HTML criados
- [ ] Registrado no main.py
- [ ] Tabela criada no banco
- [ ] Logs funcionando
- [ ] Flash messages exibindo
- [ ] Autenticação funcionando
- [ ] Testado manualmente

---

## Próximos Passos

Após criar o CRUD básico, você pode adicionar:

- Busca e filtros
- Paginação
- Ordenação
- Relacionamentos com outras entidades
- Upload de imagens
- Exportação (CSV, PDF)
- API REST endpoints
- Testes automatizados

---

## Dicas e Truques

### Atalhos
- Copie um CRUD existente e adapte
- Use replace all para trocar nomes
- Mantenha consistência nos nomes

### Debugging
- Use `print()` temporariamente
- Verifique logs em `logs/app.log`
- Use `logger.debug()` para detalhes
- Teste queries SQL no sqlite3 diretamente

### Performance
- Adicione índices em colunas buscadas
- Use lazy loading quando apropriado
- Cache resultados quando possível

---

**Dúvidas?** Consulte o código de exemplo ou entre em contato com o instrutor.
