import json
from pathlib import Path
from repo import usuario_repo
from model.usuario_model import Usuario
from util.security import criar_hash_senha
from util.logger_config import logger
from util.perfis import Perfil

def carregar_usuarios_seed():
    """Carrega usuários do arquivo JSON seed"""
    arquivo = Path("data/usuarios_seed.json")

    if not arquivo.exists():
        logger.warning(f"Arquivo de seed não encontrado: {arquivo.absolute()}")
        return

    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo de seed: {e}")
        return

    usuarios_criados = 0
    usuarios_existentes = 0
    usuarios_com_erro = 0

    for user_data in dados.get("usuarios", []):
        try:
            email = user_data.get("email")
            if not email:
                logger.warning("Usuário sem email no arquivo seed, ignorando")
                continue

            # Verificar se já existe
            if usuario_repo.obter_por_email(email):
                logger.info(f"Usuário {email} já existe no banco")
                usuarios_existentes += 1
                continue

            # Obter e validar perfil do JSON
            perfil_json = user_data.get("perfil", Perfil.CLIENTE.value)

            # Validar que o perfil é válido
            if not Perfil.existe(perfil_json):
                logger.warning(
                    f"Perfil inválido '{perfil_json}' para usuário {email}. "
                    f"Usando perfil padrão: {Perfil.CLIENTE.value}"
                )
                perfil_json = Perfil.CLIENTE.value

            # Criar usuário
            usuario = Usuario(
                id=0,
                nome=user_data["nome"],
                email=email,
                senha=criar_hash_senha(user_data["senha"]),
                perfil=perfil_json  # Usa Enum Perfil validado
            )

            usuario_id = usuario_repo.inserir(usuario)
            if usuario_id:
                logger.info(f"✓ Usuário {email} criado com sucesso (ID: {usuario_id})")
                usuarios_criados += 1
            else:
                logger.error(f"✗ Falha ao inserir usuário {email} no banco")
                usuarios_com_erro += 1

        except Exception as e:
            logger.error(f"✗ Erro ao processar usuário {user_data.get('email', 'desconhecido')}: {e}")
            usuarios_com_erro += 1

    # Resumo
    logger.info(f"Resumo do seed de usuários: {usuarios_criados} criados, {usuarios_existentes} já existiam, {usuarios_com_erro} com erro")

def inicializar_dados():
    """Inicializa todos os dados seed"""
    logger.info("=" * 50)
    logger.info("Iniciando carga de dados seed...")
    logger.info("=" * 50)

    try:
        carregar_usuarios_seed()
        logger.info("=" * 50)
        logger.info("Dados seed carregados!")
        logger.info("=" * 50)
    except Exception as e:
        logger.error(f"Erro crítico ao inicializar dados seed: {e}", exc_info=True)
