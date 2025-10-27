"""
Rotas administrativas para gerenciamento de chamados.

Permite que administradores:
- Listem todos os chamados do sistema
- Respondam chamados
- Alterem status de chamados
- Fechem chamados
"""

from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.chamado_dto import ResponderChamadoDTO
from repo import chamado_repo
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError

router = APIRouter(prefix="/admin/chamados")
templates = criar_templates("templates/admin/chamados")


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os chamados do sistema (apenas administradores)."""
    chamados = chamado_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/chamados/listar.html",
        {"request": request, "chamados": chamados}
    )


@router.get("/{id}/responder")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_responder(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário para responder um chamado."""
    chamado = chamado_repo.obter_por_id(id)

    if not chamado:
        informar_erro(request, "Chamado não encontrado")
        return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "admin/chamados/responder.html",
        {"request": request, "chamado": chamado}
    )


@router.post("/{id}/responder")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_responder(
    request: Request,
    id: int,
    resposta: str = Form(),
    status_chamado: str = Form(),
    usuario_logado: Optional[dict] = None
):
    """Salva resposta do administrador ao chamado."""
    assert usuario_logado is not None

    chamado = chamado_repo.obter_por_id(id)
    if not chamado:
        informar_erro(request, "Chamado não encontrado")
        return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {
        "resposta": resposta,
        "status_chamado": status_chamado,
        "chamado": chamado  # type: ignore[dict-item]
    }

    try:
        # Validar com DTO
        dto = ResponderChamadoDTO(
            resposta=resposta,
            status=status_chamado
        )

        # Atualizar chamado
        fechar = (dto.status == "Fechado")
        sucesso = chamado_repo.atualizar_status(
            id=id,
            status=dto.status,
            resposta_admin=dto.resposta,
            fechar=fechar,
            admin_id=usuario_logado["id"]
        )

        if sucesso:
            logger.info(
                f"Chamado {id} respondido por admin {usuario_logado['id']}, status: {dto.status}"
            )
            informar_sucesso(request, "Resposta salva com sucesso!")
            return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
        else:
            informar_erro(request, "Erro ao salvar resposta")
            return RedirectResponse(f"/admin/chamados/{id}/responder", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/chamados/responder.html",
            dados_formulario=dados_formulario,
            campo_padrao="resposta",
        )


@router.post("/{id}/fechar")
@requer_autenticacao([Perfil.ADMIN.value])
async def fechar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Fecha um chamado sem adicionar resposta."""
    assert usuario_logado is not None

    chamado = chamado_repo.obter_por_id(id)
    if not chamado:
        informar_erro(request, "Chamado não encontrado")
        return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    sucesso = chamado_repo.atualizar_status(
        id=id,
        status="Fechado",
        resposta_admin=chamado.resposta_admin,  # Mantém resposta existente
        fechar=True
    )

    if sucesso:
        logger.info(f"Chamado {id} fechado por admin {usuario_logado['id']}")
        informar_sucesso(request, "Chamado fechado com sucesso!")
    else:
        informar_erro(request, "Erro ao fechar chamado")

    return RedirectResponse("/admin/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
