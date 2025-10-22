from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import animal_repo

router = APIRouter(prefix="/admin/animais")
templates = criar_templates("templates/admin/animais")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de animais"""
    return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os animais cadastrados"""
    animais = animal_repo.obter_todos_com_relacoes()
    return templates.TemplateResponse(
        "admin/animais/listar.html",
        {"request": request, "animais": animais}
    )