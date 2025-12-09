import uvicorn
import sqlite3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path

# Configurações
from util.config import APP_NAME, SECRET_KEY, HOST, PORT, RELOAD, VERSION

# Logger
from util.logger_config import logger

# Exception Handlers
from util.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    form_validation_exception_handler,
)
from util.exceptions import ErroValidacaoFormulario

# Repositórios
from repo import (
    usuario_repo,
    configuracao_repo,
    chamado_repo,
    chamado_interacao_repo,
    indices_repo,
)
from repo import chat_sala_repo, chat_participante_repo, chat_mensagem_repo
from repo import categoria_repo
from repo import raca_repo, abrigo_repo, adotante_repo, animal_repo, endereco_repo
from repo import solicitacao_repo, adocao_repo, visita_repo
from repo import especie_repo

# Rotas
from routes.auth_routes import router as auth_router
from routes.chamados_routes import router as chamados_router
from routes.admin_usuarios_routes import router as admin_usuarios_router
from routes.admin_categorias_routes import router as admin_categorias_router
from routes.admin_configuracoes_routes import router as admin_config_router
from routes.admin_backups_routes import router as admin_backups_router
from routes.admin_chamados_routes import router as admin_chamados_router
from routes.usuario_routes import router as usuario_router
from routes.chat_routes import router as chat_router
from routes.public_routes import router as public_router
from routes.examples_routes import router as examples_router
from routes.admin_racas_routes import router as admin_racas_router
from routes.admin_abrigos_routes import router as admin_abrigos_router
from routes.admin_animais_routes import router as admin_animais_router
from routes.admin_especies_routes import router as admin_especies_router

# Seeds
from util.seed_data import inicializar_dados

# CSRF Protection
from util.csrf_protection import MiddlewareProtecaoCSRF

# Criar aplicação FastAPI
app = FastAPI(title=APP_NAME, version=VERSION)

# Configurar SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Configurar CSRF Protection Middleware
app.add_middleware(MiddlewareProtecaoCSRF)
logger.info("CSRF Protection habilitado")

# Registrar Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ErroValidacaoFormulario, form_validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
logger.info("Exception handlers registrados")

# Montar arquivos estáticos
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Arquivos estáticos montados em /static")

# Definir repositórios e nomes das tabelas
TABELAS = [
    (usuario_repo, "usuario"),
    (configuracao_repo, "configuracao"),
    (chamado_repo, "chamado"),
    (chamado_interacao_repo, "chamado_interacao"),
    (chat_sala_repo, "chat_sala"),
    (chat_participante_repo, "chat_participante"),
    (chat_mensagem_repo, "chat_mensagem"),
]

# Criar tabelas do banco de dados
logger.info("Criando tabelas do banco de dados...")
try:
    for repo, nome in TABELAS:
        repo.criar_tabela()
        logger.info(f"Tabela '{nome}' criada/verificada")

    categoria_repo.criar_tabela()
    logger.info("Tabela 'categoria' criada/verificada")

    especie_repo.criar_tabela()
    logger.info("Tabela 'especie' criada/verificada")

    # Tabelas específicas do PetLar
    raca_repo.criar_tabela()
    logger.info("Tabela 'raca' criada/verificada")

    abrigo_repo.criar_tabela()
    logger.info("Tabela 'abrigo' criada/verificada")

    adotante_repo.criar_tabela()
    logger.info("Tabela 'adotante' criada/verificada")

    endereco_repo.criar_tabela()
    logger.info("Tabela 'endereco' criada/verificada")

    animal_repo.criar_tabela()
    logger.info("Tabela 'animal' criada/verificada")

    solicitacao_repo.criar_tabela()
    logger.info("Tabela 'solicitacao' criada/verificada")

    adocao_repo.criar_tabela()
    logger.info("Tabela 'adocao' criada/verificada")

    visita_repo.criar_tabela()
    logger.info("Tabela 'visita' criada/verificada")

    # Criar índices para otimização de performance
    indices_repo.criar_indices()

except sqlite3.Error as e:
    logger.error(f"Erro ao criar tabelas: {e}")
    raise



# Inicializar dados seed
try:
    inicializar_dados()
except sqlite3.Error as e:
    logger.error(f"Erro ao inicializar dados seed: {e}", exc_info=True)

# Migrar configurações do .env para o banco de dados
try:
    from util.migrar_config import migrar_configs_para_banco

    migrar_configs_para_banco()
except sqlite3.Error as e:
    logger.error(f"Erro ao migrar configurações para banco: {e}", exc_info=True)

# Definir routers e suas configurações
# IMPORTANTE: public_router e examples_router devem ser incluídos por último
ROUTERS = [
    (auth_router, ["Autenticação"], "autenticação"),
    (chamados_router, ["Chamados"], "chamados"),
    (admin_usuarios_router, ["Admin - Usuários"], "admin de usuários"),
    (admin_config_router, ["Admin - Configurações"], "admin de configurações"),
    (admin_backups_router, ["Admin - Backups"], "admin de backups"),
    (admin_chamados_router, ["Admin - Chamados"], "admin de chamados"),
    (usuario_router, ["Usuário"], "usuário"),
    (chat_router, ["Chat"], "chat"),
    (admin_racas_router, ["Admin - Raças"], "admin de raças"),
    (admin_abrigos_router, ["Admin - Abrigos"], "admin de abrigos"),
    (admin_animais_router, ["Admin - Animais"], "admin de animais"),
    (admin_especies_router, ["Admin - Espécies"], "admin de espécies"),
    (admin_categorias_router, ["Admin - Categorias"], "admin de categorias"),
    (public_router, ["Público"], "público"),
    (examples_router, ["Exemplos"], "exemplos"),
]

# Incluir routers
for router, tags, nome in ROUTERS:
    app.include_router(router, tags=tags)
    logger.info(f"Router de {nome} incluído")

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info(f"Iniciando {APP_NAME} v{VERSION}")
    logger.info("=" * 60)

    logger.info(f"Servidor rodando em http://{HOST}:{PORT}")
    logger.info(f"Hot reload: {'Ativado' if RELOAD else 'Desativado'}")
    logger.info(f"Documentação API: http://{HOST}:{PORT}/docs")
    logger.info("=" * 60)

    try:
        uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD, log_level="info")
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise
