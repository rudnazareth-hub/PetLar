from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import adotante_repo, usuario_repo

router = APIRouter(prefix="/admin/adotantes")
templates = criar_templates("templates/admin/adotantes")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de adotantes"""
    return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os adotantes cadastrados com seus dados de usuário"""
    # Obter todos os usuários com perfil ADOTANTE
    usuarios = usuario_repo.obter_todos()
    adotantes_completos = []

    for usuario in usuarios:
        if usuario.perfil == Perfil.ADOTANTE.value:
            adotante = adotante_repo.obter_por_id(usuario.id)
            if adotante:
                adotantes_completos.append({
                    'id_adotante': adotante.id_adotante,
                    'nome': usuario.nome,
                    'email': usuario.email,
                    'telefone': usuario.telefone,
                    'renda_media': adotante.renda_media,
                    'tem_filhos': adotante.tem_filhos,
                    'estado_saude': adotante.estado_saude
                })

    return templates.TemplateResponse(
        "admin/adotantes/listar.html",
        {"request": request, "adotantes": adotantes_completos}
    )

@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de adotante"""
    adotante = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    dados = {
        'id_adotante': adotante.id_adotante,
        'nome': usuario.nome,
        'email': usuario.email,
        'renda_media': adotante.renda_media,
        'tem_filhos': adotante.tem_filhos,
        'estado_saude': adotante.estado_saude
    }

    return templates.TemplateResponse(
        "admin/adotantes/editar.html",
        {
            "request": request,
            "adotante": adotante,
            "dados": dados
        }
    )