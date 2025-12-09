from typing import Optional

from model.especie_model import Especie
from sql.especie_sql import (
    ATUALIZAR,
    BUSCAR_POR_TERMO,
    CONTAR,
    CRIAR_TABELA,
    EXCLUIR,
    INSERIR,
    OBTER_POR_ID,
    OBTER_POR_NOME,
    OBTER_TODOS,
    VERIFICAR_USO_EM_RACAS,
)
from util.db_util import obter_conexao


def _row_to_especie(row) -> Especie:
    """Converte uma linha do banco de dados em um objeto Especie."""
    return Especie(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"],
    )


def criar_tabela():
    """Cria a tabela de espécies no banco de dados."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(especie: Especie) -> Optional[int]:
    """
    Insere uma nova espécie no banco de dados.

    Args:
        especie: Objeto Especie com os dados a serem inseridos

    Returns:
        ID da espécie inserida ou None em caso de erro
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(
            INSERIR,
            (
                especie.nome,
                especie.descricao,
            ),
        )
        return cursor.lastrowid if cursor.lastrowid else None


def obter_todos() -> list[Especie]:
    """
    Obtém todas as espécies cadastradas.

    Returns:
        Lista de objetos Especie
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_especie(row) for row in rows]


def obter_por_id(id: int) -> Optional[Especie]:
    """
    Obtém uma espécie pelo ID.

    Args:
        id: ID da espécie

    Returns:
        Objeto Especie ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_especie(row) if row else None


def obter_por_nome(nome: str) -> Optional[Especie]:
    """
    Obtém uma espécie pelo nome.

    Args:
        nome: Nome da espécie

    Returns:
        Objeto Especie ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_NOME, (nome,))
        row = cursor.fetchone()
        return _row_to_especie(row) if row else None


def atualizar(especie: Especie) -> bool:
    """
    Atualiza uma espécie existente.

    Args:
        especie: Objeto Especie com os dados atualizados

    Returns:
        True se a atualização foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(
            ATUALIZAR,
            (
                especie.nome,
                especie.descricao,
                especie.id,
            ),
        )
        return cursor.rowcount > 0


def excluir(id: int) -> bool:
    """
    Exclui uma espécie pelo ID.

    Args:
        id: ID da espécie a ser excluída

    Returns:
        True se a exclusão foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def contar() -> int:
    """
    Conta o número total de espécies.

    Returns:
        Número total de espécies
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        row = cursor.fetchone()
        return row["total"] if row else 0


def buscar_por_termo(termo: str) -> list[Especie]:
    """
    Busca espécies por termo (nome ou descrição).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Especie que correspondem ao termo
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like))
        rows = cursor.fetchall()
        return [_row_to_especie(row) for row in rows]


def esta_em_uso(id: int) -> bool:
    """
    Verifica se uma espécie está sendo usada em alguma raça.

    Args:
        id: ID da espécie

    Returns:
        True se a espécie está em uso, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(VERIFICAR_USO_EM_RACAS, (id,))
        row = cursor.fetchone()
        return row["total"] > 0 if row else False
