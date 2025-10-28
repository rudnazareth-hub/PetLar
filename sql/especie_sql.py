
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