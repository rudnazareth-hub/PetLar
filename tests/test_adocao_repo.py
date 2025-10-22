"""
Testes para o repositório de adoções.

Testa todas as operações do adocao_repo,
incluindo models e SQLs relacionados.
"""

import pytest
from datetime import datetime
from model.adocao_model import Adocao
from model.usuario_model import Usuario
from model.abrigo_model import Abrigo
from model.adotante_model import Adotante
from model.especie_model import Especie
from model.raca_model import Raca
from model.animal_model import Animal
from repo import (
    adocao_repo, usuario_repo, abrigo_repo,
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
    adocao_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM adocao")
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
    especie = Especie(id_especie=0, nome="Gato", descricao=None)
    id_especie = especie_repo.inserir(especie)
    raca = Raca(
        id_raca=0, id_especie=id_especie, nome="Persa",
        descricao=None, temperamento=None,
        expectativa_de_vida=None, porte=None
    )
    id_raca = raca_repo.inserir(raca)

    # Criar animal
    animal = Animal(
        id_animal=0, id_raca=id_raca, id_abrigo=id_abrigo,
        nome="Mimi", sexo="F", data_nascimento=None,
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
        resultado = adocao_repo.criar_tabela()
        assert resultado is True


class TestInserir:
    """Testes para inserção."""

    def test_inserir_adocao_com_observacoes(self, setup_completo):
        """Deve inserir adoção com observações."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id_adocao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluída",
            observacoes="Adoção realizada com sucesso"
        )
        id_inserido = adocao_repo.inserir(adocao)

        assert id_inserido > 0

    def test_inserir_adocao_sem_observacoes(self, setup_completo):
        """Deve inserir adoção sem observações."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id_adocao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluída",
            observacoes=None
        )
        id_inserido = adocao_repo.inserir(adocao)

        assert id_inserido > 0


class TestObterPorAbrigo:
    """Testes para busca por abrigo."""

    def test_obter_adocoes_por_abrigo(self, setup_completo):
        """Deve retornar adoções do abrigo."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id_adocao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluída",
            observacoes="Teste"
        )
        adocao_repo.inserir(adocao)

        adocoes = adocao_repo.obter_por_abrigo(setup_completo["id_abrigo"])

        assert len(adocoes) >= 1
        assert adocoes[0]["status"] == "Concluída"

    def test_obter_por_abrigo_vazio(self, setup_completo):
        """Deve retornar lista vazia se não há adoções."""
        adocoes = adocao_repo.obter_por_abrigo(setup_completo["id_abrigo"])
        assert adocoes == []

    def test_obter_multiplas_adocoes(self, setup_completo):
        """Deve retornar múltiplas adoções do abrigo."""
        # Criar segundo animal
        animal2 = Animal(
            id_animal=0,
            id_raca=setup_completo["id_animal"],  # usar mesmo id_raca
            id_abrigo=setup_completo["id_abrigo"],
            nome="Felix",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponível",
            foto=None
        )
        id_animal2 = animal_repo.inserir(animal2)

        # Criar 2 adoções
        for id_animal in [setup_completo["id_animal"], id_animal2]:
            data_solicitacao = datetime.now()
            adocao = Adocao(
                id_adocao=0,
                id_adotante=setup_completo["id_adotante"],
                id_animal=id_animal,
                data_solicitacao=data_solicitacao,
                data_adocao=None,
                status="Concluída",
                observacoes=None
            )
            adocao_repo.inserir(adocao)

        adocoes = adocao_repo.obter_por_abrigo(setup_completo["id_abrigo"])
        assert len(adocoes) == 2


class TestIntegracao:
    """Testes de integração."""

    def test_criar_adocao_completa(self, setup_completo):
        """Deve criar adoção com todas as informações."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id_adocao=0,
            id_adotante=setup_completo["id_adotante"],
            id_animal=setup_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluída",
            observacoes="Animal entregue ao adotante"
        )
        id_inserido = adocao_repo.inserir(adocao)

        assert id_inserido > 0

        adocoes = adocao_repo.obter_por_abrigo(setup_completo["id_abrigo"])
        assert len(adocoes) == 1
        assert adocoes[0]["id_adocao"] == id_inserido
