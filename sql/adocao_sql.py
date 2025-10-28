"""SQL para adoções finalizadas."""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS adocao (
    id_adocao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_adotante INTEGER NOT NULL,
    id_animal INTEGER NOT NULL,
    data_solicitacao DATETIME NOT NULL,
    data_adocao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Concluída',
    observacoes TEXT,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_adotante) REFERENCES adotante(id_adotante),
    FOREIGN KEY (id_animal) REFERENCES animal(id_animal),
    UNIQUE(id_animal)
)
"""

INSERIR = """
INSERT INTO adocao (id_adotante, id_animal, data_solicitacao, observacoes)
VALUES (?, ?, ?, ?)
"""

OBTER_POR_ABRIGO = """
SELECT
    ad.id_adocao, ad.id_adotante, ad.id_animal, ad.data_solicitacao,
    ad.data_adocao, ad.status, ad.observacoes, ad.data_atualizacao,
    a.nome as animal_nome,
    u.nome as adotante_nome
FROM adocao ad
INNER JOIN animal a ON ad.id_animal = a.id_animal
INNER JOIN usuario u ON ad.id_adotante = u.id
WHERE a.id_abrigo = ?
ORDER BY ad.data_adocao DESC
"""