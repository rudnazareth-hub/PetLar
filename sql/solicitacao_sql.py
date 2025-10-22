"""
Comandos SQL para solicitações de adoção.
Relacionamento: Solicitacao N:1 Adotante, Solicitacao N:1 Animal
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS solicitacao (
    id_solicitacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_animal INTEGER NOT NULL,
    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pendente',
    observacoes TEXT,
    resposta_abrigo TEXT,
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_animal) REFERENCES animal(id_animal)
)
"""

INSERIR = """
INSERT INTO solicitacao (id_adotante, id_animal, observacoes)
VALUES (?, ?, ?)
"""

OBTER_POR_ADOTANTE = """
SELECT s.*, a.nome as animal_nome, a.foto
FROM solicitacao s
INNER JOIN animal a ON s.id_animal = a.id_animal
WHERE s.id_adotante = ?
ORDER BY s.data_solicitacao DESC
"""

OBTER_POR_ABRIGO = """
SELECT
    s.*,
    a.nome as animal_nome,
    u.nome as adotante_nome, u.email as adotante_email, u.telefone
FROM solicitacao s
INNER JOIN animal a ON s.id_animal = a.id_animal
INNER JOIN adotante ad ON s.id_adotante = ad.id_adotante
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE a.id_abrigo = ?
ORDER BY s.data_solicitacao DESC
"""

ATUALIZAR_STATUS = """
UPDATE solicitacao
SET status = ?, resposta_abrigo = ?
WHERE id_solicitacao = ?
"""