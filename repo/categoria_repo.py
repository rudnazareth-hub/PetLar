from typing import Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import get_connection


def _row_to_categoria(row) -> Categoria:
    """Converte uma linha do banco de dados em um objeto Categoria."""
    return Categoria(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"],
    )


def criar_tabela():
    """Cria a tabela de categorias no banco de dados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(categoria: Categoria) -> Optional[int]:
    """
    Insere uma nova categoria no banco de dados.

    Args:
        categoria: Objeto Categoria com os dados a serem inseridos

    Returns:
        ID da categoria inserida ou None em caso de erro
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (
                categoria.nome,
                categoria.descricao,
            ),
        )
        return cursor.lastrowid if cursor.lastrowid else None


def obter_todos() -> list[Categoria]:
    """
    Obtém todas as categorias cadastradas.

    Returns:
        Lista de objetos Categoria
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_categoria(row) for row in rows]


def obter_por_id(id: int) -> Optional[Categoria]:
    """
    Obtém uma categoria pelo ID.

    Args:
        id: ID da categoria

    Returns:
        Objeto Categoria ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_categoria(row) if row else None


def obter_por_nome(nome: str) -> Optional[Categoria]:
    """
    Obtém uma categoria pelo nome.

    Args:
        nome: Nome da categoria

    Returns:
        Objeto Categoria ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_NOME, (nome,))
        row = cursor.fetchone()
        return _row_to_categoria(row) if row else None


def atualizar(categoria: Categoria) -> bool:
    """
    Atualiza uma categoria existente.

    Args:
        categoria: Objeto Categoria com os dados atualizados

    Returns:
        True se a atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ATUALIZAR,
            (
                categoria.nome,
                categoria.descricao,
                categoria.id,
            ),
        )
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """
    Exclui uma categoria pelo ID.

    Args:
        id: ID da categoria a ser excluída

    Returns:
        True se a exclusão foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def contar() -> int:
    """
    Conta o número total de categorias.

    Returns:
        Número total de categorias
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        row = cursor.fetchone()
        return row["total"] if row else 0


def buscar_por_termo(termo: str) -> list[Categoria]:
    """
    Busca categorias por termo (nome ou descrição).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Categoria que correspondem ao termo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like))
        rows = cursor.fetchall()
        return [_row_to_categoria(row) for row in rows]
