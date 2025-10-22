"""SQL para visitas."""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS visita (
    id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_abrigo INTEGER NOT NULL,
    data_agendada DATETIME NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'Agendada',
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo)
)
"""

INSERIR = """
INSERT INTO visita (id_adotante, id_abrigo, data_agendada, observacoes)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ADOTANTE = """
SELECT v.*, ab.responsavel as abrigo_nome
FROM visita v
INNER JOIN abrigo ab ON v.id_abrigo = ab.id_abrigo
WHERE v.id_adotante = ?
ORDER BY v.data_agendada DESC
"""

OBTER_POR_ABRIGO = """
SELECT v.*, u.nome as adotante_nome, u.telefone
FROM visita v
INNER JOIN usuario u ON v.id_adotante = u.id
WHERE v.id_abrigo = ?
ORDER BY v.data_agendada DESC
"""

ATUALIZAR_STATUS = """
UPDATE visita SET status = ? WHERE id_visita = ?
"""

REAGENDAR = """
UPDATE visita SET data_agendada = ?, status = 'Agendada' WHERE id_visita = ?
"""