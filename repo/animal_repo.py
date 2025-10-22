"""Repository para animais."""

from typing import List, Optional
from model.animal_model import Animal
from model.raca_model import Raca
from model.especie_model import Especie
from model.abrigo_model import Abrigo
from sql.animal_sql import *
from util.db_util import get_connection


def _row_to_animal(row) -> Animal:
    """Converte linha em objeto Animal com relacionamentos."""
    return Animal(
        id_animal=row["id_animal"],
        id_raca=row["id_raca"],
        id_abrigo=row["id_abrigo"],
        data_nascimento=row.get("data_nascimento"),
        data_entrada=row["data_entrada"],
        observacoes=row.get("observacoes"),
        raca=Raca(
            id_raca=row["id_raca"],
            id_especie=row.get("id_especie", 0),
            nome=row.get("raca_nome", ""),
            descricao=row.get("raca_descricao", ""),
            temperamento=row.get("temperamento", ""),
            expectativa_de_vida=row.get("expectativa_de_vida", ""),
            porte=row.get("porte", ""),
            especie=None
        ) if row.get("raca_nome") else None,
        abrigo=Abrigo(
            id_abrigo=row["id_abrigo"],
            responsavel=row.get("responsavel", ""),
            data_abertura=None
        ) if row.get("id_abrigo") else None
    )


def criar_tabela() -> None:
    """Cria a tabela animal se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(animal: Animal) -> int:
    """
    Insere um novo animal no banco de dados.

    Args:
        animal: Objeto Animal a ser inserido

    Returns:
        ID do animal inserido
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            animal.id_raca,
            animal.id_abrigo,
            animal.nome,
            animal.sexo,
            animal.data_nascimento,
            animal.data_entrada,
            animal.observacoes,
            animal.status,
            animal.foto
        ))
        return cursor.lastrowid


def obter_todos_disponiveis() -> List[Animal]:
    """
    Retorna todos os animais disponíveis para adoção.

    Returns:
        Lista de objetos Animal
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_animal(row) for row in cursor.fetchall()]


def obter_por_id(id_animal: int) -> Optional[Animal]:
    """
    Busca um animal pelo ID.

    Args:
        id_animal: ID do animal

    Returns:
        Objeto Animal ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_animal,))
        row = cursor.fetchone()
        return _row_to_animal(row) if row else None


def obter_por_abrigo(id_abrigo: int) -> List[Animal]:
    """
    Retorna todos os animais de um abrigo específico.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Lista de objetos Animal
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [_row_to_animal(row) for row in cursor.fetchall()]


def atualizar_status(id_animal: int, novo_status: str) -> bool:
    """
    Atualiza status do animal.

    Args:
        id_animal: ID do animal
        novo_status: Novo status (Disponível, Em Processo, Adotado, Indisponível)

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (novo_status, id_animal))
        return cursor.rowcount > 0