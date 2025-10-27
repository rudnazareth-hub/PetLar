"""
Repositório para operações de banco de dados relacionadas a interações de chamados.

Implementa a camada de acesso a dados (DAL) para a entidade ChamadoInteracao,
seguindo o padrão de Repository com funções CRUD.
"""

from datetime import datetime
from typing import Optional
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from sql.chamado_interacao_sql import *
from util.db_util import get_connection


def _converter_data(data_str: Optional[str]) -> datetime:
    """
    Converte string de data do banco em objeto datetime.

    Args:
        data_str: String no formato 'YYYY-MM-DD HH:MM:SS'

    Returns:
        datetime object
    """
    if not data_str:
        return datetime.now()
    try:
        return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return datetime.now()


def _row_to_interacao(row) -> ChamadoInteracao:
    """
    Converte uma linha do banco de dados em objeto ChamadoInteracao.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto ChamadoInteracao populado
    """
    # Verificar se os campos do JOIN existem
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None
    usuario_email = row["usuario_email"] if "usuario_email" in row.keys() else None

    return ChamadoInteracao(
        id=row["id"],
        chamado_id=row["chamado_id"],
        usuario_id=row["usuario_id"],
        mensagem=row["mensagem"],
        tipo=TipoInteracao(row["tipo"]),
        data_interacao=_converter_data(row["data_interacao"]),
        status_resultante=row["status_resultante"] if row["status_resultante"] else None,
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )


def criar_tabela() -> bool:
    """
    Cria a tabela de interações de chamados no banco de dados se não existir.

    Returns:
        True se operação foi bem sucedida
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(interacao: ChamadoInteracao) -> Optional[int]:
    """
    Insere uma nova interação no banco de dados.

    Args:
        interacao: Objeto ChamadoInteracao a ser inserido

    Returns:
        ID da interação inserida ou None em caso de erro
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            interacao.chamado_id,
            interacao.usuario_id,
            interacao.mensagem,
            interacao.tipo.value,
            interacao.status_resultante
        ))
        return cursor.lastrowid


def obter_por_chamado(chamado_id: int) -> list[ChamadoInteracao]:
    """
    Obtém todas as interações de um chamado específico.

    Args:
        chamado_id: ID do chamado

    Returns:
        Lista de objetos ChamadoInteracao ordenados por data
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CHAMADO, (chamado_id,))
        rows = cursor.fetchall()
        return [_row_to_interacao(row) for row in rows]


def obter_por_id(id: int) -> Optional[ChamadoInteracao]:
    """
    Obtém uma interação específica por ID.

    Args:
        id: ID da interação

    Returns:
        Objeto ChamadoInteracao ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_interacao(row)
        return None


def contar_por_chamado(chamado_id: int) -> int:
    """
    Conta quantas interações um chamado possui.

    Args:
        chamado_id: ID do chamado

    Returns:
        Número de interações
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_CHAMADO, (chamado_id,))
        row = cursor.fetchone()
        return row["total"] if row else 0


def excluir_por_chamado(chamado_id: int) -> bool:
    """
    Exclui todas as interações de um chamado.

    Esta função é chamada automaticamente quando um chamado é excluído
    devido ao ON DELETE CASCADE no banco.

    Args:
        chamado_id: ID do chamado

    Returns:
        True se exclusão foi bem sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_POR_CHAMADO, (chamado_id,))
        return cursor.rowcount >= 0  # Pode ser 0 se não havia interações
