CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS configuracao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descricao TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO configuracao (chave, valor, descricao)
VALUES (?, ?, ?)
"""

OBTER_POR_ID = """
SELECT id, chave, valor, descricao, data_cadastro, data_atualizacao
FROM configuracao
WHERE id = ?
"""

OBTER_POR_CHAVE = """
SELECT id, chave, valor, descricao, data_cadastro, data_atualizacao
FROM configuracao
WHERE chave = ?
"""

OBTER_TODOS = """
SELECT id, chave, valor, descricao, data_cadastro, data_atualizacao
FROM configuracao
ORDER BY chave
"""

ATUALIZAR = """
UPDATE configuracao
SET valor = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE chave = ?
"""

EXCLUIR = """
DELETE FROM configuracao WHERE id = ?
"""

CONTAR = """
SELECT COUNT(*) FROM configuracao
"""

BUSCAR_POR_TERMO = """
SELECT id, chave, valor, descricao, data_cadastro, data_atualizacao
FROM configuracao
WHERE chave LIKE ? OR valor LIKE ? OR descricao LIKE ?
ORDER BY chave
"""
