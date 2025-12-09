"""Rotas para gerenciamento de animais por abrigos."""

import base64
import io
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, Request, UploadFile, File, status
from fastapi.responses import RedirectResponse
from PIL import Image, UnidentifiedImageError
from pydantic import ValidationError

from dtos.animal_dto import CadastrarAnimalDTO, AlterarAnimalDTO
from model.animal_model import Animal
from repo import animal_repo, raca_repo, abrigo_repo, adocao_repo
from util.auth_decorator import requer_autenticacao
from util.exceptions import FormValidationError
from util.flash_messages import informar_erro, informar_sucesso
from util.logger_config import logger
from util.perfis import Perfil
from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.template_util import criar_templates

# Configuração do router e templates
router = APIRouter(prefix="/abrigo/animais")
templates = criar_templates()

# Pasta para fotos de animais
PASTA_FOTOS_ANIMAIS = Path("static/img/animais")
PASTA_FOTOS_ANIMAIS.mkdir(parents=True, exist_ok=True)

# Rate limiter para operações do abrigo
abrigo_animais_limiter = RateLimiter(
    max_tentativas=30,
    janela_minutos=1,
    nome="abrigo_animais"
)


def _obter_id_abrigo(usuario_logado) -> Optional[int]:
    """Obtém o ID do abrigo do usuário logado."""
    abrigo = abrigo_repo.obter_por_usuario(usuario_logado.id)
    return abrigo.id_abrigo if abrigo else None


def _salvar_foto_animal(arquivo: UploadFile, id_animal: int) -> Optional[str]:
    """
    Salva a foto do animal.

    Args:
        arquivo: Arquivo de upload
        id_animal: ID do animal

    Returns:
        Caminho da foto salva ou None em caso de erro
    """
    try:
        # Ler conteúdo do arquivo
        conteudo = arquivo.file.read()
        if not conteudo:
            return None

        # Abrir imagem
        imagem = Image.open(io.BytesIO(conteudo))

        # Converter para RGB se necessário
        if imagem.mode in ("RGBA", "LA", "P"):
            fundo = Image.new("RGB", imagem.size, (255, 255, 255))
            if imagem.mode == "P":
                imagem = imagem.convert("RGBA")
            fundo.paste(imagem, mask=imagem.split()[-1] if "A" in imagem.mode else None)
            imagem = fundo
        elif imagem.mode != "RGB":
            imagem = imagem.convert("RGB")

        # Redimensionar se muito grande
        tamanho_max = 800
        if imagem.width > tamanho_max or imagem.height > tamanho_max:
            imagem.thumbnail((tamanho_max, tamanho_max), Image.Resampling.LANCZOS)

        # Salvar
        nome_arquivo = f"{id_animal:06d}.jpg"
        caminho = PASTA_FOTOS_ANIMAIS / nome_arquivo
        imagem.save(caminho, format="JPEG", quality=85, optimize=True)

        return f"/static/img/animais/{nome_arquivo}"

    except (OSError, UnidentifiedImageError) as e:
        logger.error(f"Erro ao salvar foto do animal {id_animal}: {e}")
        return None


@router.get("/")
@requer_autenticacao([Perfil.ABRIGO.value])
async def index(request: Request, usuario_logado: Optional[dict] = None):
    """Redireciona para lista de animais"""
    return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/listar")
@requer_autenticacao([Perfil.ABRIGO.value])
async def listar(request: Request, usuario_logado: Optional[dict] = None):
    """Lista todos os animais do abrigo"""
    id_abrigo = _obter_id_abrigo(usuario_logado)

    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    animais = animal_repo.obter_por_abrigo(id_abrigo)
    total = animal_repo.contar_por_abrigo(id_abrigo)

    return templates.TemplateResponse(
        "abrigo/animais/listar.html",
        {
            "request": request,
            "animais": animais,
            "total": total,
            "usuario_logado": usuario_logado
        }
    )


