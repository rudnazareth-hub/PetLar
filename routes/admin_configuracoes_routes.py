from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

from repo import configuracao_repo
from util.config_cache import config
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil

router = APIRouter(prefix="/admin/configuracoes")
templates = criar_templates("templates/admin/configuracoes")

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_listar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe lista de configurações do sistema"""
    configuracoes = configuracao_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/configuracoes/listar.html",
        {"request": request, "configuracoes": configuracoes}
    )

@router.post("/atualizar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_atualizar(
    request: Request,
    chave: str = Form(...),
    valor: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """
    Atualiza valor de uma configuração do sistema

    Após atualizar, limpa o cache para forçar recarregamento
    """
    assert usuario_logado is not None
    # Verificar se configuração existe
    config_existente = configuracao_repo.obter_por_chave(chave)

    if not config_existente:
        informar_erro(request, "Configuração não encontrada")
        logger.warning(f"Tentativa de atualizar configuração inexistente: {chave}")
        return RedirectResponse("/admin/configuracoes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Atualizar configuração
    sucesso = configuracao_repo.atualizar(chave, valor)

    if sucesso:
        # Limpar cache para forçar recarregamento
        config.limpar()

        logger.info(
            f"Configuração '{chave}' atualizada de '{config_existente.valor}' "
            f"para '{valor}' por admin {usuario_logado['id']}"
        )
        informar_sucesso(request, f"Configuração '{chave}' atualizada com sucesso!")
    else:
        logger.error(f"Erro ao atualizar configuração '{chave}'")
        informar_erro(request, "Erro ao atualizar configuração")

    return RedirectResponse("/admin/configuracoes/listar", status_code=status.HTTP_303_SEE_OTHER)
