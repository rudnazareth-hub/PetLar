"""
Repository para criação de índices do banco de dados
"""
from util.db_util import get_connection
from util.logger_config import logger
from sql import indices_sql


def criar_indices() -> None:
    """
    Cria todos os índices do banco de dados.

    Deve ser chamado no startup da aplicação após criar todas as tabelas.
    Índices melhoram performance de queries frequentes.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            for indice_sql in indices_sql.TODOS_INDICES:
                try:
                    cursor.execute(indice_sql)
                    logger.debug(f"Índice criado com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao criar índice (pode já existir): {e}")

            logger.info("Todos os índices verificados/criados com sucesso")

    except Exception as e:
        logger.error(f"Erro ao criar índices: {e}")
        # Não lançar exceção - índices são otimização, não críticos
