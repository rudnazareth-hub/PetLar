"""Repository para animais."""

from typing import List, Optional
from model.animal_model import Animal
from model.raca_model import Raca
from model.especie_model import Especie
from model.abrigo_model import Abrigo
from sql.animal_sql import *
from util.db_util import obter_conexao


def _row_to_animal(row) -> Animal:
    """Converte linha em objeto Animal com relacionamentos."""
    status = row["status"] if row["status"] else "Disponível"

    # Criar objeto Especie se houver dados
    especie = None
    if row.get("id_especie") and row.get("especie_nome"):
        especie = Especie(
            id=row["id_especie"],
            nome=row["especie_nome"],
            descricao=None
        )

    # Criar objeto Raca com Especie
    raca = None
    if row.get("raca_nome"):
        raca = Raca(
            id=row["id_raca"],
            id_especie=row["id_especie"] if row.get("id_especie") else 0,
            nome=row["raca_nome"],
            descricao=row.get("raca_descricao"),
            temperamento=row.get("temperamento"),
            expectativa_de_vida=row.get("expectativa_de_vida"),
            porte=row.get("porte"),
            especie=especie
        )

    # Criar objeto Abrigo
    abrigo = None
    if row.get("id_abrigo"):
        abrigo = Abrigo(
            id_abrigo=row["id_abrigo"],
            responsavel=row.get("responsavel", ""),
            data_abertura=None
        )

    return Animal(
        id=row["id"],
        id_raca=row["id_raca"],
        id_abrigo=row["id_abrigo"],
        nome=row["nome"],
        sexo=row["sexo"],
        data_nascimento=row["data_nascimento"],
        data_entrada=row["data_entrada"],
        observacoes=row["observacoes"],
        status=status,
        foto=row["foto"],
        id_adotante_reserva=row.get("id_adotante_reserva"),
        data_reserva=row.get("data_reserva"),
        raca=raca,
        abrigo=abrigo,
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"]
    )


def _row_to_animal_com_localizacao(row) -> dict:
    """Converte linha em dict com dados do animal e localização do abrigo."""
    animal = _row_to_animal(row)
    return {
        "animal": animal,
        "abrigo_cidade": row.get("abrigo_cidade"),
        "abrigo_uf": row.get("abrigo_uf")
    }


def criar_tabela() -> bool:
    """Cria a tabela animal se não existir."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def migrar_colunas_reserva() -> bool:
    """Adiciona colunas de reserva se não existirem."""
    with obter_conexao() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(ADICIONAR_COLUNA_ID_ADOTANTE_RESERVA)
        except Exception:
            pass  # Coluna já existe
        try:
            cursor.execute(ADICIONAR_COLUNA_DATA_RESERVA)
        except Exception:
            pass  # Coluna já existe
        return True


def inserir(animal: Animal) -> int:
    """
    Insere um novo animal no banco de dados.

    Args:
        animal: Objeto Animal a ser inserido

    Returns:
        ID do animal inserido
    """
    with obter_conexao() as conn:
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
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_animal(row) for row in cursor.fetchall()]


def obter_todos() -> List[Animal]:
    """
    Retorna todos os animais sem filtro de status.

    Returns:
        Lista de objetos Animal
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS_SEM_FILTRO)
        return [_row_to_animal(row) for row in cursor.fetchall()]


def obter_por_id(id_animal: int) -> Optional[Animal]:
    """
    Busca um animal pelo ID.

    Args:
        id_animal: ID do animal

    Returns:
        Objeto Animal ou None se não encontrado
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id_animal,))
        row = cursor.fetchone()
        return _row_to_animal(row) if row else None


def obter_por_id_com_relacoes(id_animal: int) -> Optional[Animal]:
    """
    Busca um animal pelo ID com todas as relações carregadas.
    Alias para obter_por_id para compatibilidade.

    Args:
        id_animal: ID do animal

    Returns:
        Objeto Animal ou None se não encontrado
    """
    return obter_por_id(id_animal)


def obter_por_id_com_adotante(id_animal: int) -> Optional[dict]:
    """
    Busca um animal pelo ID com dados do adotante que reservou.

    Args:
        id_animal: ID do animal

    Returns:
        Dicionário com animal e dados do adotante ou None
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID_COM_ADOTANTE, (id_animal,))
        row = cursor.fetchone()
        if not row:
            return None

        animal = _row_to_animal(row)
        return {
            "animal": animal,
            "adotante_id": row.get("adotante_id"),
            "adotante_nome": row.get("adotante_nome"),
            "adotante_email": row.get("adotante_email"),
            "adotante_telefone": row.get("adotante_telefone")
        }


def obter_por_abrigo(id_abrigo: int) -> List[Animal]:
    """
    Retorna todos os animais de um abrigo específico.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Lista de objetos Animal
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ABRIGO, (id_abrigo,))
        return [_row_to_animal(row) for row in cursor.fetchall()]


def obter_reservados_por_abrigo(id_abrigo: int) -> List[dict]:
    """
    Retorna todos os animais reservados de um abrigo com dados do adotante.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Lista de dicionários com animal e dados do adotante
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_RESERVADOS_POR_ABRIGO, (id_abrigo,))
        result = []
        for row in cursor.fetchall():
            animal = _row_to_animal(row)
            result.append({
                "animal": animal,
                "adotante_nome": row.get("adotante_nome"),
                "adotante_email": row.get("adotante_email"),
                "adotante_telefone": row.get("adotante_telefone")
            })
        return result


