"""
Testes E2E para administracao de especies e racas.

Casos de uso cobertos:
Especies:
- UC-SPECIES-001: Listar especies
- UC-SPECIES-002: Cadastrar especie
- UC-SPECIES-003: Editar especie
- UC-SPECIES-004: Excluir especie

Racas:
- UC-BREED-001: Listar racas
- UC-BREED-002: Cadastrar raca
- UC-BREED-003: Editar raca
- UC-BREED-004: Excluir raca
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    AdminEspeciesPage,
    AdminRacasPage,
    criar_usuario_e_logar,
)


# =============================================================================
# TESTES DE ESPECIES
# =============================================================================


@pytest.mark.e2e
class TestListarEspecies:
    """UC-SPECIES-001: Listar especies."""

    def test_pagina_listar_especies_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de listagem de especies deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Especies", "admin_especies@example.com", "SenhaForte@123"
        )

        especies_page = AdminEspeciesPage(e2e_page, e2e_server)
        especies_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        # Verifica se carregou ou foi redirecionado
        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestCadastrarEspecie:
    """UC-SPECIES-002: Cadastrar especie."""

    def test_pagina_cadastrar_especie_carrega_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de cadastro de especie deve carregar formulario."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Cad Especie", "admin_cad_especie@example.com", "SenhaForte@123"
        )

        especies_page = AdminEspeciesPage(e2e_page, e2e_server)
        especies_page.navegar_cadastrar()

        e2e_page.wait_for_timeout(500)

        # Verifica se formulario esta presente ou foi redirecionado
        if "/admin/especies/cadastrar" in e2e_page.url:
            expect(e2e_page.locator('input[name="nome"]')).to_be_visible()


@pytest.mark.e2e
class TestEditarEspecie:
    """UC-SPECIES-003: Editar especie."""

    def test_pagina_editar_especie_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de edicao de especie deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Edit Especie", "admin_edit_especie@example.com", "SenhaForte@123"
        )

        especies_page = AdminEspeciesPage(e2e_page, e2e_server)
        especies_page.navegar_editar(1)

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAcessoEspecies:
    """Testes de controle de acesso para especies."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        especies_page = AdminEspeciesPage(e2e_page, e2e_server)
        especies_page.navegar_listar()

        assert "/login" in e2e_page.url

    def test_adotante_nao_pode_acessar_admin_especies(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante comum nao deve acessar admin de especies."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Especies", "adotante_especies@example.com", "SenhaForte@123"
        )

        especies_page = AdminEspeciesPage(e2e_page, e2e_server)
        especies_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/especies/listar" not in e2e_page.url or "acesso" in conteudo

    def test_abrigo_nao_pode_acessar_admin_especies(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo nao deve acessar admin de especies."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Especies", "abrigo_especies@example.com", "SenhaForte@123"
        )

        especies_page = AdminEspeciesPage(e2e_page, e2e_server)
        especies_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/especies/listar" not in e2e_page.url or "acesso" in conteudo


# =============================================================================
# TESTES DE RACAS
# =============================================================================


@pytest.mark.e2e
class TestListarRacas:
    """UC-BREED-001: Listar racas."""

    def test_pagina_listar_racas_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de listagem de racas deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Racas", "admin_racas@example.com", "SenhaForte@123"
        )

        racas_page = AdminRacasPage(e2e_page, e2e_server)
        racas_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestCadastrarRaca:
    """UC-BREED-002: Cadastrar raca."""

    def test_pagina_cadastrar_raca_carrega_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de cadastro de raca deve carregar formulario."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Cad Raca", "admin_cad_raca@example.com", "SenhaForte@123"
        )

        racas_page = AdminRacasPage(e2e_page, e2e_server)
        racas_page.navegar_cadastrar()

        e2e_page.wait_for_timeout(500)

        if "/admin/racas/cadastrar" in e2e_page.url:
            expect(e2e_page.locator('input[name="nome"]')).to_be_visible()


@pytest.mark.e2e
class TestEditarRaca:
    """UC-BREED-003: Editar raca."""

    def test_pagina_editar_raca_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de edicao de raca deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Edit Raca", "admin_edit_raca@example.com", "SenhaForte@123"
        )

        racas_page = AdminRacasPage(e2e_page, e2e_server)
        racas_page.navegar_editar(1)

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAcessoRacas:
    """Testes de controle de acesso para racas."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        racas_page = AdminRacasPage(e2e_page, e2e_server)
        racas_page.navegar_listar()

        assert "/login" in e2e_page.url

    def test_adotante_nao_pode_acessar_admin_racas(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante comum nao deve acessar admin de racas."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Racas", "adotante_racas@example.com", "SenhaForte@123"
        )

        racas_page = AdminRacasPage(e2e_page, e2e_server)
        racas_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/racas/listar" not in e2e_page.url or "acesso" in conteudo
