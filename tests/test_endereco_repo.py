"""
Testes para o repositório de endereços.

Testa todas as operações CRUD do endereco_repo,
incluindo models e SQLs relacionados.
"""

import pytest
from model.endereco_model import Endereco
from model.usuario_model import Usuario
from repo import endereco_repo, usuario_repo
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_dados():
    """Limpa tabelas antes de cada teste."""
    # Criar tabelas se não existirem
    usuario_repo.criar_tabela()
    endereco_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM endereco")
        cursor.execute("DELETE FROM usuario")
        cursor.execute("PRAGMA foreign_keys = ON")
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM endereco")
        cursor.execute("DELETE FROM usuario")
        cursor.execute("PRAGMA foreign_keys = ON")


@pytest.fixture
def usuario_teste():
    """Cria usuário para testes de endereço."""
    usuario = Usuario(
        id=0, nome="João", email="joao@test.com",
        senha="hash", perfil="ADOTANTE"
    )
    return usuario_repo.inserir(usuario)


class TestCriarTabela:
    """Testes para criação da tabela."""

    def test_criar_tabela_retorna_true(self):
        resultado = endereco_repo.criar_tabela()
        assert resultado is True


class TestInserir:
    """Testes para inserção."""

    def test_inserir_endereco_completo(self, usuario_teste):
        """Deve inserir endereço completo."""
        endereco = Endereco(
            id_endereco=0,
            id_usuario=usuario_teste,
            titulo="Casa",
            logradouro="Rua das Flores",
            numero="123",
            complemento="Apto 45",
            bairro="Centro",
            cidade="Vitória",
            uf="ES",
            cep="29000-000"
        )
        id_inserido = endereco_repo.inserir(endereco)

        assert id_inserido > 0
        enderecos = endereco_repo.obter_por_usuario(usuario_teste)
        assert len(enderecos) == 1
        assert enderecos[0].titulo == "Casa"
        assert enderecos[0].logradouro == "Rua das Flores"

    def test_inserir_sem_complemento(self, usuario_teste):
        """Deve inserir endereço sem complemento."""
        endereco = Endereco(
            id_endereco=0,
            id_usuario=usuario_teste,
            titulo="Trabalho",
            logradouro="Av. Principal",
            numero="500",
            complemento=None,
            bairro="Industrial",
            cidade="Vila Velha",
            uf="ES",
            cep="29100-000"
        )
        id_inserido = endereco_repo.inserir(endereco)

        assert id_inserido > 0
        enderecos = endereco_repo.obter_por_usuario(usuario_teste)
        assert enderecos[0].complemento is None


class TestObterPorUsuario:
    """Testes para busca por usuário."""

    def test_obter_multiplos_enderecos(self, usuario_teste):
        """Deve retornar todos os endereços do usuário."""
        titulos = ["Casa", "Trabalho", "Fazenda"]

        for titulo in titulos:
            endereco = Endereco(
                id_endereco=0,
                id_usuario=usuario_teste,
                titulo=titulo,
                logradouro="Rua X",
                numero="1",
                complemento=None,
                bairro="Centro",
                cidade="Vitória",
                uf="ES",
                cep="29000-000"
            )
            endereco_repo.inserir(endereco)

        enderecos = endereco_repo.obter_por_usuario(usuario_teste)

        assert len(enderecos) == 3
        titulos_retornados = [e.titulo for e in enderecos]
        assert "Casa" in titulos_retornados
        assert "Trabalho" in titulos_retornados
        assert "Fazenda" in titulos_retornados

    def test_obter_por_usuario_vazio(self, usuario_teste):
        """Deve retornar lista vazia se usuário não tem endereços."""
        enderecos = endereco_repo.obter_por_usuario(usuario_teste)
        assert enderecos == []


class TestAtualizar:
    """Testes para atualização."""

    def test_atualizar_endereco(self, usuario_teste):
        """Deve atualizar endereço existente."""
        endereco = Endereco(
            id_endereco=0,
            id_usuario=usuario_teste,
            titulo="Original",
            logradouro="Rua Antiga",
            numero="100",
            complemento=None,
            bairro="Bairro Antigo",
            cidade="Cidade Antiga",
            uf="ES",
            cep="00000-000"
        )
        id_inserido = endereco_repo.inserir(endereco)

        endereco_atualizado = Endereco(
            id_endereco=id_inserido,
            id_usuario=usuario_teste,
            titulo="Atualizado",
            logradouro="Rua Nova",
            numero="200",
            complemento="Casa 2",
            bairro="Bairro Novo",
            cidade="Cidade Nova",
            uf="RJ",
            cep="11111-111"
        )
        resultado = endereco_repo.atualizar(endereco_atualizado)

        assert resultado is True
        enderecos = endereco_repo.obter_por_usuario(usuario_teste)
        assert enderecos[0].titulo == "Atualizado"
        assert enderecos[0].logradouro == "Rua Nova"
        assert enderecos[0].uf == "RJ"


class TestExcluir:
    """Testes para exclusão."""

    def test_excluir_endereco(self, usuario_teste):
        """Deve excluir endereço."""
        endereco = Endereco(
            id_endereco=0,
            id_usuario=usuario_teste,
            titulo="Delete",
            logradouro="Rua X",
            numero="1",
            complemento=None,
            bairro="Centro",
            cidade="Vitória",
            uf="ES",
            cep="29000-000"
        )
        id_inserido = endereco_repo.inserir(endereco)

        resultado = endereco_repo.excluir(id_inserido)

        assert resultado is True
        enderecos = endereco_repo.obter_por_usuario(usuario_teste)
        assert len(enderecos) == 0

    def test_excluir_um_de_multiplos(self, usuario_teste):
        """Deve excluir apenas o endereço especificado."""
        ids = []
        for i in range(3):
            endereco = Endereco(
                id_endereco=0,
                id_usuario=usuario_teste,
                titulo=f"End{i}",
                logradouro="Rua",
                numero="1",
                complemento=None,
                bairro="Centro",
                cidade="Vitória",
                uf="ES",
                cep="29000-000"
            )
            ids.append(endereco_repo.inserir(endereco))

        endereco_repo.excluir(ids[1])

        enderecos = endereco_repo.obter_por_usuario(usuario_teste)
        assert len(enderecos) == 2
        titulos = [e.titulo for e in enderecos]
        assert "End0" in titulos
        assert "End1" not in titulos
        assert "End2" in titulos
