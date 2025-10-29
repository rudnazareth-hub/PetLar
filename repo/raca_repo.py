"""
Repository para operações com a tabela raca.
"""

from typing import List, Optional
from model.raca_model import Raca
from model.especie_model import Especie
from sql.raca_sql import *
from util.db_util import get_connection


def _row_to_raca(row) -> Raca:
    """Converte uma linha do banco em objeto Raca com Especie."""
    return Raca(
        id=row["id"],
        id_especie=row["id_especie"],
        nome=row["nome"],
        descricao=row["descricao"],
        temperamento=row["temperamento"],
        expectativa_de_vida=row["expectativa_de_vida"],
        porte=row["porte"],
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"],
        especie=Especie(
            id=row["especie_id"],
            nome=row["especie_nome"],
            descricao=row["especie_descricao"]
        ) if row["especie_id"] else None
    )


def criar_tabela() -> bool:
    """Cria a tabela raca se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(raca: Raca) -> Optional[int]:
    """Insere uma nova raça e retorna o ID gerado."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            raca.id_especie,
            raca.nome,
            raca.descricao,
            raca.temperamento,
            raca.expectativa_de_vida,
            raca.porte
        ))
        return cursor.lastrowid


def obter_todos() -> List[Raca]:
    """Retorna todas as raças com suas espécies."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_raca(row) for row in cursor.fetchall()]


def obter_por_id(id_raca: int) -> Optional[Raca]:
    """Busca uma raça pelo ID com sua espécie."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_raca,))
        row = cursor.fetchone()
        return _row_to_raca(row) if row else None


def obter_por_especie(id_especie: int) -> List[Raca]:
    """Retorna todas as raças de uma espécie."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ESPECIE, (id_especie,))
        return [_row_to_raca(row) for row in cursor.fetchall()]


def atualizar(raca: Raca) -> bool:
    """
    Atualiza uma raça existente.

    Args:
        raca: Objeto Raca com dados atualizados

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            raca.id_especie,
            raca.nome,
            raca.descricao,
            raca.temperamento,
            raca.expectativa_de_vida,
            raca.porte,
            raca.id
        ))
        return cursor.rowcount > 0


def excluir(id_raca: int) -> bool:
    """
    Exclui uma raça pelo ID.

    Args:
        id_raca: ID da raça a ser excluída

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário

    Raises:
        Exception: Se a raça tiver animais vinculados
    """
    # Verificar se tem animais vinculados
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_ANIMAIS, (id_raca,))
        total = cursor.fetchone()["total"]

        if total > 0:
            raise Exception(
                f"Não é possível excluir esta raça. "
                f"Existem {total} animal(is) vinculado(s)."
            )

        cursor.execute(EXCLUIR, (id_raca,))
        return cursor.rowcount > 0


def contar() -> int:
    """
    Retorna o total de raças cadastradas.

    Returns:
        Número total de raças
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[Raca]:
    """
    Busca raças por termo (nome da raça, descrição ou espécie).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Raca que correspondem ao termo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like, termo_like))
        return [_row_to_raca(row) for row in cursor.fetchall()]