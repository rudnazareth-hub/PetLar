"""
Rotas para solicitações de adoção.
Adotantes criam, Abrigos analisam.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil

import repo.solicitacao_repo as solicitacao_repo
import repo.animal_repo as animal_repo
from model.solicitacao_model import Solicitacao

router = APIRouter(prefix="/solicitacoes")


@router.post("/criar")
@requer_autenticacao([Perfil.ADOTANTE.value])
async def criar_solicitacao(
    request: Request,
    usuario_logado: dict,
    id_animal: int = Form(...),
    observacoes: str = Form("")
):
    """Adotante solicita adoção de um animal."""
    try:
        # Verificar se animal está disponível
        animal = animal_repo.obter_por_id(id_animal)
        if not animal or animal.status != "Disponível":
            return JSONResponse(
                {"success": False, "message": "Animal não disponível"},
                status_code=400
            )

        # Criar solicitação
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=usuario_logado["id"],
            id_animal=id_animal,
            data_solicitacao=None,
            status="Pendente",
            observacoes=observacoes,
            adotante=None,
            animal=None
        )

        id_criado = solicitacao_repo.inserir(solicitacao)

        # Atualizar status do animal
        animal_repo.atualizar_status(id_animal, "Em Processo")

        return JSONResponse({
            "success": True,
            "message": "Solicitação enviada com sucesso!",
            "data": {"id_solicitacao": id_criado}
        }, status_code=201)

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500
        )


@router.get("/minhas")
@requer_autenticacao([Perfil.ADOTANTE.value])
async def listar_minhas(request: Request, usuario_logado: dict):
    """Lista solicitações do adotante logado."""
    solicitacoes = solicitacao_repo.obter_por_adotante(usuario_logado["id"])
    return JSONResponse({
        "success": True,
        "data": solicitacoes
    })


@router.get("/recebidas")
@requer_autenticacao([Perfil.ABRIGO.value])
async def listar_recebidas(request: Request, usuario_logado: dict):
    """Lista solicitações recebidas pelo abrigo."""
    solicitacoes = solicitacao_repo.obter_por_abrigo(usuario_logado["id"])
    return JSONResponse({
        "success": True,
        "data": solicitacoes
    })


@router.put("/{id_solicitacao}/analisar")
@requer_autenticacao([Perfil.ABRIGO.value])
async def analisar_solicitacao(
    request: Request,
    id_solicitacao: int,
    usuario_logado: dict,
    status: str = Form(...),  # Aprovada ou Rejeitada
    resposta: str = Form("")
):
    """Abrigo aprova ou rejeita solicitação."""
    try:
        if status not in ["Aprovada", "Rejeitada"]:
            return JSONResponse(
                {"success": False, "message": "Status inválido"},
                status_code=400
            )

        solicitacao_repo.atualizar_status(id_solicitacao, status, resposta)

        return JSONResponse({
            "success": True,
            "message": f"Solicitação {status.lower()} com sucesso"
        })

    except Exception as e:
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=500
        )