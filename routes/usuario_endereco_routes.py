"""Rotas para gerenciamento de endereco do usuario."""

from typing import Optional

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.endereco_dto import AlterarEnderecoDTO, CriarEnderecoDTO
from model.endereco_model import Endereco
from repo import endereco_repo
from util.auth_decorator import requer_autenticacao
from util.exceptions import FormValidationError
from util.flash_messages import informar_erro, informar_sucesso
from util.logger_config import logger
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.template_util import criar_templates

router = APIRouter(prefix="/usuario/endereco")
templates = criar_templates()

# Rate limiter para operacoes de endereco
endereco_limiter = RateLimiter(
    max_tentativas=20,
    janela_minutos=1,
    nome="usuario_endereco",
)


def _obter_endereco_usuario(id_usuario: int) -> Optional[Endereco]:
    """Obtem o primeiro (e unico) endereco do usuario."""
    enderecos = endereco_repo.obter_por_usuario(id_usuario)
    return enderecos[0] if enderecos else None


@router.get("/")
@requer_autenticacao()
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para visualizacao ou cadastro de endereco."""
    assert usuario_logado is not None

    endereco = _obter_endereco_usuario(usuario_logado.id)

    if endereco:
        return RedirectResponse(
            "/usuario/endereco/visualizar", status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    else:
        return RedirectResponse(
            "/usuario/endereco/cadastrar", status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )


@router.get("/visualizar")
@requer_autenticacao()
async def visualizar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe o endereco do usuario."""
    assert usuario_logado is not None

    endereco = _obter_endereco_usuario(usuario_logado.id)

    if not endereco:
        informar_erro(request, "Voce ainda nao possui endereco cadastrado.")
        return RedirectResponse(
            "/usuario/endereco/cadastrar", status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "perfil/endereco/visualizar.html",
        {"request": request, "endereco": endereco, "usuario_logado": usuario_logado},
    )


