"""Repository para solicitações de adoção."""

from typing import List, Optional
from model.solicitacao_model import Solicitacao
from sql.solicitacao_sql import *
from util.db_util import get_connection


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(solicitacao: Solicitacao) -> int:
    """Cria nova solicitação de adoção."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            solicitacao.id_adotante,
            solicitacao.id_animal,
            solicitacao.observacoes
        ))
        return cursor.lastrowid


def obter_por_adotante(id_adotante: int) -> List[dict]:
    """Lista solicitações do adotante."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ADOTANTE, (id_adotante,))
        return [dict(row) for row in cursor.fetchall()]


def obter_por_abrigo(id_abrigo: int) -> List[dict]:
    """Lista solicitações recebidas pelo abrigo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [dict(row) for row in cursor.fetchall()]


def atualizar_status(id_solicitacao: int, status: str, resposta: str) -> None:
    """
    Atualiza status da solicitação.
    Status possíveis: Pendente, Aprovada, Rejeitada, Cancelada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (status, resposta, id_solicitacao))