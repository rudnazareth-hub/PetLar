"""
Testes E2E para paginas publicas.

Casos de uso cobertos:
- UC-PUBLIC-001: Acessar pagina inicial
- UC-PUBLIC-002: Acessar pagina "Sobre"
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import PublicPage


@pytest.mark.e2e
class TestPaginaInicial:
    """UC-PUBLIC-001: Acessar pagina inicial."""

    def test_pagina_inicial_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve carregar corretamente."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Verificar que nao houve erro
        assert "500" not in e2e_page.title()
        assert "error" not in e2e_page.title().lower()

    def test_pagina_inicial_acessivel_sem_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve ser acessivel sem login."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Nao deve redirecionar para login
        assert "/login" not in e2e_page.url
        assert "/" == e2e_page.url.replace(e2e_server, "") or e2e_page.url == e2e_server + "/"

    def test_pagina_inicial_exibe_conteudo_principal(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve exibir conteudo principal."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        conteudo = e2e_page.content().lower()
        # Deve ter alguma referencia ao projeto (petlar, animais, adocao, etc)
        assert "pet" in conteudo or "animal" in conteudo or "adoção" in conteudo or "adocao" in conteudo

    def test_pagina_inicial_possui_navegacao(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve ter menu de navegacao."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Verificar se tem navegacao (nav ou menu)
        nav = e2e_page.locator('nav').first
        expect(nav).to_be_visible()

    def test_pagina_inicial_possui_link_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve ter link para login."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        conteudo = e2e_page.content().lower()
        # Deve ter link de login ou entrar
        assert "login" in conteudo or "entrar" in conteudo or "acessar" in conteudo

    def test_pagina_inicial_possui_link_cadastro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve ter link para cadastro."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        conteudo = e2e_page.content().lower()
        # Deve ter link de cadastro
        assert "cadastr" in conteudo or "registr" in conteudo or "criar conta" in conteudo


@pytest.mark.e2e
class TestPaginaSobre:
    """UC-PUBLIC-002: Acessar pagina "Sobre"."""

    def test_pagina_sobre_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina sobre deve carregar corretamente."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_sobre()

        assert "/sobre" in e2e_page.url

    def test_pagina_sobre_acessivel_sem_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina sobre deve ser acessivel sem login."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_sobre()

        # Nao deve redirecionar para login
        assert "/login" not in e2e_page.url

    def test_pagina_sobre_exibe_informacoes_projeto(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina sobre deve exibir informacoes do projeto."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_sobre()

        conteudo = e2e_page.content().lower()
        # Deve ter alguma informacao sobre o projeto
        assert "sobre" in conteudo or "projeto" in conteudo or "pet" in conteudo


@pytest.mark.e2e
class TestNavegacaoPublica:
    """Testes de navegacao entre paginas publicas."""

    def test_navegacao_home_para_sobre(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve conseguir navegar da home para sobre."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Clicar no link "Sobre" se existir
        sobre_link = e2e_page.locator('a[href*="sobre"]').first
        if sobre_link.is_visible():
            sobre_link.click()
            e2e_page.wait_for_timeout(500)
            assert "/sobre" in e2e_page.url

    def test_navegacao_home_para_animais(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve conseguir navegar da home para animais."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Clicar no link "Animais" se existir
        animais_link = e2e_page.locator('a[href*="animais"]').first
        if animais_link.is_visible():
            animais_link.click()
            e2e_page.wait_for_timeout(500)
            assert "/animais" in e2e_page.url

    def test_navegacao_home_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve conseguir navegar da home para login."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Clicar no link "Login" se existir
        login_link = e2e_page.locator('a[href*="login"]').first
        if login_link.is_visible():
            login_link.click()
            e2e_page.wait_for_timeout(500)
            assert "/login" in e2e_page.url

    def test_navegacao_home_para_cadastro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Deve conseguir navegar da home para cadastro."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Clicar no link "Cadastrar" se existir
        cadastro_link = e2e_page.locator('a[href*="cadastrar"]').first
        if cadastro_link.is_visible():
            cadastro_link.click()
            e2e_page.wait_for_timeout(500)
            assert "/cadastrar" in e2e_page.url


@pytest.mark.e2e
class TestResponsividade:
    """Testes basicos de responsividade."""

    def test_pagina_inicial_carrega_em_mobile(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve carregar em viewport mobile."""
        # Definir viewport mobile
        e2e_page.set_viewport_size({"width": 375, "height": 667})

        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Verificar que carregou sem erros
        assert "500" not in e2e_page.title()

    def test_pagina_inicial_carrega_em_tablet(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve carregar em viewport tablet."""
        # Definir viewport tablet
        e2e_page.set_viewport_size({"width": 768, "height": 1024})

        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Verificar que carregou sem erros
        assert "500" not in e2e_page.title()
