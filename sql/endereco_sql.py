"""
Comandos SQL para a tabela endereco.
Relacionamento: Usuario 1:N Endereco
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS endereco (
    id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    logradouro TEXT NOT NULL,
    numero INTEGER NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cidade TEXT NOT NULL,
    uf TEXT NOT NULL,
    cep TEXT NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO endereco (
    id_usuario, titulo, logradouro, numero,
    complemento, bairro, cidade, uf, cep
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT id_endereco, id_usuario, titulo, logradouro, numero, complemento,
       bairro, cidade, uf, cep, data_cadastro, data_atualizacao
FROM endereco ORDER BY titulo
"""

OBTER_POR_ID = """
SELECT id_endereco, id_usuario, titulo, logradouro, numero, complemento,
       bairro, cidade, uf, cep, data_cadastro, data_atualizacao
FROM endereco WHERE id_endereco = ?
"""

OBTER_POR_USUARIO = """
SELECT id_endereco, id_usuario, titulo, logradouro, numero, complemento,
       bairro, cidade, uf, cep, data_cadastro, data_atualizacao
FROM endereco WHERE id_usuario = ? ORDER BY titulo
"""

ATUALIZAR = """
UPDATE endereco
SET titulo = ?, logradouro = ?, numero = ?,
    complemento = ?, bairro = ?, cidade = ?, uf = ?, cep = ?,
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id_endereco = ?
"""

EXCLUIR = """
DELETE FROM endereco WHERE id_endereco = ?
"""