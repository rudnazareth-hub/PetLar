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

# Rate limiter para operações admin
admin_adotantes_limiter = RateLimiter(
    max_tentativas=20,  # 20 operações
    janela_minutos=1,   # por minuto
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

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de adotante"""
    return templates.TemplateResponse(
        "admin/adotantes/cadastro.html",
        {"request": request}
    )

@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...),
    renda_media: float = Form(...),
    tem_filhos: str = Form(...),
    estado_saude: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Cadastra um novo adotante"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_adotantes_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "nome": nome, "email": email, "renda_media": renda_media,
        "tem_filhos": tem_filhos, "estado_saude": estado_saude
    }

    try:
        # Validar senhas
        if senha != confirmar_senha:
            informar_erro(request, "As senhas não coincidem")
            return templates.TemplateResponse(
                "admin/adotantes/cadastro.html",
                {"request": request, "dados": dados_formulario}
            )

        # Validar tamanho da senha
        if len(senha) < 6:
            informar_erro(request, "A senha deve ter no mínimo 6 caracteres")
            return templates.TemplateResponse(
                "admin/adotantes/cadastro.html",
                {"request": request, "dados": dados_formulario}
            )

        # Verificar se email já existe
        usuario_existente = usuario_repo.obter_por_email(email)
        if usuario_existente:
            informar_erro(request, f"Já existe um usuário com o email '{email}'")
            return templates.TemplateResponse(
                "admin/adotantes/cadastro.html",
                {"request": request, "dados": dados_formulario}
            )

        # Importar Usuario model e hash de senha
        from model.usuario_model import Usuario
        from util.security import gerar_hash_senha

        # Criar usuário
        usuario = Usuario(
            id=0,
            nome=nome,
            email=email,
            senha=gerar_hash_senha(senha),
            perfil=Perfil.ADOTANTE.value
        )
        id_usuario = usuario_repo.inserir(usuario)

        # Criar adotante
        adotante = Adotante(
            id_adotante=id_usuario,
            renda_media=renda_media,
            tem_filhos=(tem_filhos.lower() == 'true'),
            estado_saude=estado_saude
        )
        adotante_repo.inserir(adotante)

        logger.info(f"Adotante '{nome}' (ID: {id_usuario}) cadastrado por admin {usuario_logado['id']}")
        informar_sucesso(request, f"Adotante '{nome}' cadastrado com sucesso!")
        return RedirectResponse("/admin/adotantes/listar", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Erro ao cadastrar adotante: {str(e)}")
        informar_erro(request, "Erro ao cadastrar adotante. Verifique os dados e tente novamente.")
        return templates.TemplateResponse(
            "admin/adotantes/cadastro.html",
            {"request": request, "dados": dados_formulario}
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