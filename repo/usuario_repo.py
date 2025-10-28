from datetime import datetime
from typing import Optional
from model.usuario_model import Usuario
from sql.usuario_sql import *
from util.db_util import get_connection
from util.foto_util import criar_foto_padrao_usuario


def _row_to_usuario(row) -> Usuario:
    """
    Converte uma linha do banco de dados em objeto Usuario.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto Usuario populado
    """
    return Usuario(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        senha=row["senha"],
        perfil=row["perfil"],
        token_redefinicao=row["token_redefinicao"] if "token_redefinicao" in row.keys() else None,
        data_token=row["data_token"] if "data_token" in row.keys() else None,
        data_cadastro=row["data_cadastro"] if "data_cadastro" in row.keys() else None,
        data_atualizacao=row["data_atualizacao"] if "data_atualizacao" in row.keys() else None
    )


def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True

def inserir(usuario: Usuario) -> Optional[int]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            usuario.nome,
            usuario.email,
            usuario.senha,
            usuario.perfil
        ))
        usuario_id = cursor.lastrowid

        # Criar foto padrão para o novo usuário
        if usuario_id:
            criar_foto_padrao_usuario(usuario_id)

        return usuario_id

def alterar(usuario: Usuario) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR, (
            usuario.nome,
            usuario.email,
            usuario.perfil,
            usuario.id
        ))
        return cursor.rowcount > 0

def atualizar_senha(id: int, senha: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ALTERAR_SENHA, (senha, id))
        return cursor.rowcount > 0

def excluir(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0

def obter_por_id(id: int) -> Optional[Usuario]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_usuario(row)
        return None

def obter_todos() -> list[Usuario]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_usuario(row) for row in rows]

def obter_quantidade() -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_QUANTIDADE)
        row = cursor.fetchone()
        return row["quantidade"] if row else 0

def obter_por_email(email: str) -> Optional[Usuario]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_EMAIL, (email,))
        row = cursor.fetchone()
        if row:
            return _row_to_usuario(row)
        return None

def atualizar_token(email: str, token: str, data_expiracao: datetime) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_TOKEN, (token, data_expiracao, email))
        return cursor.rowcount > 0

def obter_por_token(token: str) -> Optional[Usuario]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_TOKEN, (token,))
        row = cursor.fetchone()
        if row:
            return _row_to_usuario(row)
        return None

def limpar_token(id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(LIMPAR_TOKEN, (id,))
        return cursor.rowcount > 0

def obter_todos_por_perfil(perfil: str) -> list[Usuario]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_POR_PERFIL, (perfil,))
        rows = cursor.fetchall()
        return [_row_to_usuario(row) for row in rows]

def buscar_por_termo(termo: str, limit: int = 10) -> list[Usuario]:
    """
    Busca usuários por termo (pesquisa em nome e email).

    Args:
        termo: Termo de busca
        limit: Número máximo de resultados

    Returns:
        Lista de usuários que correspondem à busca
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, nome, email, senha, perfil,
                      token_redefinicao, data_token,
                      data_cadastro[timestamp], data_atualizacao[timestamp]
               FROM usuario
               WHERE (LOWER(nome) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?))
               LIMIT ?""",
            (f"%{termo}%", f"%{termo}%", limit)
        )
        rows = cursor.fetchall()
        return [_row_to_usuario(row) for row in rows]
