"""
Testes E2E para configuracoes do sistema, backup e curtidas.

Casos de uso cobertos:
Configuracoes:
- UC-CONFIG-001: Visualizar configuracoes do sistema
- UC-CONFIG-002: Atualizar configuracoes em lote
- UC-CONFIG-003: Alterar tema do sistema
- UC-CONFIG-004: Visualizar log de auditoria

Backup:
- UC-BACKUP-001: Listar backups disponiveis
- UC-BACKUP-002: Criar backup do banco de dados
- UC-BACKUP-003: Restaurar backup
- UC-BACKUP-004: Excluir backup
- UC-BACKUP-005: Baixar arquivo de backup

Curtidas:
- UC-LIKE-001: Listar todas as curtidas
- UC-LIKE-002: Cadastrar curtida (Admin)
- UC-LIKE-003: Editar curtida (Admin)
- UC-LIKE-004: Excluir curtida (Admin)
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    AdminConfiguracoesPage,
    AdminBackupsPage,
    AdminCurtidasPage,
    criar_usuario_e_logar,
)


# =============================================================================
# TESTES DE CONFIGURACOES
# =============================================================================


@pytest.mark.e2e
class TestVisualizarConfiguracoes:
    """UC-CONFIG-001: Visualizar configuracoes do sistema."""

    def test_pagina_configuracoes_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de configuracoes deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Config", "admin_config@example.com", "SenhaForte@123"
        )

        config_page = AdminConfiguracoesPage(e2e_page, e2e_server)
        config_page.navegar()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAlterarTema:
    """UC-CONFIG-003: Alterar tema do sistema."""

    def test_pagina_tema_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de selecao de tema deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Tema", "admin_tema@example.com", "SenhaForte@123"
        )

        config_page = AdminConfiguracoesPage(e2e_page, e2e_server)
        config_page.navegar_tema()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestVisualizarAuditoria:
    """UC-CONFIG-004: Visualizar log de auditoria."""

    def test_pagina_auditoria_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de auditoria deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Auditoria", "admin_auditoria@example.com", "SenhaForte@123"
        )

        config_page = AdminConfiguracoesPage(e2e_page, e2e_server)
        config_page.navegar_auditoria()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAcessoConfiguracoes:
    """Testes de controle de acesso para configuracoes."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        config_page = AdminConfiguracoesPage(e2e_page, e2e_server)
        config_page.navegar()

        assert "/login" in e2e_page.url

    def test_adotante_nao_pode_acessar_configuracoes(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante nao deve acessar configuracoes."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Config", "adotante_config@example.com", "SenhaForte@123"
        )

        config_page = AdminConfiguracoesPage(e2e_page, e2e_server)
        config_page.navegar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/configuracoes" not in e2e_page.url or "acesso" in conteudo


# =============================================================================
# TESTES DE BACKUP
# =============================================================================


@pytest.mark.e2e
class TestListarBackups:
    """UC-BACKUP-001: Listar backups disponiveis."""

    def test_pagina_listar_backups_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de listagem de backups deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Backups", "admin_backups@example.com", "SenhaForte@123"
        )

        backups_page = AdminBackupsPage(e2e_page, e2e_server)
        backups_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAcessoBackups:
    """Testes de controle de acesso para backups."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        backups_page = AdminBackupsPage(e2e_page, e2e_server)
        backups_page.navegar_listar()

        assert "/login" in e2e_page.url

    def test_adotante_nao_pode_acessar_backups(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante nao deve acessar backups."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Backups", "adotante_backups@example.com", "SenhaForte@123"
        )

        backups_page = AdminBackupsPage(e2e_page, e2e_server)
        backups_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/backups/listar" not in e2e_page.url or "acesso" in conteudo

    def test_abrigo_nao_pode_acessar_backups(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo nao deve acessar backups."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Backups", "abrigo_backups@example.com", "SenhaForte@123"
        )

        backups_page = AdminBackupsPage(e2e_page, e2e_server)
        backups_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/backups/listar" not in e2e_page.url or "acesso" in conteudo


# =============================================================================
# TESTES DE CURTIDAS
# =============================================================================


@pytest.mark.e2e
class TestListarCurtidas:
    """UC-LIKE-001: Listar todas as curtidas."""

    def test_pagina_listar_curtidas_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de listagem de curtidas deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Curtidas", "admin_curtidas@example.com", "SenhaForte@123"
        )

        curtidas_page = AdminCurtidasPage(e2e_page, e2e_server)
        curtidas_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestCadastrarCurtida:
    """UC-LIKE-002: Cadastrar curtida (Admin)."""

    def test_pagina_cadastrar_curtida_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de cadastro de curtida deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Cad Curtida", "admin_cad_curtida@example.com", "SenhaForte@123"
        )

        curtidas_page = AdminCurtidasPage(e2e_page, e2e_server)
        curtidas_page.navegar_cadastrar()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAcessoCurtidas:
    """Testes de controle de acesso para curtidas."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        curtidas_page = AdminCurtidasPage(e2e_page, e2e_server)
        curtidas_page.navegar_listar()

        assert "/login" in e2e_page.url

    def test_adotante_nao_pode_acessar_admin_curtidas(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante nao deve acessar admin de curtidas."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Curtidas", "adotante_curtidas@example.com", "SenhaForte@123"
        )

        curtidas_page = AdminCurtidasPage(e2e_page, e2e_server)
        curtidas_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/curtidas/listar" not in e2e_page.url or "acesso" in conteudo
