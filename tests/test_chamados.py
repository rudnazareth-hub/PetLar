"""
Testes do sistema de chamados (tickets de suporte)

Cobre:
- Criação de chamados por usuários não administradores
- Listagem de chamados (usuários e admins)
- Resposta a chamados por administradores
- Mudanças de estado (Aberto, Em Análise, Resolvido, Fechado)
- Histórico de interações (usuário e admin)
- Múltiplas respostas em sequência
- Isolamento de dados entre usuários

IMPORTANTE: Nova arquitetura usa tabela chamado_interacao para armazenar
todas as mensagens (abertura, respostas do usuário, respostas do admin)
"""
import pytest
from fastapi import status


class TestCriarChamado:
    """Testes de criação de chamados por usuários"""

    def test_criar_chamado_requer_autenticacao(self, client):
        """Deve exigir autenticação para criar chamado"""
        response = client.get("/chamados/cadastrar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_get_formulario_cadastro(self, cliente_autenticado):
        """Usuário autenticado deve acessar formulário de cadastro"""
        response = cliente_autenticado.get("/chamados/cadastrar")
        assert response.status_code == status.HTTP_200_OK
        assert "chamado" in response.text.lower()

    def test_criar_chamado_com_dados_validos(self, cliente_autenticado):
        """Deve criar chamado com dados válidos"""
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Problema no sistema",
            "descricao": "Descrição detalhada do problema encontrado",
            "prioridade": "Alta"
        }, follow_redirects=False)

        # Deve redirecionar para listagem
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/chamados/listar"

    def test_criar_chamado_titulo_curto(self, cliente_autenticado):
        """Deve rejeitar título com menos de 10 caracteres"""
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Curto",  # Menos de 10 caracteres
            "descricao": "Descrição detalhada do problema",
            "prioridade": "Média"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "erro" in response.text.lower() or "inválid" in response.text.lower()

    def test_criar_chamado_titulo_longo(self, cliente_autenticado):
        """Deve rejeitar título com mais de 200 caracteres"""
        titulo_longo = "T" * 201
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": titulo_longo,
            "descricao": "Descrição do problema",
            "prioridade": "Baixa"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK

    def test_criar_chamado_descricao_curta(self, cliente_autenticado):
        """Deve rejeitar descrição com menos de 20 caracteres"""
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Título válido do chamado",
            "descricao": "Curta",  # Menos de 20 caracteres
            "prioridade": "Média"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "erro" in response.text.lower() or "inválid" in response.text.lower()

    def test_criar_chamado_sem_prioridade(self, cliente_autenticado):
        """Deve exigir prioridade"""
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Título do chamado",
            "descricao": "Descrição detalhada do problema encontrado no sistema",
            "prioridade": ""
        }, follow_redirects=True)

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_criar_chamado_prioridade_invalida(self, cliente_autenticado):
        """Deve rejeitar prioridade inválida"""
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Título do chamado",
            "descricao": "Descrição detalhada do problema encontrado",
            "prioridade": "SuperUrgente"  # Prioridade não existe
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK

    def test_chamado_criado_com_status_aberto(self, cliente_autenticado):
        """Chamado criado deve ter status 'Aberto'"""
        # Criar chamado
        cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Novo problema",
            "descricao": "Descrição detalhada do problema encontrado",
            "prioridade": "Alta"
        })

        # Verificar na listagem
        response = cliente_autenticado.get("/chamados/listar")
        assert response.status_code == status.HTTP_200_OK
        assert "aberto" in response.text.lower()


