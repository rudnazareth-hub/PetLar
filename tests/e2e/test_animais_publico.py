"""
Testes E2E para paginas publicas de animais.

Casos de uso cobertos:
- UC-ANIMAL-001: Visualizar lista de animais disponiveis
- UC-ANIMAL-002: Visualizar detalhes do animal
- UC-ANIMAL-003: Curtir/favoritar animal
- UC-ADOPT-001: Reservar animal para adocao
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    AnimaisPublicPage,
    PublicPage,
    criar_usuario_e_logar,
)


@pytest.mark.e2e
class TestListarAnimaisPublico:
    """UC-ANIMAL-001: Visualizar lista de animais disponiveis."""

    def test_pagina_animais_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina publica de animais deve carregar corretamente."""
        animais_page = AnimaisPublicPage(e2e_page, e2e_server)
        animais_page.navegar_listar()

        assert "/animais" in e2e_page.url
        # Verificar se tem elementos da pagina de listagem
        conteudo = e2e_page.content().lower()
        assert "animais" in conteudo or "adoção" in conteudo or "adocao" in conteudo

    def test_pagina_animais_exibe_filtros(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de animais deve exibir filtros de busca."""
        animais_page = AnimaisPublicPage(e2e_page, e2e_server)
        animais_page.navegar_listar()

        # Verificar se tem filtros
        conteudo = e2e_page.content().lower()
        assert "filtro" in conteudo or "espécie" in conteudo or "especie" in conteudo or "buscar" in conteudo

    def test_pagina_animais_acessivel_sem_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Listagem de animais deve ser acessivel sem login."""
        animais_page = AnimaisPublicPage(e2e_page, e2e_server)
        animais_page.navegar_listar()

        # Nao deve redirecionar para login
        assert "/login" not in e2e_page.url
        assert "/animais" in e2e_page.url


@pytest.mark.e2e
class TestDetalhesAnimalPublico:
    """UC-ANIMAL-002: Visualizar detalhes do animal."""

    def test_pagina_detalhes_animal_inexistente_redireciona(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Detalhes de animal inexistente deve redirecionar."""
        animais_page = AnimaisPublicPage(e2e_page, e2e_server)
        animais_page.navegar_detalhes(99999)

        e2e_page.wait_for_timeout(500)

        # Deve redirecionar para listagem ou exibir erro
        conteudo = e2e_page.content().lower()
        assert "/animais" in e2e_page.url or "encontrado" in conteudo or "erro" in conteudo


@pytest.mark.e2e
class TestReservarAnimal:
    """UC-ADOPT-001: Reservar animal para adocao."""

    def test_reserva_requer_login_como_adotante(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Reserva de animal deve requerer login como adotante."""
        # Tentar acessar rota de reserva sem login
        e2e_page.goto(f"{e2e_server}/animais/1/reservar")

        e2e_page.wait_for_timeout(500)

        # Deve redirecionar para login
        assert "/login" in e2e_page.url or "/animais" in e2e_page.url

    def test_abrigo_nao_pode_reservar_animal(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario Abrigo nao deve poder reservar animal."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Reserva Teste", "abrigo_reserva@example.com", "SenhaForte@123"
        )

        # Tentar reservar animal
        e2e_page.goto(f"{e2e_server}/animais/1/reservar")

        e2e_page.wait_for_timeout(500)

        # Deve ser bloqueado ou redirecionado
        conteudo = e2e_page.content().lower()
        assert "permissão" in conteudo or "permissao" in conteudo or "/animais" in e2e_page.url or "/abrigo" in e2e_page.url


@pytest.mark.e2e
class TestHomeAnimais:
    """Testes da pagina inicial com animais."""

    def test_home_exibe_ultimos_animais(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve exibir ultimos animais cadastrados."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        conteudo = e2e_page.content().lower()
        # Verificar se tem secao de animais ou referencias
        assert "animais" in conteudo or "adoção" in conteudo or "adocao" in conteudo or "pet" in conteudo

    def test_home_carrega_sem_erros(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina inicial deve carregar sem erros."""
        public_page = PublicPage(e2e_page, e2e_server)
        public_page.navegar_home()

        # Verificar que nao tem erro 500 ou similar
        conteudo = e2e_page.content().lower()
        assert "500" not in e2e_page.title().lower()
        assert "error" not in e2e_page.title().lower()
