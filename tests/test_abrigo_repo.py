"""
Testes para o repositório de abrigos.

Testa todas as operações CRUD do abrigo_repo,
incluindo models e SQLs relacionados.
"""

import pytest
from model.abrigo_model import Abrigo
from repo import abrigo_repo, usuario_repo
from model.usuario_model import Usuario
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_abrigos():
    """Limpa tabelas de abrigos e usuários antes de cada teste."""
    # Criar tabelas se não existirem
    usuario_repo.criar_tabela()
    abrigo_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario")  # primeiro usuario pois abrigo depende dele
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario")


@pytest.fixture
def usuario_abrigo():
    """Fixture que cria um usuário com perfil ABRIGO."""
    usuario = Usuario(
        id=0,
        nome="Abrigo Cão Feliz",
        email="cao.feliz@abrigo.com",
        senha="senha_hash",
        perfil="ABRIGO"
    )
    id_usuario = usuario_repo.inserir(usuario)
    return id_usuario


@pytest.fixture
def usuario_abrigo2():
    """Fixture que cria um segundo usuário com perfil ABRIGO."""
    usuario = Usuario(
        id=0,
        nome="Abrigo Pet Amigo",
        email="pet.amigo@abrigo.com",
        senha="senha_hash",
        perfil="ABRIGO"
    )
    id_usuario = usuario_repo.inserir(usuario)
    return id_usuario


class TestCriarTabela:
    """Testes para criação da tabela abrigo."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = abrigo_repo.criar_tabela()
        assert resultado is True

    def test_tabela_existe_apos_criacao(self):
        """Tabela deve existir após criação."""
        abrigo_repo.criar_tabela()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='abrigo'"
            )
            tabela = cursor.fetchone()
            assert tabela is not None
            assert tabela["name"] == "abrigo"


class TestInserir:
    """Testes para inserção de abrigos."""

    def test_inserir_abrigo_completo(self, usuario_abrigo):
        """Deve inserir abrigo com todos os campos."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="João Silva",
            descricao="Abrigo dedicado ao resgate de cães",
            data_abertura="2020-05-15",
            data_membros="Maria, José, Ana"
        )
        id_inserido = abrigo_repo.inserir(abrigo)

        assert id_inserido == usuario_abrigo
        abrigo_bd = abrigo_repo.obter_por_id(id_inserido)
        assert abrigo_bd is not None
        assert abrigo_bd.responsavel == "João Silva"
        assert abrigo_bd.descricao == "Abrigo dedicado ao resgate de cães"
        assert abrigo_bd.data_abertura == "2020-05-15"
        assert abrigo_bd.data_membros == "Maria, José, Ana"

    def test_inserir_abrigo_campos_minimos(self, usuario_abrigo):
        """Deve inserir abrigo apenas com campos obrigatórios."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Maria Santos",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        id_inserido = abrigo_repo.inserir(abrigo)

        assert id_inserido == usuario_abrigo
        abrigo_bd = abrigo_repo.obter_por_id(id_inserido)
        assert abrigo_bd is not None
        assert abrigo_bd.responsavel == "Maria Santos"
        assert abrigo_bd.descricao is None
        assert abrigo_bd.data_abertura is None
        assert abrigo_bd.data_membros is None

    def test_inserir_usa_id_usuario(self, usuario_abrigo):
        """Deve usar ID do usuário como ID do abrigo."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Pedro Lima",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        id_inserido = abrigo_repo.inserir(abrigo)

        assert id_inserido == usuario_abrigo


class TestObterPorId:
    """Testes para busca de abrigo por ID."""

    def test_obter_abrigo_existente(self, usuario_abrigo):
        """Deve retornar abrigo existente."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Ana Costa",
            descricao="Resgate de animais abandonados",
            data_abertura="2019-03-20",
            data_membros="Carlos, Beatriz"
        )
        abrigo_repo.inserir(abrigo)

        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo)

        assert abrigo_bd is not None
        assert abrigo_bd.id_abrigo == usuario_abrigo
        assert abrigo_bd.responsavel == "Ana Costa"
        assert abrigo_bd.descricao == "Resgate de animais abandonados"
        assert abrigo_bd.data_abertura == "2019-03-20"
        assert abrigo_bd.data_membros == "Carlos, Beatriz"

    def test_obter_abrigo_inexistente(self):
        """Deve retornar None para ID inexistente."""
        abrigo_bd = abrigo_repo.obter_por_id(99999)
        assert abrigo_bd is None

    def test_obter_abrigo_campos_opcionais_none(self, usuario_abrigo):
        """Deve retornar abrigo com campos opcionais None."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Responsável Teste",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        abrigo_repo.inserir(abrigo)

        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo)

        assert abrigo_bd is not None
        assert abrigo_bd.descricao is None
        assert abrigo_bd.data_abertura is None
        assert abrigo_bd.data_membros is None


