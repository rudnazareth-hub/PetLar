"""Repository para adoções finalizadas."""

from typing import List, Optional
from datetime import datetime
from model.adocao_model import Adocao
from sql.adocao_sql import *
from util.db_util import get_connection


def _converter_data(data_str: Optional[str]) -> Optional[datetime]:
    """Converte string de data do banco em objeto datetime"""
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def _row_to_adocao(row) -> Adocao:
    """Converte linha do banco em objeto Adocao."""
    return Adocao(
        id_adocao=row["id_adocao"],
        id_adotante=row["id_adotante"],
        id_animal=row["id_animal"],
        data_solicitacao=_converter_data(row["data_solicitacao"]),
        data_adocao=_converter_data(row["data_adocao"]),
        status=row["status"] if row["status"] else "Concluída",
        observacoes=row["observacoes"],
        data_atualizacao=row.get("data_atualizacao"),
        adotante=None,
        animal=None
    )


def criar_tabela() -> bool:
    """Cria a tabela adocao se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(adocao: Adocao) -> int:
    """
    Registra uma adoção finalizada.

    Args:
        adocao: Objeto Adocao a ser inserido

    Returns:
        ID da adoção inserida
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            adocao.id_adotante,
            adocao.id_animal,
            adocao.data_solicitacao,
            adocao.observacoes
        ))
        return cursor.lastrowid


def obter_por_abrigo(id_abrigo: int) -> List[dict]:
    """
    Lista adoções finalizadas de um abrigo.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Lista de dicionários com dados das adoções
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [dict(row) for row in cursor.fetchall()]
