from typing import Optional
from model.especie_model import Especie
from sql.especie_sql import *
from util.db_util import get_connection

def criar_tabela():
    """
    Cria a tabela de espécies se ela não existir.
    Deve ser chamada na inicialização do sistema.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)


def inserir(especie: Especie) -> Optional[Especie]:
    """
    Insere uma nova espécie no banco de dados.

    Args:
        espécie: Objeto Espécie com nome e descrição

    Returns:
        Espécie com ID preenchido se sucesso, None se erro

    Exemplo:
        nova = Espécie(nome="Esportes", descricao="Notícias esportivas")
        resultado = inserir(nova)
        if resultado:
            print(f"Espécie criada com ID: {resultado.id}")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERIR, (especie.nome, especie.descricao))

            # Pega o ID gerado automaticamente
            if cursor.lastrowid:
                especie.id = cursor.lastrowid
                return especie
            return None
    except Exception as e:
        print(f"Erro ao inserir espécie: {e}")
        return None


def alterar(especie: Especie) -> bool:
    """
    Atualiza uma espécie existente.

    Args:
        espécie: Objeto Espécie com ID, nome e descrição

    Returns:
        True se atualizou, False se erro

    Exemplo:
        cat = obter_por_id(5)
        cat.nome = "Novo Nome"
        if alterar(cat):
            print("Espécie atualizada!")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                ALTERAR,
                (especie.nome, especie.descricao, especie.id)
            )
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao alterar espécie: {e}")
        return False


def excluir(id: int) -> bool:
    """
    Exclui uma espécie do banco de dados.

    Args:
        id: ID da espécie a ser excluída

    Returns:
        True se excluiu, False se erro ou não encontrou

    Exemplo:
        if excluir(5):
            print("Espécie excluída!")
        else:
            print("Espécie não encontrada")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(EXCLUIR, (id,))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir espécie: {e}")
        return False


def obter_por_id(id: int) -> Optional[Especie]:
    """
    Busca uma espécie por ID.

    Args:
        id: ID da espécie

    Returns:
        Objeto Espécie se encontrou, None se não encontrou

    Exemplo:
        cat = obter_por_id(5)
        if cat:
            print(f"Encontrada: {cat.nome}")
        else:
            print("Espécie não existe")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_ID, (id,))
            row = cursor.fetchone()

            if row:
                return Especie(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
            return None
    except Exception as e:
        print(f"Erro ao obter espécie por ID: {e}")
        return None


def obter_todos() -> list[Especie]:
    """
    Retorna todas as espécies do banco de dados.

    Returns:
        Lista de objetos Espécie (pode ser vazia)

    Exemplo:
        espécies = obter_todos()
        for cat in espécies:
            print(f"{cat.id} - {cat.nome}")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_TODOS)
            rows = cursor.fetchall()

            return [
                Especie(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
                for row in rows
            ]
    except Exception as e:
        print(f"Erro ao obter todas as espécies: {e}")
        return []


def obter_por_nome(nome: str) -> Optional[Especie]:
    """
    Busca uma espécie pelo nome exato.
    Útil para verificar se já existe espécie com aquele nome.

    Args:
        nome: Nome da espécie (case-sensitive)

    Returns:
        Objeto Espécie se encontrou, None se não encontrou

    Exemplo:
        if obter_por_nome("Tecnologia"):
            print("Já existe espécie com este nome")
        else:
            print("Nome disponível")
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(OBTER_POR_NOME, (nome,))
            row = cursor.fetchone()

            if row:
                return Especie(
                    id=row["id"],
                    nome=row["nome"],
                    descricao=row["descricao"],
                    data_cadastro=row["data_cadastro"],
                    data_atualizacao=row["data_atualizacao"]
                )
            return None
    except Exception as e:
        print(f"Erro ao obter espécie por nome: {e}")
        return None