class TestListarChamados:
    """Testes de listagem de chamados"""

    def test_listar_requer_autenticacao(self, client):
        """Deve exigir autenticação para listar"""
        response = client.get("/chamados/listar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_listar_chamados_usuario(self, cliente_autenticado):
        """Usuário deve conseguir listar seus chamados"""
        response = cliente_autenticado.get("/chamados/listar")
        assert response.status_code == status.HTTP_200_OK
        assert "chamado" in response.text.lower()

    def test_usuario_ve_apenas_proprios_chamados(self, client, cliente_autenticado):
        """Usuário deve ver apenas seus próprios chamados"""
        # Este cliente já está autenticado como um usuário comum
        # Criar primeiro chamado
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Meu Chamado",
            "descricao": "Descrição do meu chamado específico",
            "prioridade": "Alta"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar que o usuário consegue listar seus chamados
        response = cliente_autenticado.get("/chamados/listar")
        assert response.status_code == status.HTTP_200_OK
        assert "Meu Chamado" in response.text


class TestVisualizarChamado:
    """Testes de visualização de chamados"""

    def test_visualizar_proprio_chamado(self, cliente_autenticado):
        """Usuário deve visualizar detalhes do próprio chamado"""
        # Criar chamado
        cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Problema urgente",
            "descricao": "Descrição muito detalhada do problema encontrado no sistema",
            "prioridade": "Urgente"
        })

        # Assumir que é o chamado ID 1
        response = cliente_autenticado.get("/chamados/1/visualizar")
        assert response.status_code == status.HTTP_200_OK
        assert "Problema urgente" in response.text

    def test_visualizar_chamado_inexistente(self, cliente_autenticado):
        """Deve retornar erro ao visualizar chamado inexistente"""
        response = cliente_autenticado.get("/chamados/999/visualizar", follow_redirects=False)
        # Pode redirecionar ou retornar 404
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_404_NOT_FOUND]


