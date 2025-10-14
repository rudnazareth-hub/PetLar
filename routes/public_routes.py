from fastapi import APIRouter, Request
from util.template_util import criar_templates
from util.auth_decorator import obter_usuario_logado

router = APIRouter()
templates_home = criar_templates("templates")


@router.get("/")
async def home(request: Request):
    """
    Rota inicial:
    - Se usuário estiver logado: exibe dashboard (home.html)
    - Se não estiver logado: exibe landing page pública (index.html)
    """
    usuario_logado = obter_usuario_logado(request)

    if usuario_logado:
        # Usuário autenticado - Dashboard
        return templates_home.TemplateResponse(
            "home.html",
            {
                "request": request,
                "usuario": usuario_logado
            }
        )
    else:
        # Usuário não autenticado - Landing Page
        return templates_home.TemplateResponse(
            "index.html",
            {"request": request}
        )
