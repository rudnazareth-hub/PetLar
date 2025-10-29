"""Repository para visitas agendadas."""

from typing import List, Optional
from datetime import datetime
from model.visita_model import Visita
from sql.visita_sql import *
from util.db_util import get_connection


def _converter_data(data_str: Optional[str]) -> Optional[datetime]:
    """Converte string de data do banco em objeto datetime"""
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def _row_to_visita(row) -> Visita:
    """Converte linha do banco em objeto Visita."""
    return Visita(
        id_visita=row["id_visita"],
        id_adotante=row["id_adotante"],
        id_abrigo=row["id_abrigo"],
        data_agendada=_converter_data(row["data_agendada"]),
        observacoes=row["observacoes"],
        status=row["status"] if row["status"] else "Agendada",
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"],
        adotante=None,
        abrigo=None
    )


def criar_tabela() -> bool:
    """Cria a tabela visita se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(visita: Visita) -> int:
    """
    Agenda uma nova visita.

    Args:
        visita: Objeto Visita a ser inserido

    Returns:
        ID da visita inserida
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            visita.id_adotante,
            visita.id_abrigo,
            visita.data_agendada,
            visita.observacoes
        ))
        return cursor.lastrowid


def obter_por_adotante(id_adotante: int) -> List[dict]:
    """
    Lista visitas de um adotante.

    Args:
        id_adotante: ID do adotante

    Returns:
        Lista de dicionários com dados das visitas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ADOTANTE, (id_adotante,))
        return [dict(row) for row in cursor.fetchall()]


def obter_por_abrigo(id_abrigo: int) -> List[dict]:
    """
    Lista visitas agendadas para um abrigo.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Lista de dicionários com dados das visitas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [dict(row) for row in cursor.fetchall()]


def atualizar_status(id_visita: int, status: str) -> bool:
    """
    Atualiza status de uma visita.

    Args:
        id_visita: ID da visita
        status: Novo status (Agendada, Realizada, Cancelada)

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (status, id_visita))
        return cursor.rowcount > 0


def reagendar(id_visita: int, nova_data: str) -> bool:
    """
    Reagenda uma visita.

    Args:
        id_visita: ID da visita
        nova_data: Nova data agendada

    Returns:
        True se reagendamento foi bem-sucedido, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(REAGENDAR, (nova_data, id_visita))
        return cursor.rowcount > 0


def obter_todos() -> List[dict]:
    """
    Retorna todas as visitas cadastradas.

    Returns:
        Lista de dicionários com dados das visitas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [dict(row) for row in cursor.fetchall()]


def contar() -> int:
    """
    Retorna o total de visitas cadastradas.

    Returns:
        Número total de visitas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[dict]:
    """
    Busca visitas por termo (nome do adotante, abrigo ou observações).

    Args:
        termo: Termo de busca

    Returns:
        Lista de dicionários com dados das visitas que correspondem ao termo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like, termo_like))
        return [dict(row) for row in cursor.fetchall()]


def excluir(id_visita: int) -> bool:
    """
    Exclui uma visita pelo ID.

    Args:
        id_visita: ID da visita a ser excluída

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_visita,))
        return cursor.rowcount > 0
