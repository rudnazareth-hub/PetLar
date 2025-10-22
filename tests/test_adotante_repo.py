"""
Testes para o repositório de adotantes.

Testa todas as operações CRUD do adotante_repo,
incluindo models e SQLs relacionados.
"""

import pytest
from model.adotante_model import Adotante
from model.usuario_model import Usuario
from repo import adotante_repo, usuario_repo
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_adotantes():
    """Limpa tabelas de adotantes e usuários antes de cada teste."""
    # Criar tabelas se não existirem
    usuario_repo.criar_tabela()
    adotante_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM adotante")
        cursor.execute("DELETE FROM usuario")
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM adotante")
        cursor.execute("DELETE FROM usuario")


@pytest.fixture
def usuario_adotante():
    """Fixture que cria um usuário com perfil ADOTANTE."""
    usuario = Usuario(
        id=0,
        nome="João Silva",
        email="joao@email.com",
        senha="senha_hash",
        perfil="ADOTANTE"
    )
    id_usuario = usuario_repo.inserir(usuario)
    return id_usuario


@pytest.fixture
def usuario_adotante2():
    """Fixture que cria um segundo usuário com perfil ADOTANTE."""
    usuario = Usuario(
        id=0,
        nome="Maria Santos",
        email="maria@email.com",
        senha="senha_hash",
        perfil="ADOTANTE"
    )
    id_usuario = usuario_repo.inserir(usuario)
    return id_usuario


