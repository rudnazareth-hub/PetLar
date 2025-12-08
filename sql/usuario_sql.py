# IMPORTANTE: O valor padrão corresponde a Perfil.ADOTANTE.value
# Fonte única da verdade: util.perfis.Perfil
# Valores válidos: 'Administrador' (Perfil.ADMIN.value), 'Adotante' (Perfil.ADOTANTE.value), 'Abrigo' (Perfil.ABRIGO.value)
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL,
    data_nascimento TEXT,
    numero_documento TEXT,
    telefone TEXT,
    confirmado INTEGER DEFAULT 0,
    token_redefinicao TEXT,
    data_token TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

INSERIR = """
INSERT INTO usuario (
    nome, email, senha, perfil,
    data_nascimento, numero_documento, telefone, confirmado
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

ALTERAR = """
UPDATE usuario
SET nome = ?, email = ?, perfil = ?
WHERE id = ?
"""

ATUALIZAR = """
UPDATE usuario
SET nome = ?, email = ?, perfil = ?,
    data_nascimento = ?, numero_documento = ?, telefone = ?
WHERE id = ?
"""

ALTERAR_SENHA = """
UPDATE usuario
SET senha = ?
WHERE id = ?
"""

EXCLUIR = "DELETE FROM usuario WHERE id = ?"

OBTER_POR_ID = "SELECT * FROM usuario WHERE id = ?"

OBTER_TODOS = "SELECT * FROM usuario ORDER BY nome"

OBTER_QUANTIDADE = "SELECT COUNT(*) as quantidade FROM usuario"

OBTER_POR_EMAIL = "SELECT * FROM usuario WHERE email = ?"

ATUALIZAR_TOKEN = """
UPDATE usuario
SET token_redefinicao = ?, data_token = ?
WHERE email = ?
"""

OBTER_POR_TOKEN = """
SELECT * FROM usuario
WHERE token_redefinicao = ?
"""

LIMPAR_TOKEN = """
UPDATE usuario
SET token_redefinicao = NULL, data_token = NULL
WHERE id = ?
"""

OBTER_TODOS_POR_PERFIL = """
SELECT * FROM usuario
WHERE perfil = ?
ORDER BY nome
"""

BUSCAR_POR_TERMO = """
SELECT id, nome, email, senha, perfil,
       data_nascimento, numero_documento, telefone, confirmado,
       token_redefinicao, data_token, data_cadastro
FROM usuario
WHERE (LOWER(nome) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?))
LIMIT ?
"""
