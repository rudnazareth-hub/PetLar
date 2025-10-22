"""SQL para abrigos."""

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

OBTER_POR_ID = """
SELECT * FROM abrigo WHERE id_abrigo = ?
"""

OBTER_TODOS = """
SELECT * FROM abrigo
"""

ATUALIZAR = """
UPDATE abrigo
SET responsavel = ?, descricao = ?, data_abertura = ?, data_membros = ?
WHERE id_abrigo = ?
"""

EXCLUIR = """
DELETE FROM abrigo WHERE id_abrigo = ?
"""
