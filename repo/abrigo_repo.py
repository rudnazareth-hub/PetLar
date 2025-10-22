"""Repository para abrigos."""

from typing import List, Optional
from model.abrigo_model import Abrigo
from sql.abrigo_sql import *
from util.db_util import get_connection


def _row_to_abrigo(row) -> Abrigo:
    return Abrigo(
        id_abrigo=row["id_abrigo"],
        responsavel=row["responsavel"],
        descricao=row.get("descricao"),
        data_abertura=row.get("data_abertura"),
        data_membros=row.get("data_membros")
    )


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(abrigo: Abrigo) -> None:
    """Insere abrigo usando ID do usuário existente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            abrigo.id_abrigo,
            abrigo.responsavel,
            abrigo.descricao,
            abrigo.data_abertura,
            abrigo.data_membros
        ))


def obter_por_id(id_abrigo: int) -> Optional[Abrigo]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_abrigo,))
        row = cursor.fetchone()
        return _row_to_abrigo(row) if row else None


def obter_todos() -> List[Abrigo]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_abrigo(row) for row in cursor.fetchall()]


def atualizar(abrigo: Abrigo) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            abrigo.responsavel,
            abrigo.descricao,
            abrigo.data_abertura,
            abrigo.data_membros,
            abrigo.id_abrigo
        ))


def excluir(id_abrigo: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_abrigo,))