from jinja2 import Environment, FileSystemLoader
from fastapi.templating import Jinja2Templates
from util.flash_messages import obter_mensagens

def criar_templates(pasta: str):
    """Cria Jinja2Templates com funções globais customizadas"""
    env = Environment(loader=FileSystemLoader(pasta))

    # Adicionar função global para obter mensagens
    env.globals['obter_mensagens'] = obter_mensagens

    templates = Jinja2Templates(directory=pasta, env=env)
    return templates
