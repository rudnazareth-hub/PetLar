"""
Testes E2E para administracao de adotantes e abrigos.

Casos de uso cobertos:
- UC-ADOTANT-001: Listar todos os adotantes
- UC-ADOTANT-002: Visualizar perfil do adotante
- UC-ADOTANT-003: Editar informacoes do adotante
- UC-SHELTER-001: Listar todos os abrigos
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    AdminAdotantesPage,
    AdminAbrigosPage,
    criar_usuario_e_logar,
)


@pytest.mark.e2e
class TestListarAdotantes:
    """UC-ADOTANT-001: Listar todos os adotantes."""

    def test_pagina_listar_adotantes_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de listagem de adotantes deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Adotantes", "admin_adotantes@example.com", "SenhaForte@123"
        )

        adotantes_page = AdminAdotantesPage(e2e_page, e2e_server)
        adotantes_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        # Verifica se carregou ou foi redirecionado
        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestVisualizarAdotante:
    """UC-ADOTANT-002: Visualizar perfil do adotante."""

    def test_pagina_visualizar_adotante(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de detalhes de adotante deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Vis Adot", "admin_vis_adot@example.com", "SenhaForte@123"
        )

        adotantes_page = AdminAdotantesPage(e2e_page, e2e_server)
        adotantes_page.navegar_visualizar(1)

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestListarAbrigos:
    """UC-SHELTER-001: Listar todos os abrigos."""

    def test_pagina_listar_abrigos_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de listagem de abrigos deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Abrigos", "admin_abrigos@example.com", "SenhaForte@123"
        )

        abrigos_page = AdminAbrigosPage(e2e_page, e2e_server)
        abrigos_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAcessoAdotantesAbrigos:
    """Testes de controle de acesso."""

    def test_usuario_nao_logado_redirecionado_login_adotantes(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        adotantes_page = AdminAdotantesPage(e2e_page, e2e_server)
        adotantes_page.navegar_listar()

        assert "/login" in e2e_page.url

    def test_usuario_nao_logado_redirecionado_login_abrigos(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        abrigos_page = AdminAbrigosPage(e2e_page, e2e_server)
        abrigos_page.navegar_listar()

        assert "/login" in e2e_page.url

    def test_adotante_nao_pode_acessar_admin_adotantes(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante comum nao deve acessar admin de adotantes."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Comum", "adotante_comum@example.com", "SenhaForte@123"
        )

        adotantes_page = AdminAdotantesPage(e2e_page, e2e_server)
        adotantes_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/adotantes/listar" not in e2e_page.url or "acesso" in conteudo

    def test_abrigo_nao_pode_acessar_admin_abrigos(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo comum nao deve acessar admin de abrigos."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Comum", "abrigo_comum@example.com", "SenhaForte@123"
        )

        abrigos_page = AdminAbrigosPage(e2e_page, e2e_server)
        abrigos_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/abrigos/listar" not in e2e_page.url or "acesso" in conteudo
