import json
from pathlib import Path
from repo import usuario_repo
from model.usuario_model import Usuario
from util.security import criar_hash_senha
from util.logger_config import logger

def carregar_usuarios_seed():
    """Carrega usuários do arquivo JSON seed"""
    arquivo = Path("data/usuarios_seed.json")

    if not arquivo.exists():
        logger.warning("Arquivo de seed não encontrado")
        return

    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    for user_data in dados.get("usuarios", []):
        # Verificar se já existe
        if usuario_repo.obter_por_email(user_data["email"]):
            logger.info(f"Usuário {user_data['email']} já existe")
            continue

        # Criar usuário
        usuario = Usuario(
            id=0,
            nome=user_data["nome"],
            email=user_data["email"],
            senha=criar_hash_senha(user_data["senha"]),
            perfil=user_data["perfil"]
        )

        usuario_repo.inserir(usuario)
        logger.info(f"Usuário {user_data['email']} criado")

def inicializar_dados():
    """Inicializa todos os dados seed"""
    logger.info("Iniciando carga de dados seed...")
    carregar_usuarios_seed()
    logger.info("Dados seed carregados com sucesso!")
