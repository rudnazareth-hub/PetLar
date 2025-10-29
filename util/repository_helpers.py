"""
Repository Helpers

Funções auxiliares para operações comuns em repositórios,
eliminando código duplicado em rotas.

Este módulo fornece funções para:
- Verificar existência de entidades e redirecionar em caso de erro
- Validar propriedade de entidades
- Lidar com erros comuns de forma padronizada

Exemplo de uso:
    from util.repository_helpers import obter_ou_404
    from repo import usuario_repo

    @router.get("/editar/{id}")
    @requer_autenticacao()
    async def get_editar(request: Request, id: int, usuario_logado: dict):
        # Ao invés de:
        # usuario = usuario_repo.obter_por_id(id)
        # if not usuario:
        #     informar_erro(request, "Usuário não encontrado")
        #     return RedirectResponse("/usuarios/listar")

        # Use:
        usuario = obter_ou_404(
            usuario_repo.obter_por_id(id),
            request,
            "Usuário não encontrado",
            "/admin/usuarios/listar"
        )

        # Se usuario for None, a função já retornou RedirectResponse
        # Se chegou aqui, usuario existe e pode ser usado
        return templates.TemplateResponse("usuarios/editar.html", {...})

@version 1.0.0
@author DefaultWebApp
"""

from typing import Optional, TypeVar, Union, Any, Callable
from fastapi import Request, status
from fastapi.responses import RedirectResponse

from util.flash_messages import informar_erro
from util.logger_config import logger


# TypeVar genérico para trabalhar com qualquer tipo de entidade
T = TypeVar('T')


def obter_ou_404(
    entity: Optional[T],
    request: Request,
    mensagem: str = "Registro não encontrado",
    redirect_url: str = "/",
    log_erro: bool = True
) -> Union[T, RedirectResponse]:
    """
    Verifica se uma entidade existe e retorna RedirectResponse se não existir.

    Esta função elimina o padrão repetitivo de:
    1. Buscar entidade no repository
    2. Verificar se é None
    3. Mostrar mensagem de erro
    4. Redirecionar

    Args:
        entity: Entidade retornada do repository (pode ser None)
        request: Objeto Request do FastAPI
        mensagem: Mensagem de erro a ser exibida (default: "Registro não encontrado")
        redirect_url: URL para redirecionar em caso de erro (default: "/")
        log_erro: Se True, registra erro no log (default: True)

    Returns:
        T: A entidade se existir
        RedirectResponse: Redirecionamento se entidade não existir

    Example:
        >>> # Uso básico
        >>> usuario = obter_ou_404(
        ...     usuario_repo.obter_por_id(id),
        ...     request,
        ...     "Usuário não encontrado",
        ...     "/admin/usuarios/listar"
        ... )
        >>> if isinstance(usuario, RedirectResponse):
        ...     return usuario
        >>> # usuario existe e pode ser usado

    Example:
        >>> # Uso com type guard automático
        >>> tarefa = obter_ou_404(
        ...     tarefa_repo.obter_por_id(id),
        ...     request,
        ...     "Tarefa não encontrada",
        ...     "/tarefas/listar"
        ... )
        >>> # Se não houve return, tarefa existe
        >>> print(tarefa.titulo)  # Safe to use

    Note:
        Para uso correto, verifique se o retorno é RedirectResponse:

        entity = obter_ou_404(...)
        if isinstance(entity, RedirectResponse):
            return entity
        # Agora entity é garantido como T
    """
    if entity is None:
        # Informar erro ao usuário
        informar_erro(request, mensagem)

        # Log opcional
        if log_erro:
            logger.warning(f"Entidade não encontrada - {mensagem} - URL: {request.url.path}")

        # Redirecionar
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    # Entidade existe, retornar normalmente
    return entity


def obter_lista_ou_vazia(
    lista: Optional[list],
    request: Optional[Request] = None,
    mensagem_aviso: Optional[str] = None,
    log_aviso: bool = False
) -> list:
    """
    Garante que uma lista nunca seja None, retornando lista vazia se necessário.

    Útil para queries que podem retornar None ao invés de lista vazia.

    Args:
        lista: Lista retornada do repository (pode ser None)
        request: Objeto Request (opcional, para flash message)
        mensagem_aviso: Mensagem de aviso a exibir se lista for None/vazia (opcional)
        log_aviso: Se True, registra aviso no log (default: False)

    Returns:
        list: A lista original ou lista vazia

    Example:
        >>> tarefas = obter_lista_ou_vazia(
        ...     tarefa_repo.obter_por_usuario(usuario_id),
        ...     request,
        ...     "Nenhuma tarefa encontrada"
        ... )
        >>> # tarefas sempre será uma lista, mesmo que vazia
        >>> for tarefa in tarefas:  # Safe, nunca dá erro
        ...     print(tarefa.titulo)
    """
    # Se lista for None ou não for list, retornar lista vazia
    if lista is None or not isinstance(lista, list):
        lista = []

    # Se lista vazia e mensagem fornecida, informar
    if len(lista) == 0 and mensagem_aviso and request:
        from util.flash_messages import informar_info
        informar_info(request, mensagem_aviso)

        if log_aviso:
            logger.info(f"Lista vazia retornada - {mensagem_aviso}")

    return lista