class TestCriarTabela:
    """Testes para criação da tabela adotante."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = adotante_repo.criar_tabela()
        assert resultado is True

    def test_tabela_existe_apos_criacao(self):
        """Tabela deve existir após criação."""
        adotante_repo.criar_tabela()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='adotante'"
            )
            tabela = cursor.fetchone()
            assert tabela is not None
            assert tabela["name"] == "adotante"


class TestInserir:
    """Testes para inserção de adotantes."""

    def test_inserir_adotante_completo(self, usuario_adotante):
        """Deve inserir adotante com todos os campos."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=5000.00,
            tem_filhos=True,
            estado_saude="Excelente saúde"
        )
        id_inserido = adotante_repo.inserir(adotante)

        assert id_inserido == usuario_adotante
        adotante_bd = adotante_repo.obter_por_id(id_inserido)
        assert adotante_bd is not None
        assert adotante_bd.renda_media == 5000.00
        assert adotante_bd.tem_filhos is True
        assert adotante_bd.estado_saude == "Excelente saúde"

    def test_inserir_adotante_sem_filhos(self, usuario_adotante):
        """Deve inserir adotante sem filhos."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=3000.00,
            tem_filhos=False,
            estado_saude="Boa saúde"
        )
        id_inserido = adotante_repo.inserir(adotante)

        assert id_inserido == usuario_adotante
        adotante_bd = adotante_repo.obter_por_id(id_inserido)
        assert adotante_bd is not None
        assert adotante_bd.tem_filhos is False

    def test_inserir_usa_id_usuario(self, usuario_adotante):
        """Deve usar ID do usuário como ID do adotante."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=4500.00,
            tem_filhos=True,
            estado_saude="Normal"
        )
        id_inserido = adotante_repo.inserir(adotante)

        assert id_inserido == usuario_adotante

    def test_inserir_converte_boolean_para_int(self, usuario_adotante):
        """Deve converter boolean tem_filhos para int no banco."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=2000.00,
            tem_filhos=True,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        # Verificar que foi armazenado como int no banco
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tem_filhos FROM adotante WHERE id_adotante = ?", (usuario_adotante,))
            row = cursor.fetchone()
            assert row["tem_filhos"] in (0, 1)


class TestObterPorId:
    """Testes para busca de adotante por ID."""

    def test_obter_adotante_existente(self, usuario_adotante):
        """Deve retornar adotante existente."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=6000.00,
            tem_filhos=True,
            estado_saude="Ótima saúde"
        )
        adotante_repo.inserir(adotante)

        adotante_bd = adotante_repo.obter_por_id(usuario_adotante)

        assert adotante_bd is not None
        assert adotante_bd.id_adotante == usuario_adotante
        assert adotante_bd.renda_media == 6000.00
        assert adotante_bd.tem_filhos is True
        assert adotante_bd.estado_saude == "Ótima saúde"

    def test_obter_adotante_inexistente(self):
        """Deve retornar None para ID inexistente."""
        adotante_bd = adotante_repo.obter_por_id(99999)
        assert adotante_bd is None

    def test_obter_converte_int_para_boolean(self, usuario_adotante):
        """Deve converter int do banco para boolean."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=3500.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        adotante_bd = adotante_repo.obter_por_id(usuario_adotante)

        assert isinstance(adotante_bd.tem_filhos, bool)
        assert adotante_bd.tem_filhos is False


class TestAtualizar:
    """Testes para atualização de adotantes."""

    def test_atualizar_adotante_existente(self, usuario_adotante):
        """Deve atualizar adotante existente."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=3000.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        adotante_atualizado = Adotante(
            id_adotante=usuario_adotante,
            renda_media=5500.00,
            tem_filhos=True,
            estado_saude="Excelente"
        )
        resultado = adotante_repo.atualizar(adotante_atualizado)

        assert resultado is True
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante)
        assert adotante_bd.renda_media == 5500.00
        assert adotante_bd.tem_filhos is True
        assert adotante_bd.estado_saude == "Excelente"

    def test_atualizar_adotante_inexistente(self):
        """Deve retornar False ao atualizar adotante inexistente."""
        adotante = Adotante(
            id_adotante=99999,
            renda_media=1000.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        resultado = adotante_repo.atualizar(adotante)
        assert resultado is False

    def test_atualizar_mudar_tem_filhos(self, usuario_adotante):
        """Deve permitir alterar campo tem_filhos."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=4000.00,
            tem_filhos=False,
            estado_saude="Boa"
        )
        adotante_repo.inserir(adotante)

        adotante_atualizado = Adotante(
            id_adotante=usuario_adotante,
            renda_media=4000.00,
            tem_filhos=True,
            estado_saude="Boa"
        )
        resultado = adotante_repo.atualizar(adotante_atualizado)

        assert resultado is True
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante)
        assert adotante_bd.tem_filhos is True


class TestExcluir:
    """Testes para exclusão de adotantes."""

    def test_excluir_adotante_existente(self, usuario_adotante):
        """Deve excluir adotante existente."""
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=2500.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        resultado = adotante_repo.excluir(usuario_adotante)

        assert resultado is True
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante)
        assert adotante_bd is None

    def test_excluir_adotante_inexistente(self):
        """Deve retornar False ao excluir adotante inexistente."""
        resultado = adotante_repo.excluir(99999)
        assert resultado is False


class TestIntegracaoCRUD:
    """Testes de integração das operações CRUD."""

    def test_ciclo_completo_crud(self, usuario_adotante):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        adotante = Adotante(
            id_adotante=usuario_adotante,
            renda_media=4000.00,
            tem_filhos=True,
            estado_saude="Boa saúde"
        )
        id_inserido = adotante_repo.inserir(adotante)
        assert id_inserido == usuario_adotante

        # READ
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante)
        assert adotante_bd is not None
        assert adotante_bd.renda_media == 4000.00
        assert adotante_bd.tem_filhos is True

        # UPDATE
        adotante_bd.renda_media = 6000.00
        adotante_bd.tem_filhos = False
        adotante_bd.estado_saude = "Excelente saúde"
        resultado_update = adotante_repo.atualizar(adotante_bd)
        assert resultado_update is True

        adotante_atualizado = adotante_repo.obter_por_id(usuario_adotante)
        assert adotante_atualizado.renda_media == 6000.00
        assert adotante_atualizado.tem_filhos is False
        assert adotante_atualizado.estado_saude == "Excelente saúde"

        # DELETE
        resultado_delete = adotante_repo.excluir(usuario_adotante)
        assert resultado_delete is True

        adotante_excluido = adotante_repo.obter_por_id(usuario_adotante)
        assert adotante_excluido is None

    def test_multiplos_adotantes_independentes(self):
        """Deve gerenciar múltiplos adotantes independentemente."""
        usuarios = []

        # Criar 3 usuários e adotantes
        for i in range(3):
            usuario = Usuario(
                id=0,
                nome=f"Adotante {i}",
                email=f"adotante{i}@test.com",
                senha="hash",
                perfil="ADOTANTE"
            )
            id_usuario = usuario_repo.inserir(usuario)
            usuarios.append(id_usuario)

            adotante = Adotante(
                id_adotante=id_usuario,
                renda_media=3000.00 + (i * 1000),
                tem_filhos=i % 2 == 0,
                estado_saude=f"Saúde {i}"
            )
            adotante_repo.inserir(adotante)

        # Verificar que todos foram inseridos
        for id_usuario in usuarios:
            adotante_bd = adotante_repo.obter_por_id(id_usuario)
            assert adotante_bd is not None

        # Excluir um no meio
        adotante_repo.excluir(usuarios[1])

        # Verificar que outros continuam
        assert adotante_repo.obter_por_id(usuarios[0]) is not None
        assert adotante_repo.obter_por_id(usuarios[1]) is None
        assert adotante_repo.obter_por_id(usuarios[2]) is not None

    def test_diferentes_valores_renda(self, usuario_adotante, usuario_adotante2):
        """Deve suportar diferentes valores de renda."""
        rendas = [1200.50, 10000.00, 500.00, 15000.99]

        for renda in rendas:
            # Limpar antes de cada teste de renda
            adotante_repo.excluir(usuario_adotante)

            adotante = Adotante(
                id_adotante=usuario_adotante,
                renda_media=renda,
                tem_filhos=False,
                estado_saude="Normal"
            )
            adotante_repo.inserir(adotante)

            adotante_bd = adotante_repo.obter_por_id(usuario_adotante)
            assert adotante_bd.renda_media == renda
