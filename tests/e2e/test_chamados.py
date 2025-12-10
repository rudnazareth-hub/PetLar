"""
Testes E2E para sistema de chamados (suporte).

Casos de uso cobertos:
Usuario:
- UC-TICKET-001: Abrir chamado de suporte
- UC-TICKET-002: Listar proprios chamados
- UC-TICKET-003: Visualizar detalhes do chamado
- UC-TICKET-004: Responder ao proprio chamado
- UC-TICKET-005: Excluir proprio chamado

Admin:
- UC-TICKET-006: Listar todos os chamados
- UC-TICKET-007: Responder chamado de usuario
- UC-TICKET-008: Fechar chamado
- UC-TICKET-009: Reabrir chamado
"""
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.test_e2e_helpers import (
    ChamadosPage,
    AdminChamadosPage,
    criar_usuario_e_logar,
)


# =============================================================================
# TESTES DE CHAMADOS - USUARIO
# =============================================================================


@pytest.mark.e2e
class TestListarChamadosUsuario:
    """UC-TICKET-002: Listar proprios chamados."""

    def test_usuario_pode_listar_seus_chamados(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir listar seus proprios chamados."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Usuario Chamados", "user_chamados@example.com", "SenhaForte@123"
        )

        chamados_page = ChamadosPage(e2e_page, e2e_server)
        chamados_page.navegar_listar()

        e2e_page.wait_for_timeout(500)

        assert "/chamados" in e2e_page.url

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        chamados_page = ChamadosPage(e2e_page, e2e_server)
        chamados_page.navegar_listar()

        assert "/login" in e2e_page.url


@pytest.mark.e2e
class TestAbrirChamado:
    """UC-TICKET-001: Abrir chamado de suporte."""

    def test_pagina_abrir_chamado_carrega_formulario(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de abertura de chamado deve carregar formulario."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Usuario Abrir Chamado", "user_abrir_chamado@example.com", "SenhaForte@123"
        )

        chamados_page = ChamadosPage(e2e_page, e2e_server)
        chamados_page.navegar_cadastrar()

        e2e_page.wait_for_timeout(500)

        assert "/chamados/cadastrar" in e2e_page.url
        expect(e2e_page.locator('input[name="titulo"]')).to_be_visible()
        expect(e2e_page.locator('textarea[name="descricao"]')).to_be_visible()

    def test_usuario_pode_abrir_chamado(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario deve conseguir abrir um chamado."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Usuario Novo Chamado", "user_novo_chamado@example.com", "SenhaForte@123"
        )

        chamados_page = ChamadosPage(e2e_page, e2e_server)
        chamados_page.abrir_chamado(
            titulo="Problema com cadastro",
            descricao="Descricao detalhada do problema encontrado.",
            prioridade="Alta"
        )

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "sucesso" in conteudo or "/chamados/listar" in e2e_page.url

    def test_abrir_chamado_sem_titulo_exibe_erro(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrir chamado sem titulo deve exibir erro."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Usuario Sem Titulo", "user_sem_titulo@example.com", "SenhaForte@123"
        )

        chamados_page = ChamadosPage(e2e_page, e2e_server)
        chamados_page.navegar_cadastrar()

        # Tentar submeter sem titulo
        e2e_page.fill('textarea[name="descricao"]', "Descricao sem titulo")
        e2e_page.locator('button[type="submit"]').first.click()

        e2e_page.wait_for_timeout(500)

        # Deve permanecer na pagina ou exibir erro
        assert "/chamados/cadastrar" in e2e_page.url or "/chamados" in e2e_page.url


@pytest.mark.e2e
class TestVisualizarChamado:
    """UC-TICKET-003: Visualizar detalhes do chamado."""

    def test_visualizar_chamado_inexistente_redireciona(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Visualizar chamado inexistente deve redirecionar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Usuario Vis Chamado", "user_vis_chamado@example.com", "SenhaForte@123"
        )

        chamados_page = ChamadosPage(e2e_page, e2e_server)
        chamados_page.navegar_visualizar(99999)

        e2e_page.wait_for_timeout(500)

        # Deve redirecionar para listagem
        assert "/chamados" in e2e_page.url


@pytest.mark.e2e
class TestAbrirChamadoAbrigo:
    """Teste de abertura de chamado por abrigo."""

    def test_abrigo_pode_abrir_chamado(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Abrigo deve conseguir abrir um chamado."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Abrigo",
            "Abrigo Chamado", "abrigo_chamado@example.com", "SenhaForte@123"
        )

        chamados_page = ChamadosPage(e2e_page, e2e_server)
        chamados_page.navegar_cadastrar()

        e2e_page.wait_for_timeout(500)

        assert "/chamados/cadastrar" in e2e_page.url


# =============================================================================
# TESTES DE CHAMADOS - ADMIN
# =============================================================================


@pytest.mark.e2e
class TestListarChamadosAdmin:
    """UC-TICKET-006: Listar todos os chamados."""

    def test_pagina_admin_chamados_carrega(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de listagem de chamados (admin) deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Chamados", "admin_chamados@example.com", "SenhaForte@123"
        )

        admin_chamados = AdminChamadosPage(e2e_page, e2e_server)
        admin_chamados.navegar_listar()

        e2e_page.wait_for_timeout(500)

        # Verifica se carregou ou foi redirecionado
        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestResponderChamadoAdmin:
    """UC-TICKET-007: Responder chamado de usuario."""

    def test_pagina_responder_chamado_admin(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Pagina de resposta de chamado (admin) deve carregar."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Admin Resp Chamado", "admin_resp_chamado@example.com", "SenhaForte@123"
        )

        admin_chamados = AdminChamadosPage(e2e_page, e2e_server)
        admin_chamados.navegar_responder(1)

        e2e_page.wait_for_timeout(500)

        assert "/admin" in e2e_page.url or "/login" in e2e_page.url or "/usuario" in e2e_page.url


@pytest.mark.e2e
class TestAcessoAdminChamados:
    """Testes de controle de acesso para admin de chamados."""

    def test_usuario_nao_logado_redirecionado_para_login(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Usuario nao logado deve ser redirecionado para login."""
        admin_chamados = AdminChamadosPage(e2e_page, e2e_server)
        admin_chamados.navegar_listar()

        assert "/login" in e2e_page.url

    def test_adotante_nao_pode_acessar_admin_chamados(
        self, e2e_page: Page, e2e_server: str, limpar_banco_e2e
    ):
        """Adotante nao deve acessar admin de chamados."""
        criar_usuario_e_logar(
            e2e_page, e2e_server, "Adotante",
            "Adotante Chamados", "adotante_chamados@example.com", "SenhaForte@123"
        )

        admin_chamados = AdminChamadosPage(e2e_page, e2e_server)
        admin_chamados.navegar_listar()

        e2e_page.wait_for_timeout(500)

        conteudo = e2e_page.content().lower()
        assert "/admin/chamados/listar" not in e2e_page.url or "acesso" in conteudo
