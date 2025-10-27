"""
Repositório para operações de banco de dados relacionadas a chamados.

Implementa a camada de acesso a dados (DAL) para a entidade Chamado,
seguindo o padrão de Repository com funções CRUD.
"""

from datetime import datetime
from typing import Optional
from model.chamado_model import Chamado
from sql.chamado_sql import *
from util.db_util import get_connection


def _converter_data(data_str: Optional[str]) -> Optional[datetime]:
    """
    Converte string de data do banco em objeto datetime.

    Args:
        data_str: String no formato 'YYYY-MM-DD HH:MM:SS' ou None

    Returns:
        datetime object ou None se data_str for None
    """
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def _row_to_chamado(row) -> Chamado:
    """
    Converte uma linha do banco de dados em objeto Chamado.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto Chamado populado
    """
    # Verificar se os campos do JOIN existem (nem todas as queries fazem JOIN)
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None
    usuario_email = row["usuario_email"] if "usuario_email" in row.keys() else None
    admin_nome = row["admin_nome"] if "admin_nome" in row.keys() else None

    return Chamado(
        id=row["id"],
        titulo=row["titulo"],
        descricao=row["descricao"],
        status=row["status"],
        prioridade=row["prioridade"],
        usuario_id=row["usuario_id"],
        data_abertura=_converter_data(row["data_abertura"]),
        data_fechamento=_converter_data(row["data_fechamento"]),
        resposta_admin=row["resposta_admin"],
        admin_id=row["admin_id"] if row["admin_id"] else None,
        data_resposta=_converter_data(row["data_resposta"]) if row.get("data_resposta") else None,
        usuario_nome=usuario_nome,  # Do JOIN com tabela usuario
        usuario_email=usuario_email,  # Do JOIN com tabela usuario
        admin_nome=admin_nome  # Do JOIN com tabela usuario (admin)
    )


def criar_tabela() -> bool:
    """
    Cria a tabela de chamados no banco de dados se não existir.

    Returns:
        True se operação foi bem sucedida
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(chamado: Chamado) -> Optional[int]:
    """
    Insere um novo chamado no banco de dados.

    Args:
        chamado: Objeto Chamado a ser inserido

    Returns:
        ID do chamado inserido ou None em caso de erro
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            chamado.titulo,
            chamado.descricao,
            chamado.prioridade,
            chamado.status,
            chamado.usuario_id
        ))
        return cursor.lastrowid


def obter_todos() -> list[Chamado]:
    """
    Obtém todos os chamados do sistema (para administradores).

    Ordena por prioridade (Urgente > Alta > Média > Baixa) e data de abertura.

    Returns:
        Lista de objetos Chamado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_chamado(row) for row in rows]


def obter_por_usuario(usuario_id: int) -> list[Chamado]:
    """
    Obtém todos os chamados de um usuário específico.

    Ordena por status (Aberto > Em Análise > Resolvido > Fechado)
    e data de abertura.

    Args:
        usuario_id: ID do usuário

    Returns:
        Lista de objetos Chamado do usuário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (usuario_id,))
        rows = cursor.fetchall()
        return [_row_to_chamado(row) for row in rows]


def obter_por_id(id: int) -> Optional[Chamado]:
    """
    Obtém um chamado específico por ID.

    Args:
        id: ID do chamado

    Returns:
        Objeto Chamado ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_chamado(row)
        return None


def atualizar_status(
    id: int,
    status: str,
    resposta_admin: Optional[str] = None,
    fechar: bool = False,
    admin_id: Optional[int] = None
) -> bool:
    """
    Atualiza o status de um chamado.

    Args:
        id: ID do chamado
        status: Novo status (Aberto, Em Análise, Resolvido, Fechado)
        resposta_admin: Resposta do administrador (opcional)
        fechar: Se True, define data_fechamento para agora
        admin_id: ID do administrador que está respondendo (opcional)

    Returns:
        True se atualização foi bem sucedida, False caso contrário
    """
    data_fechamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if fechar else None
    # Define data_resposta se admin_id foi fornecido
    data_resposta = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if admin_id else None

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (
            status,
            resposta_admin,
            data_fechamento,
            admin_id,
            data_resposta,
            id
        ))
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """
    Exclui um chamado do banco de dados.

    Args:
        id: ID do chamado a ser excluído

    Returns:
        True se exclusão foi bem sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def contar_abertos_por_usuario(usuario_id: int) -> int:
    """
    Conta quantos chamados abertos um usuário possui.

    Args:
        usuario_id: ID do usuário

    Returns:
        Número de chamados com status 'Aberto' ou 'Em Análise'
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_ABERTOS_POR_USUARIO, (usuario_id,))
        row = cursor.fetchone()
        return row["total"] if row else 0


def contar_pendentes() -> int:
    """
    Conta quantos chamados pendentes existem no sistema (para admins).

    Returns:
        Número de chamados com status 'Aberto' ou 'Em Análise'
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_PENDENTES)
        row = cursor.fetchone()
        return row["total"] if row else 0
