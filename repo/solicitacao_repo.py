"""Repository para solicitações de adoção."""

from typing import List, Optional
from model.solicitacao_model import Solicitacao
from sql.solicitacao_sql import *
from util.db_util import get_connection


def criar_tabela() -> None:
    """Cria a tabela solicitacao se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(solicitacao: Solicitacao) -> int:
    """
    Cria nova solicitação de adoção.

    Args:
        solicitacao: Objeto Solicitacao a ser inserido

    Returns:
        ID da solicitação criada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            solicitacao.id_adotante,
            solicitacao.id_animal,
            solicitacao.observacoes
        ))
        return cursor.lastrowid


def obter_por_adotante(id_adotante: int) -> List[dict]:
    """
    Lista solicitações do adotante.

    Args:
        id_adotante: ID do adotante

    Returns:
        Lista de dicionários com dados das solicitações
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ADOTANTE, (id_adotante,))
        return [dict(row) for row in cursor.fetchall()]


def obter_por_abrigo(id_abrigo: int) -> List[dict]:
    """
    Lista solicitações recebidas pelo abrigo.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Lista de dicionários com dados das solicitações
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [dict(row) for row in cursor.fetchall()]


def atualizar_status(id_solicitacao: int, status: str, resposta: str) -> bool:
    """
    Atualiza status da solicitação.

    Args:
        id_solicitacao: ID da solicitação
        status: Novo status (Pendente, Aprovada, Rejeitada, Cancelada)
        resposta: Resposta do abrigo

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (status, resposta, id_solicitacao))
        return cursor.rowcount > 0