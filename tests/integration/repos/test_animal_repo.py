"""
Testes de integracao para o repositorio de animais.

Testa todas as operacoes CRUD do animal_repo.

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
from model.animal_model import Animal
from model.usuario_model import Usuario
from model.especie_model import Especie
from model.raca_model import Raca
from model.abrigo_model import Abrigo
from repo import animal_repo, usuario_repo, especie_repo, raca_repo, abrigo_repo
from util.security import criar_hash_senha
from util.perfis import Perfil


@pytest.fixture
def setup_animal_completo():
    """Cria estrutura completa: usuario, abrigo, especie e raca."""
    # Criar usuario abrigo
    usuario = Usuario(
        id=0, nome="Abrigo Animal Teste", email="abrigo_animal@test.com",
        senha=criar_hash_senha("Senha@123"), perfil=Perfil.ABRIGO.value
    )
    id_usuario = usuario_repo.inserir(usuario)

    # Criar abrigo
    abrigo = Abrigo(
        id_abrigo=id_usuario, responsavel="Responsavel",
        descricao=None, data_abertura=None, data_membros=None
    )
    abrigo_repo.inserir(abrigo)

    # Criar especie
    especie = Especie(id=0, nome="Cachorro Animal", descricao=None)
    id_especie = especie_repo.inserir(especie)

    # Criar raca
    raca = Raca(
        id=0, id_especie=id_especie, nome="Labrador Animal",
        descricao=None, temperamento=None,
        expectativa_de_vida=None, porte=None
    )
    id_raca = raca_repo.inserir(raca)

    return {"id_abrigo": id_usuario, "id_raca": id_raca, "id_especie": id_especie}


class TestAnimalRepoCriarTabela:
    """Testes para criacao da tabela animal."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = animal_repo.criar_tabela()
        assert resultado is True


class TestAnimalRepoInserir:
    """Testes para insercao de animais."""

    def test_inserir_animal_completo(self, setup_animal_completo):
        """Deve inserir animal com todos os campos."""
        animal = Animal(
            id=0,
            id_raca=setup_animal_completo["id_raca"],
            id_abrigo=setup_animal_completo["id_abrigo"],
            nome="Rex",
            sexo="M",
            data_nascimento="2020-05-15",
            data_entrada="2024-01-10",
            observacoes="Docil e brincalhao",
            status="Disponivel",
            foto="rex.jpg"
        )
        id_inserido = animal_repo.inserir(animal)

        assert id_inserido > 0
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd is not None
        assert animal_bd.nome == "Rex"
        assert animal_bd.sexo == "M"
        assert animal_bd.status == "Disponivel"

    def test_inserir_animal_campos_minimos(self, setup_animal_completo):
        """Deve inserir animal com campos minimos."""
        animal = Animal(
            id=0,
            id_raca=setup_animal_completo["id_raca"],
            id_abrigo=setup_animal_completo["id_abrigo"],
            nome="Toby",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponivel",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        assert id_inserido > 0
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd.data_nascimento is None
        assert animal_bd.observacoes is None


class TestAnimalRepoObterPorId:
    """Testes para busca por ID."""

    def test_obter_animal_com_relacionamentos(self, setup_animal_completo):
        """Deve retornar animal com raca e abrigo."""
        animal = Animal(
            id=0,
            id_raca=setup_animal_completo["id_raca"],
            id_abrigo=setup_animal_completo["id_abrigo"],
            nome="Buddy",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponivel",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        animal_bd = animal_repo.obter_por_id(id_inserido)

        assert animal_bd is not None
        assert animal_bd.raca is not None
        assert animal_bd.raca.nome == "Labrador Animal"
        assert animal_bd.abrigo is not None

    def test_obter_animal_inexistente(self):
        """Deve retornar None para ID inexistente."""
        assert animal_repo.obter_por_id(99999) is None


class TestAnimalRepoObterTodosDisponiveis:
    """Testes para listagem de animais disponiveis."""

    def test_obter_animais_disponiveis(self, setup_animal_completo):
        """Deve listar apenas animais disponiveis."""
        # Criar animal disponivel
        animal1 = Animal(
            id=0,
            id_raca=setup_animal_completo["id_raca"],
            id_abrigo=setup_animal_completo["id_abrigo"],
            nome="Max Disponivel",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponivel",
            foto=None
        )
        animal_repo.inserir(animal1)

        animais = animal_repo.obter_todos_disponiveis()
        assert len(animais) >= 1
        assert all(a.status == "Disponivel" for a in animais)


class TestAnimalRepoObterPorAbrigo:
    """Testes para busca por abrigo."""

    def test_obter_animais_por_abrigo(self, setup_animal_completo):
        """Deve retornar animais do abrigo especifico."""
        # Criar 2 animais no mesmo abrigo
        for i in range(2):
            animal = Animal(
                id=0,
                id_raca=setup_animal_completo["id_raca"],
                id_abrigo=setup_animal_completo["id_abrigo"],
                nome=f"Animal Abrigo {i}",
                sexo="M",
                data_nascimento=None,
                data_entrada="2024-01-01",
                observacoes=None,
                status="Disponivel",
                foto=None
            )
            animal_repo.inserir(animal)

        animais = animal_repo.obter_por_abrigo(setup_animal_completo["id_abrigo"])
        assert len(animais) == 2


class TestAnimalRepoAtualizar:
    """Testes para atualizacao."""

    def test_atualizar_animal(self, setup_animal_completo):
        """Deve atualizar dados do animal."""
        animal = Animal(
            id=0,
            id_raca=setup_animal_completo["id_raca"],
            id_abrigo=setup_animal_completo["id_abrigo"],
            nome="Original Update",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponivel",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        animal.id_animal = id_inserido
        animal.nome = "Atualizado"
        animal.observacoes = "Nova observacao"
        resultado = animal_repo.atualizar(animal)

        assert resultado is True
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd.nome == "Atualizado"
        assert animal_bd.observacoes == "Nova observacao"


class TestAnimalRepoAtualizarStatus:
    """Testes para atualizacao de status."""

    def test_atualizar_status_animal(self, setup_animal_completo):
        """Deve atualizar status do animal."""
        animal = Animal(
            id=0,
            id_raca=setup_animal_completo["id_raca"],
            id_abrigo=setup_animal_completo["id_abrigo"],
            nome="Status Test",
            sexo="F",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponivel",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        resultado = animal_repo.atualizar_status(id_inserido, "Adotado")

        assert resultado is True
        animal_bd = animal_repo.obter_por_id(id_inserido)
        assert animal_bd.status == "Adotado"


class TestAnimalRepoExcluir:
    """Testes para exclusao."""

    def test_excluir_animal(self, setup_animal_completo):
        """Deve excluir animal."""
        animal = Animal(
            id=0,
            id_raca=setup_animal_completo["id_raca"],
            id_abrigo=setup_animal_completo["id_abrigo"],
            nome="Delete Animal",
            sexo="M",
            data_nascimento=None,
            data_entrada="2024-01-01",
            observacoes=None,
            status="Disponivel",
            foto=None
        )
        id_inserido = animal_repo.inserir(animal)

        resultado = animal_repo.excluir(id_inserido)

        assert resultado is True
        assert animal_repo.obter_por_id(id_inserido) is None
