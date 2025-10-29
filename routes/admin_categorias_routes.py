from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.categoria_dto import CriarCategoriaDTO, AlterarCategoriaDTO
from model.categoria_model import Categoria
from repo import categoria_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente

router = APIRouter(prefix="/admin/categorias")
templates = criar_templates("templates/admin/categorias")

# Rate limiter para operações admin
admin_categorias_limiter = RateLimiter(
    max_tentativas=20,  # 20 operações
    janela_minutos=1,   # por minuto
    nome="admin_categorias",
)


@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de categorias"""
    return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todas as categorias do sistema"""
    categorias = categoria_repo.obter_todos()
    total = categoria_repo.contar()
    return templates.TemplateResponse(
        "admin/categorias/listar.html",
        {
            "request": request,
            "categorias": categorias,
            "total": total
        }
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de categoria"""
    return templates.TemplateResponse(
        "admin/categorias/cadastro.html",
        {"request": request}
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(""),
    usuario_logado: Optional[dict] = None
):
    """Cadastra uma nova categoria"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = CriarCategoriaDTO(
            nome=nome,
            descricao=descricao
        )

        # Verificar se categoria já existe
        categoria_existente = categoria_repo.obter_por_nome(dto.nome)
        if categoria_existente:
            informar_erro(request, f"Já existe uma categoria com o nome '{dto.nome}'.")
            return templates.TemplateResponse(
                "admin/categorias/cadastro.html",
                {
                    "request": request,
                    "dados": dados_formulario
                }
            )

        # Criar categoria
        categoria = Categoria(
            id=0,
            nome=dto.nome,
            descricao=dto.descricao
        )

        categoria_id = categoria_repo.inserir(categoria)
        logger.info(f"Categoria '{dto.nome}' (ID: {categoria_id}) cadastrada por admin {usuario_logado['id']}")

        informar_sucesso(request, f"Categoria '{dto.nome}' cadastrada com sucesso!")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/categorias/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de alteração de categoria"""
    categoria = categoria_repo.obter_por_id(id)

    if not categoria:
        informar_erro(request, "Categoria não encontrada")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Criar cópia dos dados da categoria
    dados_categoria = categoria.__dict__.copy()

    return templates.TemplateResponse(
        "admin/categorias/editar.html",
        {
            "request": request,
            "categoria": categoria,
            "dados": dados_categoria
        }
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    descricao: str = Form(""),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de uma categoria"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se categoria existe
    categoria_atual = categoria_repo.obter_por_id(id)
    if not categoria_atual:
        informar_erro(request, "Categoria não encontrada")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Armazena os dados do formulário para reexibição em caso de erro
    dados_formulario: dict = {"id": id, "nome": nome, "descricao": descricao}

    try:
        # Validar com DTO
        dto = AlterarCategoriaDTO(
            id=id,
            nome=nome,
            descricao=descricao
        )

        # Verificar se outro registro já usa o nome
        categoria_mesmo_nome = categoria_repo.obter_por_nome(dto.nome)
        if categoria_mesmo_nome and categoria_mesmo_nome.id != id:
            informar_erro(request, f"Já existe outra categoria com o nome '{dto.nome}'.")
            return templates.TemplateResponse(
                "admin/categorias/editar.html",
                {
                    "request": request,
                    "categoria": categoria_atual,
                    "dados": dados_formulario
                }
            )

        # Atualizar categoria
        categoria_atual.nome = dto.nome
        categoria_atual.descricao = dto.descricao

        categoria_repo.atualizar(categoria_atual)
        logger.info(f"Categoria ID {id} alterada por admin {usuario_logado['id']}")

        informar_sucesso(request, f"Categoria '{dto.nome}' alterada com sucesso!")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        dados_formulario["categoria"] = categoria_atual
        raise FormValidationError(
            validation_error=e,
            template_path="admin/categorias/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome",
        )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui uma categoria"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_categorias_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se categoria existe
    categoria = categoria_repo.obter_por_id(id)
    if not categoria:
        informar_erro(request, "Categoria não encontrada")
        return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Tentar excluir
    try:
        if categoria_repo.excluir(id):
            logger.info(f"Categoria '{categoria.nome}' (ID: {id}) excluída por admin {usuario_logado['id']}")
            informar_sucesso(request, f"Categoria '{categoria.nome}' excluída com sucesso!")
        else:
            informar_erro(request, "Não foi possível excluir a categoria.")
    except Exception as e:
        logger.error(f"Erro ao excluir categoria ID {id}: {e}")
        informar_erro(request, "Não foi possível excluir a categoria. Ela pode estar sendo usada em outros registros.")

    return RedirectResponse("/admin/categorias/listar", status_code=status.HTTP_303_SEE_OTHER)
