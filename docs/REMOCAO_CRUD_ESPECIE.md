# Registro: Remoção do CRUD de Espécie

## 📅 Data
11 de novembro de 2025

## 🎯 Objetivo
Remover completamente o CRUD de espécie do projeto PetLar para que os alunos possam implementá-lo do zero seguindo o tutorial em `docs/CRUD.md`.

## 🗑️ Arquivos Removidos

### Artefatos Principais do CRUD de Espécie
1. `model/especie_model.py` - Modelo da entidade
2. `dtos/especie_dto.py` - DTOs de validação
3. `sql/especie_sql.py` - Queries SQL
4. `repo/especie_repo.py` - Repositório de dados
5. `routes/admin_especies_routes.py` - Rotas/Controllers
6. `templates/admin/especies/` - Diretório completo com templates (listar.html, cadastro.html, editar.html)

## ✏️ Arquivos Modificados (Referências Comentadas)

### 1. `main.py`
**Alterações:**
- Comentado: `from repo import especie_repo`
- Comentado: `especie_repo.criar_tabela()`
- Comentado: `from routes.admin_especies_routes import router as admin_especies_router`
- Comentado: `app.include_router(admin_especies_router, ...)`

**Motivo:** Evitar erros de importação de módulos inexistentes.

---

### 2. `model/raca_model.py`
**Alterações:**
- Comentado: `from model.especie_model import Especie`
- Comentado: `especie: Optional[Especie] = None`

**Motivo:** Remover dependência do modelo Especie que não existe mais.

---

### 3. `repo/raca_repo.py`
**Alterações:**
- Comentado: `from model.especie_model import Especie`
- Comentado: Criação do objeto `Especie` dentro de `_row_to_raca()`

**Motivo:** Evitar erro de importação e instanciação de classe inexistente.

---

### 4. `repo/animal_repo.py`
**Alterações:**
- Comentado: `from model.especie_model import Especie`

**Motivo:** Evitar erro de importação.

---

### 5. `routes/admin_racas_routes.py`
**Alterações:**
- Comentado: `from repo import especie_repo`
- Comentado: Validações que verificam se espécie existe (`especie_repo.obter_por_id()`)
- Comentado: População de dropdown de espécies (`especie_repo.obter_todos()`)
- **Código temporário ativo:** `especies_dict = {}` (lista vazia)

**Impacto:** 
- Formulários de raça não exibem dropdown de espécies
- Não há validação se espécie existe ao criar/editar raça

---

### 6. `routes/admin_animais_routes.py`
**Alterações:**
- Comentado: Exibição de espécie junto com raça nos dropdowns
- **Código temporário ativo:** `racas_dict = {str(r.id): r.nome for r in racas}` (mostra apenas nome da raça)

**Impacto:**
- Dropdowns de raça em formulários de animal mostram apenas nome da raça (sem espécie)
- Antes: "Labrador (Cão)"
- Agora: "Labrador"

---

### 7. `sql/animal_sql.py`
**Alterações:**
- Comentado: `LEFT JOIN especie e ON r.id_especie = e.id` em 4 queries:
  - `OBTER_TODOS`
  - `OBTER_POR_ID`
  - `OBTER_POR_ABRIGO`
  - `BUSCAR_DISPONIVEIS`
- Comentado: Seleção de colunas `e.id as id_especie, e.nome as especie_nome`

**Impacto:**
- Queries de animal não retornam dados de espécie
- Não afeta funcionamento básico (apenas informação adicional)

---

## 📚 Documento Atualizado

### `docs/CRUD.md`
**Alterações globais:**
- Substituído "categoria" → "espécie" (todas as variações)
- Substituído "Categoria" → "Espécie"
- Substituído "categorias" → "espécies"
- Substituído "admin_categorias" → "admin_especies"

**Nova seção adicionada:**
- **Passo 0: Preparação do Ambiente - Restauração de Referências**
  - Explica o contexto da remoção
  - Lista todos os arquivos modificados
  - Fornece instruções de quando/como descomentar cada referência
  - Inclui checklist de preparação

**Índice atualizado:**
- Adicionado item 2: "Passo 0: Preparação..."
- Renumerados todos os passos subsequentes (1-20)

---

## ✅ Validação

### Testes Realizados
1. ✅ Import do `main.py` sem erros
2. ✅ Nenhum erro relacionado a "especie" na inicialização
3. ✅ Todas as tabelas (exceto especie) são criadas corretamente
4. ✅ Aplicação inicia sem erros críticos

### Limitações Temporárias (Esperado)
- ❌ Formulários de raça não têm dropdown de espécies (lista vazia)
- ❌ Não há validação de existência de espécie ao criar raça
- ❌ Dropdowns de animal mostram apenas nome da raça (sem espécie)
- ❌ Queries de animal não retornam dados de espécie
- ⚠️ Funcionalidade de raças e animais está **parcialmente limitada** mas funcional

---

## 🎓 Instruções para o Aluno

### O que o aluno deve fazer:
1. **Estudar o Passo 0** do tutorial CRUD.md
2. **Seguir os Passos 1-10** para criar o CRUD completo de espécie
3. **Após completar o tutorial**, descomentar as referências nos 7 arquivos modificados
4. **Testar** que tudo funciona integrado

### Arquivos que o aluno criará:
1. `sql/especie_sql.py` (Passo 1)
2. `model/especie_model.py` (Passo 2)
3. `dtos/especie_dto.py` (Passo 3)
4. `repo/especie_repo.py` (Passo 4)
5. `routes/admin_especies_routes.py` (Passo 6)
6. `templates/admin/especies/listar.html` (Passo 8)
7. `templates/admin/especies/cadastro.html` (Passo 9)
8. `templates/admin/especies/editar.html` (Passo 10)

### Referências que o aluno descomentará:
1. `main.py` - 6 linhas (Passos 5 e 7)
2. `model/raca_model.py` - 2 linhas (após Passo 2)
3. `repo/raca_repo.py` - 2 linhas + bloco (após Passo 4)
4. `repo/animal_repo.py` - 1 linha (após Passo 2)
5. `routes/admin_racas_routes.py` - ~15 linhas (após Passo 4)
6. `routes/admin_animais_routes.py` - 3 linhas (após Passo 2)
7. `sql/animal_sql.py` - 8 linhas (após Passo 1)

---

## 📊 Estatísticas

- **Arquivos removidos:** 9
- **Arquivos modificados:** 7
- **Linhas comentadas:** ~40
- **Linhas do tutorial:** 3175+
- **Nova seção no tutorial:** Passo 0 (~160 linhas)

---

## 🔄 Backup

Um backup do documento original foi criado em:
- `docs/CRUD.md.backup`

---

**Documento gerado automaticamente durante a operação de remoção do CRUD de espécie.**
