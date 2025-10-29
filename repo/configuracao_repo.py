from typing import List, Optional
import sqlite3
from model.configuracao_model import Configuracao
from sql.configuracao_sql import *
from util.db_util import get_connection
from util.logger_config import logger


def _row_to_configuracao(row) -> Configuracao:
    """
    Converte uma linha do banco de dados em objeto Configuracao.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto Configuracao populado
    """
    return Configuracao(
        id=row["id"],
        chave=row["chave"],
        valor=row["valor"],
        descricao=row["descricao"] if "descricao" in row.keys() else None,
        data_cadastro=row["data_cadastro"],
        data_atualizacao=row["data_atualizacao"]
    )


def criar_tabela() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        return True


def obter_por_id(id: int) -> Optional[Configuracao]:
    """
    Busca uma configuração pelo ID.

    Args:
        id: ID da configuração

    Returns:
        Objeto Configuracao ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (id,))
        row = cursor.fetchone()
        return _row_to_configuracao(row) if row else None


def obter_por_chave(chave: str) -> Optional[Configuracao]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_CHAVE, (chave,))
        row = cursor.fetchone()
        if row:
            return _row_to_configuracao(row)
        return None

def obter_todos() -> list[Configuracao]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        rows = cursor.fetchall()
        return [_row_to_configuracao(row) for row in rows]


def obter_por_categoria() -> dict[str, list[Configuracao]]:
    """
    Obtém todas as configurações agrupadas por categoria.

    A categoria é extraída da descrição no formato "[Categoria] Descrição".
    Configurações sem categoria ficam em "Outras".

    Returns:
        Dicionário {categoria: [configuracoes]}

    Example:
        {
            "Aplicação": [config1, config2],
            "Segurança - Autenticação": [config3, config4],
            "Chat": [config5]
        }
    """
    import re

    todas = obter_todos()
    agrupadas: dict[str, list[Configuracao]] = {}

    for config in todas:
        # Extrai categoria da descrição usando regex
        categoria = "Outras"
        if config.descricao:
            match = re.match(r'^\[([^\]]+)\]', config.descricao)
            if match:
                categoria = match.group(1)

        if categoria not in agrupadas:
            agrupadas[categoria] = []

        agrupadas[categoria].append(config)

    # Ordena categorias alfabeticamente, mas mantém "Outras" por último
    categorias_ordenadas = sorted(agrupadas.keys())
    if "Outras" in categorias_ordenadas:
        categorias_ordenadas.remove("Outras")
        categorias_ordenadas.append("Outras")

    return {cat: agrupadas[cat] for cat in categorias_ordenadas}


def obter_multiplas(chaves: list[str]) -> dict[str, Optional[Configuracao]]:
    """
    Obtém múltiplas configurações de uma vez.

    Args:
        chaves: Lista de chaves a buscar

    Returns:
        Dicionário {chave: Configuracao ou None}

    Example:
        >>> obter_multiplas(["app_name", "theme", "inexistente"])
        {"app_name": Configuracao(...), "theme": Configuracao(...), "inexistente": None}
    """
    resultado = {}
    for chave in chaves:
        resultado[chave] = obter_por_chave(chave)
    return resultado

def atualizar(chave: str, valor: str) -> bool:
    """
    Atualiza o valor de uma configuração existente

    Args:
        chave: Chave da configuração
        valor: Novo valor

    Returns:
        True se atualização foi bem-sucedida, False se configuração não existe
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (valor, chave))
        return cursor.rowcount > 0


