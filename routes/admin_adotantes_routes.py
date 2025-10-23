from typing import Optional
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.perfis import Perfil
from repo import adotante_repo, usuario_repo
from fastapi import Form
from pydantic import ValidationError
from dtos.adotante_dto import AlterarAdotanteDTO
from model.adotante_model import Adotante
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from repo import solicitacao_repo, adocao_repo

@router.get("/visualizar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos do adotante"""
    adotante = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter solicitações do adotante
    solicitacoes = solicitacao_repo.obter_por_adotante(id)

    # Obter adoções realizadas
    adocoes = adocao_repo.obter_por_adotante(id) if hasattr(adocao_repo, 'obter_por_adotante') else []

    return templates.TemplateResponse(
        "admin/adotantes/visualizar.html",
        {
            "request": request,
            "adotante": adotante,
            "usuario": usuario,
            "solicitacoes": solicitacoes,
            "adocoes": adocoes
        }
    )

# Rate limiter
admin_adotantes_limiter = RateLimiter(
    max_tentativas=10,
    janela_minutos=1,
    nome="admin_adotantes"
)

@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    renda_media: float = Form(...),
    tem_filhos: str = Form(...),
    estado_saude: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de um adotante"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_adotantes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se adotante existe
    adotante_atual = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante_atual or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Converter string para bool
    tem_filhos_bool = tem_filhos.lower() == 'true'

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "id_adotante": id,
        "nome": usuario.nome,
        "email": usuario.email,
        "renda_media": renda_media,
        "tem_filhos": tem_filhos_bool,
        "estado_saude": estado_saude
    }

    try:
        # Validar com DTO
        dto = AlterarAdotanteDTO(
            id_adotante=id,
            renda_media=renda_media,
            tem_filhos=tem_filhos_bool,
            estado_saude=estado_saude
        )

        # Atualizar adotante
        adotante_atualizado = Adotante(
            id_adotante=id,
            renda_media=dto.renda_media,
            tem_filhos=dto.tem_filhos,
            estado_saude=dto.estado_saude
        )

        adotante_repo.atualizar(adotante_atualizado)
        logger.info(f"Adotante {id} alterado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Adotante alterado com sucesso!")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        dados_formulario["adotante"] = adotante_atual
        raise FormValidationError(
            validation_error=e,
            template_path="admin/adotantes/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="renda_media"
        )

router = APIRouter(prefix="/admin/adotantes")
templates = criar_templates("templates/admin/adotantes")

@router.get("/")
@requer_autenticacao([Perfil.ADMIN.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de adotantes"""
    return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os adotantes cadastrados com seus dados de usuário"""
    # Obter todos os usuários com perfil ADOTANTE
    usuarios = usuario_repo.obter_todos()
    adotantes_completos = []

    for usuario in usuarios:
        if usuario.perfil == Perfil.ADOTANTE.value:
            adotante = adotante_repo.obter_por_id(usuario.id)
            if adotante:
                adotantes_completos.append({
                    'id_adotante': adotante.id_adotante,
                    'nome': usuario.nome,
                    'email': usuario.email,
                    'telefone': usuario.telefone,
                    'renda_media': adotante.renda_media,
                    'tem_filhos': adotante.tem_filhos,
                    'estado_saude': adotante.estado_saude
                })

    return templates.TemplateResponse(
        "admin/adotantes/listar.html",
        {"request": request, "adotantes": adotantes_completos}
    )

@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de adotante"""
    adotante = adotante_repo.obter_por_id(id)
    usuario = usuario_repo.obter_por_id(id)

    if not adotante or not usuario:
        informar_erro(request, "Adotante não encontrado")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    dados = {
        'id_adotante': adotante.id_adotante,
        'nome': usuario.nome,
        'email': usuario.email,
        'renda_media': adotante.renda_media,
        'tem_filhos': adotante.tem_filhos,
        'estado_saude': adotante.estado_saude
    }

    return templates.TemplateResponse(
        "admin/adotantes/editar.html",
        {
            "request": request,
            "adotante": adotante,
            "dados": dados
        }
    )