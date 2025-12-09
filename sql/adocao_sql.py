"""SQL para adoções finalizadas."""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS adocao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_animal INTEGER NOT NULL,
    data_adocao DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_adotante) REFERENCES usuario(id),
    FOREIGN KEY (id_animal) REFERENCES animal(id),
    UNIQUE(id_animal)
)
"""

INSERIR = """
INSERT INTO adocao (id_adotante, id_animal, data_adocao, observacoes)
VALUES (?, ?, CURRENT_TIMESTAMP, ?)
"""

OBTER_POR_ID = """
SELECT
    ad.id, ad.id_adotante, ad.id_animal, ad.data_adocao,
    ad.observacoes, ad.data_cadastro, ad.data_atualizacao,
    a.nome as animal_nome, a.foto as animal_foto,
    u.nome as adotante_nome, u.email as adotante_email
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE ad.id = ?
"""

OBTER_POR_ANIMAL = """
SELECT
    ad.id, ad.id_adotante, ad.id_animal, ad.data_adocao,
    ad.observacoes, ad.data_cadastro, ad.data_atualizacao,
    a.nome as animal_nome, a.foto as animal_foto,
    u.nome as adotante_nome, u.email as adotante_email
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE ad.id_animal = ?
"""

OBTER_POR_ADOTANTE = """
SELECT
    ad.id, ad.id_adotante, ad.id_animal, ad.data_adocao,
    ad.observacoes, ad.data_cadastro, ad.data_atualizacao,
    a.nome as animal_nome, a.foto as animal_foto, a.sexo as animal_sexo,
    r.nome as raca_nome,
    e.nome as especie_nome,
    ab.responsavel as abrigo_nome,
    u.nome as adotante_nome, u.email as adotante_email
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id
INNER JOIN usuario u ON ad.id_adotante = u.id
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE ad.id_adotante = ?
ORDER BY ad.data_adocao DESC
"""

OBTER_POR_ABRIGO = """
SELECT
    ad.id, ad.id_adotante, ad.id_animal, ad.data_adocao,
    ad.observacoes, ad.data_cadastro, ad.data_atualizacao,
    a.nome as animal_nome, a.foto as animal_foto,
    u.nome as adotante_nome, u.email as adotante_email
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE a.id_abrigo = ?
ORDER BY ad.data_adocao DESC
"""

CONTAR = """
SELECT COUNT(*) FROM adocao
"""

CONTAR_POR_ABRIGO = """
SELECT COUNT(*) FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id
WHERE a.id_abrigo = ?
"""

CONTAR_POR_ADOTANTE = """
SELECT COUNT(*) FROM adocao WHERE id_adotante = ?
"""

OBTER_TODOS = """
SELECT
    ad.id, ad.id_adotante, ad.id_animal, ad.data_adocao,
    ad.observacoes, ad.data_cadastro, ad.data_atualizacao,
    a.nome as animal_nome, a.foto as animal_foto,
    u.nome as adotante_nome, u.email as adotante_email,
    ab.responsavel as abrigo_nome
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id
INNER JOIN usuario u ON ad.id_adotante = u.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
ORDER BY ad.data_adocao DESC
"""

BUSCAR_POR_TERMO = """
SELECT
    ad.id, ad.id_adotante, ad.id_animal, ad.data_adocao,
    ad.observacoes, ad.data_cadastro, ad.data_atualizacao,
    a.nome as animal_nome, a.foto as animal_foto,
    u.nome as adotante_nome, u.email as adotante_email
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE a.nome LIKE ? OR u.nome LIKE ? OR ad.observacoes LIKE ?
ORDER BY ad.data_adocao DESC
"""

EXCLUIR = """
DELETE FROM adocao WHERE id = ?
"""
