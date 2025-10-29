from typing import Optional
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from repo import abrigo_repo, raca_repo, animal_repo, solicitacao_repo, visita_repo
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.exceptions import FormValidationError
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from dtos.animal_dto import CadastrarAnimalDTO, AlterarAnimalDTO, AlterarStatusAnimalDTO
from model.animal_model import Animal


router = APIRouter(prefix="/admin/animais")
templates = criar_templates("templates/admin/animais")

@router.get("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de animal"""
    # Obter raças e abrigos para os selects
    racas = raca_repo.obter_todos_com_especies()
    abrigos = abrigo_repo.obter_todos()

    # Converter para dict para os selects
    racas_dict = {str(r.id): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}
    abrigos_dict = {str(a.id_abrigo): a.responsavel for a in abrigos}

    # Opções de sexo e status
    sexo_opcoes = {"Macho": "Macho", "Fêmea": "Fêmea"}
    status_opcoes = {
        "Disponível": "Disponível",
        "Em Processo": "Em Processo",
        "Adotado": "Adotado",
        "Indisponível": "Indisponível"
    }

    return templates.TemplateResponse(
        "admin/animais/cadastro.html",
        {
            "request": request,
            "racas": racas_dict,
            "abrigos": abrigos_dict,
            "sexo_opcoes": sexo_opcoes,
            "status_opcoes": status_opcoes
        }
    )

@router.get("/visualizar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes completos do animal"""
    animal = animal_repo.obter_por_id_com_relacoes(id)

    if not animal:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter solicitações de adoção relacionadas
    solicitacoes = solicitacao_repo.obter_por_animal(id)

    # Obter visitas agendadas
    visitas = visita_repo.obter_por_animal(id)

    return templates.TemplateResponse(
        "admin/animais/visualizar.html",
        {
            "request": request,
            "animal": animal,
            "solicitacoes": solicitacoes,
            "visitas": visitas
        }
    )

# Rate limiter para operações admin
admin_animais_limiter = RateLimiter(
    max_tentativas=20,  # 20 operações
    janela_minutos=1,   # por minuto
    nome="admin_animais"
)

@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de animal"""
    animal = animal_repo.obter_por_id(id)

    if not animal:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter raças e abrigos para os selects
    racas = raca_repo.obter_todos_com_especies()
    abrigos = abrigo_repo.obter_todos()

    # Converter para dict para os selects
    racas_dict = {str(r.id): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}
    abrigos_dict = {str(a.id_abrigo): a.responsavel for a in abrigos}

    # Opções de sexo e status
    sexo_opcoes = {"Macho": "Macho", "Fêmea": "Fêmea"}
    status_opcoes = {
        "Disponível": "Disponível",
        "Em Processo": "Em Processo",
        "Adotado": "Adotado",
        "Indisponível": "Indisponível"
    }

    # Criar cópia dos dados do animal
    dados_animal = animal.__dict__.copy()

    return templates.TemplateResponse(
        "admin/animais/editar.html",
        {
            "request": request,
            "animal": animal,
            "dados": dados_animal,
            "racas": racas_dict,
            "abrigos": abrigos_dict,
            "sexo_opcoes": sexo_opcoes,
            "status_opcoes": status_opcoes
        }
    )

@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    sexo: str = Form(...),
    id_raca: int = Form(...),
    id_abrigo: int = Form(...),
    data_nascimento: str = Form(None),
    data_entrada: str = Form(None),
    status: str = Form(...),
    observacoes: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de um animal"""
    assert usuario_logado is not None

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not admin_animais_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se animal existe
    animal_atual = animal_repo.obter_por_id(id)
    if not animal_atual:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição em caso de erro
    dados_formulario = {
        "id": id, "nome": nome, "sexo": sexo, "id_raca": id_raca,
        "id_abrigo": id_abrigo, "data_nascimento": data_nascimento,
        "data_entrada": data_entrada, "status": status, "observacoes": observacoes
    }

    try:
        # Validar com DTO
        dto = AlterarAnimalDTO(
            id=id, nome=nome, sexo=sexo, id_raca=id_raca,
            id_abrigo=id_abrigo, data_nascimento=data_nascimento,
            data_entrada=data_entrada, status=status, observacoes=observacoes
        )

        # Verificar se raça existe
        raca = raca_repo.obter_por_id(dto.id_raca)
        if not raca:
            informar_erro(request, "Raça não encontrada")
            return RedirectResponse(f"/admin/animais/editar/{id}", status_code=status.HTTP_303_SEE_OTHER)

        # Verificar se abrigo existe
        abrigo = abrigo_repo.obter_por_id(dto.id_abrigo)
        if not abrigo:
            informar_erro(request, "Abrigo não encontrado")
            return RedirectResponse(f"/admin/animais/editar/{id}", status_code=status.HTTP_303_SEE_OTHER)

        # Atualizar animal
        animal_atual.nome = dto.nome
        animal_atual.sexo = dto.sexo
        animal_atual.id_raca = dto.id_raca
        animal_atual.id_abrigo = dto.id_abrigo
        animal_atual.data_nascimento = dto.data_nascimento
        animal_atual.data_entrada = dto.data_entrada
        animal_atual.status = dto.status
        animal_atual.observacoes = dto.observacoes

        animal_repo.atualizar(animal_atual)
        logger.info(f"Animal ID {id} alterado por admin {usuario_logado['id']}")

        informar_sucesso(request, "Animal alterado com sucesso!")
        return RedirectResponse("/admin/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Recarregar dados para os selects
        racas = raca_repo.obter_todos_com_especies()
        abrigos = abrigo_repo.obter_todos()
        dados_formulario["racas"] = {str(r.id): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}
        dados_formulario["abrigos"] = {str(a.id_abrigo): a.responsavel for a in abrigos}
        dados_formulario["animal"] = animal_atual
        dados_formulario["sexo_opcoes"] = {"Macho": "Macho", "Fêmea": "Fêmea"}
        dados_formulario["status_opcoes"] = {
            "Disponível": "Disponível",
            "Em Processo": "Em Processo",
            "Adotado": "Adotado",
            "Indisponível": "Indisponível"
        }

        raise FormValidationError(
            validation_error=e,
            template_path="admin/animais/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )

@router.post("/alterar-status/{id}")
@requer_autenticacao([Perfil.ADMIN.value])
async def post_alterar_status(
    request: Request,
    id: int,
    status: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """Altera apenas o status do animal"""
    # Implementação similar aos outros POSTs