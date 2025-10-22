"""Repository para adotantes."""

from typing import Optional
from model.adotante_model import Adotante
from sql.adotante_sql import *
from util.db_util import get_connection


def _row_to_adotante(row) -> Adotante:
    return Adotante(
        id_adotante=row["id_adotante"],
        renda_media=row["renda_media"],
        tem_filhos=bool(row["tem_filhos"]),
        estado_saude=row["estado_de_saude"]
    )


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(adotante: Adotante) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            adotante.id_adotante,
            adotante.renda_media,
            1 if adotante.tem_filhos else 0,
            adotante.estado_saude
        ))


def obter_por_id(id_adotante: int) -> Optional[Adotante]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_adotante,))
        row = cursor.fetchone()
        return _row_to_adotante(row) if row else None


def atualizar(adotante: Adotante) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            adotante.renda_media,
            1 if adotante.tem_filhos else 0,
            adotante.estado_saude,
            adotante.id_adotante
        ))