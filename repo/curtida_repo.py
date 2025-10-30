from typing import Optional
from model.curtida_model import Curtida
from sql.curtida_sql import *
from util.db_util import get_connection

def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(curtida: Curtida) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (curtida.id_usuario, curtida.id_animal))
        return cursor.rowcount > 0

def excluir(id_usuario: int, id_animal: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_usuario,id_animal))
        return (cursor.rowcount > 0)

def obter_por_id(id_usuario: int, id_animal: int) -> Optional[Curtida]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_usuario, id_animal))
        row = cursor.fetchone()
        if row:
            return Curtida(
                id=row["id_usuario"],
                nome=row["id_animal"],
                descricao=row["data_curtida"]
            )
        return None

def obter_quantidade_por_animal(id_animal: int) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_QUANTIDADE_POR_ANIMAL, (id_animal,))
        return cursor.fetchone()["quantidade"]