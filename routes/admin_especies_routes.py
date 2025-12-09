from typing import Optional

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.especie_dto import AlterarEspecieDTO, CriarEspecieDTO
from model.especie_model import Especie
from repo import especie_repo
from util.auth_decorator import requer_autenticacao
from util.exceptions import FormValidationError
from util.flash_messages import informar_erro, informar_sucesso
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.template_util import criar_templates

router = APIRouter(prefix="/admin/especies")
templates = criar_templates()

# Rate limiter para operações admin
admin_especies_limiter = RateLimiter(
    max_tentativas=20,  # 20 operações
    janela_minutos=1,  # por minuto
    nome="admin_especies",
)


@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de espécies"""
    return RedirectResponse(
        "/admin/especies/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as espécies do sistema"""
    especies = especie_repo.obter_todos()
    total = especie_repo.contar()
    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {"request": request, "especies": especies, "total": total, "usuario_logado": usuario_logado},
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de espécie"""
    return templates.TemplateResponse(
        "admin/especies/cadastro.html", {"request": request, "usuario_logado": usuario_logado}
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(""),
    usuario_logado: Optional[dict] = None,
):
    """Cadastra uma nova espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(
            request, "Muitas operações. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CriarEspecieDTO(nome=nome, descricao=descricao)

        # Verificar se espécie já existe
        especie_existente = especie_repo.obter_por_nome(dto.nome)
        if especie_existente:
            informar_erro(request, f"Já existe uma espécie com o nome '{dto.nome}'.")
            return templates.TemplateResponse(
                "admin/especies/cadastro.html",
                {"request": request, "dados": dados_formulario, "usuario_logado": usuario_logado},
            )

        # Criar espécie
        especie = Especie(id=0, nome=dto.nome, descricao=dto.descricao)

        especie_id = especie_repo.inserir(especie)
        logger.info(
            f"Espécie '{dto.nome}' (ID: {especie_id}) cadastrada por admin {usuario_logado.id}"
        )

        informar_sucesso(request, f"Espécie '{dto.nome}' cadastrada com sucesso!")
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de alteração de espécie"""
    especie = especie_repo.obter_por_id(id)

    if not especie:
        informar_erro(request, "Espécie não encontrada")
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Criar cópia dos dados da espécie
    dados_especie = especie.__dict__.copy()

    return templates.TemplateResponse(
        "admin/especies/editar.html",
        {"request": request, "especie": especie, "dados": dados_especie, "usuario_logado": usuario_logado},
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(""),
    usuario_logado: Optional[dict] = None,
):
    """Altera dados de uma espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(
            request, "Muitas operações. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se espécie existe
    especie_atual = especie_repo.obter_por_id(id)
    if not especie_atual:
        informar_erro(request, "Espécie não encontrada")
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"id": id, "nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = AlterarEspecieDTO(id=id, nome=nome, descricao=descricao)

        # Verificar se outro registro já usa o nome
        especie_mesmo_nome = especie_repo.obter_por_nome(dto.nome)
        if especie_mesmo_nome and especie_mesmo_nome.id != id:
            informar_erro(
                request, f"Já existe outra espécie com o nome '{dto.nome}'."
            )
            return templates.TemplateResponse(
                "admin/especies/editar.html",
                {
                    "request": request,
                    "especie": especie_atual,
                    "dados": dados_formulario,
                    "usuario_logado": usuario_logado,
                },
            )

        # Atualizar espécie
        especie_atual.nome = dto.nome
        especie_atual.descricao = dto.descricao

        especie_repo.atualizar(especie_atual)
        logger.info(f"Espécie ID {id} alterada por admin {usuario_logado.id}")

        informar_sucesso(request, f"Espécie '{dto.nome}' alterada com sucesso!")
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    except ValidationError as e:
        dados_formulario["especie"] = especie_atual
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui uma espécie"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(
            request, "Muitas operações. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se espécie existe
    especie = especie_repo.obter_por_id(id)
    if not especie:
        informar_erro(request, "Espécie não encontrada")
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se a espécie está em uso
    if especie_repo.esta_em_uso(id):
        informar_erro(
            request,
            f"Não é possível excluir a espécie '{especie.nome}' pois ela está associada a uma ou mais raças.",
        )
        return RedirectResponse(
            "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Tentar excluir
    try:
        if especie_repo.excluir(id):
            logger.info(
                f"Espécie '{especie.nome}' (ID: {id}) excluída por admin {usuario_logado.id}"
            )
            informar_sucesso(request, f"Espécie '{especie.nome}' excluída com sucesso!")
        else:
            informar_erro(request, "Não foi possível excluir a espécie.")
    except Exception as e:
        logger.error(f"Erro ao excluir espécie ID {id}: {e}")
        informar_erro(
            request,
            "Não foi possível excluir a espécie. Ela pode estar sendo usada em outros registros.",
        )

    return RedirectResponse(
        "/admin/especies/listar", status_code=status.HTTP_303_SEE_OTHER
    )
