"""Repository para operações com endereços."""

from typing import List, Optional
from model.endereco_model import Endereco
from sql.endereco_sql import *
from util.db_util import get_connection


def _row_to_endereco(row) -> Endereco:
    return Endereco(
        id_endereco=row["id_endereco"],
        id_usuario=row["id_usuario"],
        titulo=row["titulo"],
        logradouro=row["logradouro"],
        numero=row["numero"],
        complemento=row["complemento"],
        bairro=row["bairro"],
        cidade=row["cidade"],
        Uf=row["uf"],
        CEP=row["cep"],
        usuario=None  # Carregar se necessário
    )


def criar_tabela() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(endereco: Endereco) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            endereco.id_usuario, endereco.titulo, endereco.logradouro,
            endereco.numero, endereco.complemento, endereco.bairro,
            endereco.cidade, endereco.Uf, endereco.CEP
        ))
        return cursor.lastrowid


def obter_por_usuario(id_usuario: int) -> List[Endereco]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_USUARIO, (id_usuario,))
        return [_row_to_endereco(row) for row in cursor.fetchall()]


def atualizar(endereco: Endereco) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            endereco.titulo, endereco.logradouro, endereco.numero,
            endereco.complemento, endereco.bairro, endereco.cidade,
            endereco.Uf, endereco.CEP, endereco.id_endereco
        ))


def excluir(id_endereco: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_endereco,))