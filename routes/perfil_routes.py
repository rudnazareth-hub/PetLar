from typing import Optional
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.perfil_dto import EditarPerfilDTO, AlterarSenhaDTO
from repo import usuario_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.security import criar_hash_senha, verificar_senha
from util.foto_util import salvar_foto_cropada_usuario
from util.logger_config import logger

router = APIRouter(prefix="/perfil")
templates = criar_templates("templates/perfil")


@router.get("/visualizar")
@requer_autenticacao()
async def get_visualizar(request: Request, usuario_logado: Optional[dict] = None):
    """Visualizar perfil do usuário logado"""
    assert usuario_logado is not None
    usuario = usuario_repo.obter_por_id(usuario_logado["id"])

    if not usuario:
        informar_erro(request, "Usuário não encontrado")
        return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "perfil/visualizar.html",
        {"request": request, "usuario": usuario}
    )


@router.get("/editar")
@requer_autenticacao()
async def get_editar(request: Request, usuario_logado: Optional[dict] = None):
    """Formulário para editar dados do perfil"""
    assert usuario_logado is not None
    usuario = usuario_repo.obter_por_id(usuario_logado["id"])

    if not usuario:
        informar_erro(request, "Usuário não encontrado")
        return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "perfil/editar.html",
        {"request": request, "usuario": usuario}
    )


@router.post("/editar")
@requer_autenticacao()
async def post_editar(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Processar edição de dados do perfil"""
    assert usuario_logado is not None
    try:
        # Validar com DTO
        dto = EditarPerfilDTO(nome=nome, email=email)

        # Verificar se o e-mail já está em uso por outro usuário
        usuario_existente = usuario_repo.obter_por_email(dto.email)
        if usuario_existente and usuario_existente.id != usuario_logado["id"]:
            informar_erro(request, "Este e-mail já está em uso por outro usuário")
            return RedirectResponse("/perfil/editar", status_code=status.HTTP_303_SEE_OTHER)

        # Obter usuário atual
        usuario = usuario_repo.obter_por_id(usuario_logado["id"])

        if not usuario:
            informar_erro(request, "Usuário não encontrado")
            return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

        # Atualizar dados
        usuario.nome = dto.nome
        usuario.email = dto.email

        # Salvar no banco
        if usuario_repo.alterar(usuario):
            # Atualizar sessão
            request.session["usuario_logado"]["nome"] = usuario.nome
            request.session["usuario_logado"]["email"] = usuario.email

            logger.info(f"Perfil atualizado para usuário ID: {usuario.id}")
            informar_sucesso(request, "Perfil atualizado com sucesso!")
        else:
            informar_erro(request, "Erro ao atualizar perfil. Tente novamente.")

        return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        return RedirectResponse("/perfil/editar", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        informar_erro(request, "Erro ao processar atualização")
        return RedirectResponse("/perfil/editar", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/alterar-senha")
@requer_autenticacao()
async def get_alterar_senha(request: Request, usuario_logado: Optional[dict] = None):
    """Formulário para alterar senha"""
    return templates.TemplateResponse(
        "perfil/alterar-senha.html",
        {"request": request}
    )


@router.post("/alterar-senha")
@requer_autenticacao()
async def post_alterar_senha(
    request: Request,
    senha_atual: str = Form(...),
    senha_nova: str = Form(...),
    confirmar_senha: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Processar alteração de senha"""
    assert usuario_logado is not None
    try:
        # Validar com DTO
        dto = AlterarSenhaDTO(
            senha_atual=senha_atual,
            senha_nova=senha_nova,
            confirmar_senha=confirmar_senha
        )

        # Obter usuário
        usuario = usuario_repo.obter_por_id(usuario_logado["id"])

        if not usuario:
            informar_erro(request, "Usuário não encontrado")
            return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

        # Validar senha atual
        if not verificar_senha(dto.senha_atual, usuario.senha):
            informar_erro(request, "Senha atual incorreta")
            logger.warning(f"Tentativa de alteração de senha com senha atual incorreta - Usuário ID: {usuario.id}")
            return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Verificar se a nova senha é diferente da atual
        if verificar_senha(dto.senha_nova, usuario.senha):
            informar_erro(request, "A nova senha deve ser diferente da senha atual")
            return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Atualizar senha
        senha_hash = criar_hash_senha(dto.senha_nova)
        if usuario_repo.atualizar_senha(usuario.id, senha_hash):
            logger.info(f"Senha alterada com sucesso - Usuário ID: {usuario.id}")
            informar_sucesso(request, "Senha alterada com sucesso!")
        else:
            informar_erro(request, "Erro ao alterar senha. Tente novamente.")

        return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        informar_erro(request, "Erro ao processar alteração de senha")
        return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/atualizar-foto")
@requer_autenticacao()
async def post_atualizar_foto(
    request: Request,
    foto_base64: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Upload de foto de perfil cropada"""
    assert usuario_logado is not None
    try:
        usuario_id = usuario_logado["id"]

        # Validação básica
        if not foto_base64 or len(foto_base64) < 100:
            informar_erro(request, "Foto inválida. Por favor, tente novamente.")
            return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

        # Validar tamanho aproximado (base64 é ~33% maior que binário)
        tamanho_aproximado = len(foto_base64) * 3 / 4
        max_size = 10 * 1024 * 1024  # 10MB
        if tamanho_aproximado > max_size:
            informar_erro(request, "Imagem muito grande. Tamanho máximo: 10MB")
            return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

        # Salvar foto cropada
        if salvar_foto_cropada_usuario(usuario_id, foto_base64):
            logger.info(f"Foto de perfil atualizada - Usuário ID: {usuario_id}")
            informar_sucesso(request, "Foto de perfil atualizada com sucesso!")
        else:
            informar_erro(request, "Erro ao atualizar foto. Tente novamente.")

        return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Erro ao fazer upload de foto: {e}")
        informar_erro(request, "Erro ao processar upload da foto")
        return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)
