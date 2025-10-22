from typing import Optional
from fastapi import APIRouter, Request
from repo import abrigo_repo, raca_repo
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil
from util.template_util import criar_templates


router = APIRouter(prefix="/admin/animais")
templates = criar_templates("templates/admin/animais")

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de animal"""
    # Obter raças e abrigos para os selects
    racas = raca_repo.obter_todos_com_especies()
    abrigos = abrigo_repo.obter_todos()

    # Converter para dict para os selects
    racas_dict = {str(r.id_raca): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}
    abrigos_dict = {str(a.id_abrigo): a.responsavel for a in abrigos}

    # Opções de sexo e status
    sexo_opcoes = {"Macho": "Macho", "Fêmea": "Fêmea"}
    status_opcoes = {
        "Disponível": "Disponível",
        "Em Processo": "Em Processo",
        "Adotado": "Adotado",
        "Indisponível": "Indisponível"
    }

    return templates.TemplateResponse(
        "admin/animais/cadastro.html",
        {
            "request": request,
            "racas": racas_dict,
            "abrigos": abrigos_dict,
            "sexo_opcoes": sexo_opcoes,
            "status_opcoes": status_opcoes
        }
    )