def obter_ultimos_cadastrados(limite: int = 12) -> List[dict]:
    """
    Retorna os últimos animais cadastrados disponíveis para adoção.

    Args:
        limite: Número máximo de animais a retornar

    Returns:
        Lista de dicionários com animal e localização do abrigo
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ULTIMOS_CADASTRADOS, (limite,))
        return [_row_to_animal_com_localizacao(row) for row in cursor.fetchall()]


def buscar_disponiveis_com_filtros(
    especie_id: Optional[int] = None,
    raca_id: Optional[int] = None,
    uf: Optional[str] = None,
    cidade: Optional[str] = None
) -> List[dict]:
    """
    Busca animais disponíveis com filtros opcionais.

    Args:
        especie_id: Filtrar por espécie
        raca_id: Filtrar por raça
        uf: Filtrar por UF do abrigo
        cidade: Filtrar por cidade do abrigo

    Returns:
        Lista de dicionários com animal e localização do abrigo
    """
    query = BUSCAR_DISPONIVEIS_COM_FILTROS
    params = []

    if especie_id:
        query += " AND e.id = ?"
        params.append(especie_id)

    if raca_id:
        query += " AND r.id = ?"
        params.append(raca_id)

    if uf:
        query += " AND en.uf = ?"
        params.append(uf)

    if cidade:
        query += " AND en.cidade LIKE ?"
        params.append(f"%{cidade}%")

    query += " ORDER BY a.data_cadastro DESC"

    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [_row_to_animal_com_localizacao(row) for row in cursor.fetchall()]


def atualizar(animal: Animal) -> bool:
    """
    Atualiza dados completos de um animal.

    Args:
        animal: Objeto Animal com dados atualizados

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            animal.id_raca,
            animal.nome,
            animal.sexo,
            animal.data_nascimento,
            animal.observacoes,
            animal.status,
            animal.id
        ))
        return cursor.rowcount > 0


def atualizar_completo(animal: Animal) -> bool:
    """
    Atualiza todos os campos de um animal incluindo foto e data_entrada.

    Args:
        animal: Objeto Animal com dados atualizados

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_COMPLETO, (
            animal.id_raca,
            animal.nome,
            animal.sexo,
            animal.data_nascimento,
            animal.data_entrada,
            animal.observacoes,
            animal.status,
            animal.foto,
            animal.id
        ))
        return cursor.rowcount > 0


def atualizar_status(id_animal: int, novo_status: str) -> bool:
    """
    Atualiza status do animal.

    Args:
        id_animal: ID do animal
        novo_status: Novo status (Disponível, Reservado, Adotado, Indisponível)

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_STATUS, (novo_status, id_animal))
        return cursor.rowcount > 0


def atualizar_foto(id_animal: int, caminho_foto: str) -> bool:
    """
    Atualiza a foto do animal.

    Args:
        id_animal: ID do animal
        caminho_foto: Caminho da nova foto

    Returns:
        True se atualização foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR_FOTO, (caminho_foto, id_animal))
        return cursor.rowcount > 0


def reservar_animal(id_animal: int, id_adotante: int) -> bool:
    """
    Reserva um animal para um adotante.

    Args:
        id_animal: ID do animal
        id_adotante: ID do adotante

    Returns:
        True se reserva foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(RESERVAR_ANIMAL, (id_adotante, id_animal))
        return cursor.rowcount > 0


def cancelar_reserva(id_animal: int) -> bool:
    """
    Cancela a reserva de um animal.

    Args:
        id_animal: ID do animal

    Returns:
        True se cancelamento foi bem-sucedido, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CANCELAR_RESERVA, (id_animal,))
        return cursor.rowcount > 0


def concluir_adocao(id_animal: int) -> bool:
    """
    Conclui a adoção de um animal (muda status para Adotado).

    Args:
        id_animal: ID do animal

    Returns:
        True se conclusão foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONCLUIR_ADOCAO, (id_animal,))
        return cursor.rowcount > 0


def verificar_propriedade(id_animal: int, id_abrigo: int) -> bool:
    """
    Verifica se um animal pertence a um abrigo.

    Args:
        id_animal: ID do animal
        id_abrigo: ID do abrigo

    Returns:
        True se o animal pertence ao abrigo
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(VERIFICAR_PROPRIEDADE, (id_animal, id_abrigo))
        return cursor.fetchone()[0] > 0


def excluir(id_animal: int) -> bool:
    """
    Exclui um animal pelo ID.

    Args:
        id_animal: ID do animal a ser excluído

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id_animal,))
        return cursor.rowcount > 0


def contar() -> int:
    """
    Retorna o total de animais cadastrados.

    Returns:
        Número total de animais
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def contar_por_abrigo(id_abrigo: int) -> int:
    """
    Retorna o total de animais de um abrigo.

    Args:
        id_abrigo: ID do abrigo

    Returns:
        Número total de animais do abrigo
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_ABRIGO, (id_abrigo,))
        return cursor.fetchone()[0]


def contar_disponiveis() -> int:
    """
    Retorna o total de animais disponíveis para adoção.

    Returns:
        Número de animais disponíveis
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_DISPONIVEIS)
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[Animal]:
    """
    Busca animais por termo (nome do animal, raça, espécie ou abrigo).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Animal que correspondem ao termo
    """
    with obter_conexao() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like, termo_like, termo_like))
        return [_row_to_animal(row) for row in cursor.fetchall()]
