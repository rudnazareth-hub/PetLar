# Queries SQL para operações com espécies

# Cria a tabela especie se ela não existir
CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS especie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        descricao TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP
    )
"""

# Insere uma nova especie
INSERIR = """
    INSERT INTO especie (nome, descricao)
    VALUES (?, ?)
"""

# Atualiza uma especie existente
ALTERAR = """
    UPDATE especie
    SET nome=?, descricao=?, data_atualizacao=CURRENT_TIMESTAMP
    WHERE id=?
"""

# Exclui uma especie
EXCLUIR = """
    DELETE FROM especie WHERE id=?
"""

# Busca todas as espécies ordenadas por nome
OBTER_TODOS = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM especie
    ORDER BY nome
"""

# Busca uma especie por ID
OBTER_POR_ID = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM especie
    WHERE id=?
"""

# Busca uma especie por nome
OBTER_POR_NOME = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM especie
    WHERE nome=?
"""