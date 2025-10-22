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

Permite ao administrador listar, editar, visualizar e excluir adotantes.

### 5.1. Listar Adotantes

*Seguir padrão estabelecido*

**Template**: Tabela com colunas ID, Nome, Email, Renda Média, Tem Filhos, Estado de Saúde, Ações

### 5.2. Editar Adotante

*Formulário com campos do perfil do adotante*

### 5.3. Visualizar Adotante

*Detalhes completos + histórico de solicitações e adoções*

### 5.4. Excluir Adotante

*Verificar se há adoções ativas antes de excluir*

---

## 6. Gerenciar Solicitações

Permite ao administrador visualizar, aprovar, rejeitar e cancelar solicitações de adoção.

### 6.1. Listar Solicitações

#### 6.1.1. Template

**Arquivo**: `templates/admin/solicitacoes/listar.html`

*Tabela com:*
- ID Solicitação
- Adotante (nome)
- Animal (nome)
- Data Solicitação
- Status (badge colorido)
- Ações (visualizar, aprovar, rejeitar, cancelar)

*Filtros por status: Todas, Pendentes, Aprovadas, Rejeitadas*

### 6.2. Visualizar Solicitação

*Detalhes completos da solicitação + formulário de resposta*

### 6.3. Aprovar Solicitação

**DTO**: `AprovarSolicitacaoDTO` (id_solicitacao, resposta_abrigo opcional)

### 6.4. Rejeitar Solicitação

**DTO**: `RejeitarSolicitacaoDTO` (id_solicitacao, resposta_abrigo obrigatório)

---

## 7. Gerenciar Visitas

Permite ao administrador visualizar, agendar, reagendar e cancelar visitas.

### 7.1. Listar Visitas

*Tabela com adotante, animal, abrigo, data agendada, status*

### 7.2. Agendar Visita

*Formulário com seleção de adotante, animal e data/hora*

### 7.3. Reagendar Visita

*Formulário para alterar data/hora*

### 7.4. Cancelar Visita

*Confirmação via modal*

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
