"""
Repository para operações com a tabela especie.
"""

from typing import List, Optional
from model.especie_model import Especie
from sql.especie_sql import *
from util.db_util import get_connection


def _row_to_especie(row) -> Especie:
    """Converte uma linha do banco em objeto Especie."""
    return Especie(
        id_especie=row["id_especie"],
        nome=row["nome"],
        descricao=row["descricao"]
    )


def criar_tabela() -> None:
    """Cria a tabela especie se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(especie: Especie) -> int:
    """
    Insere uma nova espécie e retorna o ID gerado.

    Args:
        especie: Objeto Especie a ser inserido

    Returns:
        ID da espécie inserida
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            especie.nome,
            especie.descricao
        ))
        return cursor.lastrowid


def obter_todos() -> List[Especie]:
    """
    Retorna todas as espécies cadastradas.

    Returns:
        Lista de objetos Especie
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_especie(row) for row in cursor.fetchall()]


def obter_por_id(id_especie: int) -> Optional[Especie]:
    """
    Busca uma espécie pelo ID.

    Args:
        id_especie: ID da espécie

    Returns:
        Objeto Especie ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_especie,))
        row = cursor.fetchone()
        return _row_to_especie(row) if row else None


def obter_por_nome(nome: str) -> Optional[Especie]:
    """
    Busca uma espécie pelo nome.

    Args:
        nome: Nome da espécie

    Returns:
        Objeto Especie ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_NOME, (nome,))
        row = cursor.fetchone()
        return _row_to_especie(row) if row else None


def atualizar(especie: Especie) -> None:
    """
    Atualiza uma espécie existente.

    Args:
        especie: Objeto Especie com dados atualizados
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            especie.nome,
            especie.descricao,
            especie.id_especie
        ))


def excluir(id_especie: int) -> None:
    """
    Exclui uma espécie pelo ID.

    Args:
        id_especie: ID da espécie a ser excluída

    Raises:
        Exception: Se a espécie tiver raças vinculadas
    """
    # Verificar se tem raças vinculadas
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_RACAS, (id_especie,))
        total = cursor.fetchone()["total"]

        if total > 0:
            raise Exception(
                f"Não é possível excluir esta espécie. "
                f"Existem {total} raça(s) vinculada(s)."
            )

        cursor.execute(EXCLUIR, (id_especie,))


def existe_nome(nome: str, id_excluir: Optional[int] = None) -> bool:
    """
    Verifica se já existe uma espécie com o nome informado.

    Args:
        nome: Nome a verificar
        id_excluir: ID a excluir da verificação (para updates)

    Returns:
        True se existe, False caso contrário
    """
    especie = obter_por_nome(nome)
    if not especie:
        return False
    if id_excluir and especie.id_especie == id_excluir:
        return False
    return True
