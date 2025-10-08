# Sistema de Perfis (Roles)

Este guia explica como funciona o sistema de perfis do DefaultWebApp e como adicionar novos perfis ao sistema.

## Sumário
1. [Visão Geral](#visão-geral)
2. [Perfis Existentes](#perfis-existentes)
3. [Como Funciona](#como-funciona)
4. [Adicionando Novo Perfil](#adicionando-novo-perfil)
5. [Usando Perfis nas Rotas](#usando-perfis-nas-rotas)
6. [Verificação de Perfil](#verificação-de-perfil)
7. [Exemplos Práticos](#exemplos-práticos)
8. [Boas Práticas](#boas-práticas)

---

## Visão Geral

O sistema de perfis (roles) permite controlar o acesso dos usuários a diferentes partes da aplicação. É implementado através de um **Enum centralizado** que define todos os perfis disponíveis.

### Vantagens desta Abordagem
- ✅ Centralização: todos os perfis em um único lugar
- ✅ Type-safe: usa Enum do Python
- ✅ Fácil manutenção: adicionar perfil é simples
- ✅ Sem strings hardcoded: evita erros de digitação
- ✅ Autocomplete: IDEs oferecem sugestões

---

## Perfis Existentes

Atualmente, o sistema possui dois perfis:

| Perfil | Valor | Descrição | Acesso |
|--------|-------|-----------|--------|
| **ADMIN** | `"admin"` | Administrador | Acesso total ao sistema, incluindo área administrativa |
| **CLIENTE** | `"cliente"` | Usuário comum | Acesso às funcionalidades básicas |

---

## Como Funciona

### Arquivo: `util/perfis.py`

```python
from enum import Enum

class Perfil(str, Enum):
    """Enum centralizado para perfis de usuário"""
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

### Métodos Auxiliares

#### `valores()`
Retorna lista com todos os valores de perfis:
```python
Perfil.valores()  # ['admin', 'cliente']
```

#### `existe(valor)`
Verifica se um perfil existe:
```python
Perfil.existe('admin')     # True
Perfil.existe('vendedor')  # False
```

---

## Adicionando Novo Perfil

### Passo 1: Adicionar ao Enum

Edite o arquivo `util/perfis.py`:

```python
from enum import Enum

class Perfil(str, Enum):
    """Enum centralizado para perfis de usuário"""
    ADMIN = "admin"
    CLIENTE = "cliente"
    VENDEDOR = "vendedor"      # NOVO PERFIL
    MODERADOR = "moderador"    # OUTRO EXEMPLO

    @classmethod
    def valores(cls):
        """Retorna lista de todos os valores de perfis"""
        return [perfil.value for perfil in cls]

    @classmethod
    def existe(cls, valor: str) -> bool:
        """Verifica se um perfil existe"""
        return valor in cls.valores()
```

### Passo 2: Adicionar ao Seeds (Opcional)

Se quiser criar usuários com o novo perfil, edite `data/usuarios_seed.json`:

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
      "nome": "Carlos Vendedor",
      "email": "carlos@email.com",
      "senha": "Carlos@123",
      "perfil": "vendedor"
    }
  ]
}
```

### Passo 3: Atualizar Validação de DTOs (Se Houver)

Se você tem DTOs que validam perfis, atualize-os:

```python
from pydantic import BaseModel, Field, field_validator
from util.perfis import Perfil

class CriarUsuarioDTO(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: str = Field(default=Perfil.CLIENTE.value)

    @field_validator('perfil')
    @classmethod
    def validar_perfil(cls, v: str) -> str:
        if not Perfil.existe(v):
            raise ValueError(f'Perfil inválido. Use: {", ".join(Perfil.valores())}')
        return v
```

### Passo 4: Atualizar Templates Admin (Se Houver)

Se você tem formulários para criar/editar usuários, adicione o novo perfil:

```html
<select name="perfil" class="form-control">
    <option value="admin">Administrador</option>
    <option value="cliente">Cliente</option>
    <option value="vendedor">Vendedor</option>
    <option value="moderador">Moderador</option>
</select>
```

Ou dinamicamente:

```python
# No route
from util.perfis import Perfil

@router.get("/usuarios/cadastrar")
async def get_cadastrar(request: Request):
    return templates.TemplateResponse(
        "cadastrar.html",
        {
            "request": request,
            "perfis": Perfil.valores()
        }
    )
```

```html
<!-- No template -->
<select name="perfil" class="form-control">
    {% for perfil in perfis %}
    <option value="{{ perfil }}">{{ perfil.title() }}</option>
    {% endfor %}
</select>
```

---

## Usando Perfis nas Rotas

### Proteção Básica (Qualquer Usuário Autenticado)

```python
from util.auth_decorator import requer_autenticacao

@router.get("/minha-rota")
@requer_autenticacao()
async def minha_rota(request: Request, usuario_logado: dict = None):
    # Qualquer usuário autenticado pode acessar
    return templates.TemplateResponse("pagina.html", {"request": request})
```

### Proteção por Perfil Único

```python
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil

@router.get("/admin/dashboard")
@requer_autenticacao([Perfil.ADMIN.value])
async def admin_dashboard(request: Request, usuario_logado: dict = None):
    # Apenas usuários com perfil ADMIN podem acessar
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})
```

### Proteção por Múltiplos Perfis

```python
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil

@router.get("/vendas")
@requer_autenticacao([Perfil.ADMIN.value, Perfil.VENDEDOR.value])
async def vendas(request: Request, usuario_logado: dict = None):
    # Usuários com perfil ADMIN ou VENDEDOR podem acessar
    return templates.TemplateResponse("vendas.html", {"request": request})
```

---

## Verificação de Perfil

### No Código Python

```python
from util.perfis import Perfil

# Verificar se usuário é admin
if usuario_logado["perfil"] == Perfil.ADMIN.value:
    # Código específico para admin
    pass

# Verificar múltiplos perfis
if usuario_logado["perfil"] in [Perfil.ADMIN.value, Perfil.VENDEDOR.value]:
    # Código para admin ou vendedor
    pass

# Verificar se perfil existe
if Perfil.existe(usuario_logado["perfil"]):
    # Perfil válido
    pass
```

### Nos Templates Jinja2

```html
<!-- Verificar perfil específico -->
{% if usuario_logado.perfil == 'admin' %}
<a href="/admin/usuarios">Gerenciar Usuários</a>
{% endif %}

<!-- Verificar múltiplos perfis -->
{% if usuario_logado.perfil in ['admin', 'vendedor'] %}
<a href="/vendas">Vendas</a>
{% endif %}

<!-- Mostrar conteúdo diferente por perfil -->
{% if usuario_logado.perfil == 'admin' %}
    <h2>Painel Administrativo</h2>
{% elif usuario_logado.perfil == 'vendedor' %}
    <h2>Painel de Vendas</h2>
{% else %}
    <h2>Painel do Cliente</h2>
{% endif %}
```

---

## Exemplos Práticos

### Exemplo 1: CRUD Restrito a Admin

```python
from fastapi import APIRouter, Request
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil

router = APIRouter(prefix="/produtos")

# Listar: todos podem ver
@router.get("/")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: dict = None):
    produtos = produto_repo.obter_todos()
    return templates.TemplateResponse("listar.html", {"request": request, "produtos": produtos})

# Cadastrar: apenas admin
@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: dict = None):
    return templates.TemplateResponse("cadastrar.html", {"request": request})

# Alterar: apenas admin
@router.post("/{id}/alterar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_alterar(request: Request, id: int, usuario_logado: dict = None):
    # Código de alteração
    pass
```

### Exemplo 2: Acesso Condicional em Templates

```html
<!-- templates/produtos/listar.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Produtos</h1>

    <!-- Botão só para admin -->
    {% if usuario_logado.perfil == 'admin' %}
    <a href="/produtos/cadastrar" class="btn btn-primary">Novo Produto</a>
    {% endif %}

    <table class="table">
        <thead>
            <tr>
                <th>Nome</th>
                <th>Preço</th>
                <!-- Coluna de ações só para admin/vendedor -->
                {% if usuario_logado.perfil in ['admin', 'vendedor'] %}
                <th>Ações</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for produto in produtos %}
            <tr>
                <td>{{ produto.nome }}</td>
                <td>R$ {{ "%.2f"|format(produto.preco) }}</td>
                {% if usuario_logado.perfil in ['admin', 'vendedor'] %}
                <td>
                    <a href="/produtos/{{ produto.id }}/alterar" class="btn btn-sm btn-warning">Editar</a>
                    {% if usuario_logado.perfil == 'admin' %}
                    <a href="/produtos/{{ produto.id }}/excluir" class="btn btn-sm btn-danger">Excluir</a>
                    {% endif %}
                </td>
                {% endif %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

### Exemplo 3: Menu Dinâmico por Perfil

```html
<!-- templates/base.html -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="/">Sistema</a>
        <ul class="navbar-nav">
            <!-- Item para todos -->
            <li class="nav-item">
                <a class="nav-link" href="/tarefas">Minhas Tarefas</a>
            </li>

            <!-- Item para vendedor e admin -->
            {% if usuario_logado.perfil in ['admin', 'vendedor'] %}
            <li class="nav-item">
                <a class="nav-link" href="/vendas">Vendas</a>
            </li>
            {% endif %}

            <!-- Item apenas para admin -->
            {% if usuario_logado.perfil == 'admin' %}
            <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                    Admin
                </a>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="/admin/usuarios">Usuários</a></li>
                    <li><a class="dropdown-item" href="/admin/configuracoes">Configurações</a></li>
                </ul>
            </li>
            {% endif %}

            <!-- Item de perfil -->
            <li class="nav-item">
                <a class="nav-link" href="/perfil">
                    {{ usuario_logado.nome }} ({{ usuario_logado.perfil.title() }})
                </a>
            </li>
        </ul>
    </div>
</nav>
```

### Exemplo 4: Lógica de Negócio por Perfil

```python
from util.perfis import Perfil

@router.post("/tarefas/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    titulo: str = Form(...),
    usuario_logado: dict = None
):
    # Lógica diferente por perfil
    if usuario_logado["perfil"] == Perfil.ADMIN.value:
        # Admin pode criar tarefas para qualquer usuário
        usuario_id = request.form.get("usuario_id", usuario_logado["id"])
    else:
        # Usuário comum só cria para si mesmo
        usuario_id = usuario_logado["id"]

    tarefa = Tarefa(
        id=0,
        titulo=titulo,
        usuario_id=usuario_id
    )

    tarefa_repo.inserir(tarefa)
    return RedirectResponse("/tarefas")
```

---

## Boas Práticas

### ✅ Fazer

1. **Use sempre o Enum**
   ```python
   # BOM
   @requer_autenticacao([Perfil.ADMIN.value])

   # RUIM
   @requer_autenticacao(["admin"])
   ```

2. **Centralize a lógica de perfis**
   ```python
   # BOM - criar função auxiliar
   def usuario_pode_editar(usuario: dict, entidade) -> bool:
       if usuario["perfil"] == Perfil.ADMIN.value:
           return True
       return entidade.usuario_id == usuario["id"]
   ```

3. **Documente perfis necessários**
   ```python
   @router.get("/admin/dashboard")
   @requer_autenticacao([Perfil.ADMIN.value])
   async def admin_dashboard(request: Request, usuario_logado: dict = None):
       """
       Dashboard administrativo
       Requer: perfil ADMIN
       """
       pass
   ```

4. **Valide perfis ao criar usuários**
   ```python
   if not Perfil.existe(perfil):
       raise ValueError("Perfil inválido")
   ```

5. **Use nomes descritivos**
   ```python
   # BOM
   VENDEDOR = "vendedor"
   GERENTE_VENDAS = "gerente_vendas"

   # RUIM
   V = "v"
   USER2 = "user2"
   ```

### ❌ Evitar

1. **Não use strings hardcoded**
   ```python
   # RUIM
   if usuario["perfil"] == "admin":
       pass
   ```

2. **Não duplique validações**
   ```python
   # RUIM - validar duas vezes
   @requer_autenticacao([Perfil.ADMIN.value])
   async def rota(request: Request, usuario_logado: dict = None):
       if usuario_logado["perfil"] != Perfil.ADMIN.value:  # Redundante!
           raise HTTPException(403)
   ```

3. **Não deixe perfis órfãos**
   - Se adicionar um perfil, use-o
   - Se não usar mais, remova

4. **Não exponha informações sensíveis**
   ```python
   # RUIM
   if usuario["perfil"] != Perfil.ADMIN.value:
       raise HTTPException(403, detail="Você não é admin")  # Expõe informação

   # BOM
   raise HTTPException(403, detail="Acesso negado")
   ```

---

## Hierarquia de Perfis (Avançado)

Se precisar de hierarquia (admin > vendedor > cliente), crie uma função auxiliar:

```python
# util/perfis.py

class Perfil(str, Enum):
    ADMIN = "admin"
    VENDEDOR = "vendedor"
    CLIENTE = "cliente"

    @classmethod
    def nivel(cls, perfil: str) -> int:
        """Retorna nível hierárquico do perfil"""
        niveis = {
            cls.ADMIN.value: 3,
            cls.VENDEDOR.value: 2,
            cls.CLIENTE.value: 1,
        }
        return niveis.get(perfil, 0)

    @classmethod
    def tem_permissao(cls, perfil_usuario: str, perfil_requerido: str) -> bool:
        """Verifica se perfil do usuário tem permissão igual ou superior"""
        return cls.nivel(perfil_usuario) >= cls.nivel(perfil_requerido)
```

Uso:

```python
from util.perfis import Perfil

if Perfil.tem_permissao(usuario_logado["perfil"], Perfil.VENDEDOR.value):
    # Admin e Vendedor podem acessar
    pass
```

---

## Checklist para Adicionar Perfil

- [ ] Adicionar perfil ao enum em `util/perfis.py`
- [ ] Adicionar usuário seed em `data/usuarios_seed.json` (opcional)
- [ ] Atualizar DTOs de validação (se houver)
- [ ] Atualizar templates de formulário (se houver)
- [ ] Criar/atualizar rotas que usam o novo perfil
- [ ] Atualizar menu de navegação
- [ ] Documentar o novo perfil e suas permissões
- [ ] Testar criação de usuário com novo perfil
- [ ] Testar acesso às rotas protegidas
- [ ] Verificar logs de auditoria

---

## Dúvidas Frequentes

### Como permitir que apenas o dono ou admin edite algo?

```python
@router.post("/{id}/alterar")
@requer_autenticacao()
async def post_alterar(request: Request, id: int, usuario_logado: dict = None):
    tarefa = tarefa_repo.obter_por_id(id)

    # Verificar permissão
    if usuario_logado["perfil"] != Perfil.ADMIN.value:
        if tarefa.usuario_id != usuario_logado["id"]:
            raise HTTPException(403, detail="Sem permissão")

    # Continuar com alteração...
```

### Como criar perfis temporários ou dinâmicos?

Para perfis fixos, use o Enum. Para permissões mais complexas, considere um sistema de permissões granulares (ACL).

### Posso ter usuário com múltiplos perfis?

Este boilerplate suporta um perfil por usuário. Para múltiplos perfis, você precisaria:
1. Mudar campo `perfil` para `perfis` (lista)
2. Ajustar validações
3. Atualizar decorator de autenticação

---

**Dúvidas?** Consulte os exemplos no código ou entre em contato com o instrutor.
