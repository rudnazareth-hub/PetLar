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
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"]
    )


def criar_tabela() -> bool:
    """Cria a tabela especie se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(especie: Especie) -> Optional[int]:
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


def atualizar(especie: Especie) -> bool:
    """
    Atualiza uma espécie existente.

    Args:
        especie: Objeto Especie com dados atualizados

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            especie.nome,
            especie.descricao,
            especie.id
        ))
        return cursor.rowcount > 0


def excluir(id_especie: int) -> bool:
    """
    Exclui uma espécie pelo ID.

    Args:
        id_especie: ID da espécie a ser excluída

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário

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
        return cursor.rowcount > 0


def contar() -> int:
    """
    Retorna o total de espécies cadastradas.

    Returns:
        Número total de espécies
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[Especie]:
    """
    Busca espécies por termo (nome ou descrição).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Especie que correspondem ao termo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like))
        return [_row_to_especie(row) for row in cursor.fetchall()]


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
    if id_excluir and especie.id == id_excluir:
        return False
    return True
