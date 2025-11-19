# Queries SQL para operações com espécies

# Cria a tabela espécie se ela não existir
CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS especie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        descricao TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP
    )
"""

# Insere uma nova espécie
INSERIR = """
    INSERT INTO especie (nome, descricao)
    VALUES (?, ?)
"""

# Atualiza uma espécie existente
ALTERAR = """
    UPDATE especie
    SET nome=?, descricao=?, data_atualizacao=CURRENT_TIMESTAMP
    WHERE id=?
"""

# Exclui uma espécie
EXCLUIR = """
    DELETE FROM especie WHERE id=?
"""

# Busca todas as espécies ordenadas por nome
OBTER_TODOS = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM especie
    ORDER BY nome
"""

# Busca uma espécie por ID
OBTER_POR_ID = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM especie
    WHERE id=?
"""

# Busca uma espécie por nome
OBTER_POR_NOME = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM especie
    WHERE nome=?
"""