class TestObterTodos:
    """Testes para listagem de todos os abrigos."""

    def test_obter_todos_lista_vazia(self):
        """Deve retornar lista vazia quando não há abrigos."""
        abrigos = abrigo_repo.obter_todos()
        assert abrigos == []

    def test_obter_todos_lista_abrigos(self, usuario_abrigo, usuario_abrigo2):
        """Deve retornar todos os abrigos cadastrados."""
        abrigo1 = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Responsável 1",
            descricao="Abrigo 1",
            data_abertura="2020-01-01",
            data_membros="Time A"
        )
        abrigo2 = Abrigo(
            id_abrigo=usuario_abrigo2,
            responsavel="Responsável 2",
            descricao="Abrigo 2",
            data_abertura="2021-02-02",
            data_membros="Time B"
        )

        abrigo_repo.inserir(abrigo1)
        abrigo_repo.inserir(abrigo2)

        abrigos = abrigo_repo.obter_todos()

        assert len(abrigos) == 2
        responsaveis = [a.responsavel for a in abrigos]
        assert "Responsável 1" in responsaveis
        assert "Responsável 2" in responsaveis

    def test_obter_todos_com_campos_opcionais_none(self, usuario_abrigo):
        """Deve retornar abrigos com campos opcionais None."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Responsável Teste",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        abrigo_repo.inserir(abrigo)

        abrigos = abrigo_repo.obter_todos()

        assert len(abrigos) == 1
        assert abrigos[0].descricao is None
        assert abrigos[0].data_abertura is None
        assert abrigos[0].data_membros is None


class TestAtualizar:
    """Testes para atualização de abrigos."""

    def test_atualizar_abrigo_existente(self, usuario_abrigo):
        """Deve atualizar abrigo existente."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Responsável Original",
            descricao="Descrição original",
            data_abertura="2020-01-01",
            data_membros="Membros originais"
        )
        abrigo_repo.inserir(abrigo)

        abrigo_atualizado = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Novo Responsável",
            descricao="Nova descrição",
            data_abertura="2021-06-15",
            data_membros="Novos membros"
        )
        resultado = abrigo_repo.atualizar(abrigo_atualizado)

        assert resultado is True
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo)
        assert abrigo_bd.responsavel == "Novo Responsável"
        assert abrigo_bd.descricao == "Nova descrição"
        assert abrigo_bd.data_abertura == "2021-06-15"
        assert abrigo_bd.data_membros == "Novos membros"

    def test_atualizar_abrigo_inexistente(self):
        """Deve retornar False ao atualizar abrigo inexistente."""
        abrigo = Abrigo(
            id_abrigo=99999,
            responsavel="Inexistente",
            descricao="Teste",
            data_abertura=None,
            data_membros=None
        )
        resultado = abrigo_repo.atualizar(abrigo)
        assert resultado is False

    def test_atualizar_campos_para_none(self, usuario_abrigo):
        """Deve permitir atualizar campos opcionais para None."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Responsável",
            descricao="Com descrição",
            data_abertura="2020-01-01",
            data_membros="Com membros"
        )
        abrigo_repo.inserir(abrigo)

        abrigo_atualizado = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Novo Responsável",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        resultado = abrigo_repo.atualizar(abrigo_atualizado)

        assert resultado is True
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo)
        assert abrigo_bd.descricao is None
        assert abrigo_bd.data_abertura is None
        assert abrigo_bd.data_membros is None


class TestExcluir:
    """Testes para exclusão de abrigos."""

    def test_excluir_abrigo_existente(self, usuario_abrigo):
        """Deve excluir abrigo existente."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="A ser excluído",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        abrigo_repo.inserir(abrigo)

        resultado = abrigo_repo.excluir(usuario_abrigo)

        assert resultado is True
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo)
        assert abrigo_bd is None

    def test_excluir_abrigo_inexistente(self):
        """Deve retornar False ao excluir abrigo inexistente."""
        resultado = abrigo_repo.excluir(99999)
        assert resultado is False


class TestIntegracaoCRUD:
    """Testes de integração das operações CRUD."""

    def test_ciclo_completo_crud(self, usuario_abrigo):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo,
            responsavel="Teste CRUD",
            descricao="Abrigo de teste",
            data_abertura="2022-05-10",
            data_membros="Equipe CRUD"
        )
        id_inserido = abrigo_repo.inserir(abrigo)
        assert id_inserido == usuario_abrigo

        # READ
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo)
        assert abrigo_bd is not None
        assert abrigo_bd.responsavel == "Teste CRUD"

        # UPDATE
        abrigo_bd.responsavel = "Teste CRUD Atualizado"
        abrigo_bd.descricao = "Descrição atualizada"
        resultado_update = abrigo_repo.atualizar(abrigo_bd)
        assert resultado_update is True

        abrigo_atualizado = abrigo_repo.obter_por_id(usuario_abrigo)
        assert abrigo_atualizado.responsavel == "Teste CRUD Atualizado"
        assert abrigo_atualizado.descricao == "Descrição atualizada"

        # DELETE
        resultado_delete = abrigo_repo.excluir(usuario_abrigo)
        assert resultado_delete is True

        abrigo_excluido = abrigo_repo.obter_por_id(usuario_abrigo)
        assert abrigo_excluido is None

    def test_multiplos_abrigos_independentes(self):
        """Deve gerenciar múltiplos abrigos independentemente."""
        usuarios = []

        # Criar 3 usuários e abrigos
        for i in range(3):
            usuario = Usuario(
                id=0,
                nome=f"Abrigo {i}",
                email=f"abrigo{i}@test.com",
                senha="hash",
                perfil="ABRIGO"
            )
            id_usuario = usuario_repo.inserir(usuario)
            usuarios.append(id_usuario)

            abrigo = Abrigo(
                id_abrigo=id_usuario,
                responsavel=f"Responsável {i}",
                descricao=f"Descrição {i}",
                data_abertura=None,
                data_membros=None
            )
            abrigo_repo.inserir(abrigo)

        # Verificar que todos foram inseridos
        todos = abrigo_repo.obter_todos()
        assert len(todos) == 3

        # Excluir um no meio
        abrigo_repo.excluir(usuarios[1])

        # Verificar que outros continuam
        todos = abrigo_repo.obter_todos()
        assert len(todos) == 2
        assert abrigo_repo.obter_por_id(usuarios[0]) is not None
        assert abrigo_repo.obter_por_id(usuarios[1]) is None
        assert abrigo_repo.obter_por_id(usuarios[2]) is not None
