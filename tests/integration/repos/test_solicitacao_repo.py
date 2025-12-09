"""
Testes de integracao para o repositorio de solicitacoes.

Testa todas as operacoes do solicitacao_repo.

NOTA: Estes testes estao desabilitados ate que o aluno implemente
model/especie_model.py, repo/especie_repo.py e sql/especie_sql.py
"""
import pytest

# Skip todo o modulo ate que especie_model e especie_repo sejam implementados
pytest.skip(
    "Modulo especie_model e especie_repo ainda nao implementados",
    allow_module_level=True
)

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
from util.security import criar_hash_senha
from util.perfis import Perfil


@pytest.fixture
def setup_solicitacao_completo():
    """Cria estrutura para testes de solicitacao."""
    # Criar adotante
    usuario_adotante = Usuario(
        id=0, nome="Adotante Solicitacao", email="adotante_solic@test.com",
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
        id=0, nome="Abrigo Solicitacao", email="abrigo_solic@test.com",
        senha=criar_hash_senha("Senha@123"), perfil=Perfil.ABRIGO.value
    )
    id_abrigo = usuario_repo.inserir(usuario_abrigo)
    abrigo = Abrigo(
        id_abrigo=id_abrigo, responsavel="Resp",
        descricao=None, data_abertura=None, data_membros=None
    )
    abrigo_repo.inserir(abrigo)

    # Criar especie e raca
    especie = Especie(id=0, nome="Cachorro Solic", descricao=None)
    id_especie = especie_repo.inserir(especie)
    raca = Raca(
        id=0, id_especie=id_especie, nome="Vira-lata Solic",
        descricao=None, temperamento=None,
        expectativa_de_vida=None, porte=None
    )
    id_raca = raca_repo.inserir(raca)

    # Criar animal
    animal = Animal(
        id=0, id_raca=id_raca, id_abrigo=id_abrigo,
        nome="Rex Solic", sexo="M", data_nascimento=None,
        data_entrada="2024-01-01", observacoes=None,
        status="Disponivel", foto=None
    )
    id_animal = animal_repo.inserir(animal)

    return {
        "id_adotante": id_adotante,
        "id_abrigo": id_abrigo,
        "id_animal": id_animal
    }


class TestSolicitacaoRepoCriarTabela:
    """Testes para criacao da tabela."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = solicitacao_repo.criar_tabela()
        assert resultado is True


class TestSolicitacaoRepoInserir:
    """Testes para insercao."""

    def test_inserir_solicitacao_com_observacoes(self, setup_solicitacao_completo):
        """Deve inserir solicitacao com observacoes."""
        solicitacao = Solicitacao(
            id=0,
            id_adotante=setup_solicitacao_completo["id_adotante"],
            id_animal=setup_solicitacao_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes="Tenho experiencia com caes"
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        assert id_inserido > 0

    def test_inserir_solicitacao_sem_observacoes(self, setup_solicitacao_completo):
        """Deve inserir solicitacao sem observacoes."""
        solicitacao = Solicitacao(
            id=0,
            id_adotante=setup_solicitacao_completo["id_adotante"],
            id_animal=setup_solicitacao_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        assert id_inserido > 0


class TestSolicitacaoRepoObterPorAdotante:
    """Testes para busca por adotante."""

    def test_obter_solicitacoes_por_adotante(self, setup_solicitacao_completo):
        """Deve retornar solicitacoes do adotante."""
        solicitacao = Solicitacao(
            id=0,
            id_adotante=setup_solicitacao_completo["id_adotante"],
            id_animal=setup_solicitacao_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        solicitacao_repo.inserir(solicitacao)

        solicitacoes = solicitacao_repo.obter_por_adotante(
            setup_solicitacao_completo["id_adotante"]
        )

        assert len(solicitacoes) >= 1
        assert solicitacoes[0]["status"] == "Pendente"

    def test_obter_por_adotante_vazio(self, setup_solicitacao_completo):
        """Deve retornar lista vazia se nao ha solicitacoes."""
        solicitacoes = solicitacao_repo.obter_por_adotante(
            setup_solicitacao_completo["id_adotante"]
        )
        assert solicitacoes == []


class TestSolicitacaoRepoObterPorAbrigo:
    """Testes para busca por abrigo."""

    def test_obter_solicitacoes_por_abrigo(self, setup_solicitacao_completo):
        """Deve retornar solicitacoes recebidas pelo abrigo."""
        solicitacao = Solicitacao(
            id=0,
            id_adotante=setup_solicitacao_completo["id_adotante"],
            id_animal=setup_solicitacao_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes="Teste"
        )
        solicitacao_repo.inserir(solicitacao)

        solicitacoes = solicitacao_repo.obter_por_abrigo(
            setup_solicitacao_completo["id_abrigo"]
        )

        assert len(solicitacoes) >= 1


class TestSolicitacaoRepoAtualizarStatus:
    """Testes para atualizacao de status."""

    def test_atualizar_status_para_aprovada(self, setup_solicitacao_completo):
        """Deve atualizar status para Aprovada."""
        solicitacao = Solicitacao(
            id=0,
            id_adotante=setup_solicitacao_completo["id_adotante"],
            id_animal=setup_solicitacao_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        resultado = solicitacao_repo.atualizar_status(
            id_inserido, "Aprovada", "Solicitacao aprovada!"
        )

        assert resultado is True

    def test_atualizar_status_para_rejeitada(self, setup_solicitacao_completo):
        """Deve atualizar status para Rejeitada."""
        solicitacao = Solicitacao(
            id=0,
            id_adotante=setup_solicitacao_completo["id_adotante"],
            id_animal=setup_solicitacao_completo["id_animal"],
            data_solicitacao=None,
            status="Pendente",
            observacoes=None
        )
        id_inserido = solicitacao_repo.inserir(solicitacao)

        resultado = solicitacao_repo.atualizar_status(
            id_inserido, "Rejeitada", "Nao atende requisitos"
        )

        assert resultado is True

    def test_atualizar_status_inexistente(self):
        """Deve retornar False para solicitacao inexistente."""
        resultado = solicitacao_repo.atualizar_status(
            99999, "Aprovada", "Teste"
        )
        assert resultado is False
