"""
Testes para o repositório de solicitações.

Testa todas as operações do solicitacao_repo,
incluindo models e SQLs relacionados.
"""

import pytest
from model.solicitacao_model import Solicitacao
from model.usuario_model import Usuario
from model.abrigo_model import Abrigo
from model.adotante_model import Adotante
from model.especie_model import Especie
from model.raca_model import Raca
from model.animal_model import Animal
from repo import (
    solicitacao_repo, usuario_repo, abrigo_repo,
    adotante_repo, especie_repo, raca_repo, animal_repo
)
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_dados():
    """Limpa todas as tabelas."""
    # Criar tabelas se não existirem
    usuario_repo.criar_tabela()
    especie_repo.criar_tabela()
    raca_repo.criar_tabela()
    abrigo_repo.criar_tabela()
    adotante_repo.criar_tabela()
    animal_repo.criar_tabela()
    solicitacao_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM solicitacao")
        cursor.execute("DELETE FROM animal")
        cursor.execute("DELETE FROM abrigo")
        cursor.execute("DELETE FROM adotante")
        cursor.execute("DELETE FROM raca")
        cursor.execute("DELETE FROM especie")
        cursor.execute("DELETE FROM usuario")
    yield


@pytest.fixture
def setup_completo():
    """Cria estrutura para testes."""
    # Criar adotante
    usuario_adotante = Usuario(
        id=0, nome="Adotante", email="adotante@test.com",
        senha="hash", perfil="ADOTANTE"
    )
    id_adotante = usuario_repo.inserir(usuario_adotante)
    adotante = Adotante(
        id_adotante=id_adotante, renda_media=3000.00,
        tem_filhos=False, estado_saude="Boa"
    )
    adotante_repo.inserir(adotante)

    # Criar abrigo
    usuario_abrigo = Usuario(
        id=0, nome="Abrigo", email="abrigo@test.com",
        senha="hash", perfil="ABRIGO"
    )
    id_abrigo = usuario_repo.inserir(usuario_abrigo)
    abrigo = Abrigo(
        id_abrigo=id_abrigo, responsavel="Resp",
        descricao=None, data_abertura=None, data_membros=None
    )
    abrigo_repo.inserir(abrigo)

    # Criar espécie e raça
    especie = Especie(id_especie=0, nome="Cachorro", descricao=None)
    id_especie = especie_repo.inserir(especie)
    raca = Raca(
        id_raca=0, id_especie=id_especie, nome="Vira-lata",
        descricao=None, temperamento=None,
        expectativa_de_vida=None, porte=None
    )
    id_raca = raca_repo.inserir(raca)

    # Criar animal
    animal = Animal(
        id_animal=0, id_raca=id_raca, id_abrigo=id_abrigo,
        nome="Rex", sexo="M", data_nascimento=None,
        data_entrada="2024-01-01", observacoes=None,
        status="Disponível", foto=None
    )
    id_animal = animal_repo.inserir(animal)

    return {
        "id_adotante": id_adotante,
        "id_abrigo": id_abrigo,
        "id_animal": id_animal
    }


class TestCriarTabela:
    """Testes para criação da tabela."""

    def test_criar_tabela_retorna_true(self):
        resultado = solicitacao_repo.criar_tabela()
        assert resultado is True


class TestInserir:
    """Testes para inserção."""

    def test_inserir_solicitacao_com_observacoes(self, setup_completo):
        """Deve inserir solicitação com observações."""
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes="Tenho experiência com cães"
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        assert id_inserido > 0

    def test_inserir_solicitacao_sem_observacoes(self, setup_completo):
        """Deve inserir solicitação sem observações."""
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        assert id_inserido > 0


class TestObterPorAdotante:
    """Testes para busca por adotante."""

    def test_obter_solicitacoes_por_adotante(self, setup_completo):
        """Deve retornar solicitações do adotante."""
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        solicitacao_repo.inserir(solicitacao)

        solicitacoes = solicitacao_repo.obter_por_adotante(
            setup_completo["id_adotante"]
        )

        assert len(solicitacoes) >= 1
        assert solicitacoes[0]["status"] == "Pendente"

    def test_obter_por_adotante_vazio(self, setup_completo):
        """Deve retornar lista vazia se não há solicitações."""
        solicitacoes = solicitacao_repo.obter_por_adotante(
            setup_completo["id_adotante"]
        )
        assert solicitacoes == []


class TestObterPorAbrigo:
    """Testes para busca por abrigo."""

    def test_obter_solicitacoes_por_abrigo(self, setup_completo):
        """Deve retornar solicitações recebidas pelo abrigo."""
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes="Teste"
        )
        solicitacao_repo.inserir(solicitacao)

        solicitacoes = solicitacao_repo.obter_por_abrigo(
            setup_completo["id_abrigo"]
        )

        assert len(solicitacoes) >= 1


class TestAtualizarStatus:
    """Testes para atualização de status."""

    def test_atualizar_status_para_aprovada(self, setup_completo):
        """Deve atualizar status para Aprovada."""
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        resultado = solicitacao_repo.atualizar_status(
            id_inserido, "Aprovada", "Solicitação aprovada!"
        )

        assert resultado is True

    def test_atualizar_status_para_rejeitada(self, setup_completo):
        """Deve atualizar status para Rejeitada."""
        solicitacao = Solicitacao(
            id_solicitacao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        resultado = solicitacao_repo.atualizar_status(
            id_inserido, "Rejeitada", "Não atende requisitos"
        )

        assert resultado is True

    def test_atualizar_status_inexistente(self):
        """Deve retornar False para solicitação inexistente."""
        resultado = solicitacao_repo.atualizar_status(
            99999, "Aprovada", "Teste"
        )
        assert resultado is False