@router.get("/cadastrar")
@requer_autenticacao([Perfil.ABRIGO.value])
async def get_cadastrar(request: Request, usuario_logado: Optional[dict] = None):
    """Exibe formulário de cadastro de animal"""
    id_abrigo = _obter_id_abrigo(usuario_logado)

    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Obter raças para o select
    racas = raca_repo.obter_todos_com_especies()
    racas_dict = {str(r.id): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}

    # Opções de sexo
    sexo_opcoes = {"Macho": "Macho", "Fêmea": "Fêmea"}

    return templates.TemplateResponse(
        "abrigo/animais/cadastro.html",
        {
            "request": request,
            "racas": racas_dict,
            "sexo_opcoes": sexo_opcoes,
            "usuario_logado": usuario_logado
        }
    )


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ABRIGO.value])
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    sexo: str = Form(...),
    id_raca: int = Form(...),
    data_nascimento: str = Form(None),
    data_entrada: str = Form(None),
    observacoes: str = Form(None),
    foto: UploadFile = File(None),
    usuario_logado: Optional[dict] = None
):
    """Cadastra um novo animal para o abrigo"""
    assert usuario_logado is not None

    id_abrigo = _obter_id_abrigo(usuario_logado)
    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not abrigo_animais_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário para reexibição
    dados_formulario = {
        "nome": nome, "sexo": sexo, "id_raca": id_raca,
        "data_nascimento": data_nascimento, "data_entrada": data_entrada,
        "observacoes": observacoes
    }

    try:
        # Validar com DTO
        dto = CadastrarAnimalDTO(
            nome=nome, sexo=sexo, id_raca=id_raca, id_abrigo=id_abrigo,
            data_nascimento=data_nascimento, data_entrada=data_entrada,
            observacoes=observacoes, status="Disponível"
        )

        # Verificar se raça existe
        raca = raca_repo.obter_por_id(dto.id_raca)
        if not raca:
            informar_erro(request, "Raça não encontrada")
            return RedirectResponse("/abrigo/animais/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

        # Criar animal
        animal = Animal(
            id=0,
            id_raca=dto.id_raca,
            id_abrigo=id_abrigo,
            nome=dto.nome,
            sexo=dto.sexo,
            data_nascimento=dto.data_nascimento,
            data_entrada=dto.data_entrada,
            observacoes=dto.observacoes,
            status="Disponível"
        )

        animal_id = animal_repo.inserir(animal)

        # Salvar foto se fornecida
        if foto and foto.filename:
            caminho_foto = _salvar_foto_animal(foto, animal_id)
            if caminho_foto:
                animal_repo.atualizar_foto(animal_id, caminho_foto)

        logger.info(f"Animal '{dto.nome}' (ID: {animal_id}) cadastrado pelo abrigo {id_abrigo}")
        informar_sucesso(request, f"Animal '{dto.nome}' cadastrado com sucesso!")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Recarregar raças
        racas = raca_repo.obter_todos_com_especies()
        dados_formulario["racas"] = {str(r.id): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}
        dados_formulario["sexo_opcoes"] = {"Macho": "Macho", "Fêmea": "Fêmea"}

        raise FormValidationError(
            validation_error=e,
            template_path="abrigo/animais/cadastro.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )


@router.get("/editar/{id}")
@requer_autenticacao([Perfil.ABRIGO.value])
async def get_editar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário de edição de animal"""
    id_abrigo = _obter_id_abrigo(usuario_logado)

    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se animal pertence ao abrigo
    animal = animal_repo.obter_por_id(id)
    if not animal:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    if animal.id_abrigo != id_abrigo:
        informar_erro(request, "Você não tem permissão para editar este animal")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Obter raças
    racas = raca_repo.obter_todos_com_especies()
    racas_dict = {str(r.id): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}

    # Opções
    sexo_opcoes = {"Macho": "Macho", "Fêmea": "Fêmea"}
    status_opcoes = {
        "Disponível": "Disponível",
        "Reservado": "Reservado",
        "Adotado": "Adotado",
        "Indisponível": "Indisponível"
    }

    dados_animal = animal.__dict__.copy()

    return templates.TemplateResponse(
        "abrigo/animais/editar.html",
        {
            "request": request,
            "animal": animal,
            "dados": dados_animal,
            "racas": racas_dict,
            "sexo_opcoes": sexo_opcoes,
            "status_opcoes": status_opcoes,
            "usuario_logado": usuario_logado
        }
    )


@router.post("/editar/{id}")
@requer_autenticacao([Perfil.ABRIGO.value])
async def post_editar(
    request: Request,
    id: int,
    nome: str = Form(...),
    sexo: str = Form(...),
    id_raca: int = Form(...),
    data_nascimento: str = Form(None),
    data_entrada: str = Form(None),
    observacoes: str = Form(None),
    status_animal: str = Form(..., alias="status"),
    foto: UploadFile = File(None),
    usuario_logado: Optional[dict] = None
):
    """Altera dados de um animal"""
    assert usuario_logado is not None

    id_abrigo = _obter_id_abrigo(usuario_logado)
    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not abrigo_animais_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se animal existe e pertence ao abrigo
    animal_atual = animal_repo.obter_por_id(id)
    if not animal_atual:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    if animal_atual.id_abrigo != id_abrigo:
        informar_erro(request, "Você não tem permissão para editar este animal")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Dados do formulário
    dados_formulario = {
        "id": id, "nome": nome, "sexo": sexo, "id_raca": id_raca,
        "data_nascimento": data_nascimento, "data_entrada": data_entrada,
        "observacoes": observacoes, "status": status_animal
    }

    try:
        # Validar com DTO
        dto = AlterarAnimalDTO(
            id=id, nome=nome, sexo=sexo, id_raca=id_raca, id_abrigo=id_abrigo,
            data_nascimento=data_nascimento, data_entrada=data_entrada,
            observacoes=observacoes, status=status_animal
        )

        # Atualizar animal
        animal_atual.nome = dto.nome
        animal_atual.sexo = dto.sexo
        animal_atual.id_raca = dto.id_raca
        animal_atual.data_nascimento = dto.data_nascimento
        animal_atual.data_entrada = dto.data_entrada
        animal_atual.observacoes = dto.observacoes
        animal_atual.status = dto.status

        # Salvar foto se fornecida
        if foto and foto.filename:
            caminho_foto = _salvar_foto_animal(foto, id)
            if caminho_foto:
                animal_atual.foto = caminho_foto

        animal_repo.atualizar_completo(animal_atual)
        logger.info(f"Animal ID {id} alterado pelo abrigo {id_abrigo}")

        informar_sucesso(request, f"Animal '{dto.nome}' alterado com sucesso!")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        racas = raca_repo.obter_todos_com_especies()
        dados_formulario["racas"] = {str(r.id): f"{r.nome} ({r.especie.nome if r.especie else 'N/A'})" for r in racas}
        dados_formulario["sexo_opcoes"] = {"Macho": "Macho", "Fêmea": "Fêmea"}
        dados_formulario["status_opcoes"] = {
            "Disponível": "Disponível", "Reservado": "Reservado",
            "Adotado": "Adotado", "Indisponível": "Indisponível"
        }
        dados_formulario["animal"] = animal_atual

        raise FormValidationError(
            validation_error=e,
            template_path="abrigo/animais/editar.html",
            dados_formulario=dados_formulario,
            campo_padrao="nome"
        )


@router.get("/visualizar/{id}")
@requer_autenticacao([Perfil.ABRIGO.value])
async def visualizar(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe detalhes do animal"""
    id_abrigo = _obter_id_abrigo(usuario_logado)

    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    animal = animal_repo.obter_por_id_com_relacoes(id)
    if not animal:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    if animal.id_abrigo != id_abrigo:
        informar_erro(request, "Você não tem permissão para visualizar este animal")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Se animal está reservado, obter dados do adotante
    adotante_info = None
    if animal.status == "Reservado" and animal.id_adotante_reserva:
        dados = animal_repo.obter_por_id_com_adotante(id)
        if dados:
            adotante_info = {
                "nome": dados.get("adotante_nome"),
                "email": dados.get("adotante_email"),
                "telefone": dados.get("adotante_telefone")
            }

    return templates.TemplateResponse(
        "abrigo/animais/visualizar.html",
        {
            "request": request,
            "animal": animal,
            "adotante_info": adotante_info,
            "usuario_logado": usuario_logado
        }
    )


@router.post("/excluir/{id}")
@requer_autenticacao([Perfil.ABRIGO.value])
async def excluir(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exclui um animal"""
    assert usuario_logado is not None

    id_abrigo = _obter_id_abrigo(usuario_logado)
    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not abrigo_animais_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    animal = animal_repo.obter_por_id(id)
    if not animal:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    if animal.id_abrigo != id_abrigo:
        informar_erro(request, "Você não tem permissão para excluir este animal")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se animal pode ser excluído (não pode estar adotado)
    if animal.status == "Adotado":
        informar_erro(request, "Não é possível excluir um animal que já foi adotado.")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        if animal_repo.excluir(id):
            logger.info(f"Animal '{animal.nome}' (ID: {id}) excluído pelo abrigo {id_abrigo}")
            informar_sucesso(request, f"Animal '{animal.nome}' excluído com sucesso!")
        else:
            informar_erro(request, "Não foi possível excluir o animal.")
    except Exception as e:
        logger.error(f"Erro ao excluir animal ID {id}: {e}")
        informar_erro(request, "Erro ao excluir o animal. Tente novamente.")

    return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)


# === Rotas para gestão de reservas ===

@router.get("/reservados")
@requer_autenticacao([Perfil.ABRIGO.value])
async def listar_reservados(request: Request, usuario_logado: Optional[dict] = None):
    """Lista animais reservados aguardando conclusão da adoção"""
    id_abrigo = _obter_id_abrigo(usuario_logado)

    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    reservados = animal_repo.obter_reservados_por_abrigo(id_abrigo)

    return templates.TemplateResponse(
        "abrigo/animais/reservados.html",
        {
            "request": request,
            "reservados": reservados,
            "total": len(reservados),
            "usuario_logado": usuario_logado
        }
    )


@router.get("/{id}/concluir-adocao")
@requer_autenticacao([Perfil.ABRIGO.value])
async def get_concluir_adocao(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Exibe formulário para conclusão de adoção"""
    id_abrigo = _obter_id_abrigo(usuario_logado)

    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Obter animal com dados do adotante
    dados = animal_repo.obter_por_id_com_adotante(id)
    if not dados:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    animal = dados["animal"]

    if animal.id_abrigo != id_abrigo:
        informar_erro(request, "Você não tem permissão para gerenciar este animal")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    if animal.status != "Reservado":
        informar_erro(request, "Este animal não está reservado")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "abrigo/animais/concluir_adocao.html",
        {
            "request": request,
            "animal": animal,
            "adotante_nome": dados.get("adotante_nome"),
            "adotante_email": dados.get("adotante_email"),
            "adotante_telefone": dados.get("adotante_telefone"),
            "adotante_id": dados.get("adotante_id"),
            "usuario_logado": usuario_logado
        }
    )


@router.post("/{id}/concluir-adocao")
@requer_autenticacao([Perfil.ABRIGO.value])
async def post_concluir_adocao(
    request: Request,
    id: int,
    observacoes: str = Form(None),
    usuario_logado: Optional[dict] = None
):
    """Conclui a adoção de um animal"""
    assert usuario_logado is not None

    id_abrigo = _obter_id_abrigo(usuario_logado)
    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not abrigo_animais_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    # Obter animal com dados do adotante
    dados = animal_repo.obter_por_id_com_adotante(id)
    if not dados:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    animal = dados["animal"]

    if animal.id_abrigo != id_abrigo:
        informar_erro(request, "Você não tem permissão para gerenciar este animal")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    if animal.status != "Reservado":
        informar_erro(request, "Este animal não está reservado")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    id_adotante = dados.get("adotante_id")
    if not id_adotante:
        informar_erro(request, "Adotante não encontrado para este animal")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    try:
        # 1. Criar registro de adoção
        adocao_repo.inserir(id_adotante, id, observacoes)

        # 2. Atualizar status do animal para Adotado
        animal_repo.concluir_adocao(id)

        logger.info(f"Adoção do animal {id} concluída pelo abrigo {id_abrigo}")
        informar_sucesso(request, f"Adoção do animal '{animal.nome}' concluída com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao concluir adoção do animal {id}: {e}")
        informar_erro(request, "Erro ao concluir a adoção. Tente novamente.")

    return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{id}/cancelar-reserva")
@requer_autenticacao([Perfil.ABRIGO.value])
async def cancelar_reserva(request: Request, id: int, usuario_logado: Optional[dict] = None):
    """Cancela a reserva de um animal"""
    assert usuario_logado is not None

    id_abrigo = _obter_id_abrigo(usuario_logado)
    if not id_abrigo:
        informar_erro(request, "Abrigo não encontrado para este usuário.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Rate limiting
    ip = obter_identificador_cliente(request)
    if not abrigo_animais_limiter.verificar(ip):
        informar_erro(request, "Muitas operações. Aguarde um momento e tente novamente.")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    animal = animal_repo.obter_por_id(id)
    if not animal:
        informar_erro(request, "Animal não encontrado")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    if animal.id_abrigo != id_abrigo:
        informar_erro(request, "Você não tem permissão para gerenciar este animal")
        return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)

    if animal.status != "Reservado":
        informar_erro(request, "Este animal não está reservado")
        return RedirectResponse("/abrigo/animais/listar", status_code=status.HTTP_303_SEE_OTHER)

    try:
        animal_repo.cancelar_reserva(id)
        logger.info(f"Reserva do animal {id} cancelada pelo abrigo {id_abrigo}")
        informar_sucesso(request, f"Reserva do animal '{animal.nome}' cancelada com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao cancelar reserva do animal {id}: {e}")
        informar_erro(request, "Erro ao cancelar a reserva. Tente novamente.")

    return RedirectResponse("/abrigo/animais/reservados", status_code=status.HTTP_303_SEE_OTHER)
