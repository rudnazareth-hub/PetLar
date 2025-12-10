# Atividade Final - Projeto PetLar

Este documento contém 4 atividades independentes para aprimoramento do sistema PetLar. Cada aluno deve realizar sua atividade individualmente.

---

## Atividade 1 - Aluno1: Adicionar Badges Visuais para Status dos Animais

### Objetivo
Melhorar a visualização do status dos animais (Disponivel, Adotado, Reservado, Indisponivel) usando badges coloridas com ícones Bootstrap em vez de texto simples.

### Tempo Estimado
45-60 minutos

### Resultado Esperado
Os status dos animais aparecerão com cores e ícones intuitivos:
- **Disponivel**: Badge verde com ícone de check
- **Adotado**: Badge azul com ícone de coração
- **Reservado**: Badge amarela com ícone de relógio
- **Indisponivel**: Badge vermelha com ícone de X

---

### Passo 1: Criar sua branch de trabalho

Abra o terminal na pasta do projeto e execute:

```bash
git checkout main
git pull origin main
git checkout -b aluno1
```

---

### Passo 2: Criar o arquivo de macro para badges

Crie um novo arquivo chamado `badge_status.html` dentro da pasta `templates/macros/`.

**Caminho completo:** `templates/macros/badge_status.html`

**Conteúdo do arquivo:**

```html
{% macro badge_status(status) %}
    {% if status == 'Disponivel' %}
        <span class="badge bg-success">
            <i class="bi bi-check-circle-fill me-1"></i>Disponível
        </span>
    {% elif status == 'Adotado' %}
        <span class="badge bg-primary">
            <i class="bi bi-heart-fill me-1"></i>Adotado
        </span>
    {% elif status == 'Reservado' %}
        <span class="badge bg-warning text-dark">
            <i class="bi bi-clock-fill me-1"></i>Reservado
        </span>
    {% elif status == 'Indisponivel' %}
        <span class="badge bg-danger">
            <i class="bi bi-x-circle-fill me-1"></i>Indisponível
        </span>
    {% else %}
        <span class="badge bg-secondary">
            <i class="bi bi-question-circle-fill me-1"></i>{{ status }}
        </span>
    {% endif %}
{% endmacro %}
```

---

### Passo 3: Atualizar o template de listagem pública de animais

Abra o arquivo `templates/animais/listar.html`.

**3.1** No início do arquivo, após a linha `{% extends "base_publica.html" %}`, adicione:

```html
{% from "macros/badge_status.html" import badge_status %}
```

**3.2** Procure no arquivo onde aparece o status do animal. Deve ser algo como:

```html
<span class="badge bg-secondary">{{ animal.status }}</span>
```

Ou similar. Substitua essa linha por:

```html
{{ badge_status(animal.status) }}
```

---

### Passo 4: Atualizar o template de detalhes do animal

Abra o arquivo `templates/animais/detalhes.html`.

**4.1** No início do arquivo, após a linha `{% extends "base_publica.html" %}`, adicione:

```html
{% from "macros/badge_status.html" import badge_status %}
```

**4.2** Procure onde aparece o status do animal e substitua por:

```html
{{ badge_status(animal.status) }}
```

---

### Passo 5: Atualizar a listagem de animais do abrigo

Abra o arquivo `templates/abrigo/animais/lista.html`.

**5.1** No início do arquivo, após o `{% extends %}`, adicione:

```html
{% from "macros/badge_status.html" import badge_status %}
```

**5.2** Procure onde aparece o status e substitua por:

```html
{{ badge_status(animal.status) }}
```

---

### Passo 6: Testar a aplicação

Execute a aplicação:

```bash
python main.py
```

Acesse no navegador:
- `http://localhost:8000/animais` - Verifique se os badges aparecem na listagem
- Clique em um animal para ver os detalhes

---

### Passo 7: Commitar suas alterações

```bash
git add .
git commit -m "feat: adicionar badges visuais coloridas para status dos animais"
```

---

## Atividade 2 - Aluno2: Adicionar Filtro por Sexo na Listagem de Animais

### Objetivo
Permitir que os usuários filtrem os animais por sexo (Macho/Fêmea/Todos) na página pública de listagem de animais.

### Tempo Estimado
45-60 minutos

### Resultado Esperado
A página de listagem de animais terá botões para filtrar por sexo, facilitando a busca.

---

### Passo 1: Criar sua branch de trabalho

Abra o terminal na pasta do projeto e execute:

```bash
git checkout main
git pull origin main
git checkout -b aluno2
```

---

### Passo 2: Modificar a rota de listagem de animais

Abra o arquivo `routes/public_routes.py`.