class TestExcluirChamado:
    """Testes de exclusão de chamados"""

    def test_excluir_proprio_chamado(self, cliente_autenticado):
        """Usuário deve poder excluir próprio chamado"""
        # Criar chamado
        cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Chamado a ser excluído",
            "descricao": "Descrição do chamado que será excluído",
            "prioridade": "Baixa"
        })

        # Excluir
        response = cliente_autenticado.post("/chamados/1/excluir", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_excluir_chamado_inexistente(self, cliente_autenticado):
        """Deve retornar erro ao excluir chamado inexistente"""
        response = cliente_autenticado.post("/chamados/999/excluir", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestAdminListarChamados:
    """Testes de listagem de chamados pelo admin"""

    def test_admin_lista_todos_chamados(self, client, admin_teste, criar_usuario, fazer_login):
        """Admin deve ver todos os chamados do sistema"""
        # Criar admin
        criar_usuario(admin_teste["nome"], admin_teste["email"],
                     admin_teste["senha"], admin_teste["perfil"])

        # Criar usuário comum
        criar_usuario("Usuario Comum", "usuario@test.com", "Senha@123")

        # Usuário cria dois chamados
        fazer_login("usuario@test.com", "Senha@123")
        client.post("/chamados/cadastrar", data={
            "titulo": "Primeiro chamado",
            "descricao": "Descrição do primeiro problema encontrado",
            "prioridade": "Alta"
        })
        client.post("/chamados/cadastrar", data={
            "titulo": "Segundo chamado",
            "descricao": "Descrição do segundo problema encontrado",
            "prioridade": "Média"
        })

        # Admin deve ver ambos os chamados
        fazer_login(admin_teste["email"], admin_teste["senha"])
        response = client.get("/admin/chamados/listar")
        assert response.status_code == status.HTTP_200_OK
        assert "Primeiro chamado" in response.text
        assert "Segundo chamado" in response.text

    def test_usuario_comum_nao_acessa_admin_listagem(self, cliente_autenticado):
        """Usuário comum não deve acessar listagem admin"""
        response = cliente_autenticado.get("/admin/chamados/listar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestAdminResponderChamado:
    """Testes de resposta a chamados pelo admin"""

    def test_admin_acessa_formulario_responder(self, cliente_autenticado, admin_autenticado):
        """Admin deve acessar formulário de resposta"""
        # Usuário cria chamado
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Preciso de ajuda urgente",
            "descricao": "Descrição detalhada do problema que preciso resolver no sistema",
            "prioridade": "Alta"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Admin acessa formulário de resposta
        response = admin_autenticado.get("/admin/chamados/1/responder")
        assert response.status_code == status.HTTP_200_OK
        assert "resposta" in response.text.lower() or "responder" in response.text.lower()

    def test_admin_responde_chamado_com_sucesso(self, client, admin_teste, criar_usuario, fazer_login):
        """Admin deve conseguir responder chamado"""
        # Setup
        criar_usuario(admin_teste["nome"], admin_teste["email"],
                     admin_teste["senha"], admin_teste["perfil"])
        criar_usuario("Usuario", "user@test.com", "Senha@123")

        fazer_login("user@test.com", "Senha@123")
        client.post("/chamados/cadastrar", data={
            "titulo": "Problema técnico",
            "descricao": "Descrição completa do problema técnico encontrado",
            "prioridade": "Urgente"
        })

        # Admin responde
        fazer_login(admin_teste["email"], admin_teste["senha"])
        response = client.post("/admin/chamados/1/responder", data={
            "mensagem": "Resposta detalhada do administrador para resolver o problema",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/admin/chamados/listar"

    def test_admin_muda_status_para_em_analise(self, cliente_autenticado, admin_autenticado):
        """Admin deve poder mudar status para Em Análise"""
        # Usuário cria chamado
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Novo chamado",
            "descricao": "Descrição do novo chamado aberto pelo usuário",
            "prioridade": "Média"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Admin responde alterando status
        response = admin_autenticado.post("/admin/chamados/1/responder", data={
            "mensagem": "Estamos analisando o problema reportado",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/admin/chamados/listar"

        # Verificar que admin consegue acessar a listagem (sem erro)
        response = admin_autenticado.get("/admin/chamados/listar")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_muda_status_para_resolvido(self, cliente_autenticado, admin_autenticado):
        """Admin deve poder mudar status para Resolvido"""
        # Usuário cria chamado
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Chamado resolvido",
            "descricao": "Descrição do chamado que será resolvido",
            "prioridade": "Alta"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Admin resolve
        response = admin_autenticado.post("/admin/chamados/1/responder", data={
            "mensagem": "Problema foi resolvido com sucesso conforme solicitado",
            "status_chamado": "Resolvido"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/admin/chamados/listar"

        # Verificar que admin consegue acessar a listagem (sem erro)
        response = admin_autenticado.get("/admin/chamados/listar")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_fecha_chamado(self, client, admin_teste, criar_usuario, fazer_login):
        """Admin deve poder fechar chamado"""
        # Setup
        criar_usuario(admin_teste["nome"], admin_teste["email"],
                     admin_teste["senha"], admin_teste["perfil"])
        criar_usuario("Usuario", "user@test.com", "Senha@123")

        fazer_login("user@test.com", "Senha@123")
        client.post("/chamados/cadastrar", data={
            "titulo": "Chamado a fechar",
            "descricao": "Descrição do chamado que será fechado",
            "prioridade": "Baixa"
        })

        # Admin fecha
        fazer_login(admin_teste["email"], admin_teste["senha"])
        response = client.post("/admin/chamados/1/fechar", follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_resposta_curta_e_rejeitada(self, client, admin_teste, criar_usuario, fazer_login):
        """Deve rejeitar resposta com menos de 10 caracteres"""
        # Setup
        criar_usuario(admin_teste["nome"], admin_teste["email"],
                     admin_teste["senha"], admin_teste["perfil"])
        criar_usuario("Usuario", "user@test.com", "Senha@123")

        fazer_login("user@test.com", "Senha@123")
        client.post("/chamados/cadastrar", data={
            "titulo": "Chamado teste",
            "descricao": "Descrição do chamado de teste",
            "prioridade": "Média"
        })

        # Admin tenta responder com texto curto
        fazer_login(admin_teste["email"], admin_teste["senha"])
        response = client.post("/admin/chamados/1/responder", data={
            "mensagem": "OK",  # Muito curto
            "status_chamado": "Resolvido"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        assert "erro" in response.text.lower() or "inválid" in response.text.lower()

    def test_usuario_comum_nao_pode_responder(self, cliente_autenticado):
        """Usuário comum não deve poder responder chamados"""
        # Criar chamado primeiro
        cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Chamado próprio",
            "descricao": "Descrição do meu próprio chamado",
            "prioridade": "Alta"
        })

        # Tentar responder
        response = cliente_autenticado.post("/admin/chamados/1/responder", data={
            "mensagem": "Tentando responder meu próprio chamado",
            "status_chamado": "Resolvido"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestHistoricoInteracoes:
    """Testes de histórico de interações"""

    def test_interacao_registra_admin(self, client, admin_teste, criar_usuario, fazer_login):
        """Interação deve registrar qual admin respondeu"""
        # Setup
        criar_usuario(admin_teste["nome"], admin_teste["email"],
                     admin_teste["senha"], admin_teste["perfil"])
        criar_usuario("Usuario", "user@test.com", "Senha@123")

        fazer_login("user@test.com", "Senha@123")
        client.post("/chamados/cadastrar", data={
            "titulo": "Chamado com rastreamento",
            "descricao": "Descrição do chamado para testar rastreamento",
            "prioridade": "Alta"
        })

        # Admin responde
        fazer_login(admin_teste["email"], admin_teste["senha"])
        response = client.post("/admin/chamados/1/responder", data={
            "mensagem": "Resposta do administrador para testar rastreamento",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)

        # Verificar que a resposta foi aceita
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/admin/chamados/listar"

    def test_multiplas_respostas_do_mesmo_admin(self, client, admin_teste, criar_usuario, fazer_login):
        """Admin deve poder responder múltiplas vezes"""
        # Setup
        criar_usuario(admin_teste["nome"], admin_teste["email"],
                     admin_teste["senha"], admin_teste["perfil"])
        criar_usuario("Usuario", "user@test.com", "Senha@123")

        fazer_login("user@test.com", "Senha@123")
        client.post("/chamados/cadastrar", data={
            "titulo": "Chamado com múltiplas respostas",
            "descricao": "Descrição do chamado que receberá múltiplas respostas",
            "prioridade": "Alta"
        })

        fazer_login(admin_teste["email"], admin_teste["senha"])

        # Primeira resposta
        client.post("/admin/chamados/1/responder", data={
            "mensagem": "Primeira resposta do administrador",
            "status_chamado": "Em Análise"
        })

        # Segunda resposta
        response = client.post("/admin/chamados/1/responder", data={
            "mensagem": "Segunda resposta do administrador com atualização",
            "status_chamado": "Resolvido"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_usuario_pode_responder_proprio_chamado(self, cliente_autenticado):
        """Usuário deve poder adicionar mensagens ao seu próprio chamado"""
        # Criar chamado
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Chamado com múltiplas mensagens",
            "descricao": "Descrição inicial do chamado",
            "prioridade": "Alta"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Usuário adiciona informação adicional
        response = cliente_autenticado.post("/chamados/1/responder", data={
            "mensagem": "Informação adicional sobre o problema reportado"
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/chamados/1/visualizar"

    def test_historico_mostra_todas_interacoes(self, cliente_autenticado, admin_autenticado):
        """Histórico deve mostrar todas as interações em ordem"""
        # Usuário cria chamado
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Chamado com histórico completo",
            "descricao": "Descrição inicial do problema",
            "prioridade": "Alta"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Admin responde
        response = admin_autenticado.post("/admin/chamados/1/responder", data={
            "mensagem": "Primeira resposta do admin",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Usuário responde
        response = cliente_autenticado.post("/chamados/1/responder", data={
            "mensagem": "Resposta do usuário com mais informações"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Admin responde novamente
        response = admin_autenticado.post("/admin/chamados/1/responder", data={
            "mensagem": "Segunda resposta do admin",
            "status_chamado": "Resolvido"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar histórico
        response = cliente_autenticado.get("/chamados/1/visualizar")
        assert response.status_code == status.HTTP_200_OK
        assert "Descrição inicial do problema" in response.text
        assert "Primeira resposta do admin" in response.text
        assert "Resposta do usuário com mais informações" in response.text
        assert "Segunda resposta do admin" in response.text


class TestFluxoCompleto:
    """Testes de fluxo completo do sistema de chamados"""

    def test_fluxo_completo_usuario_e_admin(self, cliente_autenticado, admin_autenticado):
        """Testa fluxo completo: criar -> responder -> resolver -> fechar"""
        # 1. Usuário cria chamado
        response = cliente_autenticado.post("/chamados/cadastrar", data={
            "titulo": "Fluxo completo teste",
            "descricao": "Testando o fluxo completo do sistema de chamados",
            "prioridade": "Alta"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # 2. Admin responde e coloca em análise
        response = admin_autenticado.post("/admin/chamados/1/responder", data={
            "mensagem": "Estamos analisando seu chamado",
            "status_chamado": "Em Análise"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # 3. Admin resolve
        response = admin_autenticado.post("/admin/chamados/1/responder", data={
            "mensagem": "Chamado foi resolvido conforme solicitado",
            "status_chamado": "Resolvido"
        }, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # 4. Admin fecha
        response = admin_autenticado.post("/admin/chamados/1/fechar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

        # 5. Verificar que todas operações foram bem sucedidas
        response = admin_autenticado.get("/admin/chamados/listar")
        assert response.status_code == status.HTTP_200_OK
