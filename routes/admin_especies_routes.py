from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import especie_repo

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de espécie"""
    return templates.TemplateResponse(
        "admin/especies/cadastro.html",
        {"request": request}
    )

router = APIRouter(prefix="/admin/especies")
templates = criar_templates("templates/admin/especies")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de espécies"""
    return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as espécies cadastradas"""
    especies = especie_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {"request": request, "especies": especies}
    )