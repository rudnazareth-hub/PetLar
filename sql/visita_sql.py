"""SQL para visitas."""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS visita (
    id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_abrigo INTEGER NOT NULL,
    data_agendada DATETIME NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'Agendada',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo)
)
"""

INSERIR = """
INSERT INTO visita (id_adotante, id_abrigo, data_agendada, observacoes)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ADOTANTE = """
SELECT v.id_visita, v.id_adotante, v.id_abrigo, v.data_agendada,
       v.observacoes, v.status, v.data_cadastro, v.data_atualizacao,
       ab.responsavel as abrigo_nome
FROM visita v
INNER JOIN abrigo ab ON v.id_abrigo = ab.id_abrigo
WHERE v.id_adotante = ?
ORDER BY v.data_agendada DESC
"""

OBTER_POR_ABRIGO = """
SELECT v.id_visita, v.id_adotante, v.id_abrigo, v.data_agendada,
       v.observacoes, v.status, v.data_cadastro, v.data_atualizacao,
       u.nome as adotante_nome, u.telefone
FROM visita v
INNER JOIN usuario u ON v.id_adotante = u.id
WHERE v.id_abrigo = ?
ORDER BY v.data_agendada DESC
"""

ATUALIZAR_STATUS = """
UPDATE visita SET status = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id_visita = ?
"""

REAGENDAR = """
UPDATE visita SET data_agendada = ?, status = 'Agendada', data_atualizacao = CURRENT_TIMESTAMP WHERE id_visita = ?
"""

CONTAR = """
SELECT COUNT(*) FROM visita
"""

OBTER_TODOS = """
SELECT v.id_visita, v.id_adotante, v.id_abrigo, v.data_agendada,
       v.observacoes, v.status, v.data_cadastro, v.data_atualizacao,
       u.nome as adotante_nome, ab.responsavel as abrigo_nome
FROM visita v
INNER JOIN usuario u ON v.id_adotante = u.id
INNER JOIN abrigo ab ON v.id_abrigo = ab.id_abrigo
ORDER BY v.data_agendada DESC
"""

BUSCAR_POR_TERMO = """
SELECT v.id_visita, v.id_adotante, v.id_abrigo, v.data_agendada,
       v.observacoes, v.status, v.data_cadastro, v.data_atualizacao,
       u.nome as adotante_nome, ab.responsavel as abrigo_nome
FROM visita v
INNER JOIN usuario u ON v.id_adotante = u.id
INNER JOIN abrigo ab ON v.id_abrigo = ab.id_abrigo
WHERE u.nome LIKE ? OR ab.responsavel LIKE ? OR v.observacoes LIKE ?
ORDER BY v.data_agendada DESC
"""

EXCLUIR = """
DELETE FROM visita WHERE id_visita = ?
"""