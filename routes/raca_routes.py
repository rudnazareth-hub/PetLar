from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import ValidationError

from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.exceptions import FormValidationError
from util.perfis import Perfil

import repo.raca_repo as raca_repo
from dtos.raca_dto import RacaCriarDTO, RacaAlterarDTO
from model.raca_model import Raca

router = APIRouter(prefix="/racas")

# id_raca: int
# id_especie: int
# nome: str
# descricao: str
# temperamento: str
# expectativa_de_vida: str
# porte: str 

@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: dict):
    """Lista todas as racas (apenas admin)."""
    racas = raca_repo.obter_todos()
    return JSONResponse({
        "success": True,
        "data": [
            {
                "id_raca": e.id_raca,
                "id_especie": e.id_especie,
                "nome": e.nome,
                "descricao": e.descricao,
                "temperamento": e.temperamento,
                "expectativa_de_vida": e.expectativa_de_vida,
                "porte": e.porte
            }
            for e in racas
        ]
    })


@router.get("/{id_raca}")
@requer_autenticacao([Perfil.ADMIN.value])
async def obter(request: Request, id_raca: int, usuario_logado: dict):
    """Obtém uma espécie por ID."""
    especie = raca_repo.obter_por_id(id_raca)
    if not especie:
        return JSONResponse(
            {"success": False, "message": "Espécie não encontrada"},
            status_code=404
        )

    return JSONResponse({
        "success": True,
        "data": {
            "id_raca": especie.id_raca,
            "nome": especie.nome,
            "descricao": especie.descricao
            
        }
    })


@router.post("/cadastrar")
@requer_autenticacao([Perfil.ADMIN.value])
async def cadastrar(
    request: Request,
    usuario_logado: dict,
    nome: str = Form(...),
    descricao: str = Form(...)
):
    """Cadastra uma nova espécie."""
    try:
        # Validar dados
        dto = RacaCriarDTO(nome=nome, descricao=descricao)

        # Verificar se já existe
        if raca_repo.existe_nome(dto.nome):
            return JSONResponse(
                {"success": False, "message": "Já existe uma espécie com este nome"},
                status_code=400
            )

        # Criar espécie
        especie = Raca(
            id_raca=0,  # Será gerado pelo banco
            nome=dto.nome,
            descricao=dto.descricao
        )

        id_criado = raca_repo.inserir(especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie cadastrada com sucesso",
            "data": {"id_raca": id_criado}
        }, status_code=201)

    except ValidationError as e:
        return JSONResponse(
            {"success": False, "errors": e.errors()},
            status_code=400
        )


@router.put("/{id_raca}")
@requer_autenticacao([Perfil.ADMIN.value])
async def atualizar(
    request: Request,
    id_raca: int,
    usuario_logado: dict,
    nome: str = Form(...),
    descricao: str = Form(...)
):
    """Atualiza uma espécie existente."""
    try:
        # Verificar se existe
        raca_existente = raca_repo.obter_por_id(id_raca)
        if not raca_existente:
            return JSONResponse(
                {"success": False, "message": "Espécie não encontrada"},
                status_code=404
            )

        # Validar dados
        dto = RacaAlterarDTO(nome=nome, descricao=descricao)

        # Verificar nome duplicado
        if raca_repo.existe_nome(dto.nome, id_excluir=id_raca):
            return JSONResponse(
                {"success": False, "message": "Já existe uma espécie com este nome"},
                status_code=400
            )

        # Atualizar
        especie = Raca(
            id_raca=id_raca,
            nome=dto.nome,
            descricao=dto.descricao
        )

        raca_repo.atualizar(especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie atualizada com sucesso"
        })

    except ValidationError as e:
        return JSONResponse(
            {"success": False, "errors": e.errors()},
            status_code=400
        )


@router.delete("/{id_raca}")
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir(request: Request, id_raca: int, usuario_logado: dict):
    """Exclui uma espécie."""
    try:
        # Verificar se existe
        especie = raca_repo.obter_por_id(id_raca)
        if not especie:
            return JSONResponse(
                {"success": False, "message": "Espécie não encontrada"},
                status_code=404
            )

        # Tentar excluir
        raca_repo.excluir(id_raca)

        return JSONResponse({
            "success": True,
            "message": "Espécie excluída com sucesso"
        })

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=400
        )