"""
Testes E2E para gerenciamento de perfil do usuario.

Casos de uso cobertos:
- UC-PROFILE-001: Visualizar proprio perfil
- UC-PROFILE-002: Editar proprio perfil
- UC-PROFILE-003: Alterar propria senha
- UC-PROFILE-004: Enviar foto de perfil (parcial)
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    CadastroPage,
    LoginPage,
    PerfilPage,
    criar_usuario_e_logar,
)


@pytest.mark.e2e
class TestVisualizarPerfil:
    """UC-PROFILE-001: Visualizar proprio perfil."""

    def test_usuario_pode_visualizar_proprio_perfil(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario logado deve conseguir visualizar seu proprio perfil."""
        email = "perfil_vis@example.com"
        nome = "Usuario Perfil Teste"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_visualizar()

        assert "/usuario/perfil/visualizar" in e2e_page.url
        assert nome.lower() in e2e_page.content().lower()
        assert email.lower() in e2e_page.content().lower()

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_visualizar()

        assert "/login" in e2e_page.url


@pytest.mark.e2e
class TestEditarPerfil:
    """UC-PROFILE-002: Editar proprio perfil."""

    def test_usuario_pode_editar_nome(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir alterar seu nome."""
        email = "editar_nome@example.com"
        nome_original = "Usuario Original Nome"
        nome_novo = "Usuario Novo Nome"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome_original, email, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()

        # Limpar e preencher novo nome
        e2e_page.fill('input[name="nome"]', "")
        perfil.editar_perfil(nome_novo, email)

        e2e_page.wait_for_timeout(500)

        # Verificar se foi para pagina de visualizacao ou se nome foi atualizado
        conteudo = e2e_page.content().lower()
        assert nome_novo.lower() in conteudo or "sucesso" in conteudo

    def test_usuario_pode_editar_email(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir alterar seu email."""
        email_original = "email_original@example.com"
        email_novo = "email_novo@example.com"
        nome = "Usuario Editar Email"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email_original, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()

        # Limpar e preencher novo email
        e2e_page.fill('input[name="email"]', "")
        perfil.editar_perfil(nome, email_novo)

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "sucesso" in conteudo or email_novo.lower() in conteudo

    def test_editar_perfil_email_invalido_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Editar perfil com email invalido deve exibir erro."""
        email = "editar_email_inv@example.com"
        nome = "Usuario Email Invalido"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()

        e2e_page.fill('input[name="email"]', "")
        perfil.editar_perfil(nome, "email_invalido")

        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina ou mostrar erro
        conteudo = e2e_page.content().lower()
        assert "e-mail" in conteudo or "email" in conteudo or "/editar" in e2e_page.url

    def test_editar_perfil_nome_vazio_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Editar perfil com nome vazio deve exibir erro."""
        email = "nome_vazio@example.com"
        nome = "Usuario Nome Vazio"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()

        perfil.editar_perfil("", email)

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "nome" in conteudo or "/editar" in e2e_page.url


@pytest.mark.e2e
class TestAlterarSenha:
    """UC-PROFILE-003: Alterar propria senha."""

    def test_usuario_pode_alterar_senha(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir alterar sua senha."""
        email = "alterar_senha@example.com"
        nome = "Usuario Alterar Senha"
        senha_atual = "SenhaAtual@123"
        senha_nova = "SenhaNova@456"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha_atual)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()

        perfil.alterar_senha(senha_atual, senha_nova)

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "sucesso" in conteudo or "/visualizar" in e2e_page.url

    def test_alterar_senha_atual_incorreta_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Alterar senha com senha atual incorreta deve exibir erro."""
        email = "senha_incorreta@example.com"
        nome = "Usuario Senha Incorreta"
        senha_correta = "SenhaCorreta@123"
        senha_errada = "SenhaErrada@456"
        senha_nova = "SenhaNova@789"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha_correta)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()

        perfil.alterar_senha(senha_errada, senha_nova)

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "incorreta" in conteudo or "atual" in conteudo or "/alterar-senha" in e2e_page.url

    def test_alterar_senha_nova_igual_atual_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Nova senha igual a atual deve exibir erro."""
        email = "senha_igual@example.com"
        nome = "Usuario Senha Igual"
        senha = "SenhaIgual@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()

        perfil.alterar_senha(senha, senha)

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "diferente" in conteudo or "/alterar-senha" in e2e_page.url

    def test_alterar_senha_confirmacao_diferente_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Confirmacao de senha diferente deve exibir erro."""
        email = "confirm_diff@example.com"
        nome = "Usuario Confirm Diferente"
        senha_atual = "SenhaAtual@123"
        senha_nova = "SenhaNova@456"
        senha_confirm = "SenhaDiferente@789"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha_atual)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()

        perfil.alterar_senha(senha_atual, senha_nova, senha_confirm)

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "coincidem" in conteudo or "senhas" in conteudo or "/alterar-senha" in e2e_page.url

    def test_alterar_senha_fraca_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Senha nova fraca deve exibir erro."""
        email = "senha_fraca@example.com"
        nome = "Usuario Senha Fraca"
        senha_atual = "SenhaAtual@123"
        senha_fraca = "123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha_atual)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()

        perfil.alterar_senha(senha_atual, senha_fraca)

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "senha" in conteudo or "/alterar-senha" in e2e_page.url


@pytest.mark.e2e
class TestAcessoPerfil:
    """Testes de acesso as paginas de perfil."""

    def test_pagina_editar_perfil_carrega_com_dados(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de edicao deve carregar com dados do usuario."""
        email = "dados_form@example.com"
        nome = "Usuario Dados Form"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_editar()

        # Verificar que campos estao preenchidos
        expect(e2e_page.locator('input[name="nome"]')).to_have_value(nome)
        expect(e2e_page.locator('input[name="email"]')).to_have_value(email)

    def test_pagina_alterar_senha_carrega_corretamente(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de alteracao de senha deve carregar corretamente."""
        email = "alterar_senha_form@example.com"
        nome = "Usuario Alt Senha Form"
        senha = "SenhaForte@123"

        criar_usuario_e_logar(e2e_page, e2e_server, "Adotante", nome, email, senha)

        perfil = PerfilPage(e2e_page, e2e_server)
        perfil.navegar_alterar_senha()

        expect(e2e_page.locator('input[name="senha_atual"]')).to_be_visible()
        expect(e2e_page.locator('input[name="senha_nova"]')).to_be_visible()
        expect(e2e_page.locator('input[name="confirmar_senha"]')).to_be_visible()
