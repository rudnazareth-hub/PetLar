"""SQL para abrigos."""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS abrigo (
    id_abrigo INTEGER PRIMARY KEY,
    responsavel TEXT NOT NULL,
    descricao TEXT,
    data_abertura TEXT,
    data_membros TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_abrigo) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO abrigo (id_abrigo, responsavel, descricao, data_abertura, data_membros)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_POR_ID = """
SELECT id_abrigo, responsavel, descricao, data_abertura, data_membros, data_cadastro, data_atualizacao
FROM abrigo WHERE id_abrigo = ?
"""

OBTER_TODOS = """
SELECT id_abrigo, responsavel, descricao, data_abertura, data_membros, data_cadastro, data_atualizacao
FROM abrigo
"""

ATUALIZAR = """
UPDATE abrigo
SET responsavel = ?, descricao = ?, data_abertura = ?, data_membros = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id_abrigo = ?
"""

EXCLUIR = """
DELETE FROM abrigo WHERE id_abrigo = ?
"""
