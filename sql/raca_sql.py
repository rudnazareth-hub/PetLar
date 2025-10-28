"""
Comandos SQL para a tabela raca.
Relacionamento: Raca N:1 Especie
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS raca (
    id_raca INTEGER PRIMARY KEY AUTOINCREMENT,
    id_especie INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    temperamento TEXT,
    expectativa_de_vida TEXT,
    porte TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_especie) REFERENCES especie(id_especie),
    UNIQUE(id_especie, nome)
)
"""

INSERIR = """
INSERT INTO raca (
    id_especie, nome, descricao,
    temperamento, expectativa_de_vida, porte
)
VALUES (?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT
    r.id_raca, r.id_especie, r.nome, r.descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    r.data_cadastro, r.data_atualizacao,
    e.id_especie as especie_id, e.nome as especie_nome, e.descricao as especie_descricao
FROM raca r
LEFT JOIN especie e ON r.id_especie = e.id_especie
ORDER BY e.nome, r.nome
"""

OBTER_POR_ID = """
SELECT
    r.id_raca, r.id_especie, r.nome, r.descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    r.data_cadastro, r.data_atualizacao,
    e.id_especie as especie_id, e.nome as especie_nome, e.descricao as especie_descricao
FROM raca r
LEFT JOIN especie e ON r.id_especie = e.id_especie
WHERE r.id_raca = ?
"""

OBTER_POR_ESPECIE = """
SELECT
    r.id_raca, r.id_especie, r.nome, r.descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    r.data_cadastro, r.data_atualizacao,
    e.id_especie as especie_id, e.nome as especie_nome, e.descricao as especie_descricao
FROM raca r
LEFT JOIN especie e ON r.id_especie = e.id_especie
WHERE r.id_especie = ?
ORDER BY r.nome
"""

ATUALIZAR = """
UPDATE raca
SET id_especie = ?, nome = ?, descricao = ?,
    temperamento = ?, expectativa_de_vida = ?, porte = ?,
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id_raca = ?
"""

EXCLUIR = """
DELETE FROM raca
WHERE id_raca = ?
"""

CONTAR = """
SELECT COUNT(*) FROM raca
"""

BUSCAR_POR_TERMO = """
SELECT
    r.id_raca, r.id_especie, r.nome, r.descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    r.data_cadastro, r.data_atualizacao,
    e.id_especie as especie_id, e.nome as especie_nome, e.descricao as especie_descricao
FROM raca r
LEFT JOIN especie e ON r.id_especie = e.id_especie
WHERE r.nome LIKE ? OR r.descricao LIKE ? OR e.nome LIKE ?
ORDER BY e.nome, r.nome
"""

# Query para verificar se raça tem animais vinculados
CONTAR_ANIMAIS = """
SELECT COUNT(*) as total
FROM animal
WHERE id_raca = ?
"""