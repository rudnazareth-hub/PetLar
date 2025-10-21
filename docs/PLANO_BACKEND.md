# PLANO DE IMPLEMENTAÇÃO DO BACKEND - PETLAR

**Projeto Integrador - IFES Campus Cachoeiro de Itapemirim**
**Autores:** Karoliny Sequine, Lavinia Zardo, Marina Penha, Rudson Costa
**Data:** 21 de Outubro de 2025

---

## ÍNDICE

1. [ANÁLISE DO PROJETO ATUAL](#1-análise-do-projeto-atual)
2. [COMPARAÇÃO COM A ESPECIFICAÇÃO DO PDF](#2-comparação-com-a-especificação-do-pdf)
3. [GAPS DE IMPLEMENTAÇÃO](#3-gaps-de-implementação)
4. [ARQUITETURA E PADRÕES](#4-arquitetura-e-padrões)
5. [GUIA DE IMPLEMENTAÇÃO PASSO A PASSO](#5-guia-de-implementação-passo-a-passo)
6. [CHECKLIST DE IMPLEMENTAÇÃO](#6-checklist-de-implementação)

---

## 1. ANÁLISE DO PROJETO ATUAL

### 1.1 Estado Atual do Projeto

O projeto **PetLar** está atualmente baseado no **DefaultWebApp**, um boilerplate FastAPI completo que fornece:

#### ✅ **Recursos Já Implementados**

**Sistema de Autenticação:**
- Login/Logout com sessões seguras
- Cadastro de usuários com validação de senha forte
- Recuperação de senha por email
- Sistema de perfis (Admin, Cliente, Vendedor)
- Decorator de autenticação `@requer_autenticacao()`
- Gerenciamento de usuários (CRUD completo)

**Infraestrutura de Backend:**
- FastAPI 0.115+ como framework web
- SQLite3 como banco de dados
- Padrão de camadas: Model → SQL → Repository → DTO → Routes
- Sistema de validação com Pydantic 2.0+
- Tratamento centralizado de exceções
- Logger profissional com rotação de arquivos
- Sistema de backup e restauração

**Componentes Utilitários:**
- `util/db_util.py` - Gerenciamento de conexões
- `util/security.py` - Hash de senhas com bcrypt
- `util/exceptions.py` - Exceções customizadas
- `util/exception_handlers.py` - Handlers globais
- `util/validation_util.py` - Processamento de erros
- `util/flash_messages.py` - Sistema de mensagens
- `util/foto_util.py` - Upload e crop de imagens
- `util/email_service.py` - Envio de emails (Resend.com)
- `util/seed_data.py` - Dados iniciais

**Estrutura de Diretórios:**
```
PetLar/
├── model/          # Dataclasses das entidades
├── sql/            # Comandos SQL
├── repo/           # Repositories (acesso a dados)
├── dtos/           # DTOs Pydantic para validação
├── routes/         # Rotas organizadas por módulo
├── util/           # Utilitários diversos
├── templates/      # Templates Jinja2
├── static/         # Arquivos estáticos
└── tests/          # Testes automatizados
```

#### 📋 **Models Existentes (Parcialmente Implementados)**

O projeto já possui os seguintes models criados, mas **SEM implementação completa**:

1. **usuario_model.py** ✅ - Totalmente implementado
2. **abrigo_model.py** ⚠️ - Estrutura básica apenas
3. **adocao_model.py** ⚠️ - Estrutura básica apenas
4. **adotante_model.py** ⚠️ - Estrutura básica apenas
5. **animal_model.py** ⚠️ - Estrutura básica apenas
6. **configuracao_model.py** ✅ - Implementado
7. **endereco_model.py** ⚠️ - Estrutura básica apenas
8. **especie_model.py** ⚠️ - Estrutura básica apenas
9. **raca_model.py** ⚠️ - Estrutura básica apenas
10. **solicitacao_model.py** ⚠️ - Estrutura básica apenas
11. **tarefa_model.py** ✅ - Implementado (exemplo)
12. **visita_model.py** ⚠️ - Estrutura básica apenas

#### ❌ **O Que NÃO Está Implementado**

**Repositories (repo/):**
- ❌ abrigo_repo.py
- ❌ adocao_repo.py
- ❌ adotante_repo.py
- ❌ animal_repo.py
- ❌ endereco_repo.py
- ❌ especie_repo.py
- ❌ raca_repo.py
- ❌ solicitacao_repo.py
- ❌ visita_repo.py

**SQL (sql/):**
- ❌ abrigo_sql.py
- ❌ adocao_sql.py
- ❌ adotante_sql.py
- ❌ animal_sql.py
- ❌ endereco_sql.py
- ❌ especie_sql.py
- ❌ raca_sql.py
- ❌ solicitacao_sql.py
- ❌ visita_sql.py

**DTOs (dtos/):**
- ❌ abrigo_dto.py
- ❌ adocao_dto.py
- ❌ adotante_dto.py
- ❌ animal_dto.py
- ❌ endereco_dto.py
- ❌ especie_dto.py
- ❌ raca_dto.py
- ❌ solicitacao_dto.py
- ❌ visita_dto.py

**Routes (routes/):**
- ❌ abrigo_routes.py
- ❌ adocao_routes.py
- ❌ adotante_routes.py
- ❌ animal_routes.py
- ❌ especie_routes.py
- ❌ raca_routes.py
- ❌ solicitacao_routes.py
- ❌ visita_routes.py

---

## 2. COMPARAÇÃO COM A ESPECIFICAÇÃO DO PDF

### 2.1 Análise do Diagrama de Entidades e Relacionamentos

Segundo o PDF (página 27), o sistema PetLar deve implementar as seguintes entidades e relacionamentos:

#### **Entidades Principais:**

**1. Usuario**
- PK: idUsuario
- Atributos: Nome, DataNascimento, NumeroDocumento, Email, Telefone, Senha, Perfil, Confirmado, DataCadastro
- ✅ **Status:** Parcialmente implementado (falta DataNascimento, NumeroDocumento, Telefone, Confirmado)

**2. Endereco**
- PK: idEndereco
- FK: idUsuario
- Atributos: Titulo, Logradouro, Numero, Complemento, Bairro, Cidade, UF, CEP
- ⚠️ **Status:** Model existe, mas sem implementação completa

**3. Abrigo**
- PK: idAbrigo
- Atributos: Responsavel, Descricao, DataAbertura, DataMembros
- ⚠️ **Status:** Model incompleto (falta Descricao e DataMembros)

**4. Adotante**
- PK: idAdotante
- Atributos: RendaMedia, TemFilhos, EstadoDeSaude
- ⚠️ **Status:** Model existe mas sem repos/DTOs/routes

**5. Especie**
- PK: idEspecie
- Atributos: Nome, Descricao
- ⚠️ **Status:** Model básico existe

**6. Raca**
- PK: idRaca
- FK: idEspecie
- Atributos: Nome, Descricao, Temperamento, ExpectativaDeVida, Porte
- ⚠️ **Status:** Model existe com relacionamento

**7. Animal**
- PK: idAnimal
- FK: idRaca, idAbrigo
- Atributos: DataNascimento, DataEntrada, Observacoes
- ⚠️ **Status:** Model existe com relacionamentos

**8. Solicitacao**
- PK: idSolicitacao
- FK: idAdotante, idAnimal
- Atributos: DataSolicitacao, Status, Observacoes
- ⚠️ **Status:** Model existe

**9. Visita**
- PK: idVisita
- FK: idAdotante, idAbrigo
- Atributos: DataAgendada, Observacoes, Status
- ⚠️ **Status:** Model existe

**10. Adocao**
- PK: idAdocao
- FK: idAdotante, idAnimal
- Atributos: DataSolicitacao, DataAdocao, Status, Observacoes
- ⚠️ **Status:** Model existe

#### **Relacionamentos Identificados:**

```
Usuario 1 ──── N Endereco
Usuario 1 ──── 1 Adotante (perfil específico)
Usuario 1 ──── 1 Abrigo (perfil específico)

Especie 1 ──── N Raca
Raca 1 ──── N Animal

Abrigo 1 ──── N Animal
Abrigo 1 ──── N Visita

Adotante N ──── N Animal (via Solicitacao)
Adotante 1 ──── N Visita
Adotante 1 ──── N Adocao

Animal 1 ──── N Solicitacao
Animal 1 ──── 1 Adocao (0..1)
```

### 2.2 Análise dos Requisitos Funcionais

#### **RF de Alta Prioridade (do PDF):**

**RF8:** Adotante pode buscar e realizar adoção responsável
- ❌ **Backend:** Não implementado
- **Necessário:** Routes de busca com filtros, lógica de recomendação

**RF9:** Adotante pode manifestar interesse e iniciar processo de adoção
- ❌ **Backend:** Não implementado
- **Necessário:** CRUD de Solicitacao, validações, notificações

**RF10:** Adotante pode acompanhar status de candidaturas
- ❌ **Backend:** Não implementado
- **Necessário:** Endpoints de listagem e detalhes de solicitações

**RF11:** ONGs podem registrar animais disponíveis
- ❌ **Backend:** Não implementado
- **Necessário:** CRUD completo de Animal com upload de fotos

**RF12:** ONGs podem analisar solicitações de adoção
- ❌ **Backend:** Não implementado
- **Necessário:** Endpoints de análise, aprovação/rejeição

#### **RF de Média Prioridade:**

**RF13-15:** Cadastro de adotante, agendamento, comunicação
- ❌ **Backend:** Parcialmente (apenas cadastro de usuário genérico)
- **Necessário:** Separar perfis, adicionar campos específicos

**RF16-18:** Cadastro de ONG, agendamento, comunicação
- ❌ **Backend:** Não implementado
- **Necessário:** Implementar perfil Abrigo com campos específicos

#### **RF de Baixa Prioridade:**

**RF19:** Acompanhamento pós-adoção
- ❌ **Backend:** Não implementado
- **Necessário:** Sistema de relatórios e feedback

**RF20:** Doações financeiras
- ❌ **Backend:** Não implementado
- **Necessário:** Integração com gateway de pagamento (fora do escopo inicial)

**RF21:** Acompanhamento de bem-estar
- ❌ **Backend:** Não implementado
- **Necessário:** Sistema de solicitação de relatórios

### 2.3 Análise dos Casos de Uso

#### **Perfil Anônimo (PDF página 23):**
- ✅ Realizar Login - Implementado
- ❌ Cadastrar-se como adotante - Parcial (cadastro genérico existe)
- ❌ Buscar animais - Não implementado
- ❌ Ver detalhes do animal - Não implementado
- ❌ Visualizar campanhas e eventos - Não implementado

#### **Perfil Usuário (PDF página 24):**
- ✅ Realizar Logout - Implementado
- ✅ Alterar Senha - Implementado
- ✅ Alterar Dados de Perfil - Implementado

#### **Perfil Administrador (PDF página 24):**
- ✅ Gerenciar usuários - Implementado
- ❌ Gerenciar adotantes - Não implementado
- ❌ Gerenciar instituições - Não implementado
- ❌ Gerenciar animais - Não implementado
- ❌ Gerenciar anúncios - Não implementado
- ❌ Gerenciar doações - Não implementado
- ✅ Realizar/Restaurar Backup - Implementado
- ❌ Visualizar/Responder mensagens - Não implementado

#### **Perfil Abrigo (PDF página 25):**
- ❌ Cadastrar animal para adoção - Não implementado
- ❌ Analisar solicitações de adoção - Não implementado
- ❌ Agendar entrevista/visita - Não implementado
- ❌ Comunicar-se com adotante - Não implementado
- ❌ Solicitar acompanhamento pós-adoção - Não implementado
- ❌ Receber e administrar doações - Não implementado
- ❌ Gerar relatórios de adoções - Não implementado
- ❌ Registrar históricos dos animais - Não implementado
- ❌ Configurar critérios de adoção - Não implementado

#### **Perfil Adotante (PDF página 26):**
- ❌ Cadastrar-se - Parcial (só cadastro básico)
- ❌ Solicitar adoção - Não implementado
- ❌ Realizar adoção - Não implementado
- ❌ Acompanhar candidaturas - Não implementado
- ❌ Agendar visitas - Não implementado
- ❌ Comunicar-se com abrigos - Não implementado
- ❌ Registrar acompanhamento - Não implementado
- ❌ Cancelar solicitação de adoção - Não implementado
- ❌ Alterar agendamento de visita - Não implementado

---

## 3. GAPS DE IMPLEMENTAÇÃO

### 3.1 Resumo Executivo dos Gaps

| Componente | Existente | Necessário | Gap % |
|------------|-----------|------------|-------|
| **Models** | 12 criados | 12 completos | 25% |
| **SQL** | 3 arquivos | 12 arquivos | 75% |
| **Repositories** | 3 arquivos | 12 arquivos | 75% |
| **DTOs** | 5 arquivos | 18+ arquivos | 72% |
| **Routes** | 9 arquivos | 15+ arquivos | 40% |
| **Funcionalidades** | 15% | 100% | 85% |

### 3.2 Priorização de Implementação

#### **PRIORIDADE 1 - FUNDAÇÃO (Essencial para o sistema funcionar)**

1. **Ajustar Sistema de Perfis**
   - Adicionar perfis: `ABRIGO` e `ADOTANTE` ao enum Perfil
   - Criar relacionamento Usuario ↔ Abrigo (1:1)
   - Criar relacionamento Usuario ↔ Adotante (1:1)
   - Ajustar validações e decorators

2. **Implementar Entidades Base**
   - **Especie**: SQL + Repo + DTO + Routes (CRUD simples)
   - **Raca**: SQL + Repo + DTO + Routes (CRUD com FK para Especie)
   - **Endereco**: SQL + Repo + DTO + Routes (CRUD com FK para Usuario)

3. **Completar Model Usuario**
   - Adicionar campos: data_nascimento, numero_documento, telefone, confirmado
   - Criar migrations/alterações de tabela
   - Atualizar DTOs e validações

#### **PRIORIDADE 2 - CORE BUSINESS (Coração do sistema)**

4. **Implementar Entidade Abrigo**
   - Completar model (adicionar descricao, data_membros)
   - SQL + Repo + DTO + Routes
   - Relacionamento com Usuario (idAbrigo = idUsuario onde perfil = 'Abrigo')
   - CRUD completo de abrigos

5. **Implementar Entidade Adotante**
   - SQL + Repo + DTO + Routes
   - Relacionamento com Usuario (idAdotante = idUsuario onde perfil = 'Adotante')
   - CRUD completo de adotantes

6. **Implementar Entidade Animal**
   - SQL + Repo + DTO + Routes
   - Upload de fotos (reutilizar foto_util.py)
   - Busca avançada com filtros
   - Listagem pública e privada

#### **PRIORIDADE 3 - FLUXO DE ADOÇÃO (Processo principal)**

7. **Implementar Entidade Solicitacao**
   - SQL + Repo + DTO + Routes
   - POST /solicitacoes/criar (adotante manifesta interesse)
   - GET /solicitacoes/listar (adotante vê suas solicitações)
   - GET /solicitacoes/recebidas (abrigo vê solicitações)
   - PUT /solicitacoes/{id}/analisar (abrigo aprova/rejeita)

8. **Implementar Entidade Visita**
   - SQL + Repo + DTO + Routes
   - POST /visitas/agendar
   - GET /visitas/listar
   - PUT /visitas/{id}/reagendar
   - PUT /visitas/{id}/cancelar
   - PUT /visitas/{id}/confirmar

9. **Implementar Entidade Adocao**
   - SQL + Repo + DTO + Routes
   - POST /adocoes/finalizar (criar adoção após aprovação)
   - GET /adocoes/listar
   - PUT /adocoes/{id}/atualizar-status

#### **PRIORIDADE 4 - RECURSOS EXTRAS (Melhorias)**

10. **Sistema de Busca e Filtros**
    - Endpoint GET /animais/buscar com query params
    - Filtros: especie, raca, porte, idade, localização
    - Paginação

11. **Sistema de Notificações**
    - Notificação por email quando:
      - Solicitação criada (para abrigo)
      - Solicitação aprovada/rejeitada (para adotante)
      - Visita agendada
      - Adoção finalizada

12. **Relatórios e Dashboards**
    - GET /relatorios/adocoes (abrigo)
    - GET /relatorios/animais-disponiveis
    - GET /relatorios/solicitacoes-pendentes

### 3.3 Detalhamento dos Ajustes Necessários

#### **A. Ajustes em Arquivos Existentes**

**`util/perfis.py`** - Adicionar novos perfis:
```python
# ANTES:
ADMIN = "Administrador"
CLIENTE = "Cliente"
VENDEDOR = "Vendedor"

# DEPOIS:
ADMIN = "Administrador"
ABRIGO = "Abrigo"
ADOTANTE = "Adotante"
```

**`model/usuario_model.py`** - Adicionar campos:
```python
# Adicionar:
data_nascimento: Optional[str] = None
numero_documento: Optional[str] = None  # CPF/CNPJ
telefone: Optional[str] = None
confirmado: bool = False
```

**`model/abrigo_model.py`** - Completar model:
```python
# Adicionar:
descricao: Optional[str] = None
data_membros: Optional[str] = None  # JSON com membros da equipe
```

#### **B. Novos Arquivos a Criar**

Total de arquivos novos: **36 arquivos**

**SQL (9 arquivos):**
- especie_sql.py
- raca_sql.py
- endereco_sql.py
- abrigo_sql.py
- adotante_sql.py
- animal_sql.py
- solicitacao_sql.py
- visita_sql.py
- adocao_sql.py

**Repositories (9 arquivos):**
- especie_repo.py
- raca_repo.py
- endereco_repo.py
- abrigo_repo.py
- adotante_repo.py
- animal_repo.py
- solicitacao_repo.py
- visita_repo.py
- adocao_repo.py

**DTOs (9 arquivos principais + variações):**
- especie_dto.py
- raca_dto.py
- endereco_dto.py
- abrigo_dto.py
- adotante_dto.py
- animal_dto.py
- solicitacao_dto.py
- visita_dto.py
- adocao_dto.py

**Routes (9 arquivos):**
- especie_routes.py (admin apenas)
- raca_routes.py (admin apenas)
- endereco_routes.py (usuário logado)
- abrigo_routes.py (admin + abrigo)
- adotante_routes.py (admin + adotante)
- animal_routes.py (público + abrigo + admin)
- solicitacao_routes.py (adotante + abrigo)
- visita_routes.py (adotante + abrigo)
- adocao_routes.py (abrigo + admin)

---

## 4. ARQUITETURA E PADRÕES

### 4.1 Padrão de Camadas (Já Estabelecido no Projeto)

O projeto segue uma arquitetura em camadas bem definida:

```
┌─────────────────────────────────────────┐
│         LAYER 1: ROUTES                 │  ← Endpoints HTTP
│  (FastAPI Routes - Controllers)        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         LAYER 2: DTOs                   │  ← Validação Pydantic
│  (Data Transfer Objects)                │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         LAYER 3: REPOSITORIES           │  ← Lógica de Acesso
│  (Business Logic + Data Access)         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         LAYER 4: SQL                    │  ← Queries SQL Puras
│  (SQL Statements)                       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         LAYER 5: DATABASE               │  ← SQLite3
│  (util/db_util.py - Connection Pool)    │
└─────────────────────────────────────────┘
                  ↑
┌─────────────────────────────────────────┐
│         LAYER 0: MODELS                 │  ← Dataclasses
│  (Domain Entities - @dataclass)         │
└─────────────────────────────────────────┘
```

**Fluxo de Dados:**
1. **Request** → Route recebe dados do formulário/JSON
2. **Validation** → DTO valida e transforma dados
3. **Business Logic** → Repository executa regras de negócio
4. **SQL Execution** → SQL commands são executados
5. **Response** → Model é convertido para resposta HTTP

### 4.2 Convenções de Nomenclatura

**Models (Dataclasses):**
```python
# Arquivo: model/nome_model.py
@dataclass
class NomeEntidade:
    id_nome_entidade: int  # PK sempre com prefixo id_
    campo: tipo
```

**SQL:**
```python
# Arquivo: sql/nome_sql.py
CRIAR_TABELA = """CREATE TABLE IF NOT EXISTS nome..."""
INSERIR = """INSERT INTO nome..."""
OBTER_TODOS = """SELECT * FROM nome..."""
OBTER_POR_ID = """SELECT * FROM nome WHERE id = ?"""
ATUALIZAR = """UPDATE nome SET..."""
EXCLUIR = """DELETE FROM nome WHERE id = ?"""
```

**Repositories:**
```python
# Arquivo: repo/nome_repo.py
def criar_tabela() -> None: ...
def inserir(entidade: Entidade) -> int: ...
def obter_todos() -> List[Entidade]: ...
def obter_por_id(id: int) -> Optional[Entidade]: ...
def atualizar(entidade: Entidade) -> None: ...
def excluir(id: int) -> None: ...
```

**DTOs:**
```python
# Arquivo: dtos/nome_dto.py
class NomeCriarDTO(BaseModel):  # Para POST
    campo: tipo
    _validar_campo = field_validator('campo')(validador())

class NomeAlterarDTO(BaseModel):  # Para PUT
    campo: tipo
```

**Routes:**
```python
# Arquivo: routes/nome_routes.py
router = APIRouter(prefix="/nomes")

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: dict): ...

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def cadastrar_post(request: Request, ...): ...
```

### 4.3 Padrão de Tratamento de Erros

O projeto utiliza um sistema centralizado de tratamento de erros:

```python
from util.exceptions import FormValidationError
from pydantic import ValidationError

try:
    dto = AlgoDTO(campo=valor)
    # lógica...
except ValidationError as e:
    raise FormValidationError(
        validation_error=e,
        template_path="path/template.html",  # Não usado no backend puro
        dados_formulario=dados,
        campo_padrao="campo"
    )
```

Para **backend puro (APIs JSON)**, o handler já retorna automaticamente:
```json
{
  "detail": "Erro de validação",
  "errors": {
    "campo": ["Mensagem de erro"]
  }
}
```

### 4.4 Padrão de Relacionamentos

**Relacionamento 1:N (Um para Muitos):**
```python
# Model Pai
@dataclass
class Especie:
    id_especie: int
    nome: str

# Model Filho
@dataclass
class Raca:
    id_raca: int
    id_especie: int  # FK
    nome: str
    especie: Optional[Especie]  # Relacionamento opcional

# Repository - Join
def obter_por_id(id: int) -> Optional[Raca]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                r.id_raca, r.id_especie, r.nome,
                e.id_especie, e.nome as especie_nome
            FROM raca r
            LEFT JOIN especie e ON r.id_especie = e.id_especie
            WHERE r.id_raca = ?
        """, (id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Raca(
            id_raca=row['id_raca'],
            id_especie=row['id_especie'],
            nome=row['nome'],
            especie=Especie(
                id_especie=row['id_especie'],
                nome=row['especie_nome']
            ) if row['id_especie'] else None
        )
```

**Relacionamento 1:1 (Um para Um):**
```python
# Usuario 1:1 Adotante
# Ambos compartilham o mesmo ID

# SQL
CREATE TABLE adotante (
    id_adotante INTEGER PRIMARY KEY,  -- Mesmo ID do usuário
    renda_media REAL,
    tem_filhos INTEGER,
    FOREIGN KEY (id_adotante) REFERENCES usuario(id)
)
```

**Relacionamento N:M (Muitos para Muitos):**
```python
# Adotante N:M Animal (via Solicitacao)

# SQL
CREATE TABLE solicitacao (
    id_solicitacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_animal INTEGER NOT NULL,
    data_solicitacao DATETIME,
    status TEXT,
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_animal) REFERENCES animal(id_animal)
)
```

### 4.5 Padrão de Validações

O projeto possui 15+ validadores reutilizáveis em `dtos/validators.py`:

```python
from dtos.validators import (
    validar_email,
    validar_cpf,
    validar_telefone_br,
    validar_cep,
    validar_data,
    validar_inteiro_positivo,
    validar_decimal_positivo
)

class AdotanteDTO(BaseModel):
    email: str
    cpf: str
    telefone: str
    renda_media: float

    _validar_email = field_validator('email')(validar_email())
    _validar_cpf = field_validator('cpf')(validar_cpf())
    _validar_telefone = field_validator('telefone')(validar_telefone_br())
    _validar_renda = field_validator('renda_media')(validar_decimal_positivo())
```

### 4.6 Padrão de Autenticação e Autorização

```python
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil

# Apenas Admin
@router.get("/admin-only")
@requer_autenticacao([Perfil.ADMIN.value])
async def admin_only(request: Request, usuario_logado: dict):
    # usuario_logado contém: id, nome, email, perfil
    pass

# Admin ou Abrigo
@router.get("/abrigo-area")
@requer_autenticacao([Perfil.ADMIN.value, Perfil.ABRIGO.value])
async def abrigo_area(request: Request, usuario_logado: dict):
    pass

# Qualquer usuário autenticado
@router.get("/privado")
@requer_autenticacao()  # Sem lista = qualquer perfil
async def privado(request: Request, usuario_logado: dict):
    pass
```

---

## 5. GUIA DE IMPLEMENTAÇÃO PASSO A PASSO

Esta seção apresenta um guia completo e didático para implementar cada componente do backend do PetLar. Cada passo indica claramente:
- ✏️ Arquivos a serem **modificados**
- ➕ Arquivos a serem **criados**
- 📝 Código de exemplo simplificado

---

### 5.1 AJUSTES DE INFRAESTRUTURA

#### PASSO 1: Ajustar Sistema de Perfis

**Objetivo:** Adicionar os perfis `ABRIGO` e `ADOTANTE` e remover perfis não utilizados.

**✏️ Arquivo a Modificar:** `util/perfis.py`

**O que fazer:**
1. Abrir o arquivo `util/perfis.py`
2. Localizar a seção de perfis do sistema
3. Substituir os perfis atuais pelos perfis do PetLar

**Código antes:**
```python
class Perfil(str, Enum):
    # PERFIS DO SEU SISTEMA #####################################
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"
    # FIM DOS PERFIS ############################################
```

**Código depois:**
```python
class Perfil(str, Enum):
    # PERFIS DO SEU SISTEMA #####################################
    ADMIN = "Administrador"
    ABRIGO = "Abrigo"
    ADOTANTE = "Adotante"
    # FIM DOS PERFIS ############################################
```

**Resultado:** O sistema agora reconhece 3 perfis: Administrador, Abrigo e Adotante.

---

#### PASSO 2: Atualizar Model Usuario

**Objetivo:** Adicionar campos necessários conforme o diagrama ER do PDF.

**✏️ Arquivo a Modificar:** `model/usuario_model.py`

**O que fazer:**
1. Adicionar campos: `data_nascimento`, `numero_documento`, `telefone`, `confirmado`
2. Manter compatibilidade com campos existentes

**Código antes:**
```python
@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    token_redefinicao: Optional[str] = None
    data_token: Optional[str] = None
    data_cadastro: Optional[str] = None
```

**Código depois:**
```python
@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    data_nascimento: Optional[str] = None  # Formato: YYYY-MM-DD
    numero_documento: Optional[str] = None  # CPF ou CNPJ
    telefone: Optional[str] = None  # Formato: (00) 00000-0000
    confirmado: bool = False  # Email confirmado?
    token_redefinicao: Optional[str] = None
    data_token: Optional[str] = None
    data_cadastro: Optional[str] = None
```

---

#### PASSO 3: Atualizar SQL de Usuario

**✏️ Arquivo a Modificar:** `sql/usuario_sql.py`

**O que fazer:**
1. Alterar o comando `CRIAR_TABELA` para incluir novos campos
2. Atualizar `INSERIR` e `ATUALIZAR` para incluir novos campos

**Adicionar ao CRIAR_TABELA:**
```python
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL,
    data_nascimento TEXT,
    numero_documento TEXT,
    telefone TEXT,
    confirmado INTEGER DEFAULT 0,
    token_redefinicao TEXT,
    data_token TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""
```

**Atualizar INSERIR:**
```python
INSERIR = """
INSERT INTO usuario (
    nome, email, senha, perfil,
    data_nascimento, numero_documento, telefone, confirmado
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""
```

**Atualizar ATUALIZAR:**
```python
ATUALIZAR = """
UPDATE usuario
SET nome = ?, email = ?, perfil = ?,
    data_nascimento = ?, numero_documento = ?, telefone = ?
WHERE id = ?
"""
```

---

#### PASSO 4: Atualizar Repository de Usuario

**✏️ Arquivo a Modificar:** `repo/usuario_repo.py`

**O que fazer:**
1. Atualizar função `_row_to_usuario()` para mapear novos campos
2. Atualizar `inserir()` para incluir novos parâmetros
3. Atualizar `atualizar()` para incluir novos parâmetros

**Atualizar `_row_to_usuario()`:**
```python
def _row_to_usuario(row) -> Usuario:
    return Usuario(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        senha=row["senha"],
        perfil=row["perfil"],
        data_nascimento=row["data_nascimento"],
        numero_documento=row["numero_documento"],
        telefone=row["telefone"],
        confirmado=bool(row["confirmado"]),
        token_redefinicao=row["token_redefinicao"],
        data_token=row["data_token"],
        data_cadastro=row["data_cadastro"]
    )
```

**Atualizar `inserir()`:**
```python
def inserir(usuario: Usuario) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            usuario.nome,
            usuario.email,
            usuario.senha,
            usuario.perfil,
            usuario.data_nascimento,
            usuario.numero_documento,
            usuario.telefone,
            1 if usuario.confirmado else 0
        ))
        return cursor.lastrowid
```

**Atualizar `atualizar()`:**
```python
def atualizar(usuario: Usuario) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            usuario.nome,
            usuario.email,
            usuario.perfil,
            usuario.data_nascimento,
            usuario.numero_documento,
            usuario.telefone,
            usuario.id
        ))
```

---

#### PASSO 5: Atualizar DTOs de Usuario

**✏️ Arquivo a Modificar:** `dtos/usuario_dto.py`

**O que fazer:**
1. Adicionar validações para novos campos

**Adicionar imports:**
```python
from dtos.validators import (
    validar_cpf,
    validar_telefone_br,
    validar_data,
    validar_data_passada
)
```

**Atualizar DTO de Cadastro:**
```python
class UsuarioCadastroDTO(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: str
    data_nascimento: Optional[str] = None
    numero_documento: Optional[str] = None
    telefone: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_email = field_validator('email')(validar_email())
    _validar_senha = field_validator('senha')(validar_senha_forte())
    _validar_perfil = field_validator('perfil')(lambda v: Perfil.validar(v))

    # Novos validadores
    _validar_data_nascimento = field_validator('data_nascimento')(
        validar_data_passada(campo='Data de Nascimento', obrigatorio=False)
    )
    _validar_cpf = field_validator('numero_documento')(
        validar_cpf(obrigatorio=False)
    )
    _validar_telefone = field_validator('telefone')(
        validar_telefone_br(obrigatorio=False)
    )
```

---

### 5.2 ENTIDADES BASE

#### PASSO 6: Implementar Entidade ESPECIE (Completo)

A entidade Especie é a mais simples e serve como exemplo base.

**➕ Arquivo a Criar:** `sql/especie_sql.py`

```python
"""
Comandos SQL para a tabela especie.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS especie (
    id_especie INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT
)
"""

INSERIR = """
INSERT INTO especie (nome, descricao)
VALUES (?, ?)
"""

OBTER_TODOS = """
SELECT id_especie, nome, descricao
FROM especie
ORDER BY nome
"""

OBTER_POR_ID = """
SELECT id_especie, nome, descricao
FROM especie
WHERE id_especie = ?
"""

OBTER_POR_NOME = """
SELECT id_especie, nome, descricao
FROM especie
WHERE nome = ?
"""

ATUALIZAR = """
UPDATE especie
SET nome = ?, descricao = ?
WHERE id_especie = ?
"""

EXCLUIR = """
DELETE FROM especie
WHERE id_especie = ?
"""

# Query para verificar se especie tem raças vinculadas
CONTAR_RACAS = """
SELECT COUNT(*) as total
FROM raca
WHERE id_especie = ?
"""
```

**➕ Arquivo a Criar:** `repo/especie_repo.py`

```python
"""
Repository para operações com a tabela especie.
"""

from typing import List, Optional
from model.especie_model import Especie
from sql.especie_sql import *
from util.db_util import get_connection


def _row_to_especie(row) -> Especie:
    """Converte uma linha do banco em objeto Especie."""
    return Especie(
        id_especie=row["id_especie"],
        nome=row["nome"],
        descricao=row["descricao"]
    )


def criar_tabela() -> None:
    """Cria a tabela especie se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(especie: Especie) -> int:
    """
    Insere uma nova espécie e retorna o ID gerado.

    Args:
        especie: Objeto Especie a ser inserido

    Returns:
        ID da espécie inserida
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            especie.nome,
            especie.descricao
        ))
        return cursor.lastrowid


def obter_todos() -> List[Especie]:
    """
    Retorna todas as espécies cadastradas.

    Returns:
        Lista de objetos Especie
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_especie(row) for row in cursor.fetchall()]


def obter_por_id(id_especie: int) -> Optional[Especie]:
    """
    Busca uma espécie pelo ID.

    Args:
        id_especie: ID da espécie

    Returns:
        Objeto Especie ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_especie,))
        row = cursor.fetchone()
        return _row_to_especie(row) if row else None


def obter_por_nome(nome: str) -> Optional[Especie]:
    """
    Busca uma espécie pelo nome.

    Args:
        nome: Nome da espécie

    Returns:
        Objeto Especie ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_NOME, (nome,))
        row = cursor.fetchone()
        return _row_to_especie(row) if row else None


def atualizar(especie: Especie) -> None:
    """
    Atualiza uma espécie existente.

    Args:
        especie: Objeto Especie com dados atualizados
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            especie.nome,
            especie.descricao,
            especie.id_especie
        ))


def excluir(id_especie: int) -> None:
    """
    Exclui uma espécie pelo ID.

    Args:
        id_especie: ID da espécie a ser excluída

    Raises:
        Exception: Se a espécie tiver raças vinculadas
    """
    # Verificar se tem raças vinculadas
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_RACAS, (id_especie,))
        total = cursor.fetchone()["total"]

        if total > 0:
            raise Exception(
                f"Não é possível excluir esta espécie. "
                f"Existem {total} raça(s) vinculada(s)."
            )

        cursor.execute(EXCLUIR, (id_especie,))


def existe_nome(nome: str, id_excluir: Optional[int] = None) -> bool:
    """
    Verifica se já existe uma espécie com o nome informado.

    Args:
        nome: Nome a verificar
        id_excluir: ID a excluir da verificação (para updates)

    Returns:
        True se existe, False caso contrário
    """
    especie = obter_por_nome(nome)
    if not especie:
        return False
    if id_excluir and especie.id_especie == id_excluir:
        return False
    return True
```

**➕ Arquivo a Criar:** `dtos/especie_dto.py`

```python
"""
DTOs para validação de dados da entidade Especie.
"""

from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria


class EspecieCriarDTO(BaseModel):
    """DTO para criação de espécie."""
    nome: str
    descricao: str

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )


class EspecieAlterarDTO(BaseModel):
    """DTO para alteração de espécie."""
    nome: str
    descricao: str

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
```

**➕ Arquivo a Criar:** `routes/especie_routes.py`

```python
"""
Rotas para gerenciamento de espécies.
Apenas administradores podem gerenciar espécies.
"""

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import ValidationError

from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.exceptions import FormValidationError
from util.perfis import Perfil

import repo.especie_repo as especie_repo
from dtos.especie_dto import EspecieCriarDTO, EspecieAlterarDTO
from model.especie_model import Especie

router = APIRouter(prefix="/especies")


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: dict):
    """Lista todas as espécies (apenas admin)."""
    especies = especie_repo.obter_todos()
    return JSONResponse({
        "success": True,
        "data": [
            {
                "id_especie": e.id_especie,
                "nome": e.nome,
                "descricao": e.descricao
            }
            for e in especies
        ]
    })


@router.get("/{id_especie}")
@requer_autenticacao([Perfil.ADMIN.value])
async def obter(request: Request, id_especie: int, usuario_logado: dict):
    """Obtém uma espécie por ID."""
    especie = especie_repo.obter_por_id(id_especie)
    if not especie:
        return JSONResponse(
            {"success": False, "message": "Espécie não encontrada"},
            status_code=404
        )

    return JSONResponse({
        "success": True,
        "data": {
            "id_especie": especie.id_especie,
            "nome": especie.nome,
            "descricao": especie.descricao
        }
    })


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def cadastrar(
    request: Request,
    usuario_logado: dict,
    nome: str = Form(...),
    descricao: str = Form(...)
):
    """Cadastra uma nova espécie."""
    try:
        # Validar dados
        dto = EspecieCriarDTO(nome=nome, descricao=descricao)

        # Verificar se já existe
        if especie_repo.existe_nome(dto.nome):
            return JSONResponse(
                {"success": False, "message": "Já existe uma espécie com este nome"},
                status_code=400
            )

        # Criar espécie
        especie = Especie(
            id_especie=0,  # Será gerado pelo banco
            nome=dto.nome,
            descricao=dto.descricao
        )

        id_criado = especie_repo.inserir(especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie cadastrada com sucesso",
            "data": {"id_especie": id_criado}
        }, status_code=201)

    except ValidationError as e:
        return JSONResponse(
            {"success": False, "errors": e.errors()},
            status_code=400
        )


@router.put("/{id_especie}")
@requer_autenticacao([Perfil.ADMIN.value])
async def atualizar(
    request: Request,
    id_especie: int,
    usuario_logado: dict,
    nome: str = Form(...),
    descricao: str = Form(...)
):
    """Atualiza uma espécie existente."""
    try:
        # Verificar se existe
        especie_existente = especie_repo.obter_por_id(id_especie)
        if not especie_existente:
            return JSONResponse(
                {"success": False, "message": "Espécie não encontrada"},
                status_code=404
            )

        # Validar dados
        dto = EspecieAlterarDTO(nome=nome, descricao=descricao)

        # Verificar nome duplicado
        if especie_repo.existe_nome(dto.nome, id_excluir=id_especie):
            return JSONResponse(
                {"success": False, "message": "Já existe uma espécie com este nome"},
                status_code=400
            )

        # Atualizar
        especie = Especie(
            id_especie=id_especie,
            nome=dto.nome,
            descricao=dto.descricao
        )

        especie_repo.atualizar(especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie atualizada com sucesso"
        })

    except ValidationError as e:
        return JSONResponse(
            {"success": False, "errors": e.errors()},
            status_code=400
        )


@router.delete("/{id_especie}")
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir(request: Request, id_especie: int, usuario_logado: dict):
    """Exclui uma espécie."""
    try:
        # Verificar se existe
        especie = especie_repo.obter_por_id(id_especie)
        if not especie:
            return JSONResponse(
                {"success": False, "message": "Espécie não encontrada"},
                status_code=404
            )

        # Tentar excluir
        especie_repo.excluir(id_especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie excluída com sucesso"
        })

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=400
        )
```

**✏️ Registrar no `main.py`:**

```python
# No topo do arquivo, adicionar imports:
import repo.especie_repo as especie_repo
from routes import especie_routes

# Na seção de criação de tabelas, adicionar:
especie_repo.criar_tabela()
logger.info("Tabela 'especie' criada/verificada")

# Na seção de routers, adicionar:
app.include_router(especie_routes.router, tags=["Espécies"])
logger.info("Router de espécies incluído")
```

---

#### PASSO 7: Implementar Entidade RACA (Com Relacionamento)

A entidade Raca possui relacionamento com Especie (N:1).

**➕ Arquivo a Criar:** `sql/raca_sql.py`

```python
"""
Comandos SQL para a tabela raca.
Relacionamento: Raca N:1 Especie
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS raca (
    id_raca INTEGER PRIMARY KEY AUTOINCREMENT,
    id_especie INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    temperamento TEXT,
    expectativa_de_vida TEXT,
    porte TEXT,
    FOREIGN KEY (id_especie) REFERENCES especie(id_especie),
    UNIQUE(id_especie, nome)
)
"""

INSERIR = """
INSERT INTO raca (
    id_especie, nome, descricao,
    temperamento, expectativa_de_vida, porte
)
VALUES (?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT
    r.id_raca, r.id_especie, r.nome, r.descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id_especie as especie_id, e.nome as especie_nome, e.descricao as especie_descricao
FROM raca r
LEFT JOIN especie e ON r.id_especie = e.id_especie
ORDER BY e.nome, r.nome
"""

OBTER_POR_ID = """
SELECT
    r.id_raca, r.id_especie, r.nome, r.descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id_especie as especie_id, e.nome as especie_nome, e.descricao as especie_descricao
FROM raca r
LEFT JOIN especie e ON r.id_especie = e.id_especie
WHERE r.id_raca = ?
"""

OBTER_POR_ESPECIE = """
SELECT
    r.id_raca, r.id_especie, r.nome, r.descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id_especie as especie_id, e.nome as especie_nome, e.descricao as especie_descricao
FROM raca r
LEFT JOIN especie e ON r.id_especie = e.id_especie
WHERE r.id_especie = ?
ORDER BY r.nome
"""

ATUALIZAR = """
UPDATE raca
SET id_especie = ?, nome = ?, descricao = ?,
    temperamento = ?, expectativa_de_vida = ?, porte = ?
WHERE id_raca = ?
"""

EXCLUIR = """
DELETE FROM raca
WHERE id_raca = ?
"""

# Query para verificar se raça tem animais vinculados
CONTAR_ANIMAIS = """
SELECT COUNT(*) as total
FROM animal
WHERE id_raca = ?
"""
```

**➕ Arquivo a Criar:** `repo/raca_repo.py`

```python
"""
Repository para operações com a tabela raca.
"""

from typing import List, Optional
from model.raca_model import Raca
from model.especie_model import Especie
from sql.raca_sql import *
from util.db_util import get_connection


def _row_to_raca(row) -> Raca:
    """Converte uma linha do banco em objeto Raca com Especie."""
    return Raca(
        id_raca=row["id_raca"],
        id_especie=row["id_especie"],
        nome=row["nome"],
        descricao=row["descricao"],
        temperamento=row["temperamento"],
        expectativa_de_vida=row["expectativa_de_vida"],
        porte=row["porte"],
        especie=Especie(
            id_especie=row["especie_id"],
            nome=row["especie_nome"],
            descricao=row["especie_descricao"]
        ) if row.get("especie_id") else None
    )


def criar_tabela() -> None:
    """Cria a tabela raca se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(raca: Raca) -> int:
    """Insere uma nova raça e retorna o ID gerado."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            raca.id_especie,
            raca.nome,
            raca.descricao,
            raca.temperamento,
            raca.expectativa_de_vida,
            raca.porte
        ))
        return cursor.lastrowid


def obter_todos() -> List[Raca]:
    """Retorna todas as raças com suas espécies."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_raca(row) for row in cursor.fetchall()]


def obter_por_id(id_raca: int) -> Optional[Raca]:
    """Busca uma raça pelo ID com sua espécie."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_raca,))
        row = cursor.fetchone()
        return _row_to_raca(row) if row else None


def obter_por_especie(id_especie: int) -> List[Raca]:
    """Retorna todas as raças de uma espécie."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ESPECIE, (id_especie,))
        return [_row_to_raca(row) for row in cursor.fetchall()]


def atualizar(raca: Raca) -> None:
    """Atualiza uma raça existente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            raca.id_especie,
            raca.nome,
            raca.descricao,
            raca.temperamento,
            raca.expectativa_de_vida,
            raca.porte,
            raca.id_raca
        ))


def excluir(id_raca: int) -> None:
    """Exclui uma raça pelo ID."""
    # Verificar se tem animais vinculados
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_ANIMAIS, (id_raca,))
        total = cursor.fetchone()["total"]

        if total > 0:
            raise Exception(
                f"Não é possível excluir esta raça. "
                f"Existem {total} animal(is) vinculado(s)."
            )

        cursor.execute(EXCLUIR, (id_raca,))
```

**➕ Arquivo a Criar:** `dtos/raca_dto.py`

```python
"""
DTOs para validação de dados da entidade Raca.
"""

from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_inteiro_positivo


class RacaCriarDTO(BaseModel):
    """DTO para criação de raça."""
    id_especie: int
    nome: str
    descricao: str
    temperamento: str
    expectativa_de_vida: str
    porte: str  # Pequeno, Médio, Grande

    _validar_especie = field_validator('id_especie')(validar_inteiro_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_porte = field_validator('porte')(
        lambda v: v if v in ['Pequeno', 'Médio', 'Grande']
        else (_ for _ in ()).throw(ValueError('Porte deve ser: Pequeno, Médio ou Grande'))
    )


class RacaAlterarDTO(BaseModel):
    """DTO para alteração de raça."""
    id_especie: int
    nome: str
    descricao: str
    temperamento: str
    expectativa_de_vida: str
    porte: str

    _validar_especie = field_validator('id_especie')(validar_inteiro_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_porte = field_validator('porte')(
        lambda v: v if v in ['Pequeno', 'Médio', 'Grande']
        else (_ for _ in ()).throw(ValueError('Porte deve ser: Pequeno, Médio ou Grande'))
    )
```

**Nota:** As routes de Raca seguem o mesmo padrão de Especie. Omitidas por brevidade, mas devem incluir:
- GET /racas/listar
- GET /racas/{id}
- GET /racas/especie/{id_especie}
- POST /racas/cadastrar
- PUT /racas/{id}
- DELETE /racas/{id}

### 5.3 ENTIDADES DE NEGÓCIO

#### PASSO 8: Implementar Entidade ENDERECO

**Objetivo:** Permitir que usuários cadastrem múltiplos endereços (relacionamento 1:N).

**✏️ Completar Model:** `model/endereco_model.py` (já existe, apenas revisar)

**➕ Arquivo a Criar:** `sql/endereco_sql.py`

```python
"""
Comandos SQL para a tabela endereco.
Relacionamento: Usuario 1:N Endereco
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS endereco (
    id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    logradouro TEXT NOT NULL,
    numero INTEGER NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    cep TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO endereco (
    id_usuario, titulo, logradouro, numero,
    complemento, bairro, cidade, uf, cep
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT * FROM endereco ORDER BY titulo
"""

OBTER_POR_ID = """
SELECT * FROM endereco WHERE id_endereco = ?
"""

OBTER_POR_USUARIO = """
SELECT * FROM endereco WHERE id_usuario = ? ORDER BY titulo
"""

ATUALIZAR = """
UPDATE endereco
SET titulo = ?, logradouro = ?, numero = ?,
    complemento = ?, bairro = ?, cidade = ?, uf = ?, cep = ?
WHERE id_endereco = ?
"""

EXCLUIR = """
DELETE FROM endereco WHERE id_endereco = ?
"""
```

**➕ Arquivo a Criar:** `repo/endereco_repo.py`

```python
"""Repository para operações com endereços."""

from typing import List, Optional
from model.endereco_model import Endereco
from sql.endereco_sql import *
from util.db_util import get_connection


def _row_to_endereco(row) -> Endereco:
    return Endereco(
        id_endereco=row["id_endereco"],
        id_usuario=row["id_usuario"],
        titulo=row["titulo"],
        logradouro=row["logradouro"],
        numero=row["numero"],
        complemento=row["complemento"],
        bairro=row["bairro"],
        cidade=row["cidade"],
        Uf=row["uf"],
        CEP=row["cep"],
        usuario=None  # Carregar se necessário
    )


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(endereco: Endereco) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            endereco.id_usuario, endereco.titulo, endereco.logradouro,
            endereco.numero, endereco.complemento, endereco.bairro,
            endereco.cidade, endereco.Uf, endereco.CEP
        ))
        return cursor.lastrowid


def obter_por_usuario(id_usuario: int) -> List[Endereco]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (id_usuario,))
        return [_row_to_endereco(row) for row in cursor.fetchall()]


def atualizar(endereco: Endereco) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            endereco.titulo, endereco.logradouro, endereco.numero,
            endereco.complemento, endereco.bairro, endereco.cidade,
            endereco.Uf, endereco.CEP, endereco.id_endereco
        ))


def excluir(id_endereco: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_endereco,))
```

**Nota:** DTOs e Routes de Endereco seguem padrão similar. O usuário só pode acessar seus próprios endereços.

---

#### PASSO 9: Implementar Entidade ABRIGO

**Objetivo:** Vincular um usuário ao perfil Abrigo com dados específicos.

**✏️ Completar Model:** `model/abrigo_model.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Abrigo:
    id_abrigo: int  # Mesmo ID do usuario
    responsavel: str
    descricao: Optional[str] = None
    data_abertura: Optional[str] = None  # YYYY-MM-DD
    data_membros: Optional[str] = None  # JSON com lista de membros
```

**➕ Arquivo a Criar:** `sql/abrigo_sql.py`

```python
"""
Comandos SQL para a tabela abrigo.
Relacionamento 1:1 com usuario (id_abrigo = id do usuario)
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS abrigo (
    id_abrigo INTEGER PRIMARY KEY,
    responsavel TEXT NOT NULL,
    descricao TEXT,
    data_abertura TEXT,
    data_membros TEXT,
    FOREIGN KEY (id_abrigo) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO abrigo (id_abrigo, responsavel, descricao, data_abertura, data_membros)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT a.*, u.nome, u.email
FROM abrigo a
INNER JOIN usuario u ON a.id_abrigo = u.id
ORDER BY u.nome
"""

OBTER_POR_ID = """
SELECT a.*, u.nome, u.email
FROM abrigo a
INNER JOIN usuario u ON a.id_abrigo = u.id
WHERE a.id_abrigo = ?
"""

ATUALIZAR = """
UPDATE abrigo
SET responsavel = ?, descricao = ?, data_abertura = ?, data_membros = ?
WHERE id_abrigo = ?
"""

EXCLUIR = """
DELETE FROM abrigo WHERE id_abrigo = ?
"""
```

**➕ Arquivo a Criar:** `repo/abrigo_repo.py`

```python
"""Repository para abrigos."""

from typing import List, Optional
from model.abrigo_model import Abrigo
from sql.abrigo_sql import *
from util.db_util import get_connection


def _row_to_abrigo(row) -> Abrigo:
    return Abrigo(
        id_abrigo=row["id_abrigo"],
        responsavel=row["responsavel"],
        descricao=row.get("descricao"),
        data_abertura=row.get("data_abertura"),
        data_membros=row.get("data_membros")
    )


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(abrigo: Abrigo) -> None:
    """Insere abrigo usando ID do usuário existente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            abrigo.id_abrigo,
            abrigo.responsavel,
            abrigo.descricao,
            abrigo.data_abertura,
            abrigo.data_membros
        ))


def obter_por_id(id_abrigo: int) -> Optional[Abrigo]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_abrigo,))
        row = cursor.fetchone()
        return _row_to_abrigo(row) if row else None


def obter_todos() -> List[Abrigo]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_abrigo(row) for row in cursor.fetchall()]


def atualizar(abrigo: Abrigo) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            abrigo.responsavel,
            abrigo.descricao,
            abrigo.data_abertura,
            abrigo.data_membros,
            abrigo.id_abrigo
        ))


def excluir(id_abrigo: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_abrigo,))
```

---

#### PASSO 10: Implementar Entidade ADOTANTE

**✏️ Model já existe:** `model/adotante_model.py`

**➕ Arquivo a Criar:** `sql/adotante_sql.py`

```python
"""
Comandos SQL para a tabela adotante.
Relacionamento 1:1 com usuario (id_adotante = id do usuario)
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS adotante (
    id_adotante INTEGER PRIMARY KEY,
    renda_media REAL NOT NULL,
    tem_filhos INTEGER NOT NULL DEFAULT 0,
    estado_de_saude TEXT,
    FOREIGN KEY (id_adotante) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO adotante (id_adotante, renda_media, tem_filhos, estado_de_saude)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ID = """
SELECT * FROM adotante WHERE id_adotante = ?
"""

ATUALIZAR = """
UPDATE adotante
SET renda_media = ?, tem_filhos = ?, estado_de_saude = ?
WHERE id_adotante = ?
"""

EXCLUIR = """
DELETE FROM adotante WHERE id_adotante = ?
"""
```

**➕ Arquivo a Criar:** `repo/adotante_repo.py`

```python
"""Repository para adotantes."""

from typing import Optional
from model.adotante_model import Adotante
from sql.adotante_sql import *
from util.db_util import get_connection


def _row_to_adotante(row) -> Adotante:
    return Adotante(
        id_adotante=row["id_adotante"],
        renda_media=row["renda_media"],
        tem_filhos=bool(row["tem_filhos"]),
        estado_saude=row["estado_de_saude"]
    )


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(adotante: Adotante) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            adotante.id_adotante,
            adotante.renda_media,
            1 if adotante.tem_filhos else 0,
            adotante.estado_saude
        ))


def obter_por_id(id_adotante: int) -> Optional[Adotante]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_adotante,))
        row = cursor.fetchone()
        return _row_to_adotante(row) if row else None


def atualizar(adotante: Adotante) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            adotante.renda_media,
            1 if adotante.tem_filhos else 0,
            adotante.estado_saude,
            adotante.id_adotante
        ))
```

---

#### PASSO 11: Implementar Entidade ANIMAL (Core do Sistema)

**✏️ Model já existe:** `model/animal_model.py`

**➕ Arquivo a Criar:** `sql/animal_sql.py`

```python
"""
Comandos SQL para a tabela animal.
Relacionamentos: Animal N:1 Raca, Animal N:1 Abrigo
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS animal (
    id_animal INTEGER PRIMARY KEY AUTOINCREMENT,
    id_raca INTEGER NOT NULL,
    id_abrigo INTEGER NOT NULL,
    nome TEXT NOT NULL,
    sexo TEXT NOT NULL,
    data_nascimento TEXT,
    data_entrada TEXT NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'Disponível',
    foto TEXT,
    FOREIGN KEY (id_raca) REFERENCES raca(id_raca),
    FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo)
)
"""

INSERIR = """
INSERT INTO animal (
    id_raca, id_abrigo, nome, sexo, data_nascimento,
    data_entrada, observacoes, status, foto
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT
    a.*,
    r.nome as raca_nome, r.porte,
    e.nome as especie_nome,
    ab.responsavel as abrigo_responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id_raca
LEFT JOIN especie e ON r.id_especie = e.id_especie
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.status = 'Disponível'
ORDER BY a.data_entrada DESC
"""

OBTER_POR_ID = """
SELECT
    a.*,
    r.id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id_raca
LEFT JOIN especie e ON r.id_especie = e.id_especie
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.id_animal = ?
"""

OBTER_POR_ABRIGO = """
SELECT * FROM animal WHERE id_abrigo = ? ORDER BY data_entrada DESC
"""

BUSCAR_DISPONIVEIS = """
SELECT
    a.*,
    r.nome as raca_nome, r.porte,
    e.nome as especie_nome
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id_raca
LEFT JOIN especie e ON r.id_especie = e.id_especie
WHERE a.status = 'Disponível'
"""

ATUALIZAR = """
UPDATE animal
SET id_raca = ?, nome = ?, sexo = ?, data_nascimento = ?,
    observacoes = ?, status = ?
WHERE id_animal = ?
"""

ATUALIZAR_STATUS = """
UPDATE animal SET status = ? WHERE id_animal = ?
"""

EXCLUIR = """
DELETE FROM animal WHERE id_animal = ?
"""
```

**➕ Arquivo a Criar:** `repo/animal_repo.py`

```python
"""Repository para animais."""

from typing import List, Optional
from model.animal_model import Animal
from model.raca_model import Raca
from model.especie_model import Especie
from model.abrigo_model import Abrigo
from sql.animal_sql import *
from util.db_util import get_connection


def _row_to_animal(row) -> Animal:
    """Converte linha em objeto Animal com relacionamentos."""
    return Animal(
        id_animal=row["id_animal"],
        id_raca=row["id_raca"],
        id_abrigo=row["id_abrigo"],
        data_nascimento=row.get("data_nascimento"),
        data_entrada=row["data_entrada"],
        observacoes=row.get("observacoes"),
        raca=Raca(
            id_raca=row["id_raca"],
            id_especie=row.get("id_especie", 0),
            nome=row.get("raca_nome", ""),
            descricao=row.get("raca_descricao", ""),
            temperamento=row.get("temperamento", ""),
            expectativa_de_vida=row.get("expectativa_de_vida", ""),
            porte=row.get("porte", ""),
            especie=None
        ) if row.get("raca_nome") else None,
        abrigo=Abrigo(
            id_abrigo=row["id_abrigo"],
            responsavel=row.get("responsavel", ""),
            data_abertura=None
        ) if row.get("id_abrigo") else None
    )


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(animal: Animal) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            animal.id_raca,
            animal.id_abrigo,
            "Nome do Animal",  # Adicionar campo nome no model
            "Macho",  # Adicionar campo sexo no model
            animal.data_nascimento,
            animal.data_entrada,
            animal.observacoes,
            "Disponível",
            None  # foto
        ))
        return cursor.lastrowid


def obter_todos_disponiveis() -> List[Animal]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_animal(row) for row in cursor.fetchall()]


def obter_por_id(id_animal: int) -> Optional[Animal]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_animal,))
        row = cursor.fetchone()
        return _row_to_animal(row) if row else None


def obter_por_abrigo(id_abrigo: int) -> List[Animal]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [_row_to_animal(row) for row in cursor.fetchall()]


def atualizar_status(id_animal: int, novo_status: str) -> None:
    """Atualiza status: Disponível, Em Processo, Adotado, Indisponível"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (novo_status, id_animal))
```

---

### 5.4 FLUXOS PRINCIPAIS - PROCESSO DE ADOÇÃO

#### PASSO 12: Implementar Entidade SOLICITACAO

**Objetivo:** Adotante solicita adoção de um animal.

**✏️ Model já existe:** `model/solicitacao_model.py`

**➕ Arquivo a Criar:** `sql/solicitacao_sql.py`

```python
"""
Comandos SQL para solicitações de adoção.
Relacionamento: Solicitacao N:1 Adotante, Solicitacao N:1 Animal
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS solicitacao (
    id_solicitacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_animal INTEGER NOT NULL,
    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pendente',
    observacoes TEXT,
    resposta_abrigo TEXT,
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_animal) REFERENCES animal(id_animal)
)
"""

INSERIR = """
INSERT INTO solicitacao (id_adotante, id_animal, observacoes)
VALUES (?, ?, ?)
"""

OBTER_POR_ADOTANTE = """
SELECT s.*, a.nome as animal_nome, a.foto
FROM solicitacao s
INNER JOIN animal a ON s.id_animal = a.id_animal
WHERE s.id_adotante = ?
ORDER BY s.data_solicitacao DESC
"""

OBTER_POR_ABRIGO = """
SELECT
    s.*,
    a.nome as animal_nome,
    u.nome as adotante_nome, u.email as adotante_email, u.telefone
FROM solicitacao s
INNER JOIN animal a ON s.id_animal = a.id_animal
INNER JOIN adotante ad ON s.id_adotante = ad.id_adotante
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE a.id_abrigo = ?
ORDER BY s.data_solicitacao DESC
"""

ATUALIZAR_STATUS = """
UPDATE solicitacao
SET status = ?, resposta_abrigo = ?
WHERE id_solicitacao = ?
"""
```

**➕ Arquivo a Criar:** `repo/solicitacao_repo.py`

```python
"""Repository para solicitações de adoção."""

from typing import List, Optional
from model.solicitacao_model import Solicitacao
from sql.solicitacao_sql import *
from util.db_util import get_connection


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(solicitacao: Solicitacao) -> int:
    """Cria nova solicitação de adoção."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            solicitacao.id_adotante,
            solicitacao.id_animal,
            solicitacao.observacoes
        ))
        return cursor.lastrowid


def obter_por_adotante(id_adotante: int) -> List[dict]:
    """Lista solicitações do adotante."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ADOTANTE, (id_adotante,))
        return [dict(row) for row in cursor.fetchall()]


def obter_por_abrigo(id_abrigo: int) -> List[dict]:
    """Lista solicitações recebidas pelo abrigo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [dict(row) for row in cursor.fetchall()]


def atualizar_status(id_solicitacao: int, status: str, resposta: str) -> None:
    """
    Atualiza status da solicitação.
    Status possíveis: Pendente, Aprovada, Rejeitada, Cancelada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (status, resposta, id_solicitacao))
```

**➕ Arquivo a Criar:** `routes/solicitacao_routes.py`

```python
"""
Rotas para solicitações de adoção.
Adotantes criam, Abrigos analisam.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil

import repo.solicitacao_repo as solicitacao_repo
import repo.animal_repo as animal_repo
from model.solicitacao_model import Solicitacao

router = APIRouter(prefix="/solicitacoes")


@router.post("/criar")
@requer_autenticacao([Perfil.ADOTANTE.value])
async def criar_solicitacao(
    request: Request,
    usuario_logado: dict,
    id_animal: int = Form(...),
    observacoes: str = Form("")
):
    """Adotante solicita adoção de um animal."""
    try:
        # Verificar se animal está disponível
        animal = animal_repo.obter_por_id(id_animal)
        if not animal or animal.status != "Disponível":
            return JSONResponse(
                {"success": False, "message": "Animal não disponível"},
                status_code=400
            )

        # Criar solicitação
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=usuario_logado["id"],
            id_animal=id_animal,
            data_solicitacao=None,
            status="Pendente",
            observacoes=observacoes,
            adotante=None,
            animal=None
        )

        id_criado = solicitacao_repo.inserir(solicitacao)

        # Atualizar status do animal
        animal_repo.atualizar_status(id_animal, "Em Processo")

        return JSONResponse({
            "success": True,
            "message": "Solicitação enviada com sucesso!",
            "data": {"id_solicitacao": id_criado}
        }, status_code=201)

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500
        )


@router.get("/minhas")
@requer_autenticacao([Perfil.ADOTANTE.value])
async def listar_minhas(request: Request, usuario_logado: dict):
    """Lista solicitações do adotante logado."""
    solicitacoes = solicitacao_repo.obter_por_adotante(usuario_logado["id"])
    return JSONResponse({
        "success": True,
        "data": solicitacoes
    })


@router.get("/recebidas")
@requer_autenticacao([Perfil.ABRIGO.value])
async def listar_recebidas(request: Request, usuario_logado: dict):
    """Lista solicitações recebidas pelo abrigo."""
    solicitacoes = solicitacao_repo.obter_por_abrigo(usuario_logado["id"])
    return JSONResponse({
        "success": True,
        "data": solicitacoes
    })


@router.put("/{id_solicitacao}/analisar")
@requer_autenticacao([Perfil.ABRIGO.value])
async def analisar_solicitacao(
    request: Request,
    id_solicitacao: int,
    usuario_logado: dict,
    status: str = Form(...),  # Aprovada ou Rejeitada
    resposta: str = Form("")
):
    """Abrigo aprova ou rejeita solicitação."""
    try:
        if status not in ["Aprovada", "Rejeitada"]:
            return JSONResponse(
                {"success": False, "message": "Status inválido"},
                status_code=400
            )

        solicitacao_repo.atualizar_status(id_solicitacao, status, resposta)

        return JSONResponse({
            "success": True,
            "message": f"Solicitação {status.lower()} com sucesso"
        })

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500
        )
```

---

#### PASSO 13: Implementar Entidade VISITA

**Objetivo:** Agendar visitas do adotante ao abrigo.

**✏️ Model já existe:** `model/visita_model.py`

**➕ Arquivo a Criar:** `sql/visita_sql.py`

```python
"""SQL para visitas."""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS visita (
    id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_abrigo INTEGER NOT NULL,
    data_agendada DATETIME NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'Agendada',
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo)
)
"""

INSERIR = """
INSERT INTO visita (id_adotante, id_abrigo, data_agendada, observacoes)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ADOTANTE = """
SELECT v.*, ab.responsavel as abrigo_nome
FROM visita v
INNER JOIN abrigo ab ON v.id_abrigo = ab.id_abrigo
WHERE v.id_adotante = ?
ORDER BY v.data_agendada DESC
"""

OBTER_POR_ABRIGO = """
SELECT v.*, u.nome as adotante_nome, u.telefone
FROM visita v
INNER JOIN usuario u ON v.id_adotante = u.id
WHERE v.id_abrigo = ?
ORDER BY v.data_agendada DESC
"""

ATUALIZAR_STATUS = """
UPDATE visita SET status = ? WHERE id_visita = ?
"""

REAGENDAR = """
UPDATE visita SET data_agendada = ?, status = 'Agendada' WHERE id_visita = ?
"""
```

---

#### PASSO 14: Implementar Entidade ADOCAO

**Objetivo:** Registrar adoções finalizadas.

**✏️ Model já existe:** `model/adocao_model.py`

**➕ Arquivo a Criar:** `sql/adocao_sql.py`

```python
"""SQL para adoções finalizadas."""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS adocao (
    id_adocao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_animal INTEGER NOT NULL,
    data_solicitacao DATETIME NOT NULL,
    data_adocao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Concluída',
    observacoes TEXT,
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_animal) REFERENCES animal(id_animal),
    UNIQUE(id_animal)
)
"""

INSERIR = """
INSERT INTO adocao (id_adotante, id_animal, data_solicitacao, observacoes)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ABRIGO = """
SELECT
    ad.*,
    a.nome as animal_nome,
    u.nome as adotante_nome
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id_animal
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE a.id_abrigo = ?
ORDER BY ad.data_adocao DESC
"""
```

---

## 6. CHECKLIST DE IMPLEMENTAÇÃO

### ✅ Fase 1: Infraestrutura (PRIORIDADE 1)

- [ ] **PASSO 1:** Atualizar `util/perfis.py` (adicionar ABRIGO e ADOTANTE)
- [ ] **PASSO 2:** Atualizar `model/usuario_model.py` (adicionar campos)
- [ ] **PASSO 3:** Atualizar `sql/usuario_sql.py` (alterar CREATE TABLE, INSERT, UPDATE)
- [ ] **PASSO 4:** Atualizar `repo/usuario_repo.py` (ajustar funções)
- [ ] **PASSO 5:** Atualizar `dtos/usuario_dto.py` (adicionar validações)

### ✅ Fase 2: Entidades Base (PRIORIDADE 1)

- [ ] **PASSO 6:** Implementar ESPECIE
  - [ ] Criar `sql/especie_sql.py`
  - [ ] Criar `repo/especie_repo.py`
  - [ ] Criar `dtos/especie_dto.py`
  - [ ] Criar `routes/especie_routes.py`
  - [ ] Registrar no `main.py`

- [ ] **PASSO 7:** Implementar RACA
  - [ ] Criar `sql/raca_sql.py`
  - [ ] Criar `repo/raca_repo.py`
  - [ ] Criar `dtos/raca_dto.py`
  - [ ] Criar `routes/raca_routes.py`
  - [ ] Registrar no `main.py`

- [ ] **PASSO 8:** Implementar ENDERECO
  - [ ] Criar `sql/endereco_sql.py`
  - [ ] Criar `repo/endereco_repo.py`
  - [ ] Criar `dtos/endereco_dto.py`
  - [ ] Criar `routes/endereco_routes.py`
  - [ ] Registrar no `main.py`

### ✅ Fase 3: Entidades de Negócio (PRIORIDADE 2)

- [ ] **PASSO 9:** Implementar ABRIGO
  - [ ] Completar `model/abrigo_model.py`
  - [ ] Criar `sql/abrigo_sql.py`
  - [ ] Criar `repo/abrigo_repo.py`
  - [ ] Criar `dtos/abrigo_dto.py`
  - [ ] Criar `routes/abrigo_routes.py`
  - [ ] Registrar no `main.py`

- [ ] **PASSO 10:** Implementar ADOTANTE
  - [ ] Criar `sql/adotante_sql.py`
  - [ ] Criar `repo/adotante_repo.py`
  - [ ] Criar `dtos/adotante_dto.py`
  - [ ] Criar `routes/adotante_routes.py`
  - [ ] Registrar no `main.py`

- [ ] **PASSO 11:** Implementar ANIMAL
  - [ ] Completar `model/animal_model.py` (adicionar nome, sexo, status, foto)
  - [ ] Criar `sql/animal_sql.py`
  - [ ] Criar `repo/animal_repo.py`
  - [ ] Criar `dtos/animal_dto.py`
  - [ ] Criar `routes/animal_routes.py` (público + abrigo)
  - [ ] Implementar upload de fotos (reutilizar `util/foto_util.py`)
  - [ ] Registrar no `main.py`

### ✅ Fase 4: Fluxo de Adoção (PRIORIDADE 3)

- [ ] **PASSO 12:** Implementar SOLICITACAO
  - [ ] Criar `sql/solicitacao_sql.py`
  - [ ] Criar `repo/solicitacao_repo.py`
  - [ ] Criar `dtos/solicitacao_dto.py`
  - [ ] Criar `routes/solicitacao_routes.py`
  - [ ] Registrar no `main.py`

- [ ] **PASSO 13:** Implementar VISITA
  - [ ] Criar `sql/visita_sql.py`
  - [ ] Criar `repo/visita_repo.py`
  - [ ] Criar `dtos/visita_dto.py`
  - [ ] Criar `routes/visita_routes.py`
  - [ ] Registrar no `main.py`

- [ ] **PASSO 14:** Implementar ADOCAO
  - [ ] Criar `sql/adocao_sql.py`
  - [ ] Criar `repo/adocao_repo.py`
  - [ ] Criar `dtos/adocao_dto.py`
  - [ ] Criar `routes/adocao_routes.py`
  - [ ] Registrar no `main.py`

### ✅ Fase 5: Recursos Extras (PRIORIDADE 4)

- [ ] Implementar busca avançada de animais (filtros)
- [ ] Implementar paginação
- [ ] Implementar sistema de notificações por email
- [ ] Implementar relatórios e dashboards
- [ ] Implementar validação de documentos (CPF/CNPJ)
- [ ] Implementar sistema de mensagens entre adotante e abrigo

---

## 7. RESUMO E CONSIDERAÇÕES FINAIS

### 7.1 Arquivos Totais a Criar/Modificar

**Modificar (5 arquivos):**
1. `util/perfis.py`
2. `model/usuario_model.py`
3. `sql/usuario_sql.py`
4. `repo/usuario_repo.py`
5. `dtos/usuario_dto.py`

**Criar (36 arquivos):**

**SQL (9):** especie, raca, endereco, abrigo, adotante, animal, solicitacao, visita, adocao

**Repositories (9):** especie, raca, endereco, abrigo, adotante, animal, solicitacao, visita, adocao

**DTOs (9):** especie, raca, endereco, abrigo, adotante, animal, solicitacao, visita, adocao

**Routes (9):** especie, raca, endereco, abrigo, adotante, animal, solicitacao, visita, adocao

### 7.2 Ordem de Implementação Recomendada

**Semana 1:** Infraestrutura
- Passos 1-5: Ajustar perfis e Usuario

**Semana 2:** Entidades Base
- Passos 6-8: Especie, Raca, Endereco

**Semana 3:** Entidades de Negócio
- Passos 9-11: Abrigo, Adotante, Animal

**Semana 4:** Fluxo de Adoção
- Passos 12-14: Solicitacao, Visita, Adocao

**Semana 5:** Testes e Refinamentos
- Testes, ajustes, melhorias

### 7.3 Boas Práticas

1. **Sempre testar cada passo** antes de avançar
2. **Fazer commits frequentes** com mensagens descritivas
3. **Seguir os padrões** do projeto existente
4. **Reutilizar código** sempre que possível
5. **Documentar** funções complexas
6. **Validar dados** em todas as camadas
7. **Tratar erros** adequadamente

### 7.4 Recursos Disponíveis no Projeto

- ✅ Sistema de validação completo (15+ validadores)
- ✅ Sistema de tratamento de erros centralizado
- ✅ Sistema de autenticação e autorização
- ✅ Sistema de upload de fotos
- ✅ Sistema de envio de emails
- ✅ Sistema de logs
- ✅ Sistema de backup

### 7.5 Próximos Passos Após Backend

Após concluir o backend:
1. Criar seeds de dados para testes
2. Implementar testes automatizados
3. Criar documentação da API
4. Implementar frontend (templates)
5. Deploy em produção

---

**FIM DO DOCUMENTO**

**Total de linhas:** ~3800 linhas
**Data de criação:** 21 de Outubro de 2025
**Versão:** 1.0

Este documento serve como guia completo para implementação do backend do PetLar. Siga os passos na ordem sugerida, teste cada componente e mantenha os padrões do projeto.
