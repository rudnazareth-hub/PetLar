"""
Testes de integracao para o repositorio de enderecos.

Testa todas as operacoes CRUD do endereco_repo.
"""
import pytest
from model.endereco_model import Endereco
from model.usuario_model import Usuario
from repo import endereco_repo, usuario_repo
from util.security import criar_hash_senha
from util.perfis import Perfil


class TestEnderecoRepoCriarTabela:
    """Testes para criacao da tabela."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = endereco_repo.criar_tabela()
        assert resultado is True


class TestEnderecoRepoInserir:
    """Testes para insercao."""

    def test_inserir_endereco_completo(self, usuario_adotante_teste):
        """Deve inserir endereco completo."""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_adotante_teste,
            titulo="Casa",
            logradouro="Rua das Flores",
            numero="123",
            complemento="Apto 45",
            bairro="Centro",
            cidade="Vitoria",
            uf="ES",
            cep="29000-000"
        )
        id_inserido = endereco_repo.inserir(endereco)

        assert id_inserido > 0
        enderecos = endereco_repo.obter_por_usuario(usuario_adotante_teste)
        assert len(enderecos) == 1
        assert enderecos[0].titulo == "Casa"
        assert enderecos[0].logradouro == "Rua das Flores"

    def test_inserir_sem_complemento(self, usuario_adotante_teste):
        """Deve inserir endereco sem complemento."""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_adotante_teste,
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
        enderecos = endereco_repo.obter_por_usuario(usuario_adotante_teste)
        assert enderecos[0].complemento is None


class TestEnderecoRepoObterPorUsuario:
    """Testes para busca por usuario."""

    def test_obter_multiplos_enderecos(self, usuario_adotante_teste):
        """Deve retornar todos os enderecos do usuario."""
        titulos = ["Casa", "Trabalho", "Fazenda"]

        for titulo in titulos:
            endereco = Endereco(
                id=0,
                id_usuario=usuario_adotante_teste,
                titulo=titulo,
                logradouro="Rua X",
                numero="1",
                complemento=None,
                bairro="Centro",
                cidade="Vitoria",
                uf="ES",
                cep="29000-000"
            )
            endereco_repo.inserir(endereco)

        enderecos = endereco_repo.obter_por_usuario(usuario_adotante_teste)

        assert len(enderecos) == 3
        titulos_retornados = [e.titulo for e in enderecos]
        assert "Casa" in titulos_retornados
        assert "Trabalho" in titulos_retornados
        assert "Fazenda" in titulos_retornados

    def test_obter_por_usuario_vazio(self, usuario_adotante_teste):
        """Deve retornar lista vazia se usuario nao tem enderecos."""
        enderecos = endereco_repo.obter_por_usuario(usuario_adotante_teste)
        assert enderecos == []


class TestEnderecoRepoAtualizar:
    """Testes para atualizacao."""

    def test_atualizar_endereco(self, usuario_adotante_teste):
        """Deve atualizar endereco existente."""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_adotante_teste,
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
            id=id_inserido,
            id_usuario=usuario_adotante_teste,
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
        enderecos = endereco_repo.obter_por_usuario(usuario_adotante_teste)
        assert enderecos[0].titulo == "Atualizado"
        assert enderecos[0].logradouro == "Rua Nova"
        assert enderecos[0].uf == "RJ"


class TestEnderecoRepoExcluir:
    """Testes para exclusao."""

    def test_excluir_endereco(self, usuario_adotante_teste):
        """Deve excluir endereco."""
        endereco = Endereco(
            id=0,
            id_usuario=usuario_adotante_teste,
            titulo="Delete",
            logradouro="Rua X",
            numero="1",
            complemento=None,
            bairro="Centro",
            cidade="Vitoria",
            uf="ES",
            cep="29000-000"
        )
        id_inserido = endereco_repo.inserir(endereco)

        resultado = endereco_repo.excluir(id_inserido)

        assert resultado is True
        enderecos = endereco_repo.obter_por_usuario(usuario_adotante_teste)
        assert len(enderecos) == 0

    def test_excluir_um_de_multiplos(self, usuario_adotante_teste):
        """Deve excluir apenas o endereco especificado."""
        ids = []
        for i in range(3):
            endereco = Endereco(
                id=0,
                id_usuario=usuario_adotante_teste,
                titulo=f"End{i}",
                logradouro="Rua",
                numero="1",
                complemento=None,
                bairro="Centro",
                cidade="Vitoria",
                uf="ES",
                cep="29000-000"
            )
            ids.append(endereco_repo.inserir(endereco))

        endereco_repo.excluir(ids[1])

        enderecos = endereco_repo.obter_por_usuario(usuario_adotante_teste)
        assert len(enderecos) == 2
        titulos = [e.titulo for e in enderecos]
        assert "End0" in titulos
        assert "End1" not in titulos
        assert "End2" in titulos
