"""
Testes de integracao para o repositorio de abrigos.

Testa todas as operacoes CRUD do abrigo_repo.
"""
import pytest
from model.abrigo_model import Abrigo
from model.usuario_model import Usuario
from repo import abrigo_repo, usuario_repo
from util.security import criar_hash_senha
from util.perfis import Perfil


class TestAbrigoRepoCriarTabela:
    """Testes para criacao da tabela abrigo."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = abrigo_repo.criar_tabela()
        assert resultado is True


class TestAbrigoRepoInserir:
    """Testes para insercao de abrigos."""

    def test_inserir_abrigo_completo(self, usuario_abrigo_teste):
        """Deve inserir abrigo com todos os campos."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Joao Silva",
            descricao="Abrigo dedicado ao resgate de caes",
            data_abertura="2020-05-15",
            data_membros="Maria, Jose, Ana"
        )
        id_inserido = abrigo_repo.inserir(abrigo)

        assert id_inserido == usuario_abrigo_teste
        abrigo_bd = abrigo_repo.obter_por_id(id_inserido)
        assert abrigo_bd is not None
        assert abrigo_bd.responsavel == "Joao Silva"
        assert abrigo_bd.descricao == "Abrigo dedicado ao resgate de caes"
        assert abrigo_bd.data_abertura == "2020-05-15"
        assert abrigo_bd.data_membros == "Maria, Jose, Ana"

    def test_inserir_abrigo_campos_minimos(self, usuario_abrigo_teste):
        """Deve inserir abrigo apenas com campos obrigatorios."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Maria Santos",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        id_inserido = abrigo_repo.inserir(abrigo)

        assert id_inserido == usuario_abrigo_teste
        abrigo_bd = abrigo_repo.obter_por_id(id_inserido)
        assert abrigo_bd is not None
        assert abrigo_bd.responsavel == "Maria Santos"
        assert abrigo_bd.descricao is None
        assert abrigo_bd.data_abertura is None
        assert abrigo_bd.data_membros is None

    def test_inserir_usa_id_usuario(self, usuario_abrigo_teste):
        """Deve usar ID do usuario como ID do abrigo."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Pedro Lima",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        id_inserido = abrigo_repo.inserir(abrigo)

        assert id_inserido == usuario_abrigo_teste


class TestAbrigoRepoObterPorId:
    """Testes para busca de abrigo por ID."""

    def test_obter_abrigo_existente(self, usuario_abrigo_teste):
        """Deve retornar abrigo existente."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Ana Costa",
            descricao="Resgate de animais abandonados",
            data_abertura="2019-03-20",
            data_membros="Carlos, Beatriz"
        )
        abrigo_repo.inserir(abrigo)

        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo_teste)

        assert abrigo_bd is not None
        assert abrigo_bd.id_abrigo == usuario_abrigo_teste
        assert abrigo_bd.responsavel == "Ana Costa"
        assert abrigo_bd.descricao == "Resgate de animais abandonados"
        assert abrigo_bd.data_abertura == "2019-03-20"
        assert abrigo_bd.data_membros == "Carlos, Beatriz"

    def test_obter_abrigo_inexistente(self):
        """Deve retornar None para ID inexistente."""
        abrigo_bd = abrigo_repo.obter_por_id(99999)
        assert abrigo_bd is None

    def test_obter_abrigo_campos_opcionais_none(self, usuario_abrigo_teste):
        """Deve retornar abrigo com campos opcionais None."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Responsavel Teste",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        abrigo_repo.inserir(abrigo)

        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo_teste)

        assert abrigo_bd is not None
        assert abrigo_bd.descricao is None
        assert abrigo_bd.data_abertura is None
        assert abrigo_bd.data_membros is None


