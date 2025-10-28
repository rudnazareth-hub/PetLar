# Fase 2 - Implementação das Rotas Administrativas do PetLar

**Data**: 2025-10-22
**Status**: Planejamento
**Referência**: docs/PetLar.pdf - Capítulo 2 (Análise e Projeto)

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Padrões do Projeto](#padrões-do-projeto)
- [Seção 1: Gerenciar Espécies](#1-gerenciar-espécies)
- [Seção 2: Gerenciar Raças](#2-gerenciar-raças)
- [Seção 3: Gerenciar Abrigos](#3-gerenciar-abrigos)
- [Seção 4: Gerenciar Animais](#4-gerenciar-animais)
- [Seção 5: Gerenciar Adotantes](#5-gerenciar-adotantes)
- [Seção 6: Gerenciar Solicitações](#6-gerenciar-solicitações)
- [Seção 7: Gerenciar Visitas](#7-gerenciar-visitas)
- [Seção 8: Dashboard Administrativo](#8-dashboard-administrativo)
- [Validadores Adicionais](#validadores-adicionais)

---

## Visão Geral

Esta fase implementa todas as rotas administrativas necessárias para o perfil **Administrador** gerenciar completamente a aplicação PetLar, conforme especificado no diagrama de casos de uso (PDF página 24).

**Funcionalidades a Implementar:**
- ✅ Gerenciar espécies e raças de animais
- ✅ Gerenciar abrigos/instituições
- ✅ Gerenciar animais cadastrados
- ✅ Gerenciar adotantes
- ✅ Gerenciar solicitações de adoção
- ✅ Gerenciar visitas agendadas
- ✅ Dashboard com visão geral do sistema
- ✅ Relatórios gerenciais

---

## Padrões do Projeto

### Estrutura de Arquivos
```
routes/
  ├── admin_{modulo}_routes.py    # Rotas administrativas
dtos/
  ├── {entidade}_dto.py           # DTOs com validadores Pydantic
templates/
  └── admin/
      └── {modulo}/
          ├── listar.html
          ├── cadastro.html
          └── editar.html
```

### Nomenclatura de Rotas
- **Prefixo**: `/admin/{modulo}`
- **Listar**: `GET /admin/{modulo}/listar`
- **Cadastrar Form**: `GET /admin/{modulo}/cadastrar`
- **Cadastrar Action**: `POST /admin/{modulo}/cadastrar`
- **Editar Form**: `GET /admin/{modulo}/editar/{id}`
- **Editar Action**: `POST /admin/{modulo}/editar/{id}`
- **Excluir**: `POST /admin/{modulo}/excluir/{id}`
- **Visualizar**: `GET /admin/{modulo}/visualizar/{id}`

### Padrões de Código

#### DTOs (Pydantic)
```python
from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_id_positivo

class CadastrarEntityDTO(BaseModel):
    campo: str

    _validar_campo = field_validator('campo')(validar_string_obrigatoria('Campo'))
```

#### Rotas (FastAPI)
```python
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/modulo")

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    # Implementação
```

#### Templates (Jinja2)
```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Título{% endblock %}

{% block content %}
<!-- Conteúdo -->
{% endblock %}
```

#### Rate Limiting
```python
admin_modulo_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_modulo"
)
```

#### Flash Messages
```python
informar_sucesso(request, "Operação realizada com sucesso!")
informar_erro(request, "Erro ao realizar operação.")
```

#### Logging
```python
logger.info(f"Operação realizada por admin {usuario_logado['id']}")
logger.warning(f"Tentativa de operação inválida por admin {usuario_logado['id']}")
logger.error(f"Erro na operação: {e}")
```

### Componentes Reutilizáveis

#### Macros de Formulário
- **field()**: Campo de formulário com validação
- Tipos suportados: text, email, password, select, textarea, radio, checkbox, date, decimal

#### Componentes de Template
- **modal_confirmacao.html**: Modal para confirmar ações destrutivas
- **alerta_erro.html**: Exibição de erros de validação

#### Funções JavaScript
- **abrirModalConfirmacao()**: Abre modal de confirmação
- **PasswordValidator**: Validação de senhas no frontend

---

## 1. Gerenciar Espécies

Permite ao administrador cadastrar, listar, editar e excluir espécies de animais (Cão, Gato, etc.).

### 1.1. Listar Espécies

#### 1.1.1. Rota GET

**Arquivo**: `routes/admin_especies_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import especie_repo

router = APIRouter(prefix="/admin/especies")
templates = criar_templates("templates/admin/especies")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de espécies"""
    return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as espécies cadastradas"""
    especies = especie_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {"request": request, "especies": especies}
    )
```

#### 1.1.2. Template

**Arquivo**: `templates/admin/especies/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Espécies{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-tag"></i> Gerenciar Espécies</h2>
            <a href="/admin/especies/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Nova Espécie
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if especies %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Nome</th>
                                <th scope="col">Descrição</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for especie in especies %}
                            <tr>
                                <td>{{ especie.id_especie }}</td>
                                <td><strong>{{ especie.nome }}</strong></td>
                                <td>{{ especie.descricao or '-' }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/especies/editar/{{ especie.id_especie }}"
                                            class="btn btn-outline-primary"
                                            title="Editar"
                                            aria-label="Editar espécie {{ especie.nome }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            aria-label="Excluir espécie {{ especie.nome }}"
                                            onclick="excluirEspecie({{ especie.id_especie }}, '{{ especie.nome|replace("'", "\\'") }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhuma espécie cadastrada.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function excluirEspecie(especieId, especieNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <p class="mb-0"><strong>Espécie:</strong> ${especieNome}</p>
                <p class="text-warning mt-2 mb-0">
                    <i class="bi bi-exclamation-triangle"></i>
                    <small>Todas as raças vinculadas a esta espécie também serão afetadas.</small>
                </p>
            </div>
        </div>
        `;

        abrirModalConfirmacao({
            url: `/admin/especies/excluir/${especieId}`,
            mensagem: 'Tem certeza que deseja excluir esta espécie?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

### 1.2. Cadastrar Espécie

#### 1.2.1. DTO

**Arquivo**: `dtos/especie_dto.py`

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_string_obrigatoria,
    validar_texto_longo_opcional,
    validar_id_positivo
)

class CadastrarEspecieDTO(BaseModel):
    """DTO para cadastro de espécie"""
    nome: str
    descricao: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_texto_longo_opcional(tamanho_maximo=200)
    )

class AlterarEspecieDTO(BaseModel):
    """DTO para alteração de espécie"""
    id_especie: int
    nome: str
    descricao: Optional[str] = None

    _validar_id = field_validator('id_especie')(validar_id_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_texto_longo_opcional(tamanho_maximo=200)
    )
```

#### 1.2.2. Rota GET

**Arquivo**: `routes/admin_especies_routes.py` (adicionar)

```python
@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de espécie"""
    return templates.TemplateResponse(
        "admin/especies/cadastro.html",
        {"request": request}
    )
```

#### 1.2.3. Template

**Arquivo**: `templates/admin/especies/cadastro.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar Espécie{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-tag-fill"></i> Cadastrar Nova Espécie</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/especies/cadastrar">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='nome', label='Nome da Espécie', type='text', required=true,
                            help_text='Ex: Cão, Gato, Pássaro') }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='descricao', label='Descrição', type='textarea', rows=3,
                            help_text='Descrição opcional sobre a espécie') }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/admin/especies/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

#### 1.2.4. Rota POST

**Arquivo**: `routes/admin_especies_routes.py` (adicionar)

```python
from fastapi import Form
from pydantic import ValidationError
from dtos.especie_dto import CadastrarEspecieDTO
from model.especie_model import Especie
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# Rate limiter
admin_especies_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_especies"
)

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Cadastra uma nova espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {"nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CadastrarEspecieDTO(nome=nome, descricao=descricao)

        # Criar espécie
        especie = Especie(
            id_especie=0,
            nome=dto.nome,
            descricao=dto.descricao
        )

        especie_repo.inserir(especie)
        logger.info(f"Espécie '{dto.nome}' cadastrada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Espécie cadastrada com sucesso!")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )
```

### 1.3. Editar Espécie

#### 1.3.1. Rota GET

**Arquivo**: `routes/admin_especies_routes.py` (adicionar)

```python
@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de espécie"""
    especie = especie_repo.obter_por_id(id)

    if not especie:
        informar_erro(request, "Espécie não encontrada")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/especies/editar.html",
        {
            "request": request,
            "especie": especie,
            "dados": especie.__dict__
        }
    )
```

#### 1.3.2. Template

**Arquivo**: `templates/admin/especies/editar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar Espécie{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-pencil-square"></i> Editar Espécie</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/especies/editar/{{ dados.id_especie }}">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='nome', label='Nome da Espécie', type='text', required=true,
                            value=dados.nome) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='descricao', label='Descrição', type='textarea', rows=3,
                            value=dados.descricao) }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Salvar Alterações
                        </button>
                        <a href="/admin/especies/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

#### 1.3.3. Rota POST

**Arquivo**: `routes/admin_especies_routes.py` (adicionar)

```python
@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de uma espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se espécie existe
    especie_atual = especie_repo.obter_por_id(id)
    if not especie_atual:
        informar_erro(request, "Espécie não encontrada")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {"id_especie": id, "nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = AlterarEspecieDTO(id_especie=id, nome=nome, descricao=descricao)

        # Atualizar espécie
        especie_atualizada = Especie(
            id_especie=id,
            nome=dto.nome,
            descricao=dto.descricao
        )

        especie_repo.alterar(especie_atualizada)
        logger.info(f"Espécie {id} alterada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Espécie alterada com sucesso!")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        dados_formulario["especie"] = especie_atual
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )
```

### 1.4. Excluir Espécie

#### 1.4.1. Rota POST

**Arquivo**: `routes/admin_especies_routes.py` (adicionar)

```python
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui uma espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    especie = especie_repo.obter_por_id(id)

    if not especie:
        informar_erro(request, "Espécie não encontrada")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se existem raças vinculadas
    racas_vinculadas = raca_repo.obter_por_especie(id)
    if racas_vinculadas:
        informar_erro(
            request,
            f"Não é possível excluir esta espécie pois existem {len(racas_vinculadas)} raça(s) vinculada(s) a ela."
        )
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    especie_repo.excluir(id)
    logger.info(f"Espécie {id} ({especie.nome}) excluída por admin {usuario_logado['id']}")
    informar_sucesso(request, "Espécie excluída com sucesso!")
    return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)
```

---

## 2. Gerenciar Raças

Permite ao administrador cadastrar, listar, editar e excluir raças de animais vinculadas a espécies.

### 2.1. Listar Raças

#### 2.1.1. Rota GET

**Arquivo**: `routes/admin_racas_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import raca_repo, especie_repo

router = APIRouter(prefix="/admin/racas")
templates = criar_templates("templates/admin/racas")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de raças"""
    return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as raças cadastradas com suas espécies"""
    racas = raca_repo.obter_todos_com_especies()
    return templates.TemplateResponse(
        "admin/racas/listar.html",
        {"request": request, "racas": racas}
    )
```

#### 2.1.2. Template

**Arquivo**: `templates/admin/racas/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Raças{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-tags"></i> Gerenciar Raças</h2>
            <a href="/admin/racas/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Nova Raça
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if racas %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Espécie</th>
                                <th scope="col">Raça</th>
                                <th scope="col">Descrição</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for raca in racas %}
                            <tr>
                                <td>{{ raca.id_raca }}</td>
                                <td>
                                    <span class="badge bg-secondary">
                                        {{ raca.especie.nome if raca.especie else '-' }}
                                    </span>
                                </td>
                                <td><strong>{{ raca.nome }}</strong></td>
                                <td>{{ raca.descricao or '-' }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/racas/editar/{{ raca.id_raca }}"
                                            class="btn btn-outline-primary"
                                            title="Editar"
                                            aria-label="Editar raça {{ raca.nome }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            aria-label="Excluir raça {{ raca.nome }}"
                                            onclick="excluirRaca({{ raca.id_raca }}, '{{ raca.nome|replace("'", "\\'") }}', '{{ raca.especie.nome if raca.especie else "N/A" }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhuma raça cadastrada.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function excluirRaca(racaId, racaNome, especieNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <table class="table table-sm table-borderless mb-0">
                    <tr>
                        <th scope="row" width="30%">Raça:</th>
                        <td>${racaNome}</td>
                    </tr>
                    <tr>
                        <th scope="row">Espécie:</th>
                        <td><span class="badge bg-secondary">${especieNome}</span></td>
                    </tr>
                </table>
                <p class="text-warning mt-2 mb-0">
                    <i class="bi bi-exclamation-triangle"></i>
                    <small>Animais cadastrados com esta raça também serão afetados.</small>
                </p>
            </div>
        </div>
        `;

        abrirModalConfirmacao({
            url: `/admin/racas/excluir/${racaId}`,
            mensagem: 'Tem certeza que deseja excluir esta raça?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

### 2.2. Cadastrar Raça

#### 2.2.1. DTO

**Arquivo**: `dtos/raca_dto.py` (complementar se necessário)

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_string_obrigatoria,
    validar_texto_longo_opcional,
    validar_id_positivo
)

class CadastrarRacaDTO(BaseModel):
    """DTO para cadastro de raça"""
    nome: str
    id_especie: int
    descricao: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_id_especie = field_validator('id_especie')(validar_id_positivo())
    _validar_descricao = field_validator('descricao')(
        validar_texto_longo_opcional(tamanho_maximo=200)
    )

class AlterarRacaDTO(BaseModel):
    """DTO para alteração de raça"""
    id_raca: int
    nome: str
    id_especie: int
    descricao: Optional[str] = None

    _validar_id = field_validator('id_raca')(validar_id_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_id_especie = field_validator('id_especie')(validar_id_positivo())
    _validar_descricao = field_validator('descricao')(
        validar_texto_longo_opcional(tamanho_maximo=200)
    )
```

#### 2.2.2. Rota GET

**Arquivo**: `routes/admin_racas_routes.py` (adicionar)

```python
@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de raça"""
    # Obter todas as espécies para o select
    especies = especie_repo.obter_todos()

    # Converter para dict para o select
    especies_dict = {str(e.id_especie): e.nome for e in especies}

    return templates.TemplateResponse(
        "admin/racas/cadastro.html",
        {
            "request": request,
            "especies": especies_dict
        }
    )
```

#### 2.2.3. Template

**Arquivo**: `templates/admin/racas/cadastro.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar Raça{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-tags-fill"></i> Cadastrar Nova Raça</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/racas/cadastrar">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='id_especie', label='Espécie', type='select', required=true,
                            options=especies, help_text='Selecione a espécie desta raça') }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='nome', label='Nome da Raça', type='text', required=true,
                            help_text='Ex: Labrador, Siamês, Periquito') }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='descricao', label='Descrição', type='textarea', rows=3,
                            help_text='Descrição opcional sobre a raça') }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/admin/racas/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

#### 2.2.4. Rota POST

**Arquivo**: `routes/admin_racas_routes.py` (adicionar)

```python
from fastapi import Form
from pydantic import ValidationError
from dtos.raca_dto import CadastrarRacaDTO
from model.raca_model import Raca
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# Rate limiter
admin_racas_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_racas"
)

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    id_especie: int = Form(...),
    descricao: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Cadastra uma nova raça"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_racas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {"nome": nome, "id_especie": id_especie, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CadastrarRacaDTO(nome=nome, id_especie=id_especie, descricao=descricao)

        # Verificar se espécie existe
        especie = especie_repo.obter_por_id(dto.id_especie)
        if not especie:
            informar_erro(request, "Espécie não encontrada")
            return RedirectResponse("/admin/racas/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

        # Criar raça
        raca = Raca(
            id_raca=0,
            nome=dto.nome,
            id_especie=dto.id_especie,
            descricao=dto.descricao
        )

        raca_repo.inserir(raca)
        logger.info(f"Raça '{dto.nome}' cadastrada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Raça cadastrada com sucesso!")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Recarregar espécies para o select
        especies = especie_repo.obter_todos()
        dados_formulario["especies"] = {str(e.id_especie): e.nome for e in especies}

        raise FormValidationError(
            validation_error=e,
            template_path="admin/racas/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )
```

### 2.3. Editar e Excluir Raça

*Seguir mesmo padrão de Espécies, adaptando para raças*

---

## 3. Gerenciar Abrigos

Permite ao administrador cadastrar, listar, editar, visualizar e excluir abrigos/instituições.

### 3.1. Listar Abrigos

#### 3.1.1. Rota GET

**Arquivo**: `routes/admin_abrigos_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import abrigo_repo, usuario_repo

router = APIRouter(prefix="/admin/abrigos")
templates = criar_templates("templates/admin/abrigos")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de abrigos"""
    return RedirectResponse("/admin/abrigos/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os abrigos cadastrados"""
    abrigos = abrigo_repo.obter_todos_com_usuarios()
    return templates.TemplateResponse(
        "admin/abrigos/listar.html",
        {"request": request, "abrigos": abrigos}
    )
```

#### 3.1.2. Template

**Arquivo**: `templates/admin/abrigos/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Abrigos{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-building"></i> Gerenciar Abrigos</h2>
            <a href="/admin/abrigos/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Novo Abrigo
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if abrigos %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Responsável</th>
                                <th scope="col">Email</th>
                                <th scope="col">Data Abertura</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for abrigo in abrigos %}
                            <tr>
                                <td>{{ abrigo.id_abrigo }}</td>
                                <td><strong>{{ abrigo.responsavel }}</strong></td>
                                <td>{{ abrigo.usuario.email if abrigo.usuario else '-' }}</td>
                                <td>{{ abrigo.data_abertura|data_br if abrigo.data_abertura else '-' }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/abrigos/visualizar/{{ abrigo.id_abrigo }}"
                                            class="btn btn-outline-info"
                                            title="Visualizar"
                                            aria-label="Visualizar abrigo {{ abrigo.responsavel }}">
                                            <i class="bi bi-eye"></i>
                                        </a>
                                        <a href="/admin/abrigos/editar/{{ abrigo.id_abrigo }}"
                                            class="btn btn-outline-primary"
                                            title="Editar"
                                            aria-label="Editar abrigo {{ abrigo.responsavel }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            aria-label="Excluir abrigo {{ abrigo.responsavel }}"
                                            onclick="excluirAbrigo({{ abrigo.id_abrigo }}, '{{ abrigo.responsavel|replace("'", "\\'") }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhum abrigo cadastrado.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function excluirAbrigo(abrigoId, abrigoNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <p class="mb-0"><strong>Abrigo:</strong> ${abrigoNome}</p>
                <p class="text-warning mt-2 mb-0">
                    <i class="bi bi-exclamation-triangle"></i>
                    <small>O usuário associado e todos os animais vinculados a este abrigo também serão excluídos.</small>
                </p>
            </div>
        </div>
        `;

        abrirModalConfirmacao({
            url: `/admin/abrigos/excluir/${abrigoId}`,
            mensagem: 'Tem certeza que deseja excluir este abrigo?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

### 3.2. Cadastrar, Editar, Visualizar e Excluir Abrigo

*Seguir mesmo padrão de Espécies e Raças, criando DTOs apropriados*

**DTO Necessário**: `dtos/abrigo_dto.py` (CadastrarAbrigoDTO, AlterarAbrigoDTO)

**Campos do Formulário**:
- Responsável (text, required)
- Descrição (textarea, optional)
- Data de Abertura (date, optional)

**Visualização Detalhada** (GET `/admin/abrigos/visualizar/{id}`):
- Informações do abrigo
- Lista de animais cadastrados pelo abrigo
- Estatísticas (total de animais, adotados, disponíveis)

---

## 4. Gerenciar Animais

Permite ao administrador cadastrar, listar, editar, visualizar, alterar status e excluir animais.

### 4.1. Listar Animais

#### 4.1.1. Rota GET

**Arquivo**: `routes/admin_animais_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import animal_repo

router = APIRouter(prefix="/admin/animais")
templates = criar_templates("templates/admin/animais")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de animais"""
    return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os animais cadastrados"""
    animais = animal_repo.obter_todos_com_relacoes()
    return templates.TemplateResponse(
        "admin/animais/listar.html",
        {"request": request, "animais": animais}
    )
```

#### 4.1.2. Template

**Arquivo**: `templates/admin/animais/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Animais{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-heart"></i> Gerenciar Animais</h2>
            <a href="/admin/animais/cadastrar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Novo Animal
            </a>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if animais %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Foto</th>
                                <th scope="col">Nome</th>
                                <th scope="col">Raça</th>
                                <th scope="col">Abrigo</th>
                                <th scope="col">Status</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for animal in animais %}
                            <tr>
                                <td>{{ animal.id_animal }}</td>
                                <td>
                                    {% if animal.foto %}
                                    <img src="{{ animal.foto }}" alt="{{ animal.nome }}"
                                        class="rounded" style="width: 50px; height: 50px; object-fit: cover;">
                                    {% else %}
                                    <div class="bg-secondary rounded d-flex align-items-center justify-content-center"
                                        style="width: 50px; height: 50px;">
                                        <i class="bi bi-image text-white"></i>
                                    </div>
                                    {% endif %}
                                </td>
                                <td><strong>{{ animal.nome }}</strong></td>
                                <td>
                                    {{ animal.raca.nome if animal.raca else '-' }}
                                    <br>
                                    <small class="text-muted">
                                        {{ animal.raca.especie.nome if animal.raca and animal.raca.especie else '' }}
                                    </small>
                                </td>
                                <td>{{ animal.abrigo.responsavel if animal.abrigo else '-' }}</td>
                                <td>
                                    {% set status_map = {
                                        'Disponível': 'success',
                                        'Em Processo': 'warning',
                                        'Adotado': 'info',
                                        'Indisponível': 'secondary'
                                    } %}
                                    <span class="badge bg-{{ status_map.get(animal.status, 'secondary') }}">
                                        {{ animal.status }}
                                    </span>
                                </td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/animais/visualizar/{{ animal.id_animal }}"
                                            class="btn btn-outline-info"
                                            title="Visualizar">
                                            <i class="bi bi-eye"></i>
                                        </a>
                                        <a href="/admin/animais/editar/{{ animal.id_animal }}"
                                            class="btn btn-outline-primary"
                                            title="Editar">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            onclick="excluirAnimal({{ animal.id_animal }}, '{{ animal.nome|replace("'", "\\'") }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhum animal cadastrado.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function excluirAnimal(animalId, animalNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <p class="mb-0"><strong>Animal:</strong> ${animalNome}</p>
                <p class="text-warning mt-2 mb-0">
                    <i class="bi bi-exclamation-triangle"></i>
                    <small>Todas as solicitações de adoção relacionadas a este animal serão removidas.</small>
                </p>
            </div>
        </div>
        `;

        abrirModalConfirmacao({
            url: `/admin/animais/excluir/${animalId}`,
            mensagem: 'Tem certeza que deseja excluir este animal?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

### 4.2. Cadastrar Animal

#### 4.2.1. DTO

**Arquivo**: `dtos/animal_dto.py`

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_string_obrigatoria,
    validar_texto_longo_opcional,
    validar_id_positivo,
    validar_data_opcional,
    validar_sexo_animal,
    validar_status_animal
)

class CadastrarAnimalDTO(BaseModel):
    """DTO para cadastro de animal"""
    nome: str
    id_raca: int
    id_abrigo: int
    sexo: str
    data_nascimento: Optional[str] = None
    data_entrada: Optional[str] = None
    observacoes: Optional[str] = None
    status: str = "Disponível"

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_id_raca = field_validator('id_raca')(validar_id_positivo())
    _validar_id_abrigo = field_validator('id_abrigo')(validar_id_positivo())
    _validar_sexo = field_validator('sexo')(validar_sexo_animal())
    _validar_status = field_validator('status')(validar_status_animal())
    _validar_data_nascimento = field_validator('data_nascimento')(validar_data_opcional())
    _validar_data_entrada = field_validator('data_entrada')(validar_data_opcional())
    _validar_observacoes = field_validator('observacoes')(
        validar_texto_longo_opcional(tamanho_maximo=1000)
    )

class AlterarAnimalDTO(BaseModel):
    """DTO para alteração de animal"""
    id_animal: int
    nome: str
    id_raca: int
    id_abrigo: int
    sexo: str
    data_nascimento: Optional[str] = None
    data_entrada: Optional[str] = None
    observacoes: Optional[str] = None
    status: str

    _validar_id = field_validator('id_animal')(validar_id_positivo())
    # Mesmos validadores do CadastrarAnimalDTO

class AlterarStatusAnimalDTO(BaseModel):
    """DTO para alteração apenas do status do animal"""
    id_animal: int
    status: str

    _validar_id = field_validator('id_animal')(validar_id_positivo())
    _validar_status = field_validator('status')(validar_status_animal())
```

#### 4.2.2. Rota GET

**Arquivo**: `routes/admin_animais_routes.py` (adicionar)

```python
@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de animal"""
    # Obter raças e abrigos para os selects
    racas = raca_repo.obter_todos_com_especies()
    abrigos = abrigo_repo.obter_todos()

    # Converter para dict para os selects
    racas_dict = {str(r.id_raca): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}
    abrigos_dict = {str(a.id_abrigo): a.responsavel for a in abrigos}

    # Opções de sexo e status
    sexo_opcoes = {"Macho": "Macho", "Fêmea": "Fêmea"}
    status_opcoes = {
        "Disponível": "Disponível",
        "Em Processo": "Em Processo",
        "Adotado": "Adotado",
        "Indisponível": "Indisponível"
    }

    return templates.TemplateResponse(
        "admin/animais/cadastro.html",
        {
            "request": request,
            "racas": racas_dict,
            "abrigos": abrigos_dict,
            "sexo_opcoes": sexo_opcoes,
            "status_opcoes": status_opcoes
        }
    )
```

#### 4.2.3. Template

**Arquivo**: `templates/admin/animais/cadastro.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Cadastrar Animal{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-10">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-heart-fill"></i> Cadastrar Novo Animal</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/animais/cadastrar" enctype="multipart/form-data">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='nome', label='Nome do Animal', type='text', required=true) }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='sexo', label='Sexo', type='radio', required=true,
                            options=sexo_opcoes, radio_style='buttons', radio_layout='horizontal') }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='id_raca', label='Raça', type='select', required=true,
                            options=racas) }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='id_abrigo', label='Abrigo', type='select', required=true,
                            options=abrigos) }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='data_nascimento', label='Data de Nascimento', type='date') }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='data_entrada', label='Data de Entrada no Abrigo', type='date') }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='status', label='Status', type='select', required=true,
                            options=status_opcoes) }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='observacoes', label='Observações', type='textarea', rows=4,
                            help_text='Informações adicionais sobre o animal (saúde, temperamento, etc.)') }}
                        </div>

                        <div class="col-12 mb-3">
                            <label for="foto" class="form-label">Foto do Animal</label>
                            <input type="file" class="form-control" id="foto" name="foto" accept="image/*">
                            <div class="form-text">Formato: JPG, PNG. Tamanho máximo: 5MB</div>
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/admin/animais/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

#### 4.2.4. Rota POST

*Seguir padrão estabelecido, incluindo upload de foto*

### 4.3. Visualizar Animal

#### 4.3.1. Rota GET

**Arquivo**: `routes/admin_animais_routes.py` (adicionar)

```python
@router.get("/visualizar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos do animal"""
    animal = animal_repo.obter_por_id_com_relacoes(id)

    if not animal:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter solicitações de adoção relacionadas
    solicitacoes = solicitacao_repo.obter_por_animal(id)

    # Obter visitas agendadas
    visitas = visita_repo.obter_por_animal(id)

    return templates.TemplateResponse(
        "admin/animais/visualizar.html",
        {
            "request": request,
            "animal": animal,
            "solicitacoes": solicitacoes,
            "visitas": visitas
        }
    )
```

#### 4.3.2. Template

**Arquivo**: `templates/admin/animais/visualizar.html`

*Template completo com:*
- Foto e informações básicas
- Detalhes da raça e espécie
- Informações do abrigo
- Lista de solicitações de adoção
- Lista de visitas agendadas
- Histórico de status

### 4.4. Alterar Status

#### 4.4.1. Rota POST

**Arquivo**: `routes/admin_animais_routes.py` (adicionar)

```python
@router.post("/alterar-status/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_alterar_status(
    request: Request,
    id: int,
    status: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Altera apenas o status do animal"""
    # Implementação similar aos outros POSTs
```

---

## 5. Gerenciar Adotantes

Permite ao administrador listar, editar, visualizar e excluir adotantes cadastrados no sistema.

### 5.1. Listar Adotantes

#### 5.1.1. Rota GET

**Arquivo**: `routes/admin_adotantes_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import adotante_repo, usuario_repo

router = APIRouter(prefix="/admin/adotantes")
templates = criar_templates("templates/admin/adotantes")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de adotantes"""
    return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os adotantes cadastrados com seus dados de usuário"""
    # Obter todos os usuários com perfil ADOTANTE
    usuarios = usuario_repo.obter_todos()
    adotantes_completos = []

    for usuario in usuarios:
        if usuario.perfil == Perfil.ADOTANTE.value:
            adotante = adotante_repo.obter_por_id(usuario.id)
            if adotante:
                adotantes_completos.append({
                    'id_adotante': adotante.id_adotante,
                    'nome': usuario.nome,
                    'email': usuario.email,
                    'telefone': usuario.telefone,
                    'renda_media': adotante.renda_media,
                    'tem_filhos': adotante.tem_filhos,
                    'estado_saude': adotante.estado_saude
                })

    return templates.TemplateResponse(
        "admin/adotantes/listar.html",
        {"request": request, "adotantes": adotantes_completos}
    )
```

#### 5.1.2. Template

**Arquivo**: `templates/admin/adotantes/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Adotantes{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-people"></i> Gerenciar Adotantes</h2>
        </div>

        <div class="card shadow-sm">
            <div class="card-body">
                {% if adotantes %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Nome</th>
                                <th scope="col">Email</th>
                                <th scope="col">Telefone</th>
                                <th scope="col">Renda Média</th>
                                <th scope="col">Tem Filhos</th>
                                <th scope="col">Estado de Saúde</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for adotante in adotantes %}
                            <tr>
                                <td>{{ adotante.id_adotante }}</td>
                                <td><strong>{{ adotante.nome }}</strong></td>
                                <td>{{ adotante.email }}</td>
                                <td>{{ adotante.telefone or '-' }}</td>
                                <td>R$ {{ "{:,.2f}".format(adotante.renda_media) if adotante.renda_media else '-' }}</td>
                                <td>
                                    {% if adotante.tem_filhos %}
                                        <span class="badge bg-info">Sim</span>
                                    {% else %}
                                        <span class="badge bg-secondary">Não</span>
                                    {% endif %}
                                </td>
                                <td>{{ adotante.estado_saude or '-' }}</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/adotantes/visualizar/{{ adotante.id_adotante }}"
                                            class="btn btn-outline-info"
                                            title="Visualizar"
                                            aria-label="Visualizar adotante {{ adotante.nome }}">
                                            <i class="bi bi-eye"></i>
                                        </a>
                                        <a href="/admin/adotantes/editar/{{ adotante.id_adotante }}"
                                            class="btn btn-outline-primary"
                                            title="Editar"
                                            aria-label="Editar adotante {{ adotante.nome }}">
                                            <i class="bi bi-pencil"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Excluir"
                                            aria-label="Excluir adotante {{ adotante.nome }}"
                                            onclick="excluirAdotante({{ adotante.id_adotante }}, '{{ adotante.nome|replace("'", "\\'") }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhum adotante cadastrado.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function excluirAdotante(adotanteId, adotanteNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <p class="mb-0"><strong>Adotante:</strong> ${adotanteNome}</p>
                <p class="text-warning mt-2 mb-0">
                    <i class="bi bi-exclamation-triangle"></i>
                    <small>O usuário e todas as solicitações relacionadas serão excluídos.</small>
                </p>
            </div>
        </div>
        `;

        abrirModalConfirmacao({
            url: `/admin/adotantes/excluir/${adotanteId}`,
            mensagem: 'Tem certeza que deseja excluir este adotante?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

### 5.2. Editar Adotante

#### 5.2.1. DTO

**Arquivo**: `dtos/adotante_dto.py`

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_id_positivo,
    validar_valor_monetario,
    validar_string_obrigatoria
)

class AlterarAdotanteDTO(BaseModel):
    """DTO para alteração de dados do adotante pelo admin"""
    id_adotante: int
    renda_media: float
    tem_filhos: bool
    estado_saude: str

    _validar_id = field_validator('id_adotante')(validar_id_positivo())
    _validar_renda = field_validator('renda_media')(validar_valor_monetario(minimo=0.0))
    _validar_estado_saude = field_validator('estado_saude')(
        validar_string_obrigatoria('Estado de Saúde', tamanho_minimo=3, tamanho_maximo=100)
    )
```

#### 5.2.2. Rota GET

**Arquivo**: `routes/admin_adotantes_routes.py` (adicionar)

```python
@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de adotante"""
    adotante = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    dados = {
        'id_adotante': adotante.id_adotante,
        'nome': usuario.nome,
        'email': usuario.email,
        'renda_media': adotante.renda_media,
        'tem_filhos': adotante.tem_filhos,
        'estado_saude': adotante.estado_saude
    }

    return templates.TemplateResponse(
        "admin/adotantes/editar.html",
        {
            "request": request,
            "adotante": adotante,
            "dados": dados
        }
    )
```

#### 5.2.3. Template

**Arquivo**: `templates/admin/adotantes/editar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Editar Adotante{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-pencil-square"></i> Editar Adotante</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/adotantes/editar/{{ dados.id_adotante }}">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-12 mb-3">
                            <div class="alert alert-info">
                                <strong>Nome:</strong> {{ dados.nome }}<br>
                                <strong>Email:</strong> {{ dados.email }}
                            </div>
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='renda_media', label='Renda Média', type='decimal', required=true,
                            value=dados.renda_media, help_text='Em reais (R$)') }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='tem_filhos', label='Tem Filhos?', type='radio', required=true,
                            options={'true': 'Sim', 'false': 'Não'},
                            value='true' if dados.tem_filhos else 'false',
                            radio_style='buttons', radio_layout='horizontal') }}
                        </div>

                        <div class="col-12 mb-3">
                            {{ field(name='estado_saude', label='Estado de Saúde', type='text', required=true,
                            value=dados.estado_saude) }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> Salvar Alterações
                        </button>
                        <a href="/admin/adotantes/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

#### 5.2.4. Rota POST

**Arquivo**: `routes/admin_adotantes_routes.py` (adicionar)

```python
from fastapi import Form
from pydantic import ValidationError
from dtos.adotante_dto import AlterarAdotanteDTO
from model.adotante_model import Adotante
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# Rate limiter
admin_adotantes_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_adotantes"
)

@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    renda_media: float = Form(...),
    tem_filhos: str = Form(...),
    estado_saude: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de um adotante"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_adotantes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se adotante existe
    adotante_atual = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante_atual or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Converter string para bool
    tem_filhos_bool = tem_filhos.lower() == 'true'

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "id_adotante": id,
        "nome": usuario.nome,
        "email": usuario.email,
        "renda_media": renda_media,
        "tem_filhos": tem_filhos_bool,
        "estado_saude": estado_saude
    }

    try:
        # Validar com DTO
        dto = AlterarAdotanteDTO(
            id_adotante=id,
            renda_media=renda_media,
            tem_filhos=tem_filhos_bool,
            estado_saude=estado_saude
        )

        # Atualizar adotante
        adotante_atualizado = Adotante(
            id_adotante=id,
            renda_media=dto.renda_media,
            tem_filhos=dto.tem_filhos,
            estado_saude=dto.estado_saude
        )

        adotante_repo.atualizar(adotante_atualizado)
        logger.info(f"Adotante {id} alterado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Adotante alterado com sucesso!")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        dados_formulario["adotante"] = adotante_atual
        raise FormValidationError(
            validation_error=e,
            template_path="admin/adotantes/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="renda_media"
        )
```

### 5.3. Visualizar Adotante

#### 5.3.1. Rota GET

**Arquivo**: `routes/admin_adotantes_routes.py` (adicionar)

```python
from repo import solicitacao_repo, adocao_repo

@router.get("/visualizar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos do adotante"""
    adotante = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter solicitações do adotante
    solicitacoes = solicitacao_repo.obter_por_adotante(id)

    # Obter adoções realizadas
    adocoes = adocao_repo.obter_por_adotante(id) if hasattr(adocao_repo, 'obter_por_adotante') else []

    return templates.TemplateResponse(
        "admin/adotantes/visualizar.html",
        {
            "request": request,
            "adotante": adotante,
            "usuario": usuario,
            "solicitacoes": solicitacoes,
            "adocoes": adocoes
        }
    )
```

#### 5.3.2. Template

**Arquivo**: `templates/admin/adotantes/visualizar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Visualizar Adotante{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-person-badge"></i> Detalhes do Adotante</h2>
            <a href="/admin/adotantes/listar" class="btn btn-secondary">
                <i class="bi bi-arrow-left"></i> Voltar
            </a>
        </div>

        <!-- Informações Pessoais -->
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="bi bi-person"></i> Informações Pessoais</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <strong>Nome:</strong><br>
                        {{ usuario.nome }}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Email:</strong><br>
                        {{ usuario.email }}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Telefone:</strong><br>
                        {{ usuario.telefone or 'Não informado' }}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Documento:</strong><br>
                        {{ usuario.numero_documento or 'Não informado' }}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Renda Média:</strong><br>
                        R$ {{ "{:,.2f}".format(adotante.renda_media) if adotante.renda_media else 'Não informado' }}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Tem Filhos:</strong><br>
                        {% if adotante.tem_filhos %}
                            <span class="badge bg-info">Sim</span>
                        {% else %}
                            <span class="badge bg-secondary">Não</span>
                        {% endif %}
                    </div>
                    <div class="col-12 mb-3">
                        <strong>Estado de Saúde:</strong><br>
                        {{ adotante.estado_saude or 'Não informado' }}
                    </div>
                </div>
            </div>
        </div>

        <!-- Solicitações de Adoção -->
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-warning">
                <h5 class="mb-0"><i class="bi bi-file-text"></i> Solicitações de Adoção</h5>
            </div>
            <div class="card-body">
                {% if solicitacoes %}
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Animal</th>
                                <th>Data</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sol in solicitacoes %}
                            <tr>
                                <td>{{ sol.id_solicitacao }}</td>
                                <td>{{ sol.animal_nome }}</td>
                                <td>{{ sol.data_solicitacao|data_hora_br }}</td>
                                <td>
                                    {% set status_map = {
                                        'Pendente': 'warning',
                                        'Aprovada': 'success',
                                        'Rejeitada': 'danger',
                                        'Cancelada': 'secondary'
                                    } %}
                                    <span class="badge bg-{{ status_map.get(sol.status, 'secondary') }}">
                                        {{ sol.status }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted mb-0">Nenhuma solicitação registrada.</p>
                {% endif %}
            </div>
        </div>

        <!-- Adoções Realizadas -->
        <div class="card shadow-sm">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="bi bi-check-circle"></i> Adoções Realizadas</h5>
            </div>
            <div class="card-body">
                {% if adocoes %}
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Animal</th>
                                <th>Data Adoção</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for adocao in adocoes %}
                            <tr>
                                <td>{{ adocao.id_adocao }}</td>
                                <td>{{ adocao.animal_nome }}</td>
                                <td>{{ adocao.data_adocao|data_br }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted mb-0">Nenhuma adoção realizada.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 5.4. Excluir Adotante

#### 5.4.1. Rota POST

**Arquivo**: `routes/admin_adotantes_routes.py` (adicionar)

```python
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um adotante"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_adotantes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    adotante = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se existem adoções ativas
    adocoes = adocao_repo.obter_por_adotante(id) if hasattr(adocao_repo, 'obter_por_adotante') else []
    if adocoes:
        informar_erro(
            request,
            f"Não é possível excluir este adotante pois existem {len(adocoes)} adoção(ões) vinculada(s)."
        )
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Excluir adotante e usuário
    adotante_repo.excluir(id)
    usuario_repo.excluir(id)

    logger.info(f"Adotante {id} ({usuario.nome}) excluído por admin {usuario_logado['id']}")
    informar_sucesso(request, "Adotante excluído com sucesso!")
    return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)
```

---

## 6. Gerenciar Solicitações

Permite ao administrador visualizar, aprovar, rejeitar e cancelar solicitações de adoção em todo o sistema.

### 6.1. Listar Solicitações

#### 6.1.1. Método no Repositório

Primeiro, adicionar método em `repo/solicitacao_repo.py`:

```python
def obter_todos() -> List[dict]:
    """
    Lista todas as solicitações do sistema com informações completas.

    Returns:
        Lista de dicionários com dados das solicitações
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [dict(row) for row in cursor.fetchall()]

def obter_por_id(id_solicitacao: int) -> Optional[dict]:
    """
    Busca uma solicitação específica pelo ID.

    Args:
        id_solicitacao: ID da solicitação

    Returns:
        Dicionário com dados da solicitação ou None se não encontrada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_solicitacao,))
        row = cursor.fetchone()
        return dict(row) if row else None

def excluir(id_solicitacao: int) -> bool:
    """
    Exclui uma solicitação.

    Args:
        id_solicitacao: ID da solicitação a ser excluída

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_solicitacao,))
        return cursor.rowcount > 0
```

#### 6.1.2. Rota GET

**Arquivo**: `routes/admin_solicitacoes_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Request, status, Query
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import solicitacao_repo

router = APIRouter(prefix="/admin/solicitacoes")
templates = criar_templates("templates/admin/solicitacoes")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de solicitações"""
    return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    filtro_status: Optional[str] = Query(None),
    usuario_logado: Optional[dict] = None
):
    """Lista todas as solicitações de adoção do sistema"""
    # Obter todas as solicitações
    solicitacoes = solicitacao_repo.obter_todos()

    # Aplicar filtro de status se especificado
    if filtro_status and filtro_status != 'Todas':
        solicitacoes = [s for s in solicitacoes if s['status'] == filtro_status]

    # Calcular estatísticas
    total_solicitacoes = len(solicitacao_repo.obter_todos())
    pendentes = len([s for s in solicitacao_repo.obter_todos() if s['status'] == 'Pendente'])
    aprovadas = len([s for s in solicitacao_repo.obter_todos() if s['status'] == 'Aprovada'])
    rejeitadas = len([s for s in solicitacao_repo.obter_todos() if s['status'] == 'Rejeitada'])

    return templates.TemplateResponse(
        "admin/solicitacoes/listar.html",
        {
            "request": request,
            "solicitacoes": solicitacoes,
            "filtro_status": filtro_status or 'Todas',
            "estatisticas": {
                'total': total_solicitacoes,
                'pendentes': pendentes,
                'aprovadas': aprovadas,
                'rejeitadas': rejeitadas
            }
        }
    )
```

#### 6.1.3. Template

**Arquivo**: `templates/admin/solicitacoes/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Solicitações de Adoção{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-file-earmark-text"></i> Gerenciar Solicitações de Adoção</h2>
        </div>

        <!-- Estatísticas -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-white bg-primary">
                    <div class="card-body">
                        <h6 class="card-title">Total</h6>
                        <h3 class="mb-0">{{ estatisticas.total }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-warning">
                    <div class="card-body">
                        <h6 class="card-title">Pendentes</h6>
                        <h3 class="mb-0">{{ estatisticas.pendentes }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success">
                    <div class="card-body">
                        <h6 class="card-title">Aprovadas</h6>
                        <h3 class="mb-0">{{ estatisticas.aprovadas }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-danger">
                    <div class="card-body">
                        <h6 class="card-title">Rejeitadas</h6>
                        <h3 class="mb-0">{{ estatisticas.rejeitadas }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Filtros -->
        <div class="card shadow-sm mb-3">
            <div class="card-body">
                <form method="GET" action="/admin/solicitacoes/listar" class="row g-3 align-items-end">
                    <div class="col-md-3">
                        <label for="filtro_status" class="form-label">Filtrar por Status</label>
                        <select name="filtro_status" id="filtro_status" class="form-select">
                            <option value="Todas" {% if filtro_status == 'Todas' %}selected{% endif %}>Todas</option>
                            <option value="Pendente" {% if filtro_status == 'Pendente' %}selected{% endif %}>Pendentes</option>
                            <option value="Aprovada" {% if filtro_status == 'Aprovada' %}selected{% endif %}>Aprovadas</option>
                            <option value="Rejeitada" {% if filtro_status == 'Rejeitada' %}selected{% endif %}>Rejeitadas</option>
                            <option value="Cancelada" {% if filtro_status == 'Cancelada' %}selected{% endif %}>Canceladas</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-funnel"></i> Filtrar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Lista de Solicitações -->
        <div class="card shadow-sm">
            <div class="card-body">
                {% if solicitacoes %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Adotante</th>
                                <th scope="col">Animal</th>
                                <th scope="col">Data Solicitação</th>
                                <th scope="col">Status</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sol in solicitacoes %}
                            <tr>
                                <td>{{ sol.id_solicitacao }}</td>
                                <td>
                                    <strong>{{ sol.adotante_nome }}</strong><br>
                                    <small class="text-muted">{{ sol.adotante_email }}</small>
                                </td>
                                <td>{{ sol.animal_nome }}</td>
                                <td>{{ sol.data_solicitacao|data_hora_br }}</td>
                                <td>
                                    {% set status_map = {
                                        'Pendente': 'warning',
                                        'Aprovada': 'success',
                                        'Rejeitada': 'danger',
                                        'Cancelada': 'secondary'
                                    } %}
                                    <span class="badge bg-{{ status_map.get(sol.status, 'secondary') }}">
                                        {{ sol.status }}
                                    </span>
                                </td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        <a href="/admin/solicitacoes/visualizar/{{ sol.id_solicitacao }}"
                                            class="btn btn-outline-info"
                                            title="Visualizar">
                                            <i class="bi bi-eye"></i>
                                        </a>
                                        {% if sol.status == 'Pendente' %}
                                        <button type="button" class="btn btn-outline-success"
                                            title="Aprovar"
                                            onclick="aprovarSolicitacao({{ sol.id_solicitacao }}, '{{ sol.adotante_nome }}', '{{ sol.animal_nome }}')">
                                            <i class="bi bi-check-circle"></i>
                                        </button>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Rejeitar"
                                            onclick="rejeitarSolicitacao({{ sol.id_solicitacao }}, '{{ sol.adotante_nome }}', '{{ sol.animal_nome }}')">
                                            <i class="bi bi-x-circle"></i>
                                        </button>
                                        {% endif %}
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhuma solicitação encontrada.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Modal para Aprovar -->
<div class="modal fade" id="modalAprovar" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <form id="formAprovar" method="POST">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title">Aprovar Solicitação</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p id="mensagemAprovar"></p>
                    <div class="mb-3">
                        <label for="respostaAprovar" class="form-label">Mensagem para o adotante (opcional)</label>
                        <textarea name="resposta_abrigo" id="respostaAprovar" class="form-control" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-success">Aprovar Solicitação</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- Modal para Rejeitar -->
<div class="modal fade" id="modalRejeitar" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <form id="formRejeitar" method="POST">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title">Rejeitar Solicitação</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p id="mensagemRejeitar"></p>
                    <div class="mb-3">
                        <label for="respostaRejeitar" class="form-label">Motivo da rejeição <span class="text-danger">*</span></label>
                        <textarea name="resposta_abrigo" id="respostaRejeitar" class="form-control" rows="3" required></textarea>
                        <div class="form-text">Obrigatório informar o motivo da rejeição</div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-danger">Rejeitar Solicitação</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function aprovarSolicitacao(solicitacaoId, adotanteNome, animalNome) {
        document.getElementById('mensagemAprovar').innerHTML =
            `Aprovar a solicitação de <strong>${adotanteNome}</strong> para adotar <strong>${animalNome}</strong>?`;
        document.getElementById('formAprovar').action = `/admin/solicitacoes/aprovar/${solicitacaoId}`;

        const modal = new bootstrap.Modal(document.getElementById('modalAprovar'));
        modal.show();
    }

    function rejeitarSolicitacao(solicitacaoId, adotanteNome, animalNome) {
        document.getElementById('mensagemRejeitar').innerHTML =
            `Rejeitar a solicitação de <strong>${adotanteNome}</strong> para adotar <strong>${animalNome}</strong>?`;
        document.getElementById('formRejeitar').action = `/admin/solicitacoes/rejeitar/${solicitacaoId}`;
        document.getElementById('respostaRejeitar').value = '';

        const modal = new bootstrap.Modal(document.getElementById('modalRejeitar'));
        modal.show();
    }
</script>
{% endblock %}
```

### 6.2. Visualizar Solicitação

#### 6.2.1. Rota GET

**Arquivo**: `routes/admin_solicitacoes_routes.py` (adicionar)

```python
@router.get("/visualizar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos de uma solicitação"""
    solicitacao = solicitacao_repo.obter_por_id(id)

    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/solicitacoes/visualizar.html",
        {
            "request": request,
            "solicitacao": solicitacao
        }
    )
```

#### 6.2.2. Template

**Arquivo**: `templates/admin/solicitacoes/visualizar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Detalhes da Solicitação #{{ solicitacao.id_solicitacao }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-file-earmark-text"></i> Detalhes da Solicitação #{{ solicitacao.id_solicitacao }}</h2>
            <a href="/admin/solicitacoes/listar" class="btn btn-secondary">
                <i class="bi bi-arrow-left"></i> Voltar
            </a>
        </div>

        <div class="row">
            <!-- Informações da Solicitação -->
            <div class="col-md-6">
                <div class="card shadow-sm mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0"><i class="bi bi-info-circle"></i> Informações da Solicitação</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <strong>Data da Solicitação:</strong><br>
                            {{ solicitacao.data_solicitacao|data_hora_br }}
                        </div>
                        <div class="mb-3">
                            <strong>Status:</strong><br>
                            {% set status_map = {
                                'Pendente': 'warning',
                                'Aprovada': 'success',
                                'Rejeitada': 'danger',
                                'Cancelada': 'secondary'
                            } %}
                            <span class="badge bg-{{ status_map.get(solicitacao.status, 'secondary') }}">
                                {{ solicitacao.status }}
                            </span>
                        </div>
                        <div class="mb-3">
                            <strong>Observações do Adotante:</strong><br>
                            {{ solicitacao.observacoes or 'Sem observações' }}
                        </div>
                        {% if solicitacao.resposta_abrigo %}
                        <div class="mb-3">
                            <strong>Resposta do Abrigo:</strong><br>
                            {{ solicitacao.resposta_abrigo }}
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <!-- Informações do Adotante -->
            <div class="col-md-6">
                <div class="card shadow-sm mb-4">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0"><i class="bi bi-person"></i> Dados do Adotante</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <strong>Nome:</strong><br>
                            {{ solicitacao.adotante_nome }}
                        </div>
                        <div class="mb-3">
                            <strong>Email:</strong><br>
                            {{ solicitacao.adotante_email }}
                        </div>
                        <div class="mb-3">
                            <a href="/admin/adotantes/visualizar/{{ solicitacao.id_adotante }}" class="btn btn-sm btn-outline-info">
                                <i class="bi bi-eye"></i> Ver Perfil Completo
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Informações do Animal -->
                <div class="card shadow-sm">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="bi bi-heart"></i> Dados do Animal</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <strong>Nome:</strong><br>
                            {{ solicitacao.animal_nome }}
                        </div>
                        <div class="mb-3">
                            <a href="/admin/animais/visualizar/{{ solicitacao.id_animal }}" class="btn btn-sm btn-outline-success">
                                <i class="bi bi-eye"></i> Ver Ficha Completa
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Ações -->
        {% if solicitacao.status == 'Pendente' %}
        <div class="card shadow-sm mt-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-lightning"></i> Ações Disponíveis</h5>
            </div>
            <div class="card-body">
                <div class="d-flex gap-3">
                    <button type="button" class="btn btn-success"
                        onclick="aprovarSolicitacao({{ solicitacao.id_solicitacao }}, '{{ solicitacao.adotante_nome }}', '{{ solicitacao.animal_nome }}')">
                        <i class="bi bi-check-circle"></i> Aprovar Solicitação
                    </button>
                    <button type="button" class="btn btn-danger"
                        onclick="rejeitarSolicitacao({{ solicitacao.id_solicitacao }}, '{{ solicitacao.adotante_nome }}', '{{ solicitacao.animal_nome }}')">
                        <i class="bi bi-x-circle"></i> Rejeitar Solicitação
                    </button>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>

<!-- Incluir mesmos modais da página de listagem -->
<!-- ... (copiar modais de aprovar e rejeitar) ... -->
{% endblock %}
```

### 6.3. Aprovar Solicitação

#### 6.3.1. DTO

**Arquivo**: `dtos/solicitacao_dto.py`

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import validar_id_positivo, validar_texto_longo_opcional

class AprovarSolicitacaoDTO(BaseModel):
    """DTO para aprovação de solicitação"""
    id_solicitacao: int
    resposta_abrigo: Optional[str] = None

    _validar_id = field_validator('id_solicitacao')(validar_id_positivo())
    _validar_resposta = field_validator('resposta_abrigo')(
        validar_texto_longo_opcional(tamanho_maximo=500)
    )

class RejeitarSolicitacaoDTO(BaseModel):
    """DTO para rejeição de solicitação"""
    id_solicitacao: int
    resposta_abrigo: str

    _validar_id = field_validator('id_solicitacao')(validar_id_positivo())
    _validar_resposta = field_validator('resposta_abrigo')(
        validar_string_obrigatoria('Motivo da rejeição', tamanho_minimo=10, tamanho_maximo=500)
    )
```

#### 6.3.2. Rota POST

**Arquivo**: `routes/admin_solicitacoes_routes.py` (adicionar)

```python
from fastapi import Form
from pydantic import ValidationError
from dtos.solicitacao_dto import AprovarSolicitacaoDTO, RejeitarSolicitacaoDTO
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# Rate limiter
admin_solicitacoes_limiter = RateLimiter(
    max_tentativas=20,
    janela_minutos=1,
    nome="admin_solicitacoes"
)

@router.post("/aprovar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_aprovar(
    request: Request,
    id: int,
    resposta_abrigo: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Aprova uma solicitação de adoção"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_solicitacoes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se solicitação existe
    solicitacao = solicitacao_repo.obter_por_id(id)
    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se está pendente
    if solicitacao['status'] != 'Pendente':
        informar_erro(request, "Esta solicitação já foi processada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Validar com DTO
        dto = AprovarSolicitacaoDTO(
            id_solicitacao=id,
            resposta_abrigo=resposta_abrigo
        )

        # Atualizar status
        resposta = dto.resposta_abrigo or "Solicitação aprovada pelo administrador do sistema."
        solicitacao_repo.atualizar_status(id, "Aprovada", resposta)

        logger.info(f"Solicitação {id} aprovada por admin {usuario_logado['id']}")
        informar_sucesso(request, "Solicitação aprovada com sucesso!")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        logger.error(f"Erro ao aprovar solicitação {id}: {e}")
        informar_erro(request, "Erro ao aprovar solicitação. Verifique os dados.")
        return RedirectResponse(f"/admin/solicitacoes/visualizar/{id}", status_code=status.HTTP_303_SEE_OTHER)
```

### 6.4. Rejeitar Solicitação

#### 6.4.1. Rota POST

**Arquivo**: `routes/admin_solicitacoes_routes.py` (adicionar)

```python
@router.post("/rejeitar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_rejeitar(
    request: Request,
    id: int,
    resposta_abrigo: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Rejeita uma solicitação de adoção"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_solicitacoes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se solicitação existe
    solicitacao = solicitacao_repo.obter_por_id(id)
    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se está pendente
    if solicitacao['status'] != 'Pendente':
        informar_erro(request, "Esta solicitação já foi processada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Validar com DTO (motivo é obrigatório)
        dto = RejeitarSolicitacaoDTO(
            id_solicitacao=id,
            resposta_abrigo=resposta_abrigo
        )

        # Atualizar status
        solicitacao_repo.atualizar_status(id, "Rejeitada", dto.resposta_abrigo)

        logger.info(f"Solicitação {id} rejeitada por admin {usuario_logado['id']}")
        informar_sucesso(request, "Solicitação rejeitada.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        logger.error(f"Erro ao rejeitar solicitação {id}: {e}")
        informar_erro(request, "Erro ao rejeitar solicitação. É obrigatório informar o motivo.")
        return RedirectResponse(f"/admin/solicitacoes/visualizar/{id}", status_code=status.HTTP_303_SEE_OTHER)
```

### 6.5. Cancelar Solicitação

#### 6.5.1. Rota POST

**Arquivo**: `routes/admin_solicitacoes_routes.py` (adicionar)

```python
@router.post("/cancelar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cancelar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Cancela uma solicitação de adoção"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_solicitacoes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se solicitação existe
    solicitacao = solicitacao_repo.obter_por_id(id)
    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Cancelar
    solicitacao_repo.atualizar_status(id, "Cancelada", "Cancelada pelo administrador do sistema")

    logger.info(f"Solicitação {id} cancelada por admin {usuario_logado['id']}")
    informar_sucesso(request, "Solicitação cancelada com sucesso!")
    return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)
```

---

## 7. Gerenciar Visitas

Permite ao administrador visualizar, agendar, reagendar e cancelar visitas agendadas entre adotantes e abrigos.

### 7.1. Listar Visitas

#### 7.1.1. Método no Repositório

Adicionar métodos em `repo/visita_repo.py`:

```python
def obter_todos() -> List[dict]:
    """
    Lista todas as visitas do sistema com informações completas.

    Returns:
        Lista de dicionários com dados das visitas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # SQL para obter todas as visitas com dados de adotante e abrigo
        sql = """
        SELECT
            v.*,
            u.nome as adotante_nome,
            u.telefone as adotante_telefone,
            ab.responsavel as abrigo_nome
        FROM visita v
        INNER JOIN usuario u ON v.id_adotante = u.id
        INNER JOIN abrigo ab ON v.id_abrigo = ab.id_abrigo
        ORDER BY v.data_agendada DESC
        """
        cursor.execute(sql)
        return [dict(row) for row in cursor.fetchall()]

def obter_por_id(id_visita: int) -> Optional[dict]:
    """
    Busca uma visita específica pelo ID.

    Args:
        id_visita: ID da visita

    Returns:
        Dicionário com dados da visita ou None se não encontrada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        sql = """
        SELECT
            v.*,
            u.nome as adotante_nome,
            u.telefone as adotante_telefone,
            u.email as adotante_email,
            ab.responsavel as abrigo_nome
        FROM visita v
        INNER JOIN usuario u ON v.id_adotante = u.id
        INNER JOIN abrigo ab ON v.id_abrigo = ab.id_abrigo
        WHERE v.id_visita = ?
        """
        cursor.execute(sql, (id_visita,))
        row = cursor.fetchone()
        return dict(row) if row else None

def excluir(id_visita: int) -> bool:
    """
    Exclui uma visita.

    Args:
        id_visita: ID da visita a ser excluída

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM visita WHERE id_visita = ?", (id_visita,))
        return cursor.rowcount > 0
```

#### 7.1.2. Rota GET

**Arquivo**: `routes/admin_visitas_routes.py`

```python
from typing import Optional
from fastapi import APIRouter, Request, status, Query
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import visita_repo

router = APIRouter(prefix="/admin/visitas")
templates = criar_templates("templates/admin/visitas")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de visitas"""
    return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    filtro_status: Optional[str] = Query(None),
    usuario_logado: Optional[dict] = None
):
    """Lista todas as visitas agendadas do sistema"""
    # Obter todas as visitas
    visitas = visita_repo.obter_todos()

    # Aplicar filtro de status se especificado
    if filtro_status and filtro_status != 'Todas':
        visitas = [v for v in visitas if v['status'] == filtro_status]

    # Calcular estatísticas
    todas_visitas = visita_repo.obter_todos()
    total_visitas = len(todas_visitas)
    agendadas = len([v for v in todas_visitas if v['status'] == 'Agendada'])
    realizadas = len([v for v in todas_visitas if v['status'] == 'Realizada'])
    canceladas = len([v for v in todas_visitas if v['status'] == 'Cancelada'])

    return templates.TemplateResponse(
        "admin/visitas/listar.html",
        {
            "request": request,
            "visitas": visitas,
            "filtro_status": filtro_status or 'Todas',
            "estatisticas": {
                'total': total_visitas,
                'agendadas': agendadas,
                'realizadas': realizadas,
                'canceladas': canceladas
            }
        }
    )
```

#### 7.1.3. Template

**Arquivo**: `templates/admin/visitas/listar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Gerenciar Visitas{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="bi bi-calendar-check"></i> Gerenciar Visitas</h2>
            <a href="/admin/visitas/agendar" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Agendar Nova Visita
            </a>
        </div>

        <!-- Estatísticas -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-white bg-primary">
                    <div class="card-body">
                        <h6 class="card-title">Total</h6>
                        <h3 class="mb-0">{{ estatisticas.total }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-info">
                    <div class="card-body">
                        <h6 class="card-title">Agendadas</h6>
                        <h3 class="mb-0">{{ estatisticas.agendadas }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success">
                    <div class="card-body">
                        <h6 class="card-title">Realizadas</h6>
                        <h3 class="mb-0">{{ estatisticas.realizadas }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-secondary">
                    <div class="card-body">
                        <h6 class="card-title">Canceladas</h6>
                        <h3 class="mb-0">{{ estatisticas.canceladas }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Filtros -->
        <div class="card shadow-sm mb-3">
            <div class="card-body">
                <form method="GET" action="/admin/visitas/listar" class="row g-3 align-items-end">
                    <div class="col-md-3">
                        <label for="filtro_status" class="form-label">Filtrar por Status</label>
                        <select name="filtro_status" id="filtro_status" class="form-select">
                            <option value="Todas" {% if filtro_status == 'Todas' %}selected{% endif %}>Todas</option>
                            <option value="Agendada" {% if filtro_status == 'Agendada' %}selected{% endif %}>Agendadas</option>
                            <option value="Realizada" {% if filtro_status == 'Realizada' %}selected{% endif %}>Realizadas</option>
                            <option value="Cancelada" {% if filtro_status == 'Cancelada' %}selected{% endif %}>Canceladas</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-funnel"></i> Filtrar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Lista de Visitas -->
        <div class="card shadow-sm">
            <div class="card-body">
                {% if visitas %}
                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th scope="col">ID</th>
                                <th scope="col">Adotante</th>
                                <th scope="col">Abrigo</th>
                                <th scope="col">Data Agendada</th>
                                <th scope="col">Status</th>
                                <th scope="col" class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for visita in visitas %}
                            <tr>
                                <td>{{ visita.id_visita }}</td>
                                <td>
                                    <strong>{{ visita.adotante_nome }}</strong><br>
                                    <small class="text-muted">{{ visita.adotante_telefone or 'Sem telefone' }}</small>
                                </td>
                                <td>{{ visita.abrigo_nome }}</td>
                                <td>{{ visita.data_agendada|data_hora_br }}</td>
                                <td>
                                    {% set status_map = {
                                        'Agendada': 'info',
                                        'Realizada': 'success',
                                        'Cancelada': 'secondary'
                                    } %}
                                    <span class="badge bg-{{ status_map.get(visita.status, 'secondary') }}">
                                        {{ visita.status }}
                                    </span>
                                </td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm" role="group">
                                        {% if visita.status == 'Agendada' %}
                                        <a href="/admin/visitas/reagendar/{{ visita.id_visita }}"
                                            class="btn btn-outline-warning"
                                            title="Reagendar">
                                            <i class="bi bi-calendar-event"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-success"
                                            title="Marcar como Realizada"
                                            onclick="marcarRealizada({{ visita.id_visita }}, '{{ visita.adotante_nome }}', '{{ visita.abrigo_nome }}')">
                                            <i class="bi bi-check-circle"></i>
                                        </button>
                                        <button type="button" class="btn btn-outline-danger"
                                            title="Cancelar"
                                            onclick="cancelarVisita({{ visita.id_visita }}, '{{ visita.adotante_nome }}', '{{ visita.abrigo_nome }}')">
                                            <i class="bi bi-x-circle"></i>
                                        </button>
                                        {% endif %}
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="alert alert-info text-center mb-0">
                    <i class="bi bi-info-circle"></i> Nenhuma visita encontrada.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function marcarRealizada(visitaId, adotanteNome, abrigoNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <p><strong>Adotante:</strong> ${adotanteNome}</p>
                <p class="mb-0"><strong>Abrigo:</strong> ${abrigoNome}</p>
            </div>
        </div>
        `;

        abrirModalConfirmacao({
            url: `/admin/visitas/marcar-realizada/${visitaId}`,
            mensagem: 'Marcar esta visita como realizada?',
            detalhes: detalhes
        });
    }

    function cancelarVisita(visitaId, adotanteNome, abrigoNome) {
        const detalhes = `
        <div class="card bg-light">
            <div class="card-body">
                <p><strong>Adotante:</strong> ${adotanteNome}</p>
                <p class="mb-0"><strong>Abrigo:</strong> ${abrigoNome}</p>
            </div>
        </div>
        `;

        abrirModalConfirmacao({
            url: `/admin/visitas/cancelar/${visitaId}`,
            mensagem: 'Tem certeza que deseja cancelar esta visita?',
            detalhes: detalhes
        });
    }
</script>
{% endblock %}
```

### 7.2. Agendar Visita

#### 7.2.1. DTO

**Arquivo**: `dtos/visita_dto.py`

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from dtos.validators import (
    validar_id_positivo,
    validar_texto_longo_opcional,
    validar_data_hora_futura
)

class AgendarVisitaDTO(BaseModel):
    """DTO para agendamento de visita"""
    id_adotante: int
    id_abrigo: int
    data_agendada: str  # Formato: YYYY-MM-DD HH:MM
    observacoes: Optional[str] = None

    _validar_id_adotante = field_validator('id_adotante')(validar_id_positivo())
    _validar_id_abrigo = field_validator('id_abrigo')(validar_id_positivo())
    _validar_data_agendada = field_validator('data_agendada')(validar_data_hora_futura())
    _validar_observacoes = field_validator('observacoes')(
        validar_texto_longo_opcional(tamanho_maximo=500)
    )

class ReagendarVisitaDTO(BaseModel):
    """DTO para reagendamento de visita"""
    id_visita: int
    data_agendada: str  # Formato: YYYY-MM-DD HH:MM

    _validar_id = field_validator('id_visita')(validar_id_positivo())
    _validar_data_agendada = field_validator('data_agendada')(validar_data_hora_futura())
```

**Adicionar validador em `dtos/validators.py`**:

```python
from datetime import datetime

def validar_data_hora_futura():
    """Valida se a data/hora é futura"""
    def validator(cls, v: str) -> str:
        if not v:
            raise ValueError("Data e hora são obrigatórias")

        try:
            # Tentar formato com hora
            dt = datetime.strptime(v, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("Data e hora devem estar no formato YYYY-MM-DD HH:MM")

        # Verificar se é futura
        if dt <= datetime.now():
            raise ValueError("Data e hora devem ser futuras")

        return v
    return validator
```

#### 7.2.2. Rota GET

**Arquivo**: `routes/admin_visitas_routes.py` (adicionar)

```python
from repo import adotante_repo, abrigo_repo, usuario_repo

@router.get("/agendar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_agendar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de agendamento de visita"""
    # Obter adotantes (usuários com perfil ADOTANTE)
    usuarios = usuario_repo.obter_todos()
    adotantes = [(u.id, u.nome) for u in usuarios if u.perfil == Perfil.ADOTANTE.value]

    # Obter abrigos
    abrigos = abrigo_repo.obter_todos()
    abrigos_list = [(a.id_abrigo, a.responsavel) for a in abrigos]

    # Converter para dict para os selects
    adotantes_dict = {str(id): nome for id, nome in adotantes}
    abrigos_dict = {str(id): nome for id, nome in abrigos_list}

    return templates.TemplateResponse(
        "admin/visitas/agendar.html",
        {
            "request": request,
            "adotantes": adotantes_dict,
            "abrigos": abrigos_dict
        }
    )
```

#### 7.2.3. Template

**Arquivo**: `templates/admin/visitas/agendar.html`

```html
{% extends "base_privada.html" %}
{% from "macros/form_fields.html" import field with context %}

{% block titulo %}Agendar Nova Visita{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-calendar-plus"></i> Agendar Nova Visita</h2>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/visitas/agendar">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='id_adotante', label='Adotante', type='select', required=true,
                            options=adotantes, help_text='Selecione o adotante') }}
                        </div>

                        <div class="col-md-6 mb-3">
                            {{ field(name='id_abrigo', label='Abrigo', type='select', required=true,
                            options=abrigos, help_text='Selecione o abrigo') }}
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="data_agendada_data" class="form-label">Data da Visita <span class="text-danger">*</span></label>
                            <input type="date" class="form-control" id="data_agendada_data" required
                                min="{{ now().strftime('%Y-%m-%d') }}">
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="data_agendada_hora" class="form-label">Hora da Visita <span class="text-danger">*</span></label>
                            <input type="time" class="form-control" id="data_agendada_hora" required>
                        </div>

                        <input type="hidden" name="data_agendada" id="data_agendada">

                        <div class="col-12 mb-3">
                            {{ field(name='observacoes', label='Observações', type='textarea', rows=3,
                            help_text='Informações adicionais sobre a visita') }}
                        </div>
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary" onclick="combinarDataHora(event)">
                            <i class="bi bi-check-circle"></i> Agendar Visita
                        </button>
                        <a href="/admin/visitas/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function combinarDataHora(event) {
        const data = document.getElementById('data_agendada_data').value;
        const hora = document.getElementById('data_agendada_hora').value;

        if (data && hora) {
            document.getElementById('data_agendada').value = `${data} ${hora}`;
        }
    }
</script>
{% endblock %}
```

#### 7.2.4. Rota POST

**Arquivo**: `routes/admin_visitas_routes.py` (adicionar)

```python
from fastapi import Form
from pydantic import ValidationError
from dtos.visita_dto import AgendarVisitaDTO, ReagendarVisitaDTO
from model.visita_model import Visita
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# Rate limiter
admin_visitas_limiter = RateLimiter(
    max_tentativas=20,
    janela_minutos=1,
    nome="admin_visitas"
)

@router.post("/agendar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_agendar(
    request: Request,
    id_adotante: int = Form(...),
    id_abrigo: int = Form(...),
    data_agendada: str = Form(...),
    observacoes: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Agenda uma nova visita"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_visitas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "id_adotante": id_adotante,
        "id_abrigo": id_abrigo,
        "data_agendada": data_agendada,
        "observacoes": observacoes
    }

    try:
        # Validar com DTO
        dto = AgendarVisitaDTO(
            id_adotante=id_adotante,
            id_abrigo=id_abrigo,
            data_agendada=data_agendada,
            observacoes=observacoes
        )

        # Verificar se adotante e abrigo existem
        adotante = adotante_repo.obter_por_id(dto.id_adotante)
        abrigo = abrigo_repo.obter_por_id(dto.id_abrigo)

        if not adotante:
            informar_erro(request, "Adotante não encontrado")
            return RedirectResponse("/admin/visitas/agendar", status_code=status.HTTP_303_SEE_OTHER)

        if not abrigo:
            informar_erro(request, "Abrigo não encontrado")
            return RedirectResponse("/admin/visitas/agendar", status_code=status.HTTP_303_SEE_OTHER)

        # Criar visita
        visita = Visita(
            id_visita=0,
            id_adotante=dto.id_adotante,
            id_abrigo=dto.id_abrigo,
            data_agendada=dto.data_agendada,
            observacoes=dto.observacoes,
            status="Agendada"
        )

        visita_repo.inserir(visita)
        logger.info(f"Visita agendada por admin {usuario_logado['id']}: adotante {dto.id_adotante}, abrigo {dto.id_abrigo}")

        informar_sucesso(request, "Visita agendada com sucesso!")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Recarregar listas
        usuarios = usuario_repo.obter_todos()
        adotantes = [(u.id, u.nome) for u in usuarios if u.perfil == Perfil.ADOTANTE.value]
        abrigos = abrigo_repo.obter_todos()
        abrigos_list = [(a.id_abrigo, a.responsavel) for a in abrigos]

        dados_formulario["adotantes"] = {str(id): nome for id, nome in adotantes}
        dados_formulario["abrigos"] = {str(id): nome for id, nome in abrigos_list}

        raise FormValidationError(
            validation_error=e,
            template_path="admin/visitas/agendar.html",
            dados_formulario=dados_formulario,
            campo_padrao="data_agendada"
        )
```

### 7.3. Reagendar Visita

#### 7.3.1. Rota GET

**Arquivo**: `routes/admin_visitas_routes.py` (adicionar)

```python
@router.get("/reagendar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_reagendar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de reagendamento de visita"""
    visita = visita_repo.obter_por_id(id)

    if not visita:
        informar_erro(request, "Visita não encontrada")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    if visita['status'] != 'Agendada':
        informar_erro(request, "Somente visitas agendadas podem ser reagendadas")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/visitas/reagendar.html",
        {
            "request": request,
            "visita": visita
        }
    )
```

#### 7.3.2. Template

**Arquivo**: `templates/admin/visitas/reagendar.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Reagendar Visita{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="d-flex align-items-center mb-4">
            <h2 class="mb-0"><i class="bi bi-calendar-event"></i> Reagendar Visita</h2>
        </div>

        <div class="card shadow-sm mb-4">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0">Informações da Visita</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <strong>Adotante:</strong> {{ visita.adotante_nome }}
                    </div>
                    <div class="col-md-6">
                        <strong>Abrigo:</strong> {{ visita.abrigo_nome }}
                    </div>
                    <div class="col-12 mt-2">
                        <strong>Data Atual:</strong> {{ visita.data_agendada|data_hora_br }}
                    </div>
                </div>
            </div>
        </div>

        <div class="card shadow-sm">
            <form method="POST" action="/admin/visitas/reagendar/{{ visita.id_visita }}">
                <div class="card-body p-4">
                    <div class="row">
                        <div class="col-12">
                            {% include "components/alerta_erro.html" %}
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="nova_data" class="form-label">Nova Data <span class="text-danger">*</span></label>
                            <input type="date" class="form-control" id="nova_data" required
                                min="{{ now().strftime('%Y-%m-%d') }}">
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="nova_hora" class="form-label">Nova Hora <span class="text-danger">*</span></label>
                            <input type="time" class="form-control" id="nova_hora" required>
                        </div>

                        <input type="hidden" name="data_agendada" id="data_agendada">
                    </div>
                </div>
                <div class="card-footer p-4">
                    <div class="d-flex gap-3">
                        <button type="submit" class="btn btn-primary" onclick="combinarDataHora(event)">
                            <i class="bi bi-check-circle"></i> Reagendar
                        </button>
                        <a href="/admin/visitas/listar" class="btn btn-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                    </div>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    function combinarDataHora(event) {
        const data = document.getElementById('nova_data').value;
        const hora = document.getElementById('nova_hora').value;

        if (data && hora) {
            document.getElementById('data_agendada').value = `${data} ${hora}`;
        }
    }
</script>
{% endblock %}
```

#### 7.3.3. Rota POST

**Arquivo**: `routes/admin_visitas_routes.py` (adicionar)

```python
@router.post("/reagendar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_reagendar(
    request: Request,
    id: int,
    data_agendada: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Reagenda uma visita"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_visitas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se visita existe
    visita = visita_repo.obter_por_id(id)
    if not visita:
        informar_erro(request, "Visita não encontrada")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    if visita['status'] != 'Agendada':
        informar_erro(request, "Somente visitas agendadas podem ser reagendadas")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Validar com DTO
        dto = ReagendarVisitaDTO(
            id_visita=id,
            data_agendada=data_agendada
        )

        # Reagendar
        visita_repo.reagendar(id, dto.data_agendada)
        logger.info(f"Visita {id} reagendada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Visita reagendada com sucesso!")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        logger.error(f"Erro ao reagendar visita {id}: {e}")
        informar_erro(request, "Erro ao reagendar. A data deve ser futura.")
        return RedirectResponse(f"/admin/visitas/reagendar/{id}", status_code=status.HTTP_303_SEE_OTHER)
```

### 7.4. Marcar como Realizada

#### 7.4.1. Rota POST

**Arquivo**: `routes/admin_visitas_routes.py` (adicionar)

```python
@router.post("/marcar-realizada/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_marcar_realizada(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Marca uma visita como realizada"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_visitas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se visita existe
    visita = visita_repo.obter_por_id(id)
    if not visita:
        informar_erro(request, "Visita não encontrada")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Marcar como realizada
    visita_repo.atualizar_status(id, "Realizada")
    logger.info(f"Visita {id} marcada como realizada por admin {usuario_logado['id']}")

    informar_sucesso(request, "Visita marcada como realizada!")
    return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)
```

### 7.5. Cancelar Visita

#### 7.5.1. Rota POST

**Arquivo**: `routes/admin_visitas_routes.py` (adicionar)

```python
@router.post("/cancelar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cancelar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Cancela uma visita"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_visitas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se visita existe
    visita = visita_repo.obter_por_id(id)
    if not visita:
        informar_erro(request, "Visita não encontrada")
        return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Cancelar
    visita_repo.atualizar_status(id, "Cancelada")
    logger.info(f"Visita {id} cancelada por admin {usuario_logado['id']}")

    informar_sucesso(request, "Visita cancelada com sucesso!")
    return RedirectResponse("/admin/visitas/listar", status_code=status.HTTP_303_SEE_OTHER)
```

---

## 8. Dashboard Administrativo

### 8.1. Visão Geral

**Rota**: `GET /admin/dashboard`

**Template**: `templates/admin/dashboard.html`

**Conteúdo**:

```html
<div class="row">
    <!-- Cards de Estatísticas -->
    <div class="col-md-3 mb-4">
        <div class="card text-white bg-primary">
            <div class="card-body">
                <h5>Total de Animais</h5>
                <h2>{{ total_animais }}</h2>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-4">
        <div class="card text-white bg-success">
            <div class="card-body">
                <h5>Animais Adotados</h5>
                <h2>{{ animais_adotados }}</h2>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-4">
        <div class="card text-white bg-warning">
            <div class="card-body">
                <h5>Solicitações Pendentes</h5>
                <h2>{{ solicitacoes_pendentes }}</h2>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-4">
        <div class="card text-white bg-info">
            <div class="card-body">
                <h5>Abrigos Ativos</h5>
                <h2>{{ abrigos_ativos }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Gráfico de Adoções por Mês -->
    <div class="col-md-8 mb-4">
        <div class="card">
            <div class="card-header">
                <h5>Adoções por Mês</h5>
            </div>
            <div class="card-body">
                <canvas id="graficoAdocoes"></canvas>
            </div>
        </div>
    </div>

    <!-- Animais por Espécie -->
    <div class="col-md-4 mb-4">
        <div class="card">
            <div class="card-header">
                <h5>Animais por Espécie</h5>
            </div>
            <div class="card-body">
                <canvas id="graficoEspecies"></canvas>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Atividades Recentes -->
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5>Atividades Recentes</h5>
            </div>
            <div class="card-body">
                <ul class="list-group">
                    {% for atividade in atividades_recentes %}
                    <li class="list-group-item">
                        <i class="bi {{ atividade.icone }}"></i>
                        {{ atividade.descricao }}
                        <span class="text-muted float-end">{{ atividade.data|data_hora_br }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</div>
```

**Scripts**: Usar Chart.js para gráficos

### 8.2. Relatórios

**Rota**: `GET /admin/relatorios`

**Tipos de Relatórios**:
1. Relatório de Adoções por Período
2. Relatório de Animais por Abrigo
3. Relatório de Solicitações por Status
4. Relatório de Desempenho de Abrigos

**Exportação**: PDF, Excel, CSV

---

## Validadores Adicionais

Adicionar em `dtos/validators.py`:

```python
def validar_sexo_animal():
    """Valida sexo do animal (Macho/Fêmea)"""
    def validator(cls, v: str) -> str:
        valores_validos = {'Macho', 'Fêmea'}
        if v not in valores_validos:
            raise ValueError(f"Sexo deve ser 'Macho' ou 'Fêmea', recebido: '{v}'")
        return v
    return validator

def validar_status_animal():
    """Valida status do animal"""
    def validator(cls, v: str) -> str:
        valores_validos = {'Disponível', 'Em Processo', 'Adotado', 'Indisponível'}
        if v not in valores_validos:
            raise ValueError(f"Status inválido: '{v}'")
        return v
    return validator

def validar_valor_monetario(minimo: float = 0.0):
    """Valida valores monetários"""
    def validator(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < minimo:
            raise ValueError(f"Valor deve ser maior ou igual a R$ {minimo:.2f}")
        return v
    return validator

def validar_data_opcional():
    """Valida datas opcionais no formato YYYY-MM-DD ou dd/mm/yyyy"""
    def validator(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == '':
            return None

        # Tentar formato ISO (YYYY-MM-DD)
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            pass

        # Tentar formato brasileiro (dd/mm/yyyy)
        try:
            dt = datetime.strptime(v, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Data deve estar no formato YYYY-MM-DD ou dd/mm/yyyy")

    return validator

def validar_status_solicitacao():
    """Valida status da solicitação"""
    def validator(cls, v: str) -> str:
        valores_validos = {'Pendente', 'Aprovada', 'Rejeitada', 'Cancelada'}
        if v not in valores_validos:
            raise ValueError(f"Status inválido: '{v}'")
        return v
    return validator
```

---

## Integração com main.py

Adicionar os novos routers em `main.py`:

```python
from routes.admin_especies_routes import router as admin_especies_router
from routes.admin_racas_routes import router as admin_racas_router
from routes.admin_abrigos_routes import router as admin_abrigos_router
from routes.admin_animais_routes import router as admin_animais_router
from routes.admin_adotantes_routes import router as admin_adotantes_router
from routes.admin_solicitacoes_routes import router as admin_solicitacoes_router
from routes.admin_visitas_routes import router as admin_visitas_router
from routes.admin_dashboard_routes import router as admin_dashboard_router

# Incluir routers
app.include_router(admin_especies_router, tags=["Admin - Espécies"])
app.include_router(admin_racas_router, tags=["Admin - Raças"])
app.include_router(admin_abrigos_router, tags=["Admin - Abrigos"])
app.include_router(admin_animais_router, tags=["Admin - Animais"])
app.include_router(admin_adotantes_router, tags=["Admin - Adotantes"])
app.include_router(admin_solicitacoes_router, tags=["Admin - Solicitações"])
app.include_router(admin_visitas_router, tags=["Admin - Visitas"])
app.include_router(admin_dashboard_router, tags=["Admin - Dashboard"])
```

---

## Checklist de Implementação

### Rotas
- [ ] admin_especies_routes.py (GET/POST listar, cadastrar, editar, excluir)
- [ ] admin_racas_routes.py (GET/POST listar, cadastrar, editar, excluir)
- [ ] admin_abrigos_routes.py (GET/POST listar, cadastrar, editar, visualizar, excluir)
- [ ] admin_animais_routes.py (GET/POST listar, cadastrar, editar, visualizar, alterar-status, excluir)
- [ ] admin_adotantes_routes.py (GET/POST listar, editar, visualizar, excluir)
- [ ] admin_solicitacoes_routes.py (GET/POST listar, visualizar, aprovar, rejeitar, cancelar)
- [ ] admin_visitas_routes.py (GET/POST listar, agendar, reagendar, cancelar)
- [ ] admin_dashboard_routes.py (GET dashboard, relatorios)

### DTOs
- [ ] especie_dto.py (CadastrarEspecieDTO, AlterarEspecieDTO)
- [ ] raca_dto.py (CadastrarRacaDTO, AlterarRacaDTO)
- [ ] abrigo_dto.py (CadastrarAbrigoDTO, AlterarAbrigoDTO)
- [ ] animal_dto.py (CadastrarAnimalDTO, AlterarAnimalDTO, AlterarStatusAnimalDTO)
- [ ] adotante_dto.py (AlterarAdotanteDTO)
- [ ] solicitacao_dto.py (AprovarSolicitacaoDTO, RejeitarSolicitacaoDTO)
- [ ] visita_dto.py (AgendarVisitaDTO, ReagendarVisitaDTO)

### Templates
- [ ] templates/admin/especies/ (listar, cadastro, editar)
- [ ] templates/admin/racas/ (listar, cadastro, editar)
- [ ] templates/admin/abrigos/ (listar, cadastro, editar, visualizar)
- [ ] templates/admin/animais/ (listar, cadastro, editar, visualizar)
- [ ] templates/admin/adotantes/ (listar, editar, visualizar)
- [ ] templates/admin/solicitacoes/ (listar, visualizar)
- [ ] templates/admin/visitas/ (listar, agendar)
- [ ] templates/admin/dashboard.html
- [ ] templates/admin/relatorios.html

### Validadores
- [ ] validar_sexo_animal()
- [ ] validar_status_animal()
- [ ] validar_valor_monetario()
- [ ] validar_data_opcional()
- [ ] validar_status_solicitacao()

### Integração
- [ ] Adicionar imports em main.py
- [ ] Incluir todos os routers
- [ ] Testar todas as rotas
- [ ] Validar autenticação e permissões

---

## Observações Finais

1. **Upload de Fotos**: Implementar utilizando o mesmo padrão de upload já existente no projeto
2. **Soft Delete**: Considerar implementar soft delete para animais e abrigos
3. **Paginação**: Adicionar paginação nas listagens com muitos registros
4. **Filtros**: Implementar filtros nas listagens (por status, data, etc.)
5. **Ordenação**: Permitir ordenação das colunas nas tabelas
6. **Busca**: Adicionar busca por nome/ID nas listagens
7. **Logs de Auditoria**: Registrar todas as ações administrativas
8. **Notificações**: Notificar abrigos sobre aprovação/rejeição de solicitações
9. **Validações**: Verificar integridade referencial antes de exclusões
10. **Performance**: Otimizar queries com índices e eager loading

---

**Próxima Fase**: Fase 3 - Rotas para Perfil Abrigo e Adotante
