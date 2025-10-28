"""
Comandos SQL para a tabela adotante.
Relacionamento 1:1 com usuario (id_adotante = id do usuario)
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS adotante (
    id_adotante INTEGER PRIMARY KEY,
    renda_media REAL NOT NULL,
    tem_filhos INTEGER NOT NULL DEFAULT 0,
    estado_de_saude TEXT,
    FOREIGN KEY (id_adotante) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO adotante (id_adotante, renda_media, tem_filhos, estado_de_saude)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ID = """
SELECT * FROM adotante WHERE id_adotante = ?
"""

ATUALIZAR = """
UPDATE adotante
SET renda_media = ?, tem_filhos = ?, estado_de_saude = ?
WHERE id_adotante = ?
"""

EXCLUIR = """
DELETE FROM adotante WHERE id_adotante = ?
"""