Localize a função que lista os animais públicos. Deve ser algo como `listar_animais` ou similar com o decorator `@router.get("/animais")`.

**2.1** Adicione o parâmetro `sexo` na função. Modifique a assinatura da função para incluir:

```python
@router.get("/animais")
async def listar_animais(
    request: Request,
    sexo: str = None
):
```

**2.2** Dentro da função, após obter os animais do banco, adicione o filtro por sexo:

Localize onde os animais são obtidos (algo como `animais = AnimalRepo.obter_todos()` ou similar).

Logo após essa linha, adicione:

```python
    # Filtrar por sexo se especificado
    if sexo and sexo in ['M', 'F']:
        animais = [a for a in animais if a.sexo == sexo]
```

**2.3** Passe o filtro atual para o template. Na linha do `return templates.TemplateResponse`, adicione `sexo_filtro` no contexto:

```python
    return templates.TemplateResponse(
        "animais/listar.html",
        {
            "request": request,
            "animais": animais,
            "sexo_filtro": sexo,  # Adicione esta linha
            # ... outros parâmetros existentes
        }
    )
```

---

### Passo 3: Adicionar os botões de filtro no template

Abra o arquivo `templates/animais/listar.html`.

Localize o início da seção de conteúdo (geralmente após o `{% block content %}`).

Adicione o seguinte código HTML para os botões de filtro, logo após o título da página:

```html
<!-- Filtro por Sexo -->
<div class="d-flex justify-content-center mb-4">
    <div class="btn-group" role="group" aria-label="Filtro por sexo">
        <a href="/animais"
           class="btn {% if not sexo_filtro %}btn-primary{% else %}btn-outline-primary{% endif %}">
            <i class="bi bi-grid-fill me-1"></i>Todos
        </a>
        <a href="/animais?sexo=M"
           class="btn {% if sexo_filtro == 'M' %}btn-primary{% else %}btn-outline-primary{% endif %}">
            <i class="bi bi-gender-male me-1"></i>Machos
        </a>
        <a href="/animais?sexo=F"
           class="btn {% if sexo_filtro == 'F' %}btn-primary{% else %}btn-outline-primary{% endif %}">
            <i class="bi bi-gender-female me-1"></i>Fêmeas
        </a>
    </div>
</div>
```

---

### Passo 4: Adicionar contador de resultados

Logo abaixo dos botões de filtro, adicione:

```html
<!-- Contador de resultados -->
<p class="text-center text-muted mb-4">
    {% if sexo_filtro == 'M' %}
        Mostrando {{ animais|length }} macho(s)
    {% elif sexo_filtro == 'F' %}
        Mostrando {{ animais|length }} fêmea(s)
    {% else %}
        Mostrando todos os {{ animais|length }} animais
    {% endif %}
</p>
```

---

### Passo 5: Testar a aplicação

Execute a aplicação:

```bash
python main.py
```

Acesse no navegador:
- `http://localhost:8000/animais` - Todos os animais
- `http://localhost:8000/animais?sexo=M` - Apenas machos
- `http://localhost:8000/animais?sexo=F` - Apenas fêmeas

Verifique se os botões ficam destacados conforme o filtro selecionado.

---

### Passo 6: Commitar suas alterações

```bash
git add .
git commit -m "feat: adicionar filtro por sexo na listagem publica de animais"
```

---

## Atividade 3 - Aluno3: Adicionar Estatísticas de Animais por Espécie no Dashboard Admin

### Objetivo
Criar um card no dashboard do administrador mostrando a quantidade de animais cadastrados por espécie.

### Tempo Estimado
45-60 minutos

### Resultado Esperado
O dashboard do admin exibirá um card com estatísticas visuais mostrando quantos animais existem de cada espécie.

---

### Passo 1: Criar sua branch de trabalho

Abra o terminal na pasta do projeto e execute:

```bash
git checkout main
git pull origin main
git checkout -b aluno3
```

---

### Passo 2: Criar a função de estatísticas no repositório

Abra o arquivo `repo/animal_repo.py`.

Adicione a seguinte função no final da classe `AnimalRepo`:

```python
    @staticmethod
    def contar_por_especie() -> list:
        """Retorna a contagem de animais agrupados por espécie."""
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    SELECT e.nome as especie, COUNT(a.id) as total
                    FROM animal a
                    INNER JOIN raca r ON a.id_raca = r.id
                    INNER JOIN especie e ON r.id_especie = e.id
                    GROUP BY e.id, e.nome
                    ORDER BY total DESC
                """)
                resultados = cursor.fetchall()
                return [{"especie": row[0], "total": row[1]} for row in resultados]
        except Exception as e:
            print(f"Erro ao contar animais por espécie: {e}")
            return []
```

