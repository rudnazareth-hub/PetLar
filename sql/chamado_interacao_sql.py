"""
Queries SQL para a tabela de interações de chamados.

Todas as queries usam prepared statements com placeholders (?)
para prevenir SQL injection.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chamado_interacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chamado_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    tipo TEXT NOT NULL,
    data_interacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status_resultante TEXT,
    FOREIGN KEY (chamado_id) REFERENCES chamado(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
)
"""

INSERIR = """
INSERT INTO chamado_interacao (chamado_id, usuario_id, mensagem, tipo, status_resultante)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_POR_CHAMADO = """
SELECT ci.*,
       u.nome as usuario_nome,
       u.email as usuario_email
FROM chamado_interacao ci
INNER JOIN usuario u ON ci.usuario_id = u.id
WHERE ci.chamado_id = ?
ORDER BY ci.data_interacao ASC
"""

OBTER_POR_ID = """
SELECT ci.*,
       u.nome as usuario_nome,
       u.email as usuario_email
FROM chamado_interacao ci
INNER JOIN usuario u ON ci.usuario_id = u.id
WHERE ci.id = ?
"""

CONTAR_POR_CHAMADO = """
SELECT COUNT(*) as total
FROM chamado_interacao
WHERE chamado_id = ?
"""

EXCLUIR_POR_CHAMADO = """
DELETE FROM chamado_interacao WHERE chamado_id = ?
"""