@router.get("/cadastrar")
@requer_autenticacao()
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulario de cadastro de endereco."""
    assert usuario_logado is not None

    # Verifica se ja possui endereco
    endereco = _obter_endereco_usuario(usuario_logado.id)
    if endereco:
        informar_erro(request, "Voce ja possui um endereco cadastrado. Use a opcao Editar.")
        return RedirectResponse(
            "/usuario/endereco/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "perfil/endereco/cadastro.html",
        {"request": request, "usuario_logado": usuario_logado},
    )


@router.post("/cadastrar")
@requer_autenticacao()
async def post_cadastrar(
    request: Request,
    titulo: str = Form(...),
    logradouro: str = Form(...),
    numero: str = Form(""),
    complemento: str = Form(""),
    bairro: str = Form(...),
    cidade: str = Form(...),
    uf: str = Form(...),
    cep: str = Form(...),
    usuario_logado: Optional[dict] = None,
):
    """Cadastra um novo endereco para o usuario."""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not endereco_limiter.verificar(ip):
        informar_erro(
            request, "Muitas operacoes. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            "/usuario/endereco/", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verifica se ja possui endereco
    endereco_existente = _obter_endereco_usuario(usuario_logado.id)
    if endereco_existente:
        informar_erro(request, "Voce ja possui um endereco cadastrado.")
        return RedirectResponse(
            "/usuario/endereco/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Armazena os dados do formulario para reexibicao em caso de erro
    dados_formulario = {
        "titulo": titulo,
        "logradouro": logradouro,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cidade": cidade,
        "uf": uf,
        "cep": cep,
    }

    try:
        # Validar com DTO
        dto = CriarEnderecoDTO(
            titulo=titulo,
            logradouro=logradouro,
            numero=numero if numero else None,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            cep=cep,
        )

        # Criar endereco
        endereco = Endereco(
            id=0,
            id_usuario=usuario_logado.id,
            titulo=dto.titulo,
            logradouro=dto.logradouro,
            numero=dto.numero or 0,
            complemento=dto.complemento,
            bairro=dto.bairro,
            cidade=dto.cidade,
            uf=dto.uf,
            cep=dto.cep,
        )

        endereco_id = endereco_repo.inserir(endereco)
        logger.info(
            f"Endereco (ID: {endereco_id}) cadastrado por usuario {usuario_logado.id}"
        )

        informar_sucesso(request, "Endereco cadastrado com sucesso!")
        return RedirectResponse(
            "/usuario/endereco/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="perfil/endereco/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
        )


@router.get("/editar")
@requer_autenticacao()
async def get_editar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulario de edicao de endereco."""
    assert usuario_logado is not None

    endereco = _obter_endereco_usuario(usuario_logado.id)

    if not endereco:
        informar_erro(request, "Voce ainda nao possui endereco cadastrado.")
        return RedirectResponse(
            "/usuario/endereco/cadastrar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Criar copia dos dados do endereco
    dados_endereco = endereco.__dict__.copy()

    return templates.TemplateResponse(
        "perfil/endereco/editar.html",
        {"request": request, "endereco": endereco, "dados": dados_endereco, "usuario_logado": usuario_logado},
    )


@router.post("/editar")
@requer_autenticacao()
async def post_editar(
    request: Request,
    titulo: str = Form(...),
    logradouro: str = Form(...),
    numero: str = Form(""),
    complemento: str = Form(""),
    bairro: str = Form(...),
    cidade: str = Form(...),
    uf: str = Form(...),
    cep: str = Form(...),
    usuario_logado: Optional[dict] = None,
):
    """Altera dados do endereco do usuario."""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not endereco_limiter.verificar(ip):
        informar_erro(
            request, "Muitas operacoes. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            "/usuario/endereco/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se endereco existe
    endereco_atual = _obter_endereco_usuario(usuario_logado.id)
    if not endereco_atual:
        informar_erro(request, "Endereco nao encontrado.")
        return RedirectResponse(
            "/usuario/endereco/cadastrar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Armazena os dados do formulario para reexibicao em caso de erro
    dados_formulario = {
        "id": endereco_atual.id,
        "titulo": titulo,
        "logradouro": logradouro,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cidade": cidade,
        "uf": uf,
        "cep": cep,
    }

    try:
        # Validar com DTO
        dto = AlterarEnderecoDTO(
            id=endereco_atual.id,
            titulo=titulo,
            logradouro=logradouro,
            numero=numero if numero else None,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
            cep=cep,
        )

        # Atualizar endereco
        endereco_atual.titulo = dto.titulo
        endereco_atual.logradouro = dto.logradouro
        endereco_atual.numero = dto.numero or 0
        endereco_atual.complemento = dto.complemento
        endereco_atual.bairro = dto.bairro
        endereco_atual.cidade = dto.cidade
        endereco_atual.uf = dto.uf
        endereco_atual.cep = dto.cep

        endereco_repo.atualizar(endereco_atual)
        logger.info(f"Endereco ID {endereco_atual.id} alterado por usuario {usuario_logado.id}")

        informar_sucesso(request, "Endereco alterado com sucesso!")
        return RedirectResponse(
            "/usuario/endereco/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    except ValidationError as e:
        dados_formulario["endereco"] = endereco_atual
        raise FormValidationError(
            validation_error=e,
            template_path="perfil/endereco/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="titulo",
        )


@router.post("/excluir")
@requer_autenticacao()
async def excluir(request: Request, usuario_logado: Optional[dict] = None):
    """Exclui o endereco do usuario."""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not endereco_limiter.verificar(ip):
        informar_erro(
            request, "Muitas operacoes. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            "/usuario/endereco/visualizar", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se endereco existe
    endereco = _obter_endereco_usuario(usuario_logado.id)
    if not endereco:
        informar_erro(request, "Endereco nao encontrado.")
        return RedirectResponse(
            "/usuario/endereco/", status_code=status.HTTP_303_SEE_OTHER
        )

    # Tentar excluir
    try:
        if endereco_repo.excluir(endereco.id):
            logger.info(
                f"Endereco (ID: {endereco.id}) excluido por usuario {usuario_logado.id}"
            )
            informar_sucesso(request, "Endereco excluido com sucesso!")
        else:
            informar_erro(request, "Nao foi possivel excluir o endereco.")
    except Exception as e:
        logger.error(f"Erro ao excluir endereco ID {endereco.id}: {e}")
        informar_erro(request, "Nao foi possivel excluir o endereco.")

    return RedirectResponse(
        "/usuario/endereco/", status_code=status.HTTP_303_SEE_OTHER
    )
