from fastapi import APIRouter, Request
from util.template_util import criar_templates

router = APIRouter(prefix="/examples")
templates_home = criar_templates("templates")


@router.get("")
async def home(request: Request):
    """
    Página inicial de exemplos
    """
    return templates_home.TemplateResponse(
        "examples/index.html",
        {"request": request}
    )


@router.get("/form-fields")
async def form_fields_demo(request: Request):
    """
    Página de demonstração da macro de campos de formulário
    """
    return templates_home.TemplateResponse(
        "examples/form_fields_demo.html",
        {"request": request}
    )


@router.get("/cards-grid")
async def cards_grid_demo(request: Request):
    """
    Página de demonstração de grid de cards responsivo
    """
    return templates_home.TemplateResponse(
        "examples/cards_grid.html",
        {"request": request}
    )


@router.get("/bootswatch")
async def bootswatch_demo(request: Request):
    """
    Página de demonstração de temas Bootswatch
    """
    return templates_home.TemplateResponse(
        "examples/bootswatch.html",
        {"request": request}
    )


@router.get("/product-detail")
async def product_detail_demo(request: Request):
    """
    Página de demonstração de detalhes de produto e-commerce
    """
    return templates_home.TemplateResponse(
        "examples/product_detail.html",
        {"request": request}
    )


@router.get("/service-detail")
async def service_detail_demo(request: Request):
    """
    Página de demonstração de detalhes de serviço profissional
    """
    return templates_home.TemplateResponse(
        "examples/service_detail.html",
        {"request": request}
    )


@router.get("/profile-detail")
async def profile_detail_demo(request: Request):
    """
    Página de demonstração de perfil de pessoa
    """
    return templates_home.TemplateResponse(
        "examples/profile_detail.html",
        {"request": request}
    )


@router.get("/property-detail")
async def property_detail_demo(request: Request):
    """
    Página de demonstração de detalhes de imóvel
    """
    return templates_home.TemplateResponse(
        "examples/property_detail.html",
        {"request": request}
    )
