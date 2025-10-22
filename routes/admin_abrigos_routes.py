from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import abrigo_repo, usuario_repo

router = APIRouter(prefix="/admin/abrigos")
templates = criar_templates("templates/admin/abrigos")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de abrigos"""
    return RedirectResponse("/admin/abrigos/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os abrigos cadastrados"""
    abrigos = abrigo_repo.obter_todos_com_usuarios()
    return templates.TemplateResponse(
        "admin/abrigos/listar.html",
        {"request": request, "abrigos": abrigos}
    )