"""
Configuracoes e fixtures para testes E2E com Playwright.

Gerencia o ciclo de vida do servidor FastAPI e fornece fixtures
para interacao com o browser via Playwright.

Testes E2E simulam interacoes reais do usuario via browser,
testando fluxos completos da aplicacao.
"""

import os
import socket
import sqlite3
import subprocess
import tempfile
import time
from typing import Generator
import urllib.request
import urllib.error

import pytest
from playwright.sync_api import Page


# Configuracoes do servidor E2E
E2E_SERVER_HOST = "127.0.0.1"
E2E_SERVER_PORT = 8404
E2E_BASE_URL = f"http://{E2E_SERVER_HOST}:{E2E_SERVER_PORT}"
E2E_SERVER_STARTUP_TIMEOUT = 30


def _porta_disponivel(host: str, port: int) -> bool:
    """Verifica se a porta esta disponivel."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def _aguardar_servidor_online(host: str, port: int, timeout: int = 30) -> bool:
    """Aguarda o servidor ficar disponivel."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def _verificar_servidor_saude(base_url: str, timeout: int = 5) -> bool:
    """Verifica se o servidor esta saudavel via health check."""
    try:
        req = urllib.request.Request(f"{base_url}/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return False


@pytest.fixture(scope="session")
def e2e_test_database():
    """
    Cria banco de dados de teste isolado para E2E.
    Session-scoped para persistir durante toda a sessao de testes.

    IMPORTANTE: Todas as tabelas devem ser criadas ANTES de iniciar o servidor,
    pois alguns routers consultam a tabela de configuracao durante a importacao.
    """
    test_db = tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix="_e2e.db", prefix="test_"
    )
    test_db_path = test_db.name
    test_db.close()

    # Importar todos os SQLs necessarios para criar as tabelas
    from sql.usuario_sql import CRIAR_TABELA as CRIAR_USUARIO
    from sql.configuracao_sql import CRIAR_TABELA as CRIAR_CONFIGURACAO, INSERIR
    from sql.chamado_sql import CRIAR_TABELA as CRIAR_CHAMADO
    from sql.chamado_interacao_sql import CRIAR_TABELA as CRIAR_CHAMADO_INTERACAO
    from sql.chat_sala_sql import CRIAR_TABELA as CRIAR_CHAT_SALA
    from sql.chat_participante_sql import CRIAR_TABELA as CRIAR_CHAT_PARTICIPANTE
    from sql.chat_mensagem_sql import CRIAR_TABELA as CRIAR_CHAT_MENSAGEM
    from sql.especie_sql import CRIAR_TABELA as CRIAR_ESPECIE
    from sql.raca_sql import CRIAR_TABELA as CRIAR_RACA
    from sql.abrigo_sql import CRIAR_TABELA as CRIAR_ABRIGO
    from sql.adotante_sql import CRIAR_TABELA as CRIAR_ADOTANTE
    from sql.endereco_sql import CRIAR_TABELA as CRIAR_ENDERECO
    from sql.animal_sql import CRIAR_TABELA as CRIAR_ANIMAL
    from sql.solicitacao_sql import CRIAR_TABELA as CRIAR_SOLICITACAO
    from sql.adocao_sql import CRIAR_TABELA as CRIAR_ADOCAO
    from sql.visita_sql import CRIAR_TABELA as CRIAR_VISITA

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Criar todas as tabelas na ordem correta (respeitando foreign keys)
    cursor.execute(CRIAR_USUARIO)
    cursor.execute(CRIAR_CONFIGURACAO)
    cursor.execute(CRIAR_CHAMADO)
    cursor.execute(CRIAR_CHAMADO_INTERACAO)
    cursor.execute(CRIAR_CHAT_SALA)
    cursor.execute(CRIAR_CHAT_PARTICIPANTE)
    cursor.execute(CRIAR_CHAT_MENSAGEM)
    cursor.execute(CRIAR_ESPECIE)
    cursor.execute(CRIAR_RACA)
    cursor.execute(CRIAR_ABRIGO)
    cursor.execute(CRIAR_ADOTANTE)
    cursor.execute(CRIAR_ENDERECO)
    cursor.execute(CRIAR_ANIMAL)
    cursor.execute(CRIAR_SOLICITACAO)
    cursor.execute(CRIAR_ADOCAO)
    cursor.execute(CRIAR_VISITA)

    # Inserir rate limits muito altos para evitar bloqueios nos testes
    configs = [
        ("rate_limit_cadastro_max", "10000", "Rate limit cadastro - maximo"),
        ("rate_limit_cadastro_minutos", "1", "Rate limit cadastro - janela"),
        ("rate_limit_login_max", "10000", "Rate limit login - maximo"),
        ("rate_limit_login_minutos", "1", "Rate limit login - janela"),
        ("rate_limit_admin_usuarios_max", "10000", "Rate limit admin usuarios"),
        ("rate_limit_admin_usuarios_minutos", "1", "Rate limit admin usuarios - janela"),
        ("rate_limit_admin_backups_max", "10000", "Rate limit admin backups"),
        ("rate_limit_admin_backups_minutos", "1", "Rate limit admin backups - janela"),
        ("rate_limit_backup_download_max", "10000", "Rate limit backup download"),
        ("rate_limit_backup_download_minutos", "1", "Rate limit backup download - janela"),
        ("rate_limit_admin_config_max", "10000", "Rate limit admin config"),
        ("rate_limit_admin_config_minutos", "1", "Rate limit admin config - janela"),
        ("rate_limit_chamado_criar_max", "10000", "Rate limit criar chamado"),
        ("rate_limit_chamado_criar_minutos", "1", "Rate limit criar chamado - janela"),
        ("rate_limit_chamado_responder_max", "10000", "Rate limit responder chamado"),
        ("rate_limit_chamado_responder_minutos", "1", "Rate limit responder chamado - janela"),
        ("rate_limit_admin_chamado_responder_max", "10000", "Rate limit admin responder"),
        ("rate_limit_admin_chamado_responder_minutos", "1", "Rate limit admin responder - janela"),
        ("rate_limit_upload_foto_max", "10000", "Rate limit upload foto"),
        ("rate_limit_upload_foto_minutos", "1", "Rate limit upload foto - janela"),
        ("rate_limit_alterar_senha_max", "10000", "Rate limit alterar senha"),
        ("rate_limit_alterar_senha_minutos", "1", "Rate limit alterar senha - janela"),
        ("rate_limit_form_get_max", "10000", "Rate limit form get"),
        ("rate_limit_form_get_minutos", "1", "Rate limit form get - janela"),
        ("rate_limit_chat_message_max", "10000", "Rate limit chat message"),
        ("rate_limit_chat_message_minutos", "1", "Rate limit chat message - janela"),
        ("rate_limit_chat_sala_max", "10000", "Rate limit chat sala"),
        ("rate_limit_chat_sala_minutos", "1", "Rate limit chat sala - janela"),
        ("rate_limit_busca_usuarios_max", "10000", "Rate limit busca usuarios"),
        ("rate_limit_busca_usuarios_minutos", "1", "Rate limit busca usuarios - janela"),
        ("rate_limit_chat_listagem_max", "10000", "Rate limit chat listagem"),
        ("rate_limit_chat_listagem_minutos", "1", "Rate limit chat listagem - janela"),
        ("rate_limit_public_max", "10000", "Rate limit public"),
        ("rate_limit_public_minutos", "1", "Rate limit public - janela"),
        ("rate_limit_examples_max", "10000", "Rate limit examples"),
        ("rate_limit_examples_minutos", "1", "Rate limit examples - janela"),
        ("rate_limit_esqueci_senha_max", "10000", "Rate limit esqueci senha"),
        ("rate_limit_esqueci_senha_minutos", "1", "Rate limit esqueci senha - janela"),
        ("toast_auto_hide_delay_ms", "5000", "Delay do toast"),
    ]

    for chave, valor, descricao in configs:
        cursor.execute(INSERIR, (chave, valor, descricao))

    conn.commit()
    conn.close()

    yield test_db_path

    try:
        os.unlink(test_db_path)
    except Exception:
        pass


