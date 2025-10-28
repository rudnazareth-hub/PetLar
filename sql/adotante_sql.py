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
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_adotante) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO adotante (id_adotante, renda_media, tem_filhos, estado_de_saude)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ID = """
SELECT id_adotante, renda_media, tem_filhos, estado_de_saude, data_cadastro, data_atualizacao
FROM adotante WHERE id_adotante = ?
"""

ATUALIZAR = """
UPDATE adotante
SET renda_media = ?, tem_filhos = ?, estado_de_saude = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id_adotante = ?
"""

EXCLUIR = """
DELETE FROM adotante WHERE id_adotante = ?
"""