def atualizar_multiplas(configs: dict[str, str]) -> tuple[int, list[str]]:
    """
    Atualiza múltiplas configurações de uma vez (operação atômica).

    Todas as atualizações são executadas em uma única transação.
    Se alguma falhar, todas são revertidas (rollback automático).

    Args:
        configs: Dicionário {chave: valor} com as configurações a atualizar

    Returns:
        Tupla (quantidade_atualizada, chaves_nao_encontradas)
        - quantidade_atualizada: Número de configurações atualizadas com sucesso
        - chaves_nao_encontradas: Lista de chaves que não existem no banco

    Examples:
        >>> atualizar_multiplas({
        ...     "app_name": "Meu Sistema",
        ...     "rate_limit_login_max": "10",
        ...     "chave_inexistente": "valor"
        ... })
        (2, ["chave_inexistente"])

    Note:
        A operação é atômica: ou todas as configurações válidas são atualizadas,
        ou nenhuma é (em caso de erro de banco de dados).
    """
    if not configs:
        return (0, [])

    quantidade_atualizada = 0
    chaves_nao_encontradas = []

    with get_connection() as conn:
        cursor = conn.cursor()

        for chave, valor in configs.items():
            # Verificar se configuração existe
            cursor.execute(OBTER_POR_CHAVE, (chave,))
            if not cursor.fetchone():
                chaves_nao_encontradas.append(chave)
                logger.warning(f"Configuração '{chave}' não existe, ignorando atualização")
                continue

            # Atualizar configuração
            cursor.execute(ATUALIZAR, (valor, chave))
            if cursor.rowcount > 0:
                quantidade_atualizada += 1
                logger.debug(f"Configuração '{chave}' atualizada para: {valor}")

    logger.info(
        f"Atualização em lote concluída: {quantidade_atualizada} atualizadas, "
        f"{len(chaves_nao_encontradas)} não encontradas"
    )

    return (quantidade_atualizada, chaves_nao_encontradas)


def inserir_ou_atualizar(chave: str, valor: str, descricao: str = "") -> bool:
    """
    Insere ou atualiza uma configuração (operação upsert)

    Se a configuração já existe, atualiza o valor.
    Se não existe, insere nova configuração.

    Args:
        chave: Chave da configuração
        valor: Valor da configuração
        descricao: Descrição da configuração (usado apenas em inserção)

    Returns:
        True se operação foi bem-sucedida, False caso contrário

    Examples:
        >>> # Primeira vez - insere
        >>> inserir_ou_atualizar("theme", "darkly", "Tema visual")
        True

        >>> # Segunda vez - atualiza
        >>> inserir_ou_atualizar("theme", "flatly", "Tema visual")
        True
    """
    try:
        # Verificar se configuração já existe
        config_existente = obter_por_chave(chave)

        if config_existente:
            # Configuração existe - atualizar
            logger.debug(f"Atualizando configuração existente: {chave} = {valor}")
            return atualizar(chave, valor)
        else:
            # Configuração não existe - inserir
            logger.debug(f"Inserindo nova configuração: {chave} = {valor}")
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(INSERIR, (chave, valor, descricao))
                return cursor.rowcount > 0

    except Exception as e:
        logger.error(f"Erro ao inserir ou atualizar configuração '{chave}': {e}")
        raise

def excluir(id: int) -> bool:
    """
    Exclui uma configuração pelo ID.

    Args:
        id: ID da configuração a ser excluída

    Returns:
        True se exclusão foi bem-sucedida, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (id,))
        return cursor.rowcount > 0


def contar() -> int:
    """
    Retorna o total de configurações cadastradas.

    Returns:
        Número total de configurações
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()[0]


def buscar_por_termo(termo: str) -> List[Configuracao]:
    """
    Busca configurações por termo (chave, valor ou descrição).

    Args:
        termo: Termo de busca

    Returns:
        Lista de objetos Configuracao que correspondem ao termo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute(BUSCAR_POR_TERMO, (termo_like, termo_like, termo_like))
        return [_row_to_configuracao(row) for row in cursor.fetchall()]


def inserir_padrao() -> None:
    """Insere configurações padrão se não existirem"""
    configs_padrao = [
        ("nome_sistema", "Sistema Web", "Nome do sistema"),
        ("email_contato", "contato@sistema.com", "E-mail de contato"),
        ("tema_padrao", "claro", "Tema padrão (claro/escuro)"),
        ("theme", "original", "Tema visual da aplicação (Bootswatch)"),
    ]

    with get_connection() as conn:
        cursor = conn.cursor()
        for chave, valor, descricao in configs_padrao:
            try:
                cursor.execute(INSERIR, (chave, valor, descricao))
            except sqlite3.IntegrityError:
                # Configuração já existe (violação de UNIQUE constraint)
                logger.debug(f"Configuração '{chave}' já existe, pulando inserção")
            except Exception as e:
                # Outro tipo de erro - logar e re-raise para não mascarar problema
                logger.error(f"Erro ao inserir configuração padrão '{chave}': {e}")
                raise
