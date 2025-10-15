from fastapi import Request, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from util.template_util import criar_templates
from util.flash_messages import informar_erro, informar_aviso
from util.logger_config import logger

# Configurar templates de erro
templates = criar_templates("templates")


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handler para exceções HTTP do Starlette/FastAPI

    - 401 (Unauthorized): Redireciona para login com mensagem
    - 403 (Forbidden): Redireciona para login com mensagem
    - 404 (Not Found): Exibe página de erro 404
    - Outros: Loga e retorna página de erro genérica
    """
    status_code = exc.status_code

    # Log da exceção
    logger.warning(
        f"HTTPException {status_code}: {exc.detail} - "
        f"Path: {request.url.path} - "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )

    # 401 - Não autenticado
    if status_code == status.HTTP_401_UNAUTHORIZED:
        informar_erro(request, "Você precisa estar autenticado para acessar esta página.")
        return RedirectResponse(
            f"/login?redirect={request.url.path}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 403 - Sem permissão
    if status_code == status.HTTP_403_FORBIDDEN:
        informar_erro(request, "Você não tem permissão para acessar esta página.")
        return RedirectResponse(
            "/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 404 - Não encontrado
    if status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Outros erros HTTP - página de erro genérica
    return templates.TemplateResponse(
        "errors/500.html",
        {
            "request": request,
            "error_code": status_code,
            "error_message": exc.detail
        },
        status_code=status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler para erros de validação do Pydantic
    Loga o erro e exibe mensagem amigável
    """
    logger.warning(
        f"Erro de validação: {exc.errors()} - "
        f"Path: {request.url.path} - "
        f"Body: {exc.body}"
    )

    # Extrair mensagens de erro
    erros = []
    for error in exc.errors():
        campo = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        mensagem = error["msg"]
        erros.append(f"{campo}: {mensagem}" if campo else mensagem)

    informar_erro(request, f"Dados inválidos: {'; '.join(erros)}")

    return templates.TemplateResponse(
        "errors/500.html",
        {
            "request": request,
            "error_code": 422,
            "error_message": "Erro de validação de dados"
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handler genérico para todas as exceções não tratadas
    Loga o erro completo e exibe página de erro amigável
    """
    logger.error(
        f"Exceção não tratada: {type(exc).__name__}: {str(exc)} - "
        f"Path: {request.url.path} - "
        f"IP: {request.client.host if request.client else 'unknown'}",
        exc_info=True
    )

    return templates.TemplateResponse(
        "errors/500.html",
        {
            "request": request,
            "error_code": 500,
            "error_message": "Erro interno do servidor"
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
