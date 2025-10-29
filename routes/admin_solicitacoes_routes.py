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


@router.get("/visualizar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos de uma solicitação"""
    solicitacao = solicitacao_repo.obter_por_id(id)

    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/solicitacoes/visualizar.html",
        {
            "request": request,
            "solicitacao": solicitacao
        }
    )


from fastapi import Form
from pydantic import ValidationError
from dtos.solicitacao_dto import AprovarSolicitacaoDTO, RejeitarSolicitacaoDTO
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# Rate limiter
admin_solicitacoes_limiter = RateLimiter(
    max_tentativas=20,
    janela_minutos=1,
    nome="admin_solicitacoes"
)

@router.post("/aprovar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_aprovar(
    request: Request,
    id: int,
    resposta_abrigo: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Aprova uma solicitação de adoção"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_solicitacoes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se solicitação existe
    solicitacao = solicitacao_repo.obter_por_id(id)
    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se está pendente
    if solicitacao['status'] != 'Pendente':
        informar_erro(request, "Esta solicitação já foi processada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Validar com DTO
        dto = AprovarSolicitacaoDTO(
            id=id,
            resposta_abrigo=resposta_abrigo
        )

        # Atualizar status
        resposta = dto.resposta_abrigo or "Solicitação aprovada pelo administrador do sistema."
        solicitacao_repo.atualizar_status(id, "Aprovada", resposta)

        logger.info(f"Solicitação {id} aprovada por admin {usuario_logado['id']}")
        informar_sucesso(request, "Solicitação aprovada com sucesso!")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        logger.error(f"Erro ao aprovar solicitação {id}: {e}")
        informar_erro(request, "Erro ao aprovar solicitação. Verifique os dados.")
        return RedirectResponse(f"/admin/solicitacoes/visualizar/{id}", status_code=status.HTTP_303_SEE_OTHER)
    
@router.post("/rejeitar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_rejeitar(
    request: Request,
    id: int,
    resposta_abrigo: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Rejeita uma solicitação de adoção"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_solicitacoes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se solicitação existe
    solicitacao = solicitacao_repo.obter_por_id(id)
    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se está pendente
    if solicitacao['status'] != 'Pendente':
        informar_erro(request, "Esta solicitação já foi processada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # Validar com DTO (motivo é obrigatório)
        dto = RejeitarSolicitacaoDTO(
            id=id,
            resposta_abrigo=resposta_abrigo
        )

        # Atualizar status
        solicitacao_repo.atualizar_status(id, "Rejeitada", dto.resposta_abrigo)

        logger.info(f"Solicitação {id} rejeitada por admin {usuario_logado['id']}")
        informar_sucesso(request, "Solicitação rejeitada.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        logger.error(f"Erro ao rejeitar solicitação {id}: {e}")
        informar_erro(request, "Erro ao rejeitar solicitação. É obrigatório informar o motivo.")
        return RedirectResponse(f"/admin/solicitacoes/visualizar/{id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/cancelar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cancelar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Cancela uma solicitação de adoção"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_solicitacoes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se solicitação existe
    solicitacao = solicitacao_repo.obter_por_id(id)
    if not solicitacao:
        informar_erro(request, "Solicitação não encontrada")
        return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Cancelar
    solicitacao_repo.atualizar_status(id, "Cancelada", "Cancelada pelo administrador do sistema")

    logger.info(f"Solicitação {id} cancelada por admin {usuario_logado['id']}")
    informar_sucesso(request, "Solicitação cancelada com sucesso!")
    return RedirectResponse("/admin/solicitacoes/listar", status_code=status.HTTP_303_SEE_OTHER)