@pytest.fixture(scope="session")
def e2e_server(e2e_test_database) -> Generator[str, None, None]:
    """
    Inicia servidor FastAPI para testes E2E.

    Session-scoped para evitar reiniciar o servidor entre testes.
    Retorna a URL base do servidor.
    """
    if not _porta_disponivel(E2E_SERVER_HOST, E2E_SERVER_PORT):
        pytest.skip(f"Porta {E2E_SERVER_PORT} ja esta em uso")

    env = os.environ.copy()
    env.update(
        {
            "DATABASE_PATH": e2e_test_database,
            "HOST": E2E_SERVER_HOST,
            "PORT": str(E2E_SERVER_PORT),
            "RUNNING_MODE": "Development",
            "RESEND_API_KEY": "",
            "LOG_LEVEL": "ERROR",
            "RELOAD": "False",
            # Rate limits muito altos para evitar bloqueios durante testes
            "RATE_LIMIT_CADASTRO_MAX": "1000",
            "RATE_LIMIT_CADASTRO_MINUTOS": "1",
            "RATE_LIMIT_LOGIN_MAX": "1000",
            "RATE_LIMIT_LOGIN_MINUTOS": "1",
        }
    )

    process = subprocess.Popen(
        ["python", "main.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    )

    if not _aguardar_servidor_online(
        E2E_SERVER_HOST, E2E_SERVER_PORT, E2E_SERVER_STARTUP_TIMEOUT
    ):
        process.terminate()
        process.wait()
        pytest.fail(
            f"Servidor nao iniciou em {E2E_SERVER_STARTUP_TIMEOUT}s."
        )

    yield E2E_BASE_URL

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@pytest.fixture(scope="session")
def browser_context_args():
    """Configuracoes do contexto do browser."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "locale": "pt-BR",
        "timezone_id": "America/Sao_Paulo",
    }


@pytest.fixture(scope="function")
def e2e_page(page: Page, e2e_server: str) -> Page:
    """
    Fixture que fornece uma pagina Playwright configurada.

    Function-scoped para garantir isolamento entre testes.
    Verifica saude do servidor antes de cada teste.
    """
    # Verificar se o servidor esta saudavel antes do teste
    if not _verificar_servidor_saude(e2e_server):
        # Aguardar um pouco caso esteja se recuperando
        time.sleep(2)
        if not _verificar_servidor_saude(e2e_server):
            pytest.fail(f"Servidor E2E nao esta respondendo em {e2e_server}")

    page.set_default_timeout(30000)
    page.set_default_navigation_timeout(30000)
    page.base_url = e2e_server  # type: ignore
    yield page


@pytest.fixture(scope="function")
def limpar_banco_e2e(e2e_test_database):
    """
    Limpa o banco de dados E2E antes de cada teste.

    Garante isolamento entre testes E2E.
    """

    def _limpar():
        try:
            conn = sqlite3.connect(e2e_test_database)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
            tabelas = [row[0] for row in cursor.fetchall()]

            # Nao limpar 'configuracao' para manter rate limits altos
            # Ordem de limpeza respeitando constraints de foreign key
            ordem_limpeza = [
                "chamado_interacao",
                "chamado",
                "chat_mensagem",
                "chat_participante",
                "chat_sala",
                "adocao",
                "visita",
                "solicitacao",
                "animal",
                "raca",
                "especie",
                "endereco",
                "abrigo",
                "adotante",
                "usuario",
            ]

            for tabela in ordem_limpeza:
                if tabela in tabelas:
                    cursor.execute(f"DELETE FROM {tabela}")

            if "sqlite_sequence" in [
                row[0]
                for row in cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            ]:
                cursor.execute("DELETE FROM sqlite_sequence")

            conn.commit()
            conn.close()
        except Exception:
            pass

    _limpar()
    yield
    _limpar()


@pytest.fixture
def usuario_e2e_dados():
    """Dados de usuario para testes E2E."""
    return {
        "perfil": "Adotante",
        "nome": "Usuario E2E Teste",
        "email": "e2e_teste@example.com",
        "senha": "SenhaE2E@123",
    }


# Marca todos os testes nesta pasta como e2e
def pytest_collection_modifyitems(items):
    """Adiciona marca 'e2e' a todos os testes nesta pasta."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
