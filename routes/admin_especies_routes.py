from typing import Optional
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.especie_dto import CriarEspecieDTO, AlterarEspecieDTO
from model.especie_model import Especie
from repo import especie_repo
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.exceptions import FormValidationError
from util.perfis import Perfil
from util.template_util import criar_templates

# Configura o roteador com prefixo /admin/espécies
router = APIRouter(prefix="/admin/especies")

# Configura os templates HTML com as funções globais necessárias (csrf_input, etc.)
templates = criar_templates("templates")

# Rate Limiter: máximo 10 operações por minuto
admin_espécies_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_especies"
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona a raiz para /listar"""
    return RedirectResponse(
        url="/admin/especies/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """
    Lista todas as espécies.
    Acessível em: GET /admin/espécies/listar
    """
    # Busca todas as espécies do banco
    especies = especie_repo.obter_todos()

    # Renderiza o template com os dados
    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "especies": especies
        }
    )

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona a raiz para /listar"""
    return RedirectResponse(
        url="/admin/especies/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """
    Lista todas as espécies.
    Acessível em: GET /admin/especies/listar
    """
    # Busca todas as espécies do banco
    especies = especie_repo.obter_todos()

    # Renderiza o template com os dados
    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "especies": especies
        }
    )