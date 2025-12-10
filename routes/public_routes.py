from typing import Optional

from fastapi import APIRouter, Form, Query, Request, status
from fastapi.responses import RedirectResponse

from repo import animal_repo, especie_repo, raca_repo
from util.template_util import criar_templates
from util.rate_limiter import DynamicRateLimiter, obter_identificador_cliente
from util.flash_messages import informar_erro, informar_sucesso
from util.logger_config import logger
from util.auth_decorator import requer_autenticacao
from util.perfis import Perfil

router = APIRouter()
templates_public = criar_templates()

# Rate limiter para páginas públicas (proteção contra DDoS)
public_limiter = DynamicRateLimiter(
    chave_max="rate_limit_public_max",
    chave_minutos="rate_limit_public_minutos",
    padrao_max=100,
    padrao_minutos=1,
    nome="public_pages",
)


@router.get("/")
async def home(request: Request):
    """
    Rota inicial - Landing Page pública com últimos animais cadastrados
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Obter últimos 12 animais disponíveis
    ultimos_animais = animal_repo.obter_ultimos_cadastrados(12)
    total_disponiveis = animal_repo.contar_disponiveis()

    return templates_public.TemplateResponse(
        "index.html",
        {
            "request": request,
            "ultimos_animais": ultimos_animais,
            "total_disponiveis": total_disponiveis
        }
    )


@router.get("/index")
async def index(request: Request):
    """
    Página pública inicial (Landing Page)
    Sempre exibe a página pública, independentemente de autenticação
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Obter últimos 12 animais disponíveis
    ultimos_animais = animal_repo.obter_ultimos_cadastrados(12)
    total_disponiveis = animal_repo.contar_disponiveis()

    return templates_public.TemplateResponse(
        "index.html",
        {
            "request": request,
            "ultimos_animais": ultimos_animais,
            "total_disponiveis": total_disponiveis
        }
    )


@router.get("/sobre")
async def sobre(request: Request):
    """
    Página "Sobre" com informações do projeto acadêmico
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    return templates_public.TemplateResponse(
        "sobre.html",
        {"request": request}
    )


# =============== ROTAS DE ANIMAIS PUBLICAS ===============

@router.get("/animais")
async def listar_animais(
    request: Request,
    especie: Optional[str] = Query(None),
    raca: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    cidade: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
):
    """
    Página pública de listagem de animais disponíveis para adoção.
    Suporta filtros por espécie, raça, UF e cidade com paginação.
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Converter strings vazias para None e validar inteiros
    especie_id = int(especie) if especie and especie.strip() else None
    raca_id = int(raca) if raca and raca.strip() else None
    uf_valor = uf.strip().upper() if uf and uf.strip() else None
    cidade_valor = cidade.strip() if cidade and cidade.strip() else None

    # Buscar animais com filtros e paginação
    resultado = animal_repo.buscar_disponiveis_com_filtros(
        especie_id=especie_id,
        raca_id=raca_id,
        uf=uf_valor,
        cidade=cidade_valor,
        pagina=pagina,
        por_pagina=12
    )

    # Obter listas para os filtros
    especies = especie_repo.obter_todos()
    racas = raca_repo.obter_todos_com_especies()

    # Lista de UFs para o filtro
    ufs = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]

    # Filtros atuais para manter seleção no formulário
    filtros = {
        "especie": especie_id,
        "raca": raca_id,
        "uf": uf_valor,
        "cidade": cidade_valor or ""
    }

    return templates_public.TemplateResponse(
        "animais/listar.html",
        {
            "request": request,
            "animais": resultado["animais"],
            "especies": especies,
            "racas": racas,
            "ufs": ufs,
            "filtros": filtros,
            "total": resultado["total"],
            "pagina": resultado["pagina"],
            "total_paginas": resultado["total_paginas"]
        }
    )


@router.get("/animais/{id}")
async def detalhes_animal(request: Request, id: int):
    """
    Página pública de detalhes de um animal.
    """
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        logger.warning(f"Rate limit excedido para página pública - IP: {ip}")
        return templates_public.TemplateResponse(
            "errors/429.html",
            {"request": request},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    # Buscar animal
    animal = animal_repo.obter_por_id(id)

    if not animal:
        informar_erro(request, "Animal não encontrado.")
        return RedirectResponse(
            "/animais", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se animal está disponível para exibição pública
    if animal.status not in ['Disponível', 'Reservado']:
        informar_erro(request, "Este animal não está disponível para visualização.")
        return RedirectResponse(
            "/animais", status_code=status.HTTP_303_SEE_OTHER
        )

    return templates_public.TemplateResponse(
        "animais/detalhes.html",
        {
            "request": request,
            "animal": animal
        }
    )


@router.post("/animais/{id}/reservar")
@requer_autenticacao([Perfil.ADOTANTE.value])
async def reservar_animal(
    request: Request,
    id: int,
    usuario_logado: Optional[dict] = None
):
    """
    Reserva um animal para adoção.
    Apenas adotantes logados podem reservar.
    """
    assert usuario_logado is not None

    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        informar_erro(request, "Muitas requisições. Aguarde alguns minutos.")
        return RedirectResponse(
            f"/animais/{id}", status_code=status.HTTP_303_SEE_OTHER
        )

    # Buscar animal
    animal = animal_repo.obter_por_id(id)

    if not animal:
        informar_erro(request, "Animal não encontrado.")
        return RedirectResponse(
            "/animais", status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se animal está disponível
    if animal.status != 'Disponível':
        informar_erro(request, "Este animal não está disponível para adoção.")
        return RedirectResponse(
            f"/animais/{id}", status_code=status.HTTP_303_SEE_OTHER
        )

    # Reservar animal
    if animal_repo.reservar_animal(id, usuario_logado.id):
        logger.info(
            f"Animal ID {id} reservado por adotante {usuario_logado.id}"
        )
        informar_sucesso(
            request,
            f"Parabéns! Você reservou {animal.nome}! "
            "Entre em contato com o abrigo para finalizar a adoção."
        )
    else:
        informar_erro(request, "Não foi possível reservar o animal. Tente novamente.")

    return RedirectResponse(
        f"/animais/{id}", status_code=status.HTTP_303_SEE_OTHER
    )
