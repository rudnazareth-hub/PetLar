"""Repository para adoções finalizadas."""

from typing import List, Optional
from datetime import datetime
from model.adocao_model import Adocao
from sql.adocao_sql import *
from util.db_util import obter_conexao


def _converter_data(data_str: Optional[str]) -> Optional[datetime]:
    """Converte string de data do banco em objeto datetime"""
    if not data_str:
        return None
    try:
        return datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.strptime(data_str, '%Y-%m-%d')
        except ValueError:
            return None


def _row_to_adocao(row) -> Adocao:
    """Converte linha do banco em objeto Adocao."""
    return Adocao(
        id=row["id"],
        id_adotante=row["id_adotante"],
        id_animal=row["id_animal"],
        data_adocao=_converter_data(row.get("data_adocao")),
        observacoes=row.get("observacoes"),
        data_cadastro=row.get("data_cadastro"),
        data_atualizacao=row.get("data_atualizacao"),
        animal_nome=row.get("animal_nome"),
        animal_foto=row.get("animal_foto"),
        animal_sexo=row.get("animal_sexo"),
        raca_nome=row.get("raca_nome"),
        especie_nome=row.get("especie_nome"),
        abrigo_nome=row.get("abrigo_nome"),
        adotante_nome=row.get("adotante_nome"),
        adotante_email=row.get("adotante_email")
    )


def criar_tabela() -> bool:
    """Cria a tabela adocao se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(id_adotante: int, id_animal: int, observacoes: Optional[str] = None) -> int:
    """
    Registra uma adoção finalizada.

    Args:
        id_adotante: ID do adotante
        id_animal: ID do animal
        observacoes: Observações sobre a adoção

    Returns:
        ID da adoção inserida
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (id_adotante, id_animal, observacoes))
        return cursor.lastrowid


def obter_por_id(id_adocao: int) -> Optional[Adocao]:
    """
    Busca uma adoção pelo ID.

    Args:
        id_adocao: ID da adoção

    Returns:
        Objeto Adocao ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_adocao,))
        row = cursor.fetchone()
        return _row_to_adocao(row) if row else None


def obter_por_animal(id_animal: int) -> Optional[Adocao]:
    """
    Busca adoção de um animal específico.

    Args:
        id_animal: ID do animal

    Returns:
        Objeto Adocao ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ANIMAL, (id_animal,))
        row = cursor.fetchone()
        return _row_to_adocao(row) if row else None


def obter_por_adotante(id_adotante: int) -> List[Adocao]:
    """
    Lista adoções de um adotante.

    Args:
        id_adotante: ID do adotante

    Returns:
        Lista de objetos Adocao
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ADOTANTE, (id_adotante,))
        return [_row_to_adocao(row) for row in cursor.fetchall()]


def obter_por_abrigo(id_abrigo: int) -> List[Adocao]:
    """
    Lista adoções finalizadas de um abrigo.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Lista de objetos Adocao
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [_row_to_adocao(row) for row in cursor.fetchall()]


def obter_todos() -> List[Adocao]:
    """
    Retorna todas as adoções cadastradas.

    Returns:
        Lista de objetos Adocao
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_adocao(row) for row in cursor.fetchall()]


def contar() -> int:
    """
    Retorna o total de adoções cadastradas.

    Returns:
        Número total de adoções
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def contar_por_abrigo(id_abrigo: int) -> int:
    """
    Retorna o total de adoções de um abrigo.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Número de adoções do abrigo
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_ABRIGO, (id_abrigo,))
        return cursor.fetchone()[0]


def contar_por_adotante(id_adotante: int) -> int:
    """
    Retorna o total de adoções de um adotante.

    Args:
        id_adotante: ID do adotante

    Returns:
        Número de adoções do adotante
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_ADOTANTE, (id_adotante,))
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[Adocao]:
    """
    Busca adoções por termo (nome do animal, adotante ou observações).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Adocao que correspondem ao termo
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like, termo_like))
        return [_row_to_adocao(row) for row in cursor.fetchall()]


def excluir(id_adocao: int) -> bool:
    """
    Exclui uma adoção pelo ID.

    Args:
        id_adocao: ID da adoção a ser excluída

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_adocao,))
        return cursor.rowcount > 0