class TestAbrigoRepoObterTodos:
    """Testes para listagem de todos os abrigos."""

    def test_obter_todos_lista_abrigos(self, usuario_abrigo_teste, usuario_abrigo2_teste):
        """Deve retornar todos os abrigos cadastrados."""
        abrigo1 = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Responsavel 1",
            descricao="Abrigo 1",
            data_abertura="2020-01-01",
            data_membros="Time A"
        )
        abrigo2 = Abrigo(
            id_abrigo=usuario_abrigo2_teste,
            responsavel="Responsavel 2",
            descricao="Abrigo 2",
            data_abertura="2021-02-02",
            data_membros="Time B"
        )

        abrigo_repo.inserir(abrigo1)
        abrigo_repo.inserir(abrigo2)

        abrigos = abrigo_repo.obter_todos()

        assert len(abrigos) >= 2
        responsaveis = [a.responsavel for a in abrigos]
        assert "Responsavel 1" in responsaveis
        assert "Responsavel 2" in responsaveis

    def test_obter_todos_com_campos_opcionais_none(self, usuario_abrigo_teste):
        """Deve retornar abrigos com campos opcionais None."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Responsavel Teste",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        abrigo_repo.inserir(abrigo)

        abrigos = abrigo_repo.obter_todos()

        assert len(abrigos) >= 1
        abrigo_encontrado = next(
            (a for a in abrigos if a.id_abrigo == usuario_abrigo_teste), None
        )
        assert abrigo_encontrado is not None
        assert abrigo_encontrado.descricao is None
        assert abrigo_encontrado.data_abertura is None
        assert abrigo_encontrado.data_membros is None


class TestAbrigoRepoAtualizar:
    """Testes para atualizacao de abrigos."""

    def test_atualizar_abrigo_existente(self, usuario_abrigo_teste):
        """Deve atualizar abrigo existente."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Responsavel Original",
            descricao="Descricao original",
            data_abertura="2020-01-01",
            data_membros="Membros originais"
        )
        abrigo_repo.inserir(abrigo)

        abrigo_atualizado = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Novo Responsavel",
            descricao="Nova descricao",
            data_abertura="2021-06-15",
            data_membros="Novos membros"
        )
        resultado = abrigo_repo.atualizar(abrigo_atualizado)

        assert resultado is True
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo_teste)
        assert abrigo_bd.responsavel == "Novo Responsavel"
        assert abrigo_bd.descricao == "Nova descricao"
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

    def test_atualizar_campos_para_none(self, usuario_abrigo_teste):
        """Deve permitir atualizar campos opcionais para None."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Responsavel",
            descricao="Com descricao",
            data_abertura="2020-01-01",
            data_membros="Com membros"
        )
        abrigo_repo.inserir(abrigo)

        abrigo_atualizado = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Novo Responsavel",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        resultado = abrigo_repo.atualizar(abrigo_atualizado)

        assert resultado is True
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo_teste)
        assert abrigo_bd.descricao is None
        assert abrigo_bd.data_abertura is None
        assert abrigo_bd.data_membros is None


class TestAbrigoRepoExcluir:
    """Testes para exclusao de abrigos."""

    def test_excluir_abrigo_existente(self, usuario_abrigo_teste):
        """Deve excluir abrigo existente."""
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="A ser excluido",
            descricao=None,
            data_abertura=None,
            data_membros=None
        )
        abrigo_repo.inserir(abrigo)

        resultado = abrigo_repo.excluir(usuario_abrigo_teste)

        assert resultado is True
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo_teste)
        assert abrigo_bd is None

    def test_excluir_abrigo_inexistente(self):
        """Deve retornar False ao excluir abrigo inexistente."""
        resultado = abrigo_repo.excluir(99999)
        assert resultado is False


class TestAbrigoRepoIntegracaoCRUD:
    """Testes de integracao das operacoes CRUD."""

    def test_ciclo_completo_crud(self, usuario_abrigo_teste):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        abrigo = Abrigo(
            id_abrigo=usuario_abrigo_teste,
            responsavel="Teste CRUD",
            descricao="Abrigo de teste",
            data_abertura="2022-05-10",
            data_membros="Equipe CRUD"
        )
        id_inserido = abrigo_repo.inserir(abrigo)
        assert id_inserido == usuario_abrigo_teste

        # READ
        abrigo_bd = abrigo_repo.obter_por_id(usuario_abrigo_teste)
        assert abrigo_bd is not None
        assert abrigo_bd.responsavel == "Teste CRUD"

        # UPDATE
        abrigo_bd.responsavel = "Teste CRUD Atualizado"
        abrigo_bd.descricao = "Descricao atualizada"
        resultado_update = abrigo_repo.atualizar(abrigo_bd)
        assert resultado_update is True

        abrigo_atualizado = abrigo_repo.obter_por_id(usuario_abrigo_teste)
        assert abrigo_atualizado.responsavel == "Teste CRUD Atualizado"
        assert abrigo_atualizado.descricao == "Descricao atualizada"

        # DELETE
        resultado_delete = abrigo_repo.excluir(usuario_abrigo_teste)
        assert resultado_delete is True

        abrigo_excluido = abrigo_repo.obter_por_id(usuario_abrigo_teste)
        assert abrigo_excluido is None

    def test_multiplos_abrigos_independentes(self):
        """Deve gerenciar multiplos abrigos independentemente."""
        usuarios = []

        # Criar 3 usuarios e abrigos
        for i in range(3):
            usuario = Usuario(
                id=0,
                nome=f"Abrigo {i}",
                email=f"abrigo_multi{i}@test.com",
                senha=criar_hash_senha("Senha@123"),
                perfil=Perfil.ABRIGO.value
            )
            id_usuario = usuario_repo.inserir(usuario)
            usuarios.append(id_usuario)

            abrigo = Abrigo(
                id_abrigo=id_usuario,
                responsavel=f"Responsavel {i}",
                descricao=f"Descricao {i}",
                data_abertura=None,
                data_membros=None
            )
            abrigo_repo.inserir(abrigo)

        # Verificar que todos foram inseridos
        todos = abrigo_repo.obter_todos()
        assert len(todos) >= 3

        # Excluir um no meio
        abrigo_repo.excluir(usuarios[1])

        # Verificar que outros continuam
        assert abrigo_repo.obter_por_id(usuarios[0]) is not None
        assert abrigo_repo.obter_por_id(usuarios[1]) is None
        assert abrigo_repo.obter_por_id(usuarios[2]) is not None
