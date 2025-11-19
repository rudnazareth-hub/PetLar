
from typing import Optional
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from dtos.especie_dto import CriarEspecieDTO, AlterarEspecieDTO
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
    nome="admin_espécies"
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
    # Busca todas as especies do banco
    especies = especie_repo.obter_todos()

    # Renderiza o template com os dados
    return templates.TemplateResponse(
        "admin/especies/listar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "especies": especies
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
        "admin/espécies/cadastro.html",
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
    Acessível em: POST /admin/espécies/cadastrar
    """
    # Verifica rate limiting
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
        dto = CriarEspecieDTO(nome=nome, descricao=descricao)

        # Verifica se já existe espécie com este nome
        espécie_existente = especie_repo.obter_por_nome(dto.nome)
        if espécie_existente:
            informar_erro(request, "Já existe uma especie com este nome.")
            return RedirectResponse(
                url="/admin/espécies/cadastrar",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # Cria o objeto Espécie
        nova_espécie = Especie(
            nome=dto.nome,
            descricao=dto.descricao
        )

        # Insere no banco de dados
        espécie_inserida = especie_repo.inserir(nova_especie)

        if espécie_inserida:
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
        # Em caso de erro de validação, levanta exception
        # que será capturada pelo handler global
        raise FormValidationError(
            validation_error=e,
            template_path="admin/especies/cadastro.html",
            dados_formulario={"nome": nome, "descricao": descricao},
            campo_padrao="nome"
        )
    

    @router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None
):
    """
    Exibe o formulário de edição de uma espécie.
    Acessível em: GET /admin/espécies/editar/1
    """
    # Busca a espécie pelo ID
    especie = especie_repo.obter_por_id(id)

    if not especie:
        informar_erro(request, "Especie não encontrada.")
        return RedirectResponse(
            url="/admin/espécies/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Renderiza o formulário com os dados da espécie
    return templates.TemplateResponse(
        "admin/especies/editar.html",
        {
            "request": request,
            "usuario_logado": usuario_logado,
            "espécie": espécie
        }
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None,
    nome: str = Form(""),
    descricao: str = Form("")
):
    """
    Processa a edição de uma especie.
    Acessível em: POST /admin/especies/editar/1
    """
    # Verifica rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_especies_limiter.verificar(ip):
        informar_erro(
            request,
            "Muitas operações em pouco tempo. Aguarde um momento e tente novamente."
        )
        return RedirectResponse(
            url=f"/admin/especies/editar/{id}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Busca a espécie atual
    espécie_atual = especie_repo.obter_por_id(id)
    if not espécie_atual:
        informar_erro(request, "Especie não encontrada.")
        return RedirectResponse(
            url="/admin/espécies/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Valida os dados
        dto = AlterarEspecieDTO(nome=nome, descricao=descricao)

        # Se o nome mudou, verifica se não existe outra espécie com o novo nome
        if dto.nome != espécie_atual.nome:
            espécie_existente = especie_repo.obter_por_nome(dto.nome)
            if espécie_existente:
                informar_erro(request, "Já existe uma especie com este nome.")
                return RedirectResponse(
                    url=f"/admin/espécies/editar/{id}",
                    status_code=status.HTTP_303_SEE_OTHER
                )

        # Atualiza os dados da espécie
        espécie_atual.nome = dto.nome
        espécie_atual.descricao = dto.descricao

        # Salva no banco
        if espécie_repo.alterar(espécie_atual):
            informar_sucesso(request, "Espécie alterada com sucesso!")
            return RedirectResponse(
                url="/admin/especies/listar",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            informar_erro(request, "Erro ao alterar espécie.")
            return RedirectResponse(
                url=f"/admin/espécies/editar/{id}",
                status_code=status.HTTP_303_SEE_OTHER
            )

    except ValidationError as e:
        raise FormValidationError(
            validation_error=e,
            template_path="admin/espécies/editar.html",
            dados_formulario={
                "nome": nome,
                "descricao": descricao,
                "id": id
            },
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
    Acessível em: POST /admin/especies/excluir/1
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

    # Busca a espécie
    espécie = especie_repo.obter_por_id(id)
    if not espécie:
        informar_erro(request, "Especie não encontrada.")
        return RedirectResponse(
            url="/admin/especies/listar",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Exclui do banco
    if especie_repo.excluir(id):
        informar_sucesso(request, f"Especie '{especie.nome}' excluída com sucesso!")
    else:
        informar_erro(request, "Erro ao excluir especie.")

    return RedirectResponse(
        url="/admin/especies/listar",
        status_code=status.HTTP_303_SEE_OTHER
    )

