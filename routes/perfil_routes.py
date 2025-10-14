from fastapi import APIRouter, Form, Request, status, UploadFile, File
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from pathlib import Path
import shutil
import uuid

from repo import usuario_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.security import criar_hash_senha, verificar_senha
from util.senha_util import validar_forca_senha
from util.logger_config import logger

router = APIRouter(prefix="/perfil")
templates = criar_templates("templates/perfil")

# Configurações de upload
UPLOAD_DIR = Path("static/img/usuarios")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


@router.get("/visualizar")
@requer_autenticacao()
async def get_visualizar(request: Request, usuario_logado: dict = None):
    """Visualizar perfil do usuário logado"""
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
async def get_editar(request: Request, usuario_logado: dict = None):
    """Formulário para editar dados do perfil"""
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
    usuario_logado: dict = None
):
    """Processar edição de dados do perfil"""
    try:
        # Validações básicas
        if not nome or len(nome.strip()) < 3:
            informar_erro(request, "Nome deve ter no mínimo 3 caracteres")
            return RedirectResponse("/perfil/editar", status_code=status.HTTP_303_SEE_OTHER)

        if not email or '@' not in email:
            informar_erro(request, "E-mail inválido")
            return RedirectResponse("/perfil/editar", status_code=status.HTTP_303_SEE_OTHER)

        # Verificar se o e-mail já está em uso por outro usuário
        usuario_existente = usuario_repo.obter_por_email(email)
        if usuario_existente and usuario_existente.id != usuario_logado["id"]:
            informar_erro(request, "Este e-mail já está em uso por outro usuário")
            return RedirectResponse("/perfil/editar", status_code=status.HTTP_303_SEE_OTHER)

        # Obter usuário atual
        usuario = usuario_repo.obter_por_id(usuario_logado["id"])

        if not usuario:
            informar_erro(request, "Usuário não encontrado")
            return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

        # Atualizar dados
        usuario.nome = nome.strip()
        usuario.email = email.strip().lower()

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

    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {e}")
        informar_erro(request, "Erro ao processar atualização")
        return RedirectResponse("/perfil/editar", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/alterar-senha")
@requer_autenticacao()
async def get_alterar_senha(request: Request, usuario_logado: dict = None):
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
    usuario_logado: dict = None
):
    """Processar alteração de senha"""
    try:
        # Obter usuário
        usuario = usuario_repo.obter_por_id(usuario_logado["id"])

        if not usuario:
            informar_erro(request, "Usuário não encontrado")
            return RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

        # Validar senha atual
        if not verificar_senha(senha_atual, usuario.senha):
            informar_erro(request, "Senha atual incorreta")
            logger.warning(f"Tentativa de alteração de senha com senha atual incorreta - Usuário ID: {usuario.id}")
            return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Validar se novas senhas coincidem
        if senha_nova != confirmar_senha:
            informar_erro(request, "As senhas novas não coincidem")
            return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Validar força da senha
        senha_valida, mensagem = validar_forca_senha(senha_nova)
        if not senha_valida:
            informar_erro(request, mensagem)
            return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Verificar se a nova senha é diferente da atual
        if verificar_senha(senha_nova, usuario.senha):
            informar_erro(request, "A nova senha deve ser diferente da senha atual")
            return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Atualizar senha
        senha_hash = criar_hash_senha(senha_nova)
        if usuario_repo.atualizar_senha(usuario.id, senha_hash):
            logger.info(f"Senha alterada com sucesso - Usuário ID: {usuario.id}")
            informar_sucesso(request, "Senha alterada com sucesso!")
        else:
            informar_erro(request, "Erro ao alterar senha. Tente novamente.")

        return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        informar_erro(request, "Erro ao processar alteração de senha")
        return RedirectResponse("/perfil/alterar-senha", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/atualizar-foto")
@requer_autenticacao()
async def post_atualizar_foto(
    request: Request,
    foto: UploadFile = File(...),
    usuario_logado: dict = None
):
    """Upload de foto de perfil"""
    try:
        # Validar arquivo
        if not foto.filename:
            informar_erro(request, "Nenhum arquivo selecionado")
            return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

        # Verificar extensão
        file_ext = Path(foto.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            informar_erro(request, f"Formato não permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}")
            return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

        # Verificar tamanho (ler conteúdo)
        contents = await foto.read()
        if len(contents) > MAX_FILE_SIZE:
            informar_erro(request, f"Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE // (1024*1024)}MB")
            return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

        # Gerar nome único para o arquivo
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename

        # Salvar arquivo
        with open(file_path, "wb") as f:
            f.write(contents)

        # Caminho relativo para salvar no banco
        foto_url = f"/static/img/usuarios/{unique_filename}"

        # Obter usuário e foto antiga
        usuario = usuario_repo.obter_por_id(usuario_logado["id"])
        foto_antiga = usuario.foto if usuario else None

        # Atualizar no banco
        if usuario_repo.atualizar_foto(usuario_logado["id"], foto_url):
            # Atualizar sessão
            request.session["usuario_logado"]["foto"] = foto_url

            # Remover foto antiga se existir
            if foto_antiga and (foto_antiga.startswith("/static/img/usuarios/") or foto_antiga.startswith("/static/uploads/fotos/")):
                try:
                    antiga_path = Path(foto_antiga.replace("/static/", "static/"))
                    if antiga_path.exists():
                        antiga_path.unlink()
                except Exception as e:
                    logger.warning(f"Erro ao remover foto antiga: {e}")

            logger.info(f"Foto de perfil atualizada - Usuário ID: {usuario_logado['id']}")
            informar_sucesso(request, "Foto de perfil atualizada com sucesso!")
        else:
            # Remover arquivo se falhou ao salvar no banco
            if file_path.exists():
                file_path.unlink()
            informar_erro(request, "Erro ao atualizar foto. Tente novamente.")

        return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Erro ao fazer upload de foto: {e}")
        informar_erro(request, "Erro ao processar upload da foto")
        return RedirectResponse("/perfil/visualizar", status_code=status.HTTP_303_SEE_OTHER)