---

### Passo 3: Modificar a rota do dashboard admin

Abra o arquivo `routes/admin_routes.py` (ou o arquivo que contém a rota do dashboard do admin).

**3.1** No início do arquivo, verifique se o `AnimalRepo` está importado. Se não estiver, adicione:

```python
from repo.animal_repo import AnimalRepo
```

**3.2** Localize a função do dashboard (geralmente decorada com `@router.get("/admin")` ou `@router.get("/admin/dashboard")`).

Dentro dessa função, adicione a chamada para obter as estatísticas:

```python
    # Obter estatísticas de animais por espécie
    animais_por_especie = AnimalRepo.contar_por_especie()
```

**3.3** Passe os dados para o template. No `return templates.TemplateResponse`, adicione:

```python
    "animais_por_especie": animais_por_especie,
```

---

### Passo 4: Adicionar o card de estatísticas no template

Abra o arquivo do dashboard admin (provavelmente `templates/admin/dashboard.html` ou `templates/dashboard.html`).

Adicione o seguinte card onde desejar exibir as estatísticas (recomendo após os cards existentes):

```html
<!-- Card de Estatísticas por Espécie -->
<div class="col-md-6 col-lg-4 mb-4">
    <div class="card h-100 shadow-sm">
        <div class="card-header bg-info text-white">
            <h5 class="card-title mb-0">
                <i class="bi bi-pie-chart-fill me-2"></i>Animais por Espécie
            </h5>
        </div>
        <div class="card-body">
            {% if animais_por_especie %}
                <ul class="list-group list-group-flush">
                    {% for item in animais_por_especie %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span>
                            {% if item.especie == 'Cachorro' %}
                                <i class="bi bi-house-heart me-2"></i>
                            {% elif item.especie == 'Gato' %}
                                <i class="bi bi-emoji-smile me-2"></i>
                            {% else %}
                                <i class="bi bi-heart me-2"></i>
                            {% endif %}
                            {{ item.especie }}
                        </span>
                        <span class="badge bg-info rounded-pill">{{ item.total }}</span>
                    </li>
                    {% endfor %}
                </ul>

                <!-- Total geral -->
                <div class="mt-3 pt-3 border-top">
                    <div class="d-flex justify-content-between">
                        <strong>Total de Animais:</strong>
                        <strong class="text-info">
                            {{ animais_por_especie | sum(attribute='total') }}
                        </strong>
                    </div>
                </div>
            {% else %}
                <p class="text-muted text-center mb-0">
                    <i class="bi bi-inbox me-2"></i>Nenhum animal cadastrado
                </p>
            {% endif %}
        </div>
    </div>
</div>
```

---

### Passo 5: Testar a aplicação

Execute a aplicação:

```bash
python main.py
```

Acesse no navegador:
- Faça login como administrador
- Acesse o dashboard admin
- Verifique se o card de estatísticas aparece corretamente

---

### Passo 6: Commitar suas alterações

```bash
git add .
git commit -m "feat: adicionar card de estatisticas de animais por especie no dashboard admin"
```

---

## Atividade 4 - Aluno4: Adicionar Seção "Últimas Adoções" no Dashboard Admin

### Objetivo
Exibir as 5 adoções mais recentes no dashboard do administrador, mostrando o nome do animal, do adotante e a data da adoção.

### Tempo Estimado
45-60 minutos

### Resultado Esperado
O dashboard do admin terá uma seção mostrando as últimas adoções realizadas com informações resumidas.

---

### Passo 1: Criar sua branch de trabalho

Abra o terminal na pasta do projeto e execute:

```bash
git checkout main
git pull origin main
git checkout -b aluno4
```

---

### Passo 2: Criar a função para obter últimas adoções

Abra o arquivo `repo/adocao_repo.py`.

Adicione a seguinte função na classe `AdocaoRepo`:

```python
    @staticmethod
    def obter_ultimas_adocoes(limite: int = 5) -> list:
        """Retorna as últimas adoções realizadas com detalhes."""
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute("""
                    SELECT
                        ad.id,
                        an.nome as nome_animal,
                        u.nome as nome_adotante,
                        ad.data_adocao,
                        an.foto
                    FROM adocao ad
                    INNER JOIN animal an ON ad.id_animal = an.id
                    INNER JOIN adotante adt ON ad.id_adotante = adt.id
                    INNER JOIN usuario u ON adt.id = u.id
                    ORDER BY ad.data_adocao DESC
                    LIMIT ?
                """, (limite,))
                resultados = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "nome_animal": row[1],
                        "nome_adotante": row[2],
                        "data_adocao": row[3],
                        "foto": row[4]
                    }
                    for row in resultados
                ]
        except Exception as e:
            print(f"Erro ao obter últimas adoções: {e}")
            return []
```

