"""
Testes para o repositório de visitas.

Testa todas as operações do visita_repo,
incluindo models e SQLs relacionados.
"""

import pytest
from datetime import datetime
from model.visita_model import Visita
from model.usuario_model import Usuario
from model.abrigo_model import Abrigo
from model.adotante_model import Adotante
from repo import visita_repo, usuario_repo, abrigo_repo, adotante_repo
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_dados():
    """Limpa todas as tabelas."""
    # Criar tabelas se não existirem
    usuario_repo.criar_tabela()
    abrigo_repo.criar_tabela()
    adotante_repo.criar_tabela()
    visita_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM visita")
        cursor.execute("DELETE FROM abrigo")
        cursor.execute("DELETE FROM adotante")
        cursor.execute("DELETE FROM usuario")
        cursor.execute("PRAGMA foreign_keys = ON")
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM visita")
        cursor.execute("DELETE FROM abrigo")
        cursor.execute("DELETE FROM adotante")
        cursor.execute("DELETE FROM usuario")
        cursor.execute("PRAGMA foreign_keys = ON")


@pytest.fixture
def setup_visita():
    """Cria estrutura para testes de visita."""
    # Criar adotante
    usuario_adotante = Usuario(
        id=0, nome="Visitante", email="visitante@test.com",
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
        id=0, nome="Abrigo Recebe Visitas", email="visitas@test.com",
        senha="hash", perfil="ABRIGO"
    )
    id_abrigo = usuario_repo.inserir(usuario_abrigo)
    abrigo = Abrigo(
        id_abrigo=id_abrigo, responsavel="Resp Visitas",
        descricao=None, data_abertura=None, data_membros=None
    )
    abrigo_repo.inserir(abrigo)

    return {"id_adotante": id_adotante, "id_abrigo": id_abrigo}


class TestCriarTabela:
    """Testes para criação da tabela."""

    def test_criar_tabela_retorna_true(self):
        resultado = visita_repo.criar_tabela()
        assert resultado is True


class TestInserir:
    """Testes para inserção."""

    def test_inserir_visita_com_observacoes(self, setup_visita):
        """Deve inserir visita com observações."""
        data_agendada = datetime(2024, 12, 20, 14, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_agendada,
            observacoes="Gostaria de conhecer os gatos",
            status="Agendada"
        )
        id_inserido = visita_repo.inserir(visita)

        assert id_inserido > 0

    def test_inserir_visita_sem_observacoes(self, setup_visita):
        """Deve inserir visita sem observações."""
        data_agendada = datetime(2024, 12, 25, 10, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_agendada,
            observacoes=None,
            status="Agendada"
        )
        id_inserido = visita_repo.inserir(visita)

        assert id_inserido > 0


class TestObterPorAdotante:
    """Testes para busca por adotante."""

    def test_obter_visitas_por_adotante(self, setup_visita):
        """Deve retornar visitas do adotante."""
        data_agendada = datetime(2024, 12, 30, 15, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_agendada,
            observacoes="Visita de reconhecimento",
            status="Agendada"
        )
        visita_repo.inserir(visita)

        visitas = visita_repo.obter_por_adotante(setup_visita["id_adotante"])

        assert len(visitas) >= 1
        assert visitas[0]["status"] == "Agendada"

    def test_obter_por_adotante_vazio(self, setup_visita):
        """Deve retornar lista vazia se não há visitas."""
        visitas = visita_repo.obter_por_adotante(setup_visita["id_adotante"])
        assert visitas == []


class TestObterPorAbrigo:
    """Testes para busca por abrigo."""

    def test_obter_visitas_por_abrigo(self, setup_visita):
        """Deve retornar visitas agendadas para o abrigo."""
        data_agendada = datetime(2025, 1, 5, 9, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_agendada,
            observacoes="Primeira visita",
            status="Agendada"
        )
        visita_repo.inserir(visita)

        visitas = visita_repo.obter_por_abrigo(setup_visita["id_abrigo"])

        assert len(visitas) >= 1

    def test_obter_multiplas_visitas(self, setup_visita):
        """Deve retornar múltiplas visitas do abrigo."""
        datas = [
            datetime(2025, 1, 10, 10, 0, 0),
            datetime(2025, 1, 15, 14, 0, 0),
            datetime(2025, 1, 20, 16, 0, 0)
        ]

        for data in datas:
            visita = Visita(
                id_visita=0,
                id_adotante=setup_visita["id_adotante"],
                id_abrigo=setup_visita["id_abrigo"],
                data_agendada=data,
                observacoes=None,
                status="Agendada"
            )
            visita_repo.inserir(visita)

        visitas = visita_repo.obter_por_abrigo(setup_visita["id_abrigo"])
        assert len(visitas) == 3


class TestAtualizarStatus:
    """Testes para atualização de status."""

    def test_atualizar_status_para_realizada(self, setup_visita):
        """Deve atualizar status para Realizada."""
        data_agendada = datetime(2024, 12, 15, 11, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_agendada,
            observacoes=None,
            status="Agendada"
        )
        id_inserido = visita_repo.inserir(visita)

        resultado = visita_repo.atualizar_status(id_inserido, "Realizada")

        assert resultado is True

    def test_atualizar_status_para_cancelada(self, setup_visita):
        """Deve atualizar status para Cancelada."""
        data_agendada = datetime(2024, 12, 18, 13, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_agendada,
            observacoes=None,
            status="Agendada"
        )
        id_inserido = visita_repo.inserir(visita)

        resultado = visita_repo.atualizar_status(id_inserido, "Cancelada")

        assert resultado is True

    def test_atualizar_status_inexistente(self):
        """Deve retornar False para visita inexistente."""
        resultado = visita_repo.atualizar_status(99999, "Realizada")
        assert resultado is False


class TestReagendar:
    """Testes para reagendamento."""

    def test_reagendar_visita(self, setup_visita):
        """Deve reagendar visita para nova data."""
        data_original = datetime(2025, 2, 1, 10, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_original,
            observacoes="Data original",
            status="Agendada"
        )
        id_inserido = visita_repo.inserir(visita)

        nova_data = "2025-02-10 15:00:00"
        resultado = visita_repo.reagendar(id_inserido, nova_data)

        assert resultado is True

    def test_reagendar_visita_inexistente(self):
        """Deve retornar False para visita inexistente."""
        resultado = visita_repo.reagendar(99999, "2025-03-01 10:00:00")
        assert resultado is False


class TestIntegracao:
    """Testes de integração."""

    def test_ciclo_completo_visita(self, setup_visita):
        """Deve executar ciclo completo de visita."""
        # Criar visita
        data_agendada = datetime(2025, 3, 15, 14, 0, 0)
        visita = Visita(
            id_visita=0,
            id_adotante=setup_visita["id_adotante"],
            id_abrigo=setup_visita["id_abrigo"],
            data_agendada=data_agendada,
            observacoes="Ciclo completo",
            status="Agendada"
        )
        id_inserido = visita_repo.inserir(visita)
        assert id_inserido > 0

        # Verificar que foi criada
        visitas = visita_repo.obter_por_adotante(setup_visita["id_adotante"])
        assert len(visitas) >= 1

        # Reagendar
        nova_data = "2025-03-20 16:00:00"
        resultado_reagendar = visita_repo.reagendar(id_inserido, nova_data)
        assert resultado_reagendar is True

        # Marcar como realizada
        resultado_status = visita_repo.atualizar_status(id_inserido, "Realizada")
        assert resultado_status is True
