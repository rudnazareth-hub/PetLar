"""
Testes para o repositório de animais.

Testa todas as operações CRUD do animal_repo,
incluindo models, SQLs e relacionamentos.
"""

import pytest
from datetime import datetime
from model.animal_model import Animal
from model.usuario_model import Usuario
from model.especie_model import Especie
from model.raca_model import Raca
from model.abrigo_model import Abrigo
from repo import animal_repo, usuario_repo, especie_repo, raca_repo, abrigo_repo
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_dados():
    """Limpa todas as tabelas relacionadas antes de cada teste."""
    # Criar tabelas se não existirem
    usuario_repo.criar_tabela()
    especie_repo.criar_tabela()
    raca_repo.criar_tabela()
    abrigo_repo.criar_tabela()
    animal_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM animal")
        cursor.execute("DELETE FROM abrigo")
        cursor.execute("DELETE FROM raca")
        cursor.execute("DELETE FROM especie")
        cursor.execute("DELETE FROM usuario")
        cursor.execute("PRAGMA foreign_keys = ON")
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM animal")
        cursor.execute("DELETE FROM abrigo")
        cursor.execute("DELETE FROM raca")
        cursor.execute("DELETE FROM especie")
        cursor.execute("DELETE FROM usuario")
        cursor.execute("PRAGMA foreign_keys = ON")


@pytest.fixture
def setup_completo():
    """Cria estrutura completa: usuário, abrigo, espécie e raça."""
    # Criar usuário abrigo
    usuario = Usuario(
        id=0, nome="Abrigo Teste", email="abrigo@test.com",
        senha="hash", perfil="ABRIGO"
    )
    id_usuario = usuario_repo.inserir(usuario)

    # Criar abrigo
    abrigo = Abrigo(
        id_abrigo=id_usuario, responsavel="Responsável",
        descricao=None, data_abertura=None, data_membros=None
    )
    abrigo_repo.inserir(abrigo)

    # Criar espécie
    especie = Especie(id=0, nome="Cachorro", descricao=None)
    id_especie = especie_repo.inserir(especie)

    # Criar raça
    raca = Raca(
        id=0, id_especie=id_especie, nome="Labrador",
        descricao=None, temperamento=None,
        expectativa_de_vida=None, porte=None
    )
    id_raca = raca_repo.inserir(raca)

    return {"id_abrigo": id_usuario, "id_raca": id_raca, "id_especie": id_especie}


class TestCriarTabela:
    """Testes para criação da tabela animal."""

    def test_criar_tabela_retorna_true(self):
        resultado = animal_repo.criar_tabela()
        assert resultado is True


class TestInserir:
    """Testes para inserção de animais."""

    def test_inserir_animal_completo(self, setup_completo):
        """Deve inserir animal com todos os campos."""
        animal = Animal(
            id=0,
            id_raca=setup_completo["id_raca"],
            id_abrigo=setup_completo["id_abrigo"],
            nome="Rex",
            sexo="M",
            data_nascimento="2020-05-15",
            data_entrada="2024-01-10",
            observacoes="Dócil e brincalhão",
            status="Disponível",
            foto="rex.jpg"
        )
        id_inserido = animal_repo.inserir(animal)

        assert id_inserido > 0
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd is not None
        assert animal_bd.nome == "Rex"
        assert animal_bd.sexo == "M"
        assert animal_bd.status == "Disponível"

    def test_inserir_animal_campos_minimos(self, setup_completo):
        """Deve inserir animal com campos mínimos."""
        animal = Animal(
            id=0,
            id_raca=setup_completo["id_raca"],
            id_abrigo=setup_completo["id_abrigo"],
            nome="Toby",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponível",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        assert id_inserido > 0
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd.data_nascimento is None
        assert animal_bd.observacoes is None


class TestObterPorId:
    """Testes para busca por ID."""

    def test_obter_animal_com_relacionamentos(self, setup_completo):
        """Deve retornar animal com raça e abrigo."""
        animal = Animal(
            id=0,
            id_raca=setup_completo["id_raca"],
            id_abrigo=setup_completo["id_abrigo"],
            nome="Buddy",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponível",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        animal_bd = animal_repo.obter_por_id(id_inserido)

        assert animal_bd is not None
        assert animal_bd.raca is not None
        assert animal_bd.raca.nome == "Labrador"
        assert animal_bd.abrigo is not None

    def test_obter_animal_inexistente(self):
        """Deve retornar None para ID inexistente."""
        assert animal_repo.obter_por_id(99999) is None


class TestObterTodosDisponiveis:
    """Testes para listagem de animais disponíveis."""

    def test_obter_animais_disponiveis(self, setup_completo):
        """Deve listar apenas animais disponíveis."""
        # Criar animal disponível
        animal1 = Animal(
            id=0,
            id_raca=setup_completo["id_raca"],
            id_abrigo=setup_completo["id_abrigo"],
            nome="Max",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponível",
            foto=None
        )
        animal_repo.inserir(animal1)

        animais = animal_repo.obter_todos_disponiveis()
        assert len(animais) >= 1
        assert all(a.status == "Disponível" for a in animais)


class TestObterPorAbrigo:
    """Testes para busca por abrigo."""

    def test_obter_animais_por_abrigo(self, setup_completo):
        """Deve retornar animais do abrigo específico."""
        # Criar 2 animais no mesmo abrigo
        for i in range(2):
            animal = Animal(
                id=0,
                id_raca=setup_completo["id_raca"],
                id_abrigo=setup_completo["id_abrigo"],
                nome=f"Animal{i}",
                sexo="M",
                data_nascimento=None,
                data_entrada="2024-01-01",
                observacoes=None,
                status="Disponível",
                foto=None
            )
            animal_repo.inserir(animal)

        animais = animal_repo.obter_por_abrigo(setup_completo["id_abrigo"])
        assert len(animais) == 2


class TestAtualizar:
    """Testes para atualização."""

    def test_atualizar_animal(self, setup_completo):
        """Deve atualizar dados do animal."""
        animal = Animal(
            id=0,
            id_raca=setup_completo["id_raca"],
            id_abrigo=setup_completo["id_abrigo"],
            nome="Original",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponível",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        animal.id_animal = id_inserido
        animal.nome = "Atualizado"
        animal.observacoes = "Nova observação"
        resultado = animal_repo.atualizar(animal)

        assert resultado is True
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd.nome == "Atualizado"
        assert animal_bd.observacoes == "Nova observação"


class TestAtualizarStatus:
    """Testes para atualização de status."""

    def test_atualizar_status_animal(self, setup_completo):
        """Deve atualizar status do animal."""
        animal = Animal(
            id=0,
            id_raca=setup_completo["id_raca"],
            id_abrigo=setup_completo["id_abrigo"],
            nome="Test",
            sexo="F",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponível",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        resultado = animal_repo.atualizar_status(id_inserido, "Adotado")

        assert resultado is True
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd.status == "Adotado"


class TestExcluir:
    """Testes para exclusão."""

    def test_excluir_animal(self, setup_completo):
        """Deve excluir animal."""
        animal = Animal(
            id=0,
            id_raca=setup_completo["id_raca"],
            id_abrigo=setup_completo["id_abrigo"],
            nome="Delete",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponível",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        resultado = animal_repo.excluir(id_inserido)

        assert resultado is True
        assert animal_repo.obter_por_id(id_inserido) is None
