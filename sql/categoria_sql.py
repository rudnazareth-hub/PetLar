"""
SQL queries para a tabela de categorias.
"""

CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""

INSERIR = """
    INSERT INTO categoria (nome, descricao)
    VALUES (?, ?)
"""

OBTER_TODOS = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    ORDER BY nome
"""

OBTER_POR_ID = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE id = ?
"""

OBTER_POR_NOME = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE nome = ?
"""

ATUALIZAR = """
    UPDATE categoria
    SET nome = ?, descricao = ?, data_atualizacao = CURRENT_TIMESTAMP
    WHERE id = ?
"""

EXCLUIR = """
    DELETE FROM categoria
    WHERE id = ?
"""

CONTAR = """
    SELECT COUNT(*) as total
    FROM categoria
"""

BUSCAR_POR_TERMO = """
    SELECT id, nome, descricao, data_cadastro, data_atualizacao
    FROM categoria
    WHERE nome LIKE ? OR descricao LIKE ?
    ORDER BY nome
"""
