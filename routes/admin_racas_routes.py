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
templates = criar_templates("templates/admin/racas")

# Rate limiter
admin_racas_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_racas"
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
            return RedirectResponse("/admin/racas/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

        # Criar raça
        raca = Raca(
            id=0,
            nome=dto.nome,
            id_especie=dto.id_especie,
            descricao=dto.descricao
        )

        raca_repo.inserir(raca)
        logger.info(f"Raça '{dto.nome}' cadastrada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Raça cadastrada com sucesso!")
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Recarregar espécies para o select
        especies = especie_repo.obter_todos()
        dados_formulario["especies"] = {str(e.id_especie): e.nome for e in especies}

        raise FormValidationError(
            validation_error=e,
            template_path="admin/racas/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
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
    return templates.TemplateResponse(
        "admin/racas/listar.html",
        {"request": request, "racas": racas}
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
            "especies": especies_dict
        }
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de raça"""
    # Obter todas as espécies para o select
    especies = especie_repo.obter_todos()

    # Converter para dict para o select
    especies_dict = {str(e.id_especie): e.nome for e in especies}

    return templates.TemplateResponse(
        "admin/racas/cadastro.html",
        {
            "request": request,
            "especies": especies_dict
        }
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

    # Verificar se existem raças vinculadas
    racas_vinculadas = raca_repo.obter_por_racas(id)
    if racas_vinculadas:
        informar_erro(
            request,
            f"Não é possível excluir esta raça pois existem {len(racas_vinculadas)} raça(s) vinculada(s) a ela."
        )
        return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)

    raca_repo.excluir(id)
    logger.info(f"Raça {id} ({raca.nome}) excluída por admin {usuario_logado['id']}")
    informar_sucesso(request, "Raça excluída com sucesso!")
    return RedirectResponse("/admin/racas/listar", status_code=status.HTTP_303_SEE_OTHER)