"""
Comandos SQL para a tabela animal.
Relacionamentos: Animal N:1 Raca, Animal N:1 Abrigo
Status: Disponível, Reservado, Adotado, Indisponível
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
    id_adotante_reserva INTEGER,
    data_reserva TIMESTAMP,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_raca) REFERENCES raca(id),
    FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo),
    FOREIGN KEY (id_adotante_reserva) REFERENCES usuario(id)
)
"""

# Adicionar colunas de reserva se não existirem (migração)
ADICIONAR_COLUNA_ID_ADOTANTE_RESERVA = """
ALTER TABLE animal ADD COLUMN id_adotante_reserva INTEGER REFERENCES usuario(id)
"""

ADICIONAR_COLUNA_DATA_RESERVA = """
ALTER TABLE animal ADD COLUMN data_reserva TIMESTAMP
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
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.status = 'Disponivel'
ORDER BY a.data_entrada DESC
"""

OBTER_TODOS_SEM_FILTRO = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
ORDER BY a.data_entrada DESC
"""

OBTER_POR_ID = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
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
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.id_abrigo = ?
ORDER BY a.data_entrada DESC
"""

OBTER_RESERVADOS_POR_ABRIGO = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel,
    u.nome as adotante_nome, u.email as adotante_email, u.telefone as adotante_telefone
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
LEFT JOIN usuario u ON a.id_adotante_reserva = u.id
WHERE a.id_abrigo = ? AND a.status = 'Reservado'
ORDER BY a.data_reserva DESC
"""

BUSCAR_DISPONIVEIS = """
SELECT
    a.*,
    r.nome as raca_nome, r.porte, r.id_especie,
    e.nome as especie_nome
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
WHERE a.status = 'Disponivel'
"""

# Query para busca publica com filtros
BUSCAR_DISPONIVEIS_COM_FILTROS = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.id as especie_id, e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel,
    en.cidade as abrigo_cidade, en.uf as abrigo_uf
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
LEFT JOIN endereco en ON ab.id_abrigo = en.id_usuario
WHERE a.status = 'Disponivel'
"""

# Query para obter ultimos animais cadastrados
OBTER_ULTIMOS_CADASTRADOS = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel,
    en.cidade as abrigo_cidade, en.uf as abrigo_uf
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
LEFT JOIN endereco en ON ab.id_abrigo = en.id_usuario
WHERE a.status = 'Disponivel'
ORDER BY a.data_cadastro DESC
LIMIT ?
"""

ATUALIZAR = """
UPDATE animal
SET id_raca = ?, nome = ?, sexo = ?, data_nascimento = ?,
    observacoes = ?, status = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

ATUALIZAR_COMPLETO = """
UPDATE animal
SET id_raca = ?, nome = ?, sexo = ?, data_nascimento = ?, data_entrada = ?,
    observacoes = ?, status = ?, foto = ?, data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

ATUALIZAR_STATUS = """
UPDATE animal SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?
"""

ATUALIZAR_FOTO = """
UPDATE animal SET foto = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?
"""

# Reservar animal para adotante
RESERVAR_ANIMAL = """
UPDATE animal
SET status = 'Reservado',
    id_adotante_reserva = ?,
    data_reserva = CURRENT_TIMESTAMP,
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ? AND status = 'Disponivel'
"""

# Cancelar reserva
CANCELAR_RESERVA = """
UPDATE animal
SET status = 'Disponivel',
    id_adotante_reserva = NULL,
    data_reserva = NULL,
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

# Concluir adocao
CONCLUIR_ADOCAO = """
UPDATE animal
SET status = 'Adotado',
    data_atualizacao = CURRENT_TIMESTAMP
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM animal WHERE id = ?
"""

CONTAR = """
SELECT COUNT(*) FROM animal
"""

CONTAR_POR_ABRIGO = """
SELECT COUNT(*) FROM animal WHERE id_abrigo = ?
"""

CONTAR_DISPONIVEIS = """
SELECT COUNT(*) FROM animal WHERE status = 'Disponivel'
"""

BUSCAR_POR_TERMO = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
WHERE a.nome LIKE ? OR r.nome LIKE ? OR e.nome LIKE ? OR ab.responsavel LIKE ?
ORDER BY a.data_entrada DESC
"""

# Verificar se animal pertence ao abrigo
VERIFICAR_PROPRIEDADE = """
SELECT COUNT(*) FROM animal WHERE id = ? AND id_abrigo = ?
"""

# Obter animal com dados do adotante que reservou
OBTER_POR_ID_COM_ADOTANTE = """
SELECT
    a.*,
    r.id as id_raca, r.nome as raca_nome, r.descricao as raca_descricao,
    r.temperamento, r.expectativa_de_vida, r.porte, r.id_especie,
    e.nome as especie_nome,
    ab.id_abrigo, ab.responsavel,
    u.id as adotante_id, u.nome as adotante_nome, u.email as adotante_email,
    u.telefone as adotante_telefone
FROM animal a
LEFT JOIN raca r ON a.id_raca = r.id
LEFT JOIN especie e ON r.id_especie = e.id
LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
LEFT JOIN usuario u ON a.id_adotante_reserva = u.id
WHERE a.id = ?
"""
