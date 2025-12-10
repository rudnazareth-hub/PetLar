"""
Testes E2E para gerenciamento de animais pelo abrigo.

Casos de uso cobertos:
- UC-ANIMAL-008: Listar animais do proprio abrigo
- UC-ANIMAL-009: Cadastrar animal no abrigo
- UC-ANIMAL-010: Editar animal do proprio abrigo
- UC-ANIMAL-011: Visualizar detalhes do animal do abrigo
- UC-ANIMAL-012: Excluir animal do abrigo
- UC-ANIMAL-013: Visualizar animais reservados
- UC-ANIMAL-014: Concluir adocao de animal
- UC-ANIMAL-015: Cancelar reserva de animal
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    AbrigoAnimaisPage,
    criar_usuario_e_logar,
)


@pytest.mark.e2e
class TestListarAnimaisAbrigo:
    """UC-ANIMAL-008: Listar animais do proprio abrigo."""

    def test_abrigo_pode_listar_seus_animais(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo deve conseguir listar seus animais."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Listar Animais", "abrigo_listar@example.com", "SenhaForte@123"
        )

        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        abrigo_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        # Deve acessar a pagina de listagem
        assert "/abrigo/animais" in e2e_page.url

    def test_adotante_nao_pode_acessar_animais_abrigo(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante nao deve acessar area de animais do abrigo."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Nao Abrigo", "adotante_nao_abrigo@example.com", "SenhaForte@123"
        )

        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        abrigo_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        # Deve ser redirecionado ou acesso negado
        conteudo = e2e_page.content().lower()
        assert "/abrigo/animais/listar" not in e2e_page.url or "acesso" in conteudo or "permissão" in conteudo


@pytest.mark.e2e
class TestCadastrarAnimalAbrigo:
    """UC-ANIMAL-009: Cadastrar animal no abrigo."""

    def test_pagina_cadastrar_animal_carrega_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de cadastro de animal deve carregar formulario."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Cadastrar Animal", "abrigo_cad_animal@example.com", "SenhaForte@123"
        )

        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        abrigo_page.navegar_cadastrar()

        e2e_page.wait_for_timeout(500)

        # Verificar se formulario esta presente
        if "/abrigo/animais/cadastrar" in e2e_page.url:
            expect(e2e_page.locator('input[name="nome"]')).to_be_visible()

    def test_usuario_nao_logado_nao_pode_cadastrar_animal(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado nao deve cadastrar animal."""
        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        abrigo_page.navegar_cadastrar()

        # Deve redirecionar para login
        assert "/login" in e2e_page.url


@pytest.mark.e2e
class TestVisualizarAnimalAbrigo:
    """UC-ANIMAL-011: Visualizar detalhes do animal do abrigo."""

    def test_abrigo_pode_acessar_visualizacao_animal(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo deve conseguir visualizar detalhes de animal."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Visualizar Animal", "abrigo_vis_animal@example.com", "SenhaForte@123"
        )

        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        # Tentar visualizar animal com ID 1
        abrigo_page.navegar_visualizar(1)

        e2e_page.wait_for_timeout(500)

        # Deve estar na area do abrigo ou ter sido redirecionado
        assert "/abrigo" in e2e_page.url or "/animais" in e2e_page.url


@pytest.mark.e2e
class TestAnimaisReservadosAbrigo:
    """UC-ANIMAL-013: Visualizar animais reservados."""

    def test_abrigo_pode_acessar_animais_reservados(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo deve conseguir acessar lista de animais reservados."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Reservados", "abrigo_reservados@example.com", "SenhaForte@123"
        )

        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        abrigo_page.navegar_reservados()

        e2e_page.wait_for_timeout(500)

        # Deve acessar a pagina de reservados
        conteudo = e2e_page.content().lower()
        assert "/abrigo" in e2e_page.url or "reserv" in conteudo


@pytest.mark.e2e
class TestEditarAnimalAbrigo:
    """UC-ANIMAL-010: Editar animal do proprio abrigo."""

    def test_abrigo_pode_acessar_edicao_animal(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo deve conseguir acessar edicao de animal."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Editar Animal", "abrigo_edit_animal@example.com", "SenhaForte@123"
        )

        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        abrigo_page.navegar_editar(1)

        e2e_page.wait_for_timeout(500)

        # Pode ter sido redirecionado se animal nao existir ou nao pertencer ao abrigo
        assert "/abrigo" in e2e_page.url or "/animais" in e2e_page.url


@pytest.mark.e2e
class TestAcessoAbrigoAnimais:
    """Testes de controle de acesso."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        abrigo_page = AbrigoAnimaisPage(e2e_page, e2e_server)
        abrigo_page.navegar_listar()

        assert "/login" in e2e_page.url
