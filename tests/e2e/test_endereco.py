"""
Testes E2E para gerenciamento de endereco do usuario.

Casos de uso cobertos:
- UC-ADDRESS-001: Visualizar proprio endereco
- UC-ADDRESS-002: Cadastrar endereco
- UC-ADDRESS-003: Editar endereco
- UC-ADDRESS-004: Excluir endereco
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    EnderecoPage,
    criar_usuario_e_logar,
)


@pytest.mark.e2e
class TestCadastrarEndereco:
    """UC-ADDRESS-002: Cadastrar endereco."""

    def test_usuario_pode_cadastrar_endereco(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir cadastrar um endereco."""
        email = "end_cadastrar@example.com"
        nome = "Usuario Cadastrar Endereco"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.cadastrar_endereco(
            titulo="Casa Principal",
            logradouro="Rua das Flores",
            numero="123",
            bairro="Centro",
            cidade="Vitoria",
            uf="ES",
            cep="29000-000"
        )

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "sucesso" in conteudo or "/visualizar" in e2e_page.url

    def test_cadastrar_endereco_campos_obrigatorios(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Cadastrar endereco sem campos obrigatorios deve exibir erro."""
        email = "end_obrig@example.com"
        nome = "Usuario End Obrigatorio"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()

        # Tentar submeter sem preencher
        endereco.submeter()

        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina de cadastro
        assert "/cadastrar" in e2e_page.url or "/endereco" in e2e_page.url


@pytest.mark.e2e
class TestVisualizarEndereco:
    """UC-ADDRESS-001: Visualizar proprio endereco."""

    def test_usuario_pode_visualizar_endereco_cadastrado(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir visualizar seu endereco cadastrado."""
        email = "end_visual@example.com"
        nome = "Usuario Visualizar Endereco"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        # Primeiro cadastrar endereco
        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.cadastrar_endereco(
            titulo="Minha Casa",
            logradouro="Av Brasil",
            numero="456",
            bairro="Jardim",
            cidade="Vila Velha",
            uf="ES",
            cep="29100-000"
        )

        e2e_page.wait_for_timeout(500)

        # Navegar para visualizar
        endereco.navegar_visualizar()

        conteudo = e2e_page.content().lower()
        assert "minha casa" in conteudo or "av brasil" in conteudo

    def test_usuario_sem_endereco_redirecionado_para_cadastro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario sem endereco deve ser redirecionado para cadastro."""
        email = "sem_end@example.com"
        nome = "Usuario Sem Endereco"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_visualizar()

        e2e_page.wait_for_timeout(500)

        # Deve ser redirecionado para cadastrar
        assert "/cadastrar" in e2e_page.url or "cadastr" in e2e_page.content().lower()


@pytest.mark.e2e
class TestEditarEndereco:
    """UC-ADDRESS-003: Editar endereco."""

    def test_usuario_pode_editar_endereco(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir editar seu endereco."""
        email = "end_editar@example.com"
        nome = "Usuario Editar Endereco"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        # Primeiro cadastrar endereco
        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.cadastrar_endereco(
            titulo="Casa Original",
            logradouro="Rua Original",
            numero="100",
            bairro="Bairro Original",
            cidade="Cidade Original",
            uf="ES",
            cep="29000-000"
        )

        e2e_page.wait_for_timeout(500)

        # Editar endereco
        endereco.navegar_editar()
        e2e_page.fill('input[name="titulo"]', "Casa Editada")
        endereco.submeter()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "sucesso" in conteudo or "casa editada" in conteudo or "/visualizar" in e2e_page.url

    def test_usuario_sem_endereco_nao_pode_editar(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario sem endereco nao deve conseguir editar."""
        email = "sem_end_edit@example.com"
        nome = "Usuario Sem End Edit"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_editar()

        e2e_page.wait_for_timeout(500)

        # Deve ser redirecionado para cadastrar
        assert "/cadastrar" in e2e_page.url


@pytest.mark.e2e
class TestExcluirEndereco:
    """UC-ADDRESS-004: Excluir endereco."""

    def test_usuario_pode_excluir_endereco(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir excluir seu endereco."""
        email = "end_excluir@example.com"
        nome = "Usuario Excluir Endereco"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        # Primeiro cadastrar endereco
        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.cadastrar_endereco(
            titulo="Casa Para Excluir",
            logradouro="Rua Excluir",
            numero="999",
            bairro="Bairro Excluir",
            cidade="Cidade Excluir",
            uf="ES",
            cep="29999-000"
        )

        e2e_page.wait_for_timeout(500)

        # Navegar para visualizar e excluir
        endereco.navegar_visualizar()
        endereco.excluir_endereco()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "sucesso" in conteudo or "/cadastrar" in e2e_page.url


@pytest.mark.e2e
class TestAcessoEndereco:
    """Testes de acesso as paginas de endereco."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()

        assert "/login" in e2e_page.url

    def test_pagina_cadastrar_endereco_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de cadastro de endereco deve carregar corretamente."""
        email = "end_form@example.com"
        nome = "Usuario End Form"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        endereco = EnderecoPage(e2e_page, e2e_server)
        endereco.navegar_cadastrar()

        expect(e2e_page.locator('input[name="titulo"]')).to_be_visible()
        expect(e2e_page.locator('input[name="logradouro"]')).to_be_visible()
        expect(e2e_page.locator('input[name="numero"]')).to_be_visible()
        expect(e2e_page.locator('select[name="uf"]')).to_be_visible()
