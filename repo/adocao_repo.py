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
        id=row["id"],
        id_adotante=row["id_adotante"],
        id_animal=row["id_animal"],
        data_solicitacao=_converter_data(row["data_solicitacao"]),
        data_adocao=_converter_data(row["data_adocao"]),
        status=row["status"] if row["status"] else "Concluída",
        observacoes=row["observacoes"],
        data_atualizacao=row["data_atualizacao"],
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


def obter_todos() -> List[dict]:
    """
    Retorna todas as adoções cadastradas.

    Returns:
        Lista de dicionários com dados das adoções
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [dict(row) for row in cursor.fetchall()]


def contar() -> int:
    """
    Retorna o total de adoções cadastradas.

    Returns:
        Número total de adoções
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[dict]:
    """
    Busca adoções por termo (nome do animal, adotante ou observações).

    Args:
        termo: Termo de busca

    Returns:
        Lista de dicionários com dados das adoções que correspondem ao termo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like, termo_like))
        return [dict(row) for row in cursor.fetchall()]
