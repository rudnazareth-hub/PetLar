"""
Comandos SQL para a tabela abrigo.
Relacionamento 1:1 com usuario (id_abrigo = id do usuario)
"""

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

OBTER_TODOS = """
SELECT a.*, u.nome, u.email
FROM abrigo a
INNER JOIN usuario u ON a.id_abrigo = u.id
ORDER BY u.nome
"""

OBTER_POR_ID = """
SELECT a.*, u.nome, u.email
FROM abrigo a
INNER JOIN usuario u ON a.id_abrigo = u.id
WHERE a.id_abrigo = ?
"""

ATUALIZAR = """
UPDATE abrigo
SET responsavel = ?, descricao = ?, data_abertura = ?, data_membros = ?
WHERE id_abrigo = ?
"""

EXCLUIR = """
DELETE FROM abrigo WHERE id_abrigo = ?
"""