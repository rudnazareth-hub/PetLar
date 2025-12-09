from fastapi import Form
from pydantic import ValidationError
from dtos.raca_dto import CadastrarRacaDTO, AlterarRacaDTO
from model.raca_model import Raca
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import raca_repo, especie_repo

# Configuração do router e templates
router = APIRouter(prefix="/admin/racas")
templates = criar_templates()

# Rate limiter para operações admin
admin_racas_limiter = RateLimiter(
    max_tentativas=20,  # 20 operações
    janela_minutos=1,   # por minuto
    nome="admin_racas"
)


@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de raças"""
    return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as raças cadastradas com suas espécies"""
    racas = raca_repo.obter_todos_com_especies()
    total = raca_repo.contar()
    return templates.TemplateResponse(
        "admin/racas/listar.html",
        {"request": request, "racas": racas, "total": total, "usuario_logado": usuario_logado}
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de raça"""
    # Obter todas as espécies para o select
    especies = especie_repo.obter_todos()
    especies_dict = {str(e.id): e.nome for e in especies}

    return templates.TemplateResponse(
        "admin/racas/cadastro.html",
        {
            "request": request,
            "especies": especies_dict,
            "usuario_logado": usuario_logado
        }
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    id_especie: int = Form(...),
    descricao: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Cadastra uma nova raça"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_racas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {"nome": nome, "id_especie": id_especie, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CadastrarRacaDTO(nome=nome, id_especie=id_especie, descricao=descricao)

        # Verificar se espécie existe
        especie = especie_repo.obter_por_id(dto.id_especie)
        if not especie:
            informar_erro(request, "Espécie não encontrada")
            # Recarregar espécies para o select
            especies = especie_repo.obter_todos()
            dados_formulario["especies"] = {str(e.id): e.nome for e in especies}
            return templates.TemplateResponse(
                "admin/racas/cadastro.html",
                {"request": request, "dados": dados_formulario, "especies": dados_formulario["especies"], "usuario_logado": usuario_logado}
            )

        # Criar raça
        raca = Raca(
            id=0,
            nome=dto.nome,
            id_especie=dto.id_especie,
            descricao=dto.descricao
        )

        raca_id = raca_repo.inserir(raca)
        logger.info(f"Raça '{dto.nome}' (ID: {raca_id}) cadastrada por admin {usuario_logado.id}")

        informar_sucesso(request, f"Raça '{dto.nome}' cadastrada com sucesso!")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Recarregar espécies para o select
        especies = especie_repo.obter_todos()
        dados_formulario["especies"] = {str(esp.id): esp.nome for esp in especies}

        raise FormValidationError(
            validation_error=e,
            template_path="admin/racas/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de alteração de raça"""
    raca = raca_repo.obter_por_id(id)

    if not raca:
        informar_erro(request, "Raça não encontrada")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter todas as espécies para o select
    especies = especie_repo.obter_todos()
    especies_dict = {str(e.id): e.nome for e in especies}

    # Criar cópia dos dados da raça
    dados_raca = raca.__dict__.copy()

    return templates.TemplateResponse(
        "admin/racas/editar.html",
        {
            "request": request,
            "raca": raca,
            "dados": dados_raca,
            "especies": especies_dict,
            "usuario_logado": usuario_logado
        }
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    id_especie: int = Form(...),
    descricao: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de uma raça"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_racas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se raça existe
    raca_atual = raca_repo.obter_por_id(id)
    if not raca_atual:
        informar_erro(request, "Raça não encontrada")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {"id": id, "nome": nome, "id_especie": id_especie, "descricao": descricao}

    try:
        # Validar com DTO
        dto = AlterarRacaDTO(id=id, nome=nome, id_especie=id_especie, descricao=descricao)

        # Verificar se espécie existe
        especie = especie_repo.obter_por_id(dto.id_especie)
        if not especie:
            informar_erro(request, "Espécie não encontrada")
            # Recarregar espécies para o select
            especies = especie_repo.obter_todos()
            especies_dict = {str(e.id): e.nome for e in especies}
            return templates.TemplateResponse(
                "admin/racas/editar.html",
                {
                    "request": request,
                    "raca": raca_atual,
                    "dados": dados_formulario,
                    "especies": especies_dict,
                    "usuario_logado": usuario_logado
                }
            )

        # Atualizar raça
        raca_atual.nome = dto.nome
        raca_atual.id_especie = dto.id_especie
        raca_atual.descricao = dto.descricao

        raca_repo.atualizar(raca_atual)
        logger.info(f"Raça ID {id} alterada por admin {usuario_logado.id}")

        informar_sucesso(request, f"Raça '{dto.nome}' alterada com sucesso!")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Recarregar espécies para o select
        especies = especie_repo.obter_todos()
        dados_formulario["especies"] = {str(esp.id): esp.nome for esp in especies}
        dados_formulario["raca"] = raca_atual

        raise FormValidationError(
            validation_error=e,
            template_path="admin/racas/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui uma raça"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_racas_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    raca = raca_repo.obter_por_id(id)

    if not raca:
        informar_erro(request, "Raça não encontrada")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se a raça está em uso (tem animais vinculados)
    if raca_repo.esta_em_uso(id):
        informar_erro(
            request,
            f"Não é possível excluir a raça '{raca.nome}' pois existem animais vinculados a ela."
        )
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Tentar excluir
    try:
        if raca_repo.excluir(id):
            logger.info(f"Raça '{raca.nome}' (ID: {id}) excluída por admin {usuario_logado.id}")
            informar_sucesso(request, f"Raça '{raca.nome}' excluída com sucesso!")
        else:
            informar_erro(request, "Não foi possível excluir a raça.")
    except Exception as e:
        logger.error(f"Erro ao excluir raça ID {id}: {e}")
        informar_erro(
            request,
            "Não foi possível excluir a raça. Ela pode estar sendo usada em outros registros."
        )

    return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)
