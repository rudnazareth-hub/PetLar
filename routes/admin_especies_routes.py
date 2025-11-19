from typing import Optional
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.especie_dto import CriarEspécieDTO, AlterarEspecieDTO
from model.especie_model import Especie
from repo import especie_repo
from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.exceptions import FormValidationError
from util.perfis import Perfil
from util.template_util import criar_templates

# Configura o roteador com prefixo /admin/espécies
router = APIRouter(prefix="/admin/espécies")

# Configura os templates HTML com as funções globais necessárias (csrf_input, etc.)
templates = criar_templates("templates")

# Rate Limiter: máximo 10 operações por minuto
admin_espécies_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_especies"
)

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona a raiz para /listar"""
    return RedirectResponse(
        url="/admin/especies/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """
    Lista todas as especies.
    Acessível em: GET /admin/especies/listar
    """
    
    especies = especie_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "espécies": especies
        }
    )

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """
    Exibe o formulário de cadastro.
    Acessível em: GET /admin/especies/cadastrar
    """
    return templates.TemplateResponse(
        "admin/especies/cadastro.html",
        {
            "request": request,
            "usuario_logado": usuario_logado
        }
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    usuario_logado: Optional[dict] = None,
    nome: str = Form(""),
    descricao: str = Form("")
):
    """
    Processa o cadastro de uma nova especie.
    Acessível em: POST /admin/especies/cadastrar
    """
    
    ip = obter_identificador_cliente(request)
    if not admin_espécies_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/admin/especies/cadastrar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Valida os dados com o DTO
        dto = CriarEspécieDTO(nome=nome, descricao=descricao)

        # Verifica se já existe espécie com este nome
        especie_existente = especie_repo.obter_por_nome(dto.nome)
        if especie_existente:
            informar_erro(request, "Já existe uma especie com este nome.")
            return RedirectResponse(
                url="/admin/especies/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # Cria o objeto Espécie
        nova_especie = Especie(
            nome=dto.nome,
            descricao=dto.descricao
        )

        # Insere no banco de dados
        especie_inserida = especie_repo.inserir(nova_especie)

        if especie_inserida:
            informar_sucesso(request, "Especie cadastrada com sucesso!")
            return RedirectResponse(
                url="/admin/especies/listar",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao cadastrar especie.")
            return RedirectResponse(
                url="/admin/especies/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER
            )

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/cadastro.html",
            dados_formulario={"nome": nome, "descricao": descricao},
            campo_padrao="nome"
        )
    
@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_excluir(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None
):
    """
    Exclui uma espécie.
    Acessível em: POST /admin/espécies/excluir/1
    """
    # Verifica rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_espécies_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url="/admin/especies/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

   
    espécie = especie_repo.obter_por_id(id)
    if not espécie:
        informar_erro(request, "Espécie não encontrada.")
        return RedirectResponse(
            url="/admin/espécies/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

   
    if especie_repo.excluir(id):
        informar_sucesso(request, f"Especie '{especie.nome}' excluída com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir especie.")

    return RedirectResponse(
        url="/admin/especies/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )
