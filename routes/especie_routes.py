"""
Rotas para gerenciamento de espécies.
Apenas administradores podem gerenciar espécies.
"""

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import ValidationError

from util.auth_decorator import requer_autenticacao
from util.flash_messages import informar_sucesso, informar_erro
from util.exceptions import FormValidationError
from util.perfis import Perfil

import repo.especie_repo as especie_repo
from dtos.especie_dto import EspecieCriarDTO, EspecieAlterarDTO
from model.especie_model import Especie

router = APIRouter(prefix="/especies")


@router.get("/listar")
@requer_autenticacao([Perfil.ADMIN.value])
async def listar(request: Request, usuario_logado: dict):
    """Lista todas as espécies (apenas admin)."""
    especies = especie_repo.obter_todos()
    return JSONResponse({
        "success": True,
        "data": [
            {
                "id_especie": e.id_especie,
                "nome": e.nome,
                "descricao": e.descricao
            }
            for e in especies
        ]
    })


@router.get("/{id_especie}")
@requer_autenticacao([Perfil.ADMIN.value])
async def obter(request: Request, id_especie: int, usuario_logado: dict):
    """Obtém uma espécie por ID."""
    especie = especie_repo.obter_por_id(id_especie)
    if not especie:
        return JSONResponse(
            {"success": False, "message": "Espécie não encontrada"},
            status_code=404
        )

    return JSONResponse({
        "success": True,
        "data": {
            "id_especie": especie.id_especie,
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
        dto = EspecieCriarDTO(nome=nome, descricao=descricao)

        # Verificar se já existe
        if especie_repo.existe_nome(dto.nome):
            return JSONResponse(
                {"success": False, "message": "Já existe uma espécie com este nome"},
                status_code=400
            )

        # Criar espécie
        especie = Especie(
            id_especie=0,  # Será gerado pelo banco
            nome=dto.nome,
            descricao=dto.descricao
        )

        id_criado = especie_repo.inserir(especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie cadastrada com sucesso",
            "data": {"id_especie": id_criado}
        }, status_code=201)

    except ValidationError as e:
        return JSONResponse(
            {"success": False, "errors": e.errors()},
            status_code=400
        )


@router.put("/{id_especie}")
@requer_autenticacao([Perfil.ADMIN.value])
async def atualizar(
    request: Request,
    id_especie: int,
    usuario_logado: dict,
    nome: str = Form(...),
    descricao: str = Form(...)
):
    """Atualiza uma espécie existente."""
    try:
        # Verificar se existe
        especie_existente = especie_repo.obter_por_id(id_especie)
        if not especie_existente:
            return JSONResponse(
                {"success": False, "message": "Espécie não encontrada"},
                status_code=404
            )

        # Validar dados
        dto = EspecieAlterarDTO(nome=nome, descricao=descricao)

        # Verificar nome duplicado
        if especie_repo.existe_nome(dto.nome, id_excluir=id_especie):
            return JSONResponse(
                {"success": False, "message": "Já existe uma espécie com este nome"},
                status_code=400
            )

        # Atualizar
        especie = Especie(
            id_especie=id_especie,
            nome=dto.nome,
            descricao=dto.descricao
        )

        especie_repo.atualizar(especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie atualizada com sucesso"
        })

    except ValidationError as e:
        return JSONResponse(
            {"success": False, "errors": e.errors()},
            status_code=400
        )


@router.delete("/{id_especie}")
@requer_autenticacao([Perfil.ADMIN.value])
async def excluir(request: Request, id_especie: int, usuario_logado: dict):
    """Exclui uma espécie."""
    try:
        # Verificar se existe
        especie = especie_repo.obter_por_id(id_especie)
        if not especie:
            return JSONResponse(
                {"success": False, "message": "Espécie não encontrada"},
                status_code=404
            )

        # Tentar excluir
        especie_repo.excluir(id_especie)

        return JSONResponse({
            "success": True,
            "message": "Espécie excluída com sucesso"
        })

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=400
        )