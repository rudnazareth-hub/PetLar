from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.usuario_dto import CriarUsuarioDTO, AlterarUsuarioDTO
from model.usuario_model import Usuario
from repo import usuario_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.perfis import Perfil
from util.security import criar_hash_senha

router = APIRouter(prefix="/admin/usuarios")
templates = criar_templates("templates/admin/usuarios")

@router.get("/lista")
@requer_autenticacao([Perfil.ADMIN.value])
async def lista(request: Request, usuario_logado: dict = None):
    """Lista todos os usuários do sistema"""
    usuarios = usuario_repo.obter_todos()
    return templates.TemplateResponse(
        "lista.html",
        {"request": request, "usuarios": usuarios}
    )

@router.get("/cadastro")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastro(request: Request, usuario_logado: dict = None):
    """Exibe formulário de cadastro de usuário"""
    perfis = Perfil.valores()
    return templates.TemplateResponse(
        "cadastro.html",
        {"request": request, "perfis": perfis}
    )

@router.post("/cadastro")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    perfil: str = Form(...),
    usuario_logado: dict = None
):
    """Cadastra um novo usuário"""
    try:
        # Validar com DTO
        dto = CriarUsuarioDTO(
            nome=nome,
            email=email,
            senha=senha,
            perfil=perfil
        )

        # Verificar se e-mail já existe
        usuario_existente = usuario_repo.obter_por_email(dto.email)
        if usuario_existente:
            informar_erro(request, "E-mail já cadastrado no sistema")
            perfis = Perfil.valores()
            return templates.TemplateResponse(
                "cadastro.html",
                {
                    "request": request,
                    "perfis": perfis,
                    "dados": {"nome": nome, "email": email, "perfil": perfil}
                }
            )

        # Criar hash da senha
        senha_hash = criar_hash_senha(dto.senha)

        # Criar usuário
        usuario = Usuario(
            id=0,
            nome=dto.nome,
            email=dto.email,
            senha=senha_hash,
            perfil=dto.perfil
        )

        usuario_repo.inserir(usuario)
        logger.info(f"Usuário '{dto.email}' cadastrado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Usuário cadastrado com sucesso!")
        return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        perfis = Perfil.valores()
        return templates.TemplateResponse(
            "cadastro.html",
            {
                "request": request,
                "perfis": perfis,
                "dados": {"nome": nome, "email": email, "perfil": perfil}
            }
        )

@router.get("/alterar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_alterar(request: Request, id: int, usuario_logado: dict = None):
    """Exibe formulário de alteração de usuário"""
    usuario = usuario_repo.obter_por_id(id)

    if not usuario:
        informar_erro(request, "Usuário não encontrado")
        return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

    perfis = Perfil.valores()
    return templates.TemplateResponse(
        "alterar.html",
        {"request": request, "usuario": usuario, "perfis": perfis}
    )

@router.post("/alterar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_alterar(
    request: Request,
    id: int,
    nome: str = Form(...),
    email: str = Form(...),
    perfil: str = Form(...),
    usuario_logado: dict = None
):
    """Altera dados de um usuário"""
    try:
        # Verificar se usuário existe
        usuario_atual = usuario_repo.obter_por_id(id)
        if not usuario_atual:
            informar_erro(request, "Usuário não encontrado")
            return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

        # Validar com DTO
        dto = AlterarUsuarioDTO(
            id=id,
            nome=nome,
            email=email,
            perfil=perfil
        )

        # Verificar se e-mail já existe em outro usuário
        usuario_email = usuario_repo.obter_por_email(dto.email)
        if usuario_email and usuario_email.id != id:
            informar_erro(request, "E-mail já cadastrado em outro usuário")
            perfis = Perfil.valores()
            return templates.TemplateResponse(
                "alterar.html",
                {
                    "request": request,
                    "usuario": usuario_atual,
                    "perfis": perfis,
                    "dados": {"nome": nome, "email": email, "perfil": perfil}
                }
            )

        # Atualizar usuário
        usuario_atualizado = Usuario(
            id=id,
            nome=dto.nome,
            email=dto.email,
            senha=usuario_atual.senha,  # Mantém senha existente
            perfil=dto.perfil
        )

        usuario_repo.alterar(usuario_atualizado)
        logger.info(f"Usuário {id} alterado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Usuário alterado com sucesso!")
        return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        usuario_atual = usuario_repo.obter_por_id(id)
        perfis = Perfil.valores()
        return templates.TemplateResponse(
            "alterar.html",
            {
                "request": request,
                "usuario": usuario_atual,
                "perfis": perfis,
                "dados": {"nome": nome, "email": email, "perfil": perfil}
            }
        )

@router.get("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_excluir(request: Request, id: int, usuario_logado: dict = None):
    """Exibe confirmação de exclusão de usuário"""
    usuario = usuario_repo.obter_por_id(id)

    if not usuario:
        informar_erro(request, "Usuário não encontrado")
        return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

    # Impedir exclusão do próprio usuário
    if usuario.id == usuario_logado["id"]:
        informar_erro(request, "Você não pode excluir seu próprio usuário")
        return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "excluir.html",
        {"request": request, "usuario": usuario}
    )

@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(request: Request, id: int, usuario_logado: dict = None):
    """Exclui um usuário"""
    usuario = usuario_repo.obter_por_id(id)

    if not usuario:
        informar_erro(request, "Usuário não encontrado")
        return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

    # Impedir exclusão do próprio usuário
    if usuario.id == usuario_logado["id"]:
        informar_erro(request, "Você não pode excluir seu próprio usuário")
        logger.warning(f"Admin {usuario_logado['id']} tentou excluir a si mesmo")
        return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)

    usuario_repo.excluir(id)
    logger.info(f"Usuário {id} ({usuario.email}) excluído por admin {usuario_logado['id']}")
    informar_sucesso(request, "Usuário excluído com sucesso!")
    return RedirectResponse("/admin/usuarios/lista", status_code=status.HTTP_303_SEE_OTHER)
