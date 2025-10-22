from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import especie_repo
from fastapi import Form
from pydantic import ValidationError
from dtos.especie_dto import CadastrarEspecieDTO
from model.especie_model import Especie
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# Rate limiter
admin_especies_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_especies"
)

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Cadastra uma nova espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {"nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CadastrarEspecieDTO(nome=nome, descricao=descricao)

        # Criar espécie
        especie = Especie(
            id_especie=0,
            nome=dto.nome,
            descricao=dto.descricao
        )

        especie_repo.inserir(especie)
        logger.info(f"Espécie '{dto.nome}' cadastrada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Espécie cadastrada com sucesso!")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )

router = APIRouter(prefix="/admin/especies")
templates = criar_templates("templates/admin/especies")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de espécies"""
    return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as espécies cadastradas"""
    especies = especie_repo.obter_todos()
    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {"request": request, "especies": especies}
    )

@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de uma espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se espécie existe
    especie_atual = especie_repo.obter_por_id(id)
    if not especie_atual:
        informar_erro(request, "Espécie não encontrada")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {"id_especie": id, "nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = AlterarEspecieDTO(id_especie=id, nome=nome, descricao=descricao)

        # Atualizar espécie
        especie_atualizada = Especie(
            id_especie=id,
            nome=dto.nome,
            descricao=dto.descricao
        )

        especie_repo.alterar(especie_atualizada)
        logger.info(f"Espécie {id} alterada por admin {usuario_logado['id']}")

        informar_sucesso(request, "Espécie alterada com sucesso!")
        return RedirectResponse("/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        dados_formulario["especie"] = especie_atual
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )