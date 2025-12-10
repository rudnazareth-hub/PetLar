"""
Funcoes auxiliares e Page Objects para testes E2E.

Fornece helpers para interacoes comuns com a UI.
"""
from typing import Optional

from playwright.sync_api import Page, expect


class BasePage:
    """Classe base para Page Objects."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def obter_mensagem_flash(self) -> Optional[str]:
        """Obtem mensagem flash (toast ou alert)."""
        toast = self.page.locator('.toast-body').first
        if toast.is_visible():
            return toast.text_content()

        alert = self.page.locator('.alert').first
        if alert.is_visible():
            return alert.text_content()

        return None

    def contem_texto(self, texto: str) -> bool:
        """Verifica se a pagina contem o texto especificado."""
        conteudo = self.page.content().lower()
        return texto.lower() in conteudo


class CadastroPage(BasePage):
    """Page Object para a pagina de cadastro."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.url = f"{base_url}/cadastrar"

    def navegar(self) -> None:
        """Navega para a pagina de cadastro."""
        self.page.goto(self.url)

    def preencher_formulario(
        self,
        perfil: str,
        nome: str,
        email: str,
        senha: str,
        confirmar_senha: Optional[str] = None
    ) -> None:
        """Preenche o formulario de cadastro."""
        if confirmar_senha is None:
            confirmar_senha = senha

        self.page.locator(f'label[for="perfil_{perfil}"]').click()
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="senha"]', senha)
        self.page.fill('input[name="confirmar_senha"]', confirmar_senha)

    def submeter(self) -> None:
        """Submete o formulario."""
        self.page.get_by_role("button", name="Criar Conta").click()

    def cadastrar(
        self,
        perfil: str,
        nome: str,
        email: str,
        senha: str,
        confirmar_senha: Optional[str] = None
    ) -> None:
        """Realiza cadastro completo: preenche e submete."""
        self.preencher_formulario(perfil, nome, email, senha, confirmar_senha)
        self.submeter()

    def obter_mensagem_erro_campo(self, campo: str) -> Optional[str]:
        """Obtem mensagem de erro de um campo especifico."""
        seletor = f'input[name="{campo}"] ~ .invalid-feedback'
        elemento = self.page.locator(seletor).first

        if elemento.is_visible():
            return elemento.text_content()
        return None

    def aguardar_navegacao_login(self, timeout: int = 5000) -> bool:
        """Aguarda redirecionamento para pagina de login."""
        try:
            self.page.wait_for_url("**/login**", timeout=timeout)
            return True
        except Exception:
            return False


class LoginPage(BasePage):
    """Page Object para a pagina de login."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.url = f"{base_url}/login"

    def navegar(self) -> None:
        """Navega para a pagina de login."""
        self.page.goto(self.url)

    def preencher_formulario(self, email: str, senha: str) -> None:
        """Preenche o formulario de login sem submeter."""
        self.page.wait_for_selector('input[name="email"]')
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="senha"]', senha)

    def submeter(self) -> None:
        """Submete o formulario de login."""
        self.page.locator('form button[type="submit"]').first.click()

    def fazer_login(self, email: str, senha: str) -> None:
        """Preenche e submete formulario de login."""
        self.navegar()
        self.preencher_formulario(email, senha)
        self.submeter()

    def esta_na_pagina_login(self) -> bool:
        """Verifica se esta na pagina de login."""
        return "/login" in self.page.url

    def aguardar_navegacao_usuario(self, timeout: int = 10000) -> bool:
        """Aguarda redirecionamento para area do usuario."""
        try:
            self.page.wait_for_url("**/usuario**", timeout=timeout)
            self.page.wait_for_load_state("domcontentloaded")
            return True
        except Exception:
            return "/usuario" in self.page.url or "/home" in self.page.url


class PerfilPage(BasePage):
    """Page Object para paginas de perfil do usuario."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_visualizar(self) -> None:
        """Navega para pagina de visualizacao do perfil."""
        self.page.goto(f"{self.base_url}/usuario/perfil/visualizar")

    def navegar_editar(self) -> None:
        """Navega para pagina de edicao do perfil."""
        self.page.goto(f"{self.base_url}/usuario/perfil/editar")

    def navegar_alterar_senha(self) -> None:
        """Navega para pagina de alteracao de senha."""
        self.page.goto(f"{self.base_url}/usuario/perfil/alterar-senha")

    def editar_perfil(self, nome: str, email: str) -> None:
        """Preenche e submete formulario de edicao de perfil."""
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('input[name="email"]', email)
        self.page.locator('button[type="submit"]').first.click()

    def alterar_senha(self, senha_atual: str, senha_nova: str, confirmar_senha: Optional[str] = None) -> None:
        """Preenche e submete formulario de alteracao de senha."""
        if confirmar_senha is None:
            confirmar_senha = senha_nova

        self.page.fill('input[name="senha_atual"]', senha_atual)
        self.page.fill('input[name="senha_nova"]', senha_nova)
        self.page.fill('input[name="confirmar_senha"]', confirmar_senha)
        self.page.locator('button[type="submit"]').first.click()


class EnderecoPage(BasePage):
    """Page Object para paginas de endereco do usuario."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_visualizar(self) -> None:
        """Navega para pagina de visualizacao do endereco."""
        self.page.goto(f"{self.base_url}/usuario/endereco/visualizar")
        self.page.wait_for_load_state("domcontentloaded")

    def navegar_cadastrar(self) -> None:
        """Navega para pagina de cadastro de endereco."""
        self.page.goto(f"{self.base_url}/usuario/endereco/cadastrar")
        self.page.wait_for_load_state("domcontentloaded")

    def navegar_editar(self) -> None:
        """Navega para pagina de edicao do endereco."""
        self.page.goto(f"{self.base_url}/usuario/endereco/editar")
        self.page.wait_for_load_state("domcontentloaded")

    def preencher_formulario(
        self,
        titulo: str,
        logradouro: str,
        numero: str,
        bairro: str,
        cidade: str,
        uf: str,
        cep: str,
        complemento: str = ""
    ) -> None:
        """Preenche o formulario de endereco."""
        # Aguarda o campo titulo estar visível antes de preencher
        # Usa seletor mais generico que funciona tanto em cadastro quanto edicao
        try:
            self.page.wait_for_selector(
                'input[name="titulo"]',
                timeout=15000
            )
        except Exception as e:
            # Debug: mostrar URL atual e conteúdo completo da página
            current_url = self.page.url
            page_content = self.page.content()
            # Se for página de erro, capturar mais detalhes
            if "Erro" in page_content or "error" in page_content.lower():
                raise Exception(
                    f"Página de erro detectada. URL: {current_url}. "
                    f"Conteudo completo: {page_content}"
                ) from e
            raise Exception(
                f"Campo titulo nao encontrado. URL atual: {current_url}. "
                f"Conteudo (primeiros 2000 chars): {page_content[:2000]}"
            ) from e
        self.page.fill('input[name="titulo"]', titulo)
        self.page.fill('input[name="logradouro"]', logradouro)
        self.page.fill('input[name="numero"]', numero)
        self.page.fill('input[name="complemento"]', complemento)
        self.page.fill('input[name="bairro"]', bairro)
        self.page.fill('input[name="cidade"]', cidade)
        self.page.select_option('select[name="uf"]', uf)
        self.page.fill('input[name="cep"]', cep)

    def submeter(self) -> None:
        """Submete o formulario de endereco."""
        # Usa seletor mais generico - primeiro botao submit dentro do card-footer
        self.page.locator('.card-footer button[type="submit"]').first.click()

    def cadastrar_endereco(
        self,
        titulo: str,
        logradouro: str,
        numero: str,
        bairro: str,
        cidade: str,
        uf: str,
        cep: str,
        complemento: str = ""
    ) -> None:
        """Cadastra um novo endereco."""
        self.navegar_cadastrar()
        self.preencher_formulario(titulo, logradouro, numero, bairro, cidade, uf, cep, complemento)
        self.submeter()

    def excluir_endereco(self) -> None:
        """Exclui o endereco atual."""
        self.page.locator('form[action*="excluir"] button[type="submit"]').click()


class AdminUsuariosPage(BasePage):
    """Page Object para paginas de administracao de usuarios."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de usuarios."""
        self.page.goto(f"{self.base_url}/admin/usuarios/listar")

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de usuario."""
        self.page.goto(f"{self.base_url}/admin/usuarios/cadastrar")

    def navegar_editar(self, id: int) -> None:
        """Navega para edicao de usuario."""
        self.page.goto(f"{self.base_url}/admin/usuarios/editar/{id}")

    def cadastrar_usuario(self, nome: str, email: str, senha: str, perfil: str) -> None:
        """Cadastra um novo usuario."""
        self.navegar_cadastrar()
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('input[name="email"]', email)
        self.page.fill('input[name="senha"]', senha)
        self.page.select_option('select[name="perfil"]', perfil)
        self.page.locator('button[type="submit"]').first.click()

    def editar_usuario(self, id: int, nome: str, email: str, perfil: str) -> None:
        """Edita um usuario existente."""
        self.navegar_editar(id)
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('input[name="email"]', email)
        self.page.select_option('select[name="perfil"]', perfil)
        self.page.locator('button[type="submit"]').first.click()

    def excluir_usuario(self, id: int) -> None:
        """Exclui um usuario."""
        self.page.locator(f'form[action*="/admin/usuarios/excluir/{id}"] button[type="submit"]').click()


class AdminEspeciesPage(BasePage):
    """Page Object para paginas de administracao de especies."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de especies."""
        self.page.goto(f"{self.base_url}/admin/especies/listar")

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de especie."""
        self.page.goto(f"{self.base_url}/admin/especies/cadastrar")

    def navegar_editar(self, id: int) -> None:
        """Navega para edicao de especie."""
        self.page.goto(f"{self.base_url}/admin/especies/editar/{id}")

    def cadastrar_especie(self, nome: str, descricao: str = "") -> None:
        """Cadastra uma nova especie."""
        self.navegar_cadastrar()
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('textarea[name="descricao"]', descricao)
        self.page.locator('button[type="submit"]').first.click()

    def editar_especie(self, id: int, nome: str, descricao: str = "") -> None:
        """Edita uma especie existente."""
        self.navegar_editar(id)
        self.page.fill('input[name="nome"]', nome)
        self.page.fill('textarea[name="descricao"]', descricao)
        self.page.locator('button[type="submit"]').first.click()

    def excluir_especie(self, id: int) -> None:
        """Exclui uma especie."""
        self.page.locator(f'form[action*="/admin/especies/excluir/{id}"] button[type="submit"]').click()


class AdminRacasPage(BasePage):
    """Page Object para paginas de administracao de racas."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de racas."""
        self.page.goto(f"{self.base_url}/admin/racas/listar")

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de raca."""
        self.page.goto(f"{self.base_url}/admin/racas/cadastrar")

    def navegar_editar(self, id: int) -> None:
        """Navega para edicao de raca."""
        self.page.goto(f"{self.base_url}/admin/racas/editar/{id}")

    def cadastrar_raca(
        self,
        nome: str,
        especie_id: str,
        descricao: str = "",
        temperamento: str = "",
        expectativa_vida: str = "",
        porte: str = ""
    ) -> None:
        """Cadastra uma nova raca."""
        self.navegar_cadastrar()
        self.page.fill('input[name="nome"]', nome)
        self.page.select_option('select[name="id_especie"]', especie_id)
        if descricao:
            self.page.fill('textarea[name="descricao"]', descricao)
        if temperamento:
            self.page.fill('input[name="temperamento"]', temperamento)
        if expectativa_vida:
            self.page.fill('input[name="expectativa_vida"]', expectativa_vida)
        if porte:
            self.page.select_option('select[name="porte"]', porte)
        self.page.locator('button[type="submit"]').first.click()


class ChamadosPage(BasePage):
    """Page Object para paginas de chamados."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de chamados."""
        self.page.goto(f"{self.base_url}/chamados/listar")

    def navegar_cadastrar(self) -> None:
        """Navega para abertura de chamado."""
        self.page.goto(f"{self.base_url}/chamados/cadastrar")

    def navegar_visualizar(self, id: int) -> None:
        """Navega para visualizacao de chamado."""
        self.page.goto(f"{self.base_url}/chamados/{id}/visualizar")

    def abrir_chamado(self, titulo: str, descricao: str, prioridade: str = "Media") -> None:
        """Abre um novo chamado."""
        self.navegar_cadastrar()
        self.page.fill('input[name="titulo"]', titulo)
        self.page.fill('textarea[name="descricao"]', descricao)
        self.page.select_option('select[name="prioridade"]', prioridade)
        self.page.locator('button[type="submit"]').first.click()

    def responder_chamado(self, id: int, mensagem: str) -> None:
        """Responde a um chamado."""
        self.navegar_visualizar(id)
        self.page.fill('textarea[name="mensagem"]', mensagem)
        self.page.locator('form[action*="responder"] button[type="submit"]').first.click()

    def excluir_chamado(self, id: int) -> None:
        """Exclui um chamado."""
        self.page.locator(f'form[action*="/chamados/{id}/excluir"] button[type="submit"]').click()


class AdminChamadosPage(BasePage):
    """Page Object para paginas de administracao de chamados."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de chamados (admin)."""
        self.page.goto(f"{self.base_url}/admin/chamados/listar")

    def navegar_responder(self, id: int) -> None:
        """Navega para resposta de chamado (admin)."""
        self.page.goto(f"{self.base_url}/admin/chamados/{id}/responder")

    def responder_chamado(self, id: int, mensagem: str) -> None:
        """Admin responde a um chamado."""
        self.navegar_responder(id)
        self.page.fill('textarea[name="mensagem"]', mensagem)
        self.page.locator('button[type="submit"]').first.click()

    def fechar_chamado(self, id: int) -> None:
        """Fecha um chamado."""
        self.page.locator(f'form[action*="/admin/chamados/{id}/fechar"] button[type="submit"]').click()

    def reabrir_chamado(self, id: int) -> None:
        """Reabre um chamado."""
        self.page.locator(f'form[action*="/admin/chamados/{id}/reabrir"] button[type="submit"]').click()


class AnimaisPublicPage(BasePage):
    """Page Object para paginas publicas de animais."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem publica de animais."""
        self.page.goto(f"{self.base_url}/animais")

    def navegar_detalhes(self, id: int) -> None:
        """Navega para detalhes de um animal."""
        self.page.goto(f"{self.base_url}/animais/{id}")

    def filtrar_por_especie(self, especie_id: str) -> None:
        """Filtra animais por especie."""
        self.page.select_option('select[name="especie"]', especie_id)
        self.page.locator('button[type="submit"]').first.click()

    def reservar_animal(self, id: int) -> None:
        """Reserva um animal para adocao."""
        self.navegar_detalhes(id)
        self.page.locator('form[action*="reservar"] button[type="submit"]').click()


class AbrigoAnimaisPage(BasePage):
    """Page Object para paginas de animais do abrigo."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de animais do abrigo."""
        self.page.goto(f"{self.base_url}/abrigo/animais/listar")

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de animal."""
        self.page.goto(f"{self.base_url}/abrigo/animais/cadastrar")

    def navegar_editar(self, id: int) -> None:
        """Navega para edicao de animal."""
        self.page.goto(f"{self.base_url}/abrigo/animais/editar/{id}")

    def navegar_visualizar(self, id: int) -> None:
        """Navega para visualizacao de animal."""
        self.page.goto(f"{self.base_url}/abrigo/animais/visualizar/{id}")

    def navegar_reservados(self) -> None:
        """Navega para lista de animais reservados."""
        self.page.goto(f"{self.base_url}/abrigo/animais/reservados")

    def cadastrar_animal(
        self,
        nome: str,
        raca_id: str,
        sexo: str,
        data_nascimento: str,
        data_entrada: str,
        observacoes: str = ""
    ) -> None:
        """Cadastra um novo animal."""
        self.navegar_cadastrar()
        self.page.fill('input[name="nome"]', nome)
        self.page.select_option('select[name="id_raca"]', raca_id)
        self.page.select_option('select[name="sexo"]', sexo)
        self.page.fill('input[name="data_nascimento"]', data_nascimento)
        self.page.fill('input[name="data_entrada"]', data_entrada)
        if observacoes:
            self.page.fill('textarea[name="observacoes"]', observacoes)
        self.page.locator('button[type="submit"]').first.click()


class AdminAnimaisPage(BasePage):
    """Page Object para paginas de administracao de animais."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de animais (admin)."""
        self.page.goto(f"{self.base_url}/admin/animais/listar")

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de animal."""
        self.page.goto(f"{self.base_url}/admin/animais/cadastrar")

    def navegar_editar(self, id: int) -> None:
        """Navega para edicao de animal."""
        self.page.goto(f"{self.base_url}/admin/animais/editar/{id}")

    def navegar_visualizar(self, id: int) -> None:
        """Navega para visualizacao de animal."""
        self.page.goto(f"{self.base_url}/admin/animais/visualizar/{id}")

    def alterar_status(self, id: int, status: str) -> None:
        """Altera o status de um animal."""
        self.page.select_option(f'select[name="status_{id}"]', status)
        self.page.locator(f'form[action*="/admin/animais/alterar-status/{id}"] button').click()


class AdminSolicitacoesPage(BasePage):
    """Page Object para paginas de administracao de solicitacoes."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de solicitacoes."""
        self.page.goto(f"{self.base_url}/admin/solicitacoes/listar")

    def navegar_visualizar(self, id: int) -> None:
        """Navega para visualizacao de solicitacao."""
        self.page.goto(f"{self.base_url}/admin/solicitacoes/visualizar/{id}")

    def aprovar_solicitacao(self, id: int) -> None:
        """Aprova uma solicitacao de adocao."""
        self.page.locator(f'form[action*="/admin/solicitacoes/aprovar/{id}"] button').click()

    def rejeitar_solicitacao(self, id: int, motivo: str = "") -> None:
        """Rejeita uma solicitacao de adocao."""
        if motivo:
            self.page.fill(f'textarea[name="motivo_{id}"]', motivo)
        self.page.locator(f'form[action*="/admin/solicitacoes/rejeitar/{id}"] button').click()

    def cancelar_solicitacao(self, id: int) -> None:
        """Cancela uma solicitacao de adocao."""
        self.page.locator(f'form[action*="/admin/solicitacoes/cancelar/{id}"] button').click()


