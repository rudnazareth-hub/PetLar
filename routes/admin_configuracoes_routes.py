from typing import Optional
import os
import shutil
from pathlib import Path
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

@router.get("/tema")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_tema(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe seletor de temas visuais da aplicação"""
    # Obter tema atual do banco de dados
    config_tema = configuracao_repo.obter_por_chave("theme")
    tema_atual = config_tema.valor if config_tema else "original"

    # Listar todos os arquivos PNG na pasta de imagens dos temas
    img_dir = Path("static/img/bootswatch")
    temas_disponiveis = []

    if img_dir.exists() and img_dir.is_dir():
        for img_file in sorted(img_dir.glob("*.png")):
            tema_nome = img_file.stem  # Nome do arquivo sem extensão
            # Verificar se existe o arquivo CSS correspondente
            css_file = Path(f"static/css/bootswatch/{tema_nome}.bootstrap.min.css")
            if css_file.exists():
                temas_disponiveis.append({
                    "nome": tema_nome,
                    "nome_exibicao": tema_nome.capitalize(),
                    "imagem": f"/static/img/bootswatch/{img_file.name}",
                    "selecionado": tema_nome == tema_atual
                })

    return templates.TemplateResponse(
        "admin/configuracoes/tema.html",
        {
            "request": request,
            "temas": temas_disponiveis,
            "tema_atual": tema_atual
        }
    )

@router.post("/tema/aplicar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_aplicar_tema(
    request: Request,
    tema: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """
    Aplica um tema visual selecionado

    Copia o arquivo CSS do tema para static/css/bootstrap.min.css
    e salva a configuração no banco de dados
    """
    assert usuario_logado is not None

    try:
        # Validar se o tema existe
        css_origem = Path(f"static/css/bootswatch/{tema}.bootstrap.min.css")

        if not css_origem.exists():
            informar_erro(request, f"Tema '{tema}' não encontrado")
            logger.warning(f"Tentativa de aplicar tema inexistente: {tema}")
            return RedirectResponse("/admin/configuracoes/tema", status_code=status.HTTP_303_SEE_OTHER)

        # Copiar arquivo CSS do tema para bootstrap.min.css
        css_destino = Path("static/css/bootstrap.min.css")
        shutil.copy2(css_origem, css_destino)

        # Atualizar ou inserir configuração no banco
        config_existente = configuracao_repo.obter_por_chave("theme")

        if config_existente:
            # Atualizar configuração existente
            sucesso = configuracao_repo.atualizar("theme", tema)
        else:
            # Inserir nova configuração (fallback caso não exista)
            from util.db_util import get_connection
            from sql.configuracao_sql import INSERIR
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(INSERIR, ("theme", tema, "Tema visual da aplicação (Bootswatch)"))
                sucesso = cursor.rowcount > 0

        if sucesso:
            # Limpar cache de configurações
            config.limpar()

            logger.info(
                f"Tema alterado para '{tema}' por admin {usuario_logado['id']} "
                f"(anterior: {config_existente.valor if config_existente else 'nenhum'})"
            )
            informar_sucesso(
                request,
                f"Tema '{tema.capitalize()}' aplicado com sucesso! Recarregue a página para ver as mudanças."
            )
        else:
            logger.error(f"Erro ao salvar configuração de tema '{tema}' no banco de dados")
            informar_erro(request, "Erro ao salvar configuração do tema")

    except Exception as e:
        logger.error(f"Erro ao aplicar tema '{tema}': {str(e)}")
        informar_erro(request, f"Erro ao aplicar tema: {str(e)}")

    return RedirectResponse("/admin/configuracoes/tema", status_code=status.HTTP_303_SEE_OTHER)