---

### Passo 3: Modificar a rota do dashboard admin

Abra o arquivo `routes/admin_routes.py` (ou o arquivo que contém a rota do dashboard do admin).

**3.1** No início do arquivo, adicione o import se não existir:

```python
from repo.adocao_repo import AdocaoRepo
```

**3.2** Localize a função do dashboard e adicione a chamada para obter as últimas adoções:

```python
    # Obter últimas adoções
    ultimas_adocoes = AdocaoRepo.obter_ultimas_adocoes(5)
```

**3.3** Passe os dados para o template. No `return templates.TemplateResponse`, adicione:

```python
    "ultimas_adocoes": ultimas_adocoes,
```

---

### Passo 4: Adicionar a seção no template do dashboard

Abra o arquivo do dashboard admin (provavelmente `templates/admin/dashboard.html` ou `templates/dashboard.html`).

Adicione o seguinte card onde desejar exibir as últimas adoções:

```html
<!-- Card de Últimas Adoções -->
<div class="col-md-6 col-lg-6 mb-4">
    <div class="card h-100 shadow-sm">
        <div class="card-header bg-success text-white">
            <h5 class="card-title mb-0">
                <i class="bi bi-heart-fill me-2"></i>Últimas Adoções
            </h5>
        </div>
        <div class="card-body p-0">
            {% if ultimas_adocoes %}
                <div class="table-responsive">
                    <table class="table table-hover mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Animal</th>
                                <th>Adotante</th>
                                <th>Data</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for adocao in ultimas_adocoes %}
                            <tr>
                                <td>
                                    <div class="d-flex align-items-center">
                                        {% if adocao.foto %}
                                            <img src="/static/img/animais/{{ adocao.foto }}"
                                                 alt="{{ adocao.nome_animal }}"
                                                 class="rounded-circle me-2"
                                                 style="width: 32px; height: 32px; object-fit: cover;">
                                        {% else %}
                                            <div class="rounded-circle bg-secondary me-2 d-flex align-items-center justify-content-center"
                                                 style="width: 32px; height: 32px;">
                                                <i class="bi bi-image text-white" style="font-size: 14px;"></i>
                                            </div>
                                        {% endif %}
                                        <span>{{ adocao.nome_animal }}</span>
                                    </div>
                                </td>
                                <td>{{ adocao.nome_adotante }}</td>
                                <td>
                                    <small class="text-muted">
                                        {{ adocao.data_adocao[:10] if adocao.data_adocao else 'N/A' }}
                                    </small>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% else %}
                <div class="text-center py-4">
                    <i class="bi bi-inbox text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2 mb-0">Nenhuma adoção registrada ainda</p>
                </div>
            {% endif %}
        </div>
        {% if ultimas_adocoes %}
        <div class="card-footer bg-light">
            <a href="/admin/adocoes" class="btn btn-sm btn-outline-success w-100">
                <i class="bi bi-list-ul me-1"></i>Ver todas as adoções
            </a>
        </div>
        {% endif %}
    </div>
</div>
```

---

### Passo 5: Testar a aplicação

Execute a aplicação:

```bash
python main.py
```

Acesse no navegador:
- Faça login como administrador
- Acesse o dashboard admin
- Verifique se a seção de últimas adoções aparece corretamente
- Se não houver adoções, a mensagem "Nenhuma adoção registrada ainda" deve aparecer

---

### Passo 6: Commitar suas alterações

```bash
git add .
git commit -m "feat: adicionar secao de ultimas adocoes no dashboard admin"
```

---

## Resumo das Atividades

| Aluno | Atividade | Arquivos Modificados |
|-------|-----------|---------------------|
| aluno1 | Badges visuais para status | `templates/macros/badge_status.html` (novo), `templates/animais/listar.html`, `templates/animais/detalhes.html`, `templates/abrigo/animais/lista.html` |
| aluno2 | Filtro por sexo | `routes/public_routes.py`, `templates/animais/listar.html` |
| aluno3 | Estatísticas por espécie | `repo/animal_repo.py`, `routes/admin_routes.py`, `templates/admin/dashboard.html` |
| aluno4 | Últimas adoções | `repo/adocao_repo.py`, `routes/admin_routes.py`, `templates/admin/dashboard.html` |

---

## Instruções Finais

1. Cada aluno deve trabalhar apenas na sua atividade
2. Não modifique arquivos que não estão listados na sua atividade
3. Teste sua implementação antes de commitar
4. Se tiver dúvidas, consulte os arquivos similares já existentes no projeto
5. Após terminar, informe o professor para avaliação
