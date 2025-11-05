CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS curtida (
    id_usuario TEXT NOT NULL UNIQUE,
    id_animal TEXT NOT NULL
    data_curtida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id),
    FOREIGN KEY (id_animal) REFERENCES animal(id)
)
"""

INSERIR = "INSERT INTO curtida (id_usuario, descricao) VALUES (?, ?)"
EXCLUIR = "DELETE FROM curtida WHERE id_animal = ? AND id_usuario = ?"
OBTER_POR_ID = "SELECT * FROM curtida WHERE id_animal = ? AND id_usuario = ?"
OBTER_QUANTIDADE_POR_ANIMAL = "SELECT COUNT(*) AS quantidade FROM: BY id_animal = ?"