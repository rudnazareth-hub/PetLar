"""Repository para operações com endereços."""

from typing import List, Optional
from model.endereco_model import Endereco
from sql.endereco_sql import *
from util.db_util import get_connection


def _row_to_endereco(row) -> Endereco:
    """Converte linha do banco em objeto Endereco."""
    return Endereco(
        id_endereco=row["id_endereco"],
        id_usuario=row["id_usuario"],
        titulo=row["titulo"],
        logradouro=row["logradouro"],
        numero=row["numero"],
        complemento=row["complemento"],
        bairro=row["bairro"],
        cidade=row["cidade"],
        uf=row["uf"],
        cep=row["cep"],
        usuario=None,
        data_cadastro=row.get("data_cadastro"),
        data_atualizacao=row.get("data_atualizacao")
    )


def criar_tabela() -> bool:
    """Cria a tabela endereco se não existir."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def inserir(endereco: Endereco) -> int:
    """
    Insere um novo endereço no banco de dados.

    Args:
        endereco: Objeto Endereco a ser inserido

    Returns:
        ID do endereço inserido
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            endereco.id_usuario, endereco.titulo, endereco.logradouro,
            endereco.numero, endereco.complemento, endereco.bairro,
            endereco.cidade, endereco.uf, endereco.cep
        ))
        return cursor.lastrowid


def obter_por_id(id_endereco: int) -> Optional[Endereco]:
    """
    Busca um endereço pelo ID.

    Args:
        id_endereco: ID do endereço

    Returns:
        Objeto Endereco ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_endereco,))
        row = cursor.fetchone()
        return _row_to_endereco(row) if row else None


def obter_todos() -> List[Endereco]:
    """
    Retorna todos os endereços cadastrados.

    Returns:
        Lista de objetos Endereco
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_endereco(row) for row in cursor.fetchall()]


def obter_por_usuario(id_usuario: int) -> List[Endereco]:
    """
    Retorna todos os endereços de um usuário.

    Args:
        id_usuario: ID do usuário

    Returns:
        Lista de objetos Endereco
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (id_usuario,))
        return [_row_to_endereco(row) for row in cursor.fetchall()]


def atualizar(endereco: Endereco) -> bool:
    """
    Atualiza um endereço existente.

    Args:
        endereco: Objeto Endereco com dados atualizados

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            endereco.titulo, endereco.logradouro, endereco.numero,
            endereco.complemento, endereco.bairro, endereco.cidade,
            endereco.uf, endereco.cep, endereco.id_endereco
        ))
        return cursor.rowcount > 0


def excluir(id_endereco: int) -> bool:
    """
    Exclui um endereço pelo ID.

    Args:
        id_endereco: ID do endereço a ser excluído

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_endereco,))
        return cursor.rowcount > 0


def contar() -> int:
    """
    Retorna o total de endereços cadastrados.

    Returns:
        Número total de endereços
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[Endereco]:
    """
    Busca endereços por termo (título, logradouro, bairro, cidade ou CEP).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Endereco que correspondem ao termo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like, termo_like, termo_like, termo_like))
        return [_row_to_endereco(row) for row in cursor.fetchall()]