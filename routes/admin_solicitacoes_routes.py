from typing import Optional
from fastapi import APIRouter, Request, status, Query
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import solicitacao_repo

router = APIRouter(prefix="/admin/solicitacoes")
templates = criar_templates("templates/admin/solicitacoes")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de solicitações"""
    return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(
    request: Request,
    filtro_status: Optional[str] = Query(None),
    usuario_logado: Optional[dict] = None
):
    """Lista todas as solicitações de adoção do sistema"""
    # Obter todas as solicitações
    solicitacoes = solicitacao_repo.obter_todos()

    # Aplicar filtro de status se especificado
    if filtro_status and filtro_status != 'Todas':
        solicitacoes = [s for s in solicitacoes if s['status'] == filtro_status]

    # Calcular estatísticas
    total_solicitacoes = len(solicitacao_repo.obter_todos())
    pendentes = len([s for s in solicitacao_repo.obter_todos() if s['status'] == 'Pendente'])
    aprovadas = len([s for s in solicitacao_repo.obter_todos() if s['status'] == 'Aprovada'])
    rejeitadas = len([s for s in solicitacao_repo.obter_todos() if s['status'] == 'Rejeitada'])

    return templates.TemplateResponse(
        "admin/solicitacoes/listar.html",
        {
            "request": request,
            "solicitacoes": solicitacoes,
            "filtro_status": filtro_status or 'Todas',
            "estatisticas": {
                'total': total_solicitacoes,
                'pendentes': pendentes,
                'aprovadas': aprovadas,
                'rejeitadas': rejeitadas
            }
        }
    )