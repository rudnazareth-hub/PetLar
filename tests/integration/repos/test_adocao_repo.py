"""
Testes de integracao para o repositorio de adocoes.

Testa todas as operacoes do adocao_repo.

NOTA: Estes testes estao desabilitados ate que o aluno implemente
model/especie_model.py, repo/especie_repo.py e sql/especie_sql.py
"""
import pytest

# Skip todo o modulo ate que especie_model e especie_repo sejam implementados
pytest.skip(
    "Modulo especie_model e especie_repo ainda nao implementados",
    allow_module_level=True
)

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
from util.security import criar_hash_senha
from util.perfis import Perfil


@pytest.fixture
def setup_adocao_completo():
    """Cria estrutura para testes de adocao."""
    # Criar adotante
    usuario_adotante = Usuario(
        id=0, nome="Adotante Adocao", email="adotante_adocao@test.com",
        senha=criar_hash_senha("Senha@123"), perfil=Perfil.ADOTANTE.value
    )
    id_adotante = usuario_repo.inserir(usuario_adotante)
    adotante = Adotante(
        id_adotante=id_adotante, renda_media=3000.00,
        tem_filhos=False, estado_saude="Boa"
    )
    adotante_repo.inserir(adotante)

    # Criar abrigo
    usuario_abrigo = Usuario(
        id=0, nome="Abrigo Adocao", email="abrigo_adocao@test.com",
        senha=criar_hash_senha("Senha@123"), perfil=Perfil.ABRIGO.value
    )
    id_abrigo = usuario_repo.inserir(usuario_abrigo)
    abrigo = Abrigo(
        id_abrigo=id_abrigo, responsavel="Resp",
        descricao=None, data_abertura=None, data_membros=None
    )
    abrigo_repo.inserir(abrigo)

    # Criar especie e raca
    especie = Especie(id=0, nome="Gato Adocao", descricao=None)
    id_especie = especie_repo.inserir(especie)
    raca = Raca(
        id=0, id_especie=id_especie, nome="Persa Adocao",
        descricao=None, temperamento=None,
        expectativa_de_vida=None, porte=None
    )
    id_raca = raca_repo.inserir(raca)

    # Criar animal
    animal = Animal(
        id=0, id_raca=id_raca, id_abrigo=id_abrigo,
        nome="Mimi Adocao", sexo="F", data_nascimento=None,
        data_entrada="2024-01-01", observacoes=None,
        status="Disponivel", foto=None
    )
    id_animal = animal_repo.inserir(animal)

    return {
        "id_adotante": id_adotante,
        "id_abrigo": id_abrigo,
        "id_animal": id_animal,
        "id_raca": id_raca
    }


class TestAdocaoRepoCriarTabela:
    """Testes para criacao da tabela."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = adocao_repo.criar_tabela()
        assert resultado is True


class TestAdocaoRepoInserir:
    """Testes para insercao."""

    def test_inserir_adocao_com_observacoes(self, setup_adocao_completo):
        """Deve inserir adocao com observacoes."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id=0,
            id_adotante=setup_adocao_completo["id_adotante"],
            id_animal=setup_adocao_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluida",
            observacoes="Adocao realizada com sucesso"
        )
        id_inserido = adocao_repo.inserir(adocao)

        assert id_inserido > 0

    def test_inserir_adocao_sem_observacoes(self, setup_adocao_completo):
        """Deve inserir adocao sem observacoes."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id=0,
            id_adotante=setup_adocao_completo["id_adotante"],
            id_animal=setup_adocao_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluida",
            observacoes=None
        )
        id_inserido = adocao_repo.inserir(adocao)

        assert id_inserido > 0


class TestAdocaoRepoObterPorAbrigo:
    """Testes para busca por abrigo."""

    def test_obter_adocoes_por_abrigo(self, setup_adocao_completo):
        """Deve retornar adocoes do abrigo."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id=0,
            id_adotante=setup_adocao_completo["id_adotante"],
            id_animal=setup_adocao_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluida",
            observacoes="Teste"
        )
        adocao_repo.inserir(adocao)

        adocoes = adocao_repo.obter_por_abrigo(setup_adocao_completo["id_abrigo"])

        assert len(adocoes) >= 1
        assert adocoes[0]["status"] == "Concluida"

    def test_obter_por_abrigo_vazio(self, setup_adocao_completo):
        """Deve retornar lista vazia se nao ha adocoes."""
        adocoes = adocao_repo.obter_por_abrigo(setup_adocao_completo["id_abrigo"])
        assert adocoes == []

    def test_obter_multiplas_adocoes(self, setup_adocao_completo):
        """Deve retornar multiplas adocoes do abrigo."""
        # Criar segundo animal
        animal2 = Animal(
            id=0,
            id_raca=setup_adocao_completo["id_raca"],
            id_abrigo=setup_adocao_completo["id_abrigo"],
            nome="Felix Adocao",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponivel",
            foto=None
        )
        id_animal2 = animal_repo.inserir(animal2)

        # Criar 2 adocoes
        for id_animal in [setup_adocao_completo["id_animal"], id_animal2]:
            data_solicitacao = datetime.now()
            adocao = Adocao(
                id=0,
                id_adotante=setup_adocao_completo["id_adotante"],
                id_animal=id_animal,
                data_solicitacao=data_solicitacao,
                data_adocao=None,
                status="Concluida",
                observacoes=None
            )
            adocao_repo.inserir(adocao)

        adocoes = adocao_repo.obter_por_abrigo(setup_adocao_completo["id_abrigo"])
        assert len(adocoes) == 2


class TestAdocaoRepoIntegracao:
    """Testes de integracao."""

    def test_criar_adocao_completa(self, setup_adocao_completo):
        """Deve criar adocao com todas as informacoes."""
        data_solicitacao = datetime.now()
        adocao = Adocao(
            id=0,
            id_adotante=setup_adocao_completo["id_adotante"],
            id_animal=setup_adocao_completo["id_animal"],
            data_solicitacao=data_solicitacao,
            data_adocao=None,
            status="Concluida",
            observacoes="Animal entregue ao adotante"
        )
        id_inserido = adocao_repo.inserir(adocao)

        assert id_inserido > 0

        adocoes = adocao_repo.obter_por_abrigo(setup_adocao_completo["id_abrigo"])
        assert len(adocoes) == 1
        assert adocoes[0]["id_adocao"] == id_inserido
