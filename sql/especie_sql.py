
"""
Comandos SQL para a tabela especie.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS especie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO especie (nome, descricao)
VALUES (?, ?)
"""

OBTER_TODOS = """
SELECT id, nome, descricao, data_cadastro, data_atualizacao
FROM especie
ORDER BY nome
"""

OBTER_POR_ID = """
SELECT id, nome, descricao, data_cadastro, data_atualizacao
FROM especie
WHERE id = ?
"""

OBTER_POR_NOME = """
SELECT id, nome, descricao, data_cadastro, data_atualizacao
FROM especie
WHERE nome = ?
"""

ATUALIZAR = """
UPDATE especie
SET nome = ?, descricao = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM especie
WHERE id = ?
"""

CONTAR = """
SELECT COUNT(*) FROM especie
"""

BUSCAR_POR_TERMO = """
SELECT id, nome, descricao, data_cadastro, data_atualizacao
FROM especie
WHERE nome LIKE ? OR descricao LIKE ?
ORDER BY nome
"""

# Query para verificar se especie tem raças vinculadas
CONTAR_RACAS = """
SELECT COUNT(*) as total
FROM raca
WHERE id_especie = ?
"""