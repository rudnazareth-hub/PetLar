"""
Comandos SQL para a tabela animal.
Relacionamentos: Animal N:1 Raca, Animal N:1 Abrigo
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS animal (
    id_animal INTEGER PRIMARY KEY AUTOINCREMENT,
    id_raca INTEGER NOT NULL,
    id_abrigo INTEGER NOT NULL,
    nome TEXT NOT NULL,
    sexo TEXT NOT NULL,
    data_nascimento TEXT,
    data_entrada TEXT NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'Disponível',
    foto TEXT,
    FOREIGN KEY (id_raca) REFERENCES raca(id_raca),
    FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo)
)
"""

INSERIR = """
INSERT INTO animal (
    id_raca, id_abrigo, nome, sexo, data_nascimento,
    data_entrada, observacoes, status, foto
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT
    a.*,
    r.id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id_raca
LEFT JOIN especie e ON r.id_especie = e.id_especie
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.status = 'Disponível'
ORDER BY a.data_entrada DESC
"""

OBTER_POR_ID = """
SELECT
    a.*,
    r.id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id_raca
LEFT JOIN especie e ON r.id_especie = e.id_especie
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.id_animal = ?
"""

OBTER_POR_ABRIGO = """
SELECT
    a.*,
    r.id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id_raca
LEFT JOIN especie e ON r.id_especie = e.id_especie
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.id_abrigo = ?
ORDER BY a.data_entrada DESC
"""

BUSCAR_DISPONIVEIS = """
SELECT
    a.*,
    r.nome as raca_nome, r.porte,
    e.nome as especie_nome
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id_raca
LEFT JOIN especie e ON r.id_especie = e.id_especie
WHERE a.status = 'Disponível'
"""

ATUALIZAR = """
UPDATE animal
SET id_raca = ?, nome = ?, sexo = ?, data_nascimento = ?,
    observacoes = ?, status = ?
WHERE id_animal = ?
"""

ATUALIZAR_STATUS = """
UPDATE animal SET status = ? WHERE id_animal = ?
"""

EXCLUIR = """
DELETE FROM animal WHERE id_animal = ?
"""