def validar_inteiro_positivo(
    valor: Any,
    request: Request,
    nome_campo: str = "ID",
    redirect_url: str = "/"
) -> Union[int, RedirectResponse]:
    """
    Valida se um valor é um inteiro positivo válido.

    Útil para validar IDs de URL antes de passar para o repository.

    Args:
        valor: Valor a ser validado
        request: Objeto Request do FastAPI
        nome_campo: Nome do campo para mensagem de erro (default: "ID")
        redirect_url: URL para redirecionar em caso de erro

    Returns:
        int: O valor convertido para inteiro se válido
        RedirectResponse: Redirecionamento se inválido

    Example:
        >>> id_valido = validar_inteiro_positivo(
        ...     id,
        ...     request,
        ...     "ID do usuário",
        ...     "/admin/usuarios/listar"
        ... )
        >>> if isinstance(id_valido, RedirectResponse):
        ...     return id_valido
        >>> usuario = usuario_repo.obter_por_id(id_valido)

    Note:
        FastAPI já faz validação básica de tipos em path parameters,
        mas esta função adiciona validação extra e mensagens amigáveis.
    """
    try:
        valor_int = int(valor)
        if valor_int <= 0:
            raise ValueError("Valor deve ser positivo")
        return valor_int
    except (ValueError, TypeError):
        informar_erro(request, f"{nome_campo} inválido")
        logger.warning(f"Validação falhou - {nome_campo} inválido: {valor}")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


def executar_operacao_repo(
    operacao: Callable,
    request: Request,
    mensagem_erro: str = "Erro ao executar operação",
    redirect_url: str = "/",
    log_exception: bool = True
) -> Union[Any, RedirectResponse]:
    """
    Executa uma operação de repository com tratamento de erros.

    Captura exceções comuns e trata de forma padronizada.

    Args:
        operacao: Função callable a ser executada (ex: lambda: repo.inserir(entity))
        request: Objeto Request do FastAPI
        mensagem_erro: Mensagem de erro a exibir (default: "Erro ao executar operação")
        redirect_url: URL para redirecionar em caso de erro
        log_exception: Se True, loga a exceção completa (default: True)

    Returns:
        any: Resultado da operação se bem-sucedida
        RedirectResponse: Redirecionamento se houver erro

    Example:
        >>> resultado = executar_operacao_repo(
        ...     lambda: usuario_repo.inserir(usuario),
        ...     request,
        ...     "Erro ao cadastrar usuário",
        ...     "/admin/usuarios/listar"
        ... )
        >>> if isinstance(resultado, RedirectResponse):
        ...     return resultado
        >>> # Operação bem-sucedida
        >>> user_id = resultado

    Example com múltiplas operações:
        >>> resultado = executar_operacao_repo(
        ...     lambda: [
        ...         usuario_repo.inserir(usuario),
        ...         foto_util.criar_foto_padrao_usuario(usuario.id)
        ...     ],
        ...     request,
        ...     "Erro ao criar usuário",
        ...     "/admin/usuarios/cadastrar"
        ... )
    """
    try:
        return operacao()
    except Exception as e:
        # Informar erro ao usuário
        informar_erro(request, mensagem_erro)

        # Log da exceção
        if log_exception:
            logger.error(f"{mensagem_erro} - Exceção: {str(e)}", exc_info=True)
        else:
            logger.error(f"{mensagem_erro} - {str(e)}")

        # Redirecionar
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# Exemplo de uso completo em uma rota:
"""
from util.repository_helpers import obter_ou_404, validar_inteiro_positivo
from repo import tarefa_repo

@router.get("/editar/{id}")
@requer_autenticacao()
async def get_editar(request: Request, id: int, usuario_logado: dict):
    # Validar ID (opcional, FastAPI já valida tipo)
    id_valido = validar_inteiro_positivo(id, request, "ID da tarefa", "/tarefas/listar")
    if isinstance(id_valido, RedirectResponse):
        return id_valido

    # Obter tarefa ou retornar 404
    tarefa = obter_ou_404(
        tarefa_repo.obter_por_id(id_valido),
        request,
        "Tarefa não encontrada",
        "/tarefas/listar"
    )
    if isinstance(tarefa, RedirectResponse):
        return tarefa

    # Verificar propriedade
    if tarefa.usuario_id != usuario_logado["id"]:
        informar_erro(request, "Você não tem permissão para editar esta tarefa")
        return RedirectResponse("/tarefas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Tarefa existe e usuário tem permissão
    return templates.TemplateResponse("tarefas/editar.html", {
        "request": request,
        "tarefa": tarefa
    })
"""
