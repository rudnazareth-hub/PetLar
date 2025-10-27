"""
Rotas para gerenciamento de chamados por usuários não-administradores.

Permite que usuários comuns:
- Listem seus próprios chamados
- Abram novos chamados
- Visualizem detalhes de chamados
- Excluam chamados próprios
"""

from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.chamado_dto import CriarChamadoDTO
from model.chamado_model import Chamado
from repo import chamado_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError

router = APIRouter(prefix="/chamados")
templates = criar_templates("templates/chamados")


@router.get("/listar")
@requer_autenticacao()
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os chamados do usuário logado."""
    assert usuario_logado is not None
    chamados = chamado_repo.obter_por_usuario(usuario_logado["id"])
    return templates.TemplateResponse(
        "chamados/listar.html",
        {"request": request, "chamados": chamados}
    )


@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de abertura de chamado."""
    return templates.TemplateResponse(
        "chamados/cadastrar.html",
        {"request": request}
    )


@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    titulo: str = Form(),
    descricao: str = Form(),
    prioridade: str = Form(default="Média"),
    usuario_logado: Optional[dict] = None
):
    """Cadastra um novo chamado."""
    assert usuario_logado is not None

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade
    }

    try:
        # Validar com DTO
        dto = CriarChamadoDTO(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade
        )

        # Criar chamado
        chamado = Chamado(
            id=0,
            titulo=dto.titulo,
            descricao=dto.descricao,
            prioridade=dto.prioridade,
            status="Aberto",
            usuario_id=usuario_logado["id"]
        )

        chamado_id = chamado_repo.inserir(chamado)
        logger.info(
            f"Chamado #{chamado_id} '{dto.titulo}' criado por usuário {usuario_logado['id']}"
        )

        informar_sucesso(request, "Chamado aberto com sucesso! Em breve responderemos.")
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="chamados/cadastrar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
        )


@router.get("/{id}/visualizar")
@requer_autenticacao()
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes de um chamado específico."""
    assert usuario_logado is not None
    chamado = chamado_repo.obter_por_id(id)

    # Verificar se chamado existe e pertence ao usuário
    if not chamado or chamado.usuario_id != usuario_logado["id"]:
        informar_erro(request, "Chamado não encontrado")
        logger.warning(
            f"Usuário {usuario_logado['id']} tentou acessar chamado {id} sem permissão"
        )
        return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "chamados/visualizar.html",
        {"request": request, "chamado": chamado}
    )


@router.post("/{id}/excluir")
@requer_autenticacao()
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um chamado do usuário."""
    assert usuario_logado is not None
    chamado = chamado_repo.obter_por_id(id)

    # Verificar se chamado existe e pertence ao usuário
    if chamado and chamado.usuario_id == usuario_logado["id"]:
        chamado_repo.excluir(id)
        logger.info(f"Chamado {id} excluído por usuário {usuario_logado['id']}")
        informar_sucesso(request, "Chamado excluído com sucesso!")
    else:
        informar_erro(request, "Chamado não encontrado")
        logger.warning(
            f"Usuário {usuario_logado['id']} tentou excluir chamado {id} sem permissão"
        )

    return RedirectResponse("/chamados/listar", status_code=status.HTTP_303_SEE_OTHER)