class AdminAdotantesPage(BasePage):
    """Page Object para paginas de administracao de adotantes."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de adotantes."""
        self.page.goto(f"{self.base_url}/admin/adotantes/listar")

    def navegar_visualizar(self, id: int) -> None:
        """Navega para visualizacao de adotante."""
        self.page.goto(f"{self.base_url}/admin/adotantes/visualizar/{id}")


class AdminAbrigosPage(BasePage):
    """Page Object para paginas de administracao de abrigos."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de abrigos."""
        self.page.goto(f"{self.base_url}/admin/abrigos/listar")


class AdminConfiguracoesPage(BasePage):
    """Page Object para paginas de configuracoes do sistema."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar(self) -> None:
        """Navega para configuracoes do sistema."""
        self.page.goto(f"{self.base_url}/admin/configuracoes")

    def navegar_tema(self) -> None:
        """Navega para configuracao de tema."""
        self.page.goto(f"{self.base_url}/admin/tema")

    def navegar_auditoria(self) -> None:
        """Navega para log de auditoria."""
        self.page.goto(f"{self.base_url}/admin/auditoria")


class AdminBackupsPage(BasePage):
    """Page Object para paginas de backups."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de backups."""
        self.page.goto(f"{self.base_url}/admin/backups/listar")

    def criar_backup(self) -> None:
        """Cria um novo backup."""
        self.page.locator('form[action*="/admin/backups/criar"] button').click()


class AdminCurtidasPage(BasePage):
    """Page Object para paginas de administracao de curtidas."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_listar(self) -> None:
        """Navega para listagem de curtidas."""
        self.page.goto(f"{self.base_url}/admin/curtidas/listar")

    def navegar_cadastrar(self) -> None:
        """Navega para cadastro de curtida."""
        self.page.goto(f"{self.base_url}/admin/curtidas/cadastrar")


class ChatPage(BasePage):
    """Page Object para paginas de chat."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_conversas(self) -> None:
        """Navega para listagem de conversas."""
        self.page.goto(f"{self.base_url}/chat/conversas")


class PublicPage(BasePage):
    """Page Object para paginas publicas."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def navegar_home(self) -> None:
        """Navega para pagina inicial."""
        self.page.goto(f"{self.base_url}/")

    def navegar_sobre(self) -> None:
        """Navega para pagina sobre."""
        self.page.goto(f"{self.base_url}/sobre")


# =============================================================================
# Funcoes auxiliares
# =============================================================================


def verificar_mensagem_sucesso_cadastro(page: Page) -> bool:
    """Verifica se a mensagem de sucesso do cadastro foi exibida."""
    try:
        toast = page.locator('.toast-body')
        if toast.is_visible():
            texto = toast.text_content() or ""
            return "cadastro realizado com sucesso" in texto.lower()

        alert = page.locator('.alert-success')
        if alert.is_visible():
            texto = alert.text_content() or ""
            return "cadastro realizado com sucesso" in texto.lower()
    except Exception:
        pass

    return False


def verificar_erro_email_duplicado(page: Page) -> bool:
    """Verifica se apareceu erro de e-mail duplicado."""
    try:
        conteudo = page.content().lower()
        return "e-mail" in conteudo and "cadastrado" in conteudo
    except Exception:
        return False


def verificar_erro_senhas_diferentes(page: Page) -> bool:
    """Verifica se apareceu erro de senhas nao coincidentes."""
    try:
        conteudo = page.content().lower()
        return "senhas" in conteudo and "coincidem" in conteudo
    except Exception:
        return False


def criar_usuario_e_logar(
    page: Page,
    base_url: str,
    perfil: str,
    nome: str,
    email: str,
    senha: str
) -> None:
    """Cria um usuario e faz login."""
    cadastro = CadastroPage(page, base_url)
    cadastro.navegar()
    cadastro.cadastrar(perfil, nome, email, senha)
    cadastro.aguardar_navegacao_login()

    login = LoginPage(page, base_url)
    login.fazer_login(email, senha)
    login.aguardar_navegacao_usuario()


def fazer_logout(page: Page, base_url: str) -> None:
    """Faz logout do usuario atual."""
    page.goto(f"{base_url}/logout")
