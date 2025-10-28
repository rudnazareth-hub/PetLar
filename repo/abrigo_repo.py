"""Repository para abrigos."""

from typing import List, Optional
from model.abrigo_model import Abrigo
from sql.abrigo_sql import *
from util.db_util import get_connection


def _row_to_abrigo(row) -> Abrigo:
    """Converte linha do banco em objeto Abrigo."""
    return Abrigo(
        id_abrigo=row["id_abrigo"],
        responsavel=row["responsavel"],
        descricao=row["descricao"],
        data_abertura=row["data_abertura"],
        data_membros=row["data_membros"],
        data_cadastro=row.get("data_cadastro"),
        data_atualizacao=row.get("data_atualizacao")
    )


def criar_tabela() -> bool:
    """Cria a tabela abrigo se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(abrigo: Abrigo) -> int:
    """
    Insere abrigo usando ID do usuário existente.

    Args:
        abrigo: Objeto Abrigo a ser inserido

    Returns:
        ID do abrigo inserido
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            abrigo.id_abrigo,
            abrigo.responsavel,
            abrigo.descricao,
            abrigo.data_abertura,
            abrigo.data_membros
        ))
        return abrigo.id_abrigo


def obter_por_id(id_abrigo: int) -> Optional[Abrigo]:
    """
    Busca um abrigo pelo ID.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Objeto Abrigo ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_abrigo,))
        row = cursor.fetchone()
        return _row_to_abrigo(row) if row else None


def obter_todos() -> List[Abrigo]:
    """
    Retorna todos os abrigos cadastrados.

    Returns:
        Lista de objetos Abrigo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_abrigo(row) for row in cursor.fetchall()]


def atualizar(abrigo: Abrigo) -> bool:
    """
    Atualiza um abrigo existente.

    Args:
        abrigo: Objeto Abrigo com dados atualizados

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            abrigo.responsavel,
            abrigo.descricao,
            abrigo.data_abertura,
            abrigo.data_membros,
            abrigo.id_abrigo
        ))
        return cursor.rowcount > 0


def excluir(id_abrigo: int) -> bool:
    """
    Exclui um abrigo pelo ID.

    Args:
        id_abrigo: ID do abrigo a ser excluído

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_abrigo,))
        return cursor.rowcount > 0