"""
Comandos SQL para a tabela animal.
Relacionamentos: Animal N:1 Raca, Animal N:1 Abrigo
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS animal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_raca INTEGER NOT NULL,
    id_abrigo INTEGER NOT NULL,
    nome TEXT NOT NULL,
    sexo TEXT NOT NULL,
    data_nascimento TEXT,
    data_entrada TEXT NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'Disponível',
    foto TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_raca) REFERENCES raca(id),
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
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id as id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.status = 'Disponível'
ORDER BY a.data_entrada DESC
"""

OBTER_POR_ID = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id as id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.id = ?
"""

OBTER_POR_ABRIGO = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id as id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
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
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
WHERE a.status = 'Disponível'
"""

ATUALIZAR = """
UPDATE animal
SET id_raca = ?, nome = ?, sexo = ?, data_nascimento = ?,
    observacoes = ?, status = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

ATUALIZAR_STATUS = """
UPDATE animal SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?
"""

EXCLUIR = """
DELETE FROM animal WHERE id = ?
"""

CONTAR = """
SELECT COUNT(*) FROM animal
"""

BUSCAR_POR_TERMO = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte,
    e.id as id_especie, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.nome LIKE ? OR r.nome LIKE ? OR e.nome LIKE ? OR ab.responsavel LIKE ?
ORDER BY a.data_entrada DESC
"""