"""
Testes de integracao para o repositorio de racas.

Testa todas as operacoes CRUD e validacoes do raca_repo.

NOTA: Estes testes estao desabilitados ate que o aluno implemente
model/especie_model.py, repo/especie_repo.py e sql/especie_sql.py
"""
import pytest

# Skip todo o modulo ate que especie_model e especie_repo sejam implementados
pytest.skip(
    "Modulo especie_model e especie_repo ainda nao implementados",
    allow_module_level=True
)

from model.raca_model import Raca
from model.especie_model import Especie
from repo import raca_repo, especie_repo
from util.db_util import obter_conexao


@pytest.fixture
def especie_cachorro_teste():
    """Cria uma especie Cachorro de teste."""
    especie = Especie(id=0, nome="Cachorro Raca", descricao="Canis lupus")
    id_especie = especie_repo.inserir(especie)
    return id_especie


@pytest.fixture
def especie_gato_teste():
    """Cria uma especie Gato de teste."""
    especie = Especie(id=0, nome="Gato Raca", descricao="Felis catus")
    id_especie = especie_repo.inserir(especie)
    return id_especie


class TestRacaRepoCriarTabela:
    """Testes para criacao da tabela raca."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = raca_repo.criar_tabela()
        assert resultado is True

    def test_tabela_existe_apos_criacao(self):
        """Tabela deve existir apos criacao."""
        raca_repo.criar_tabela()
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='raca'"
            )
            tabela = cursor.fetchone()
            assert tabela is not None
            assert tabela["name"] == "raca"


class TestRacaRepoInserir:
    """Testes para insercao de racas."""

    def test_inserir_raca_completa(self, especie_cachorro_teste):
        """Deve inserir raca com todos os campos."""
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Labrador Teste",
            descricao="Raca docil e amigavel",
            temperamento="Docil",
            expectativa_de_vida="10-12 anos",
            porte="Grande"
        )
        id_inserido = raca_repo.inserir(raca)

        assert id_inserido > 0
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd is not None
        assert raca_bd.nome == "Labrador Teste"
        assert raca_bd.descricao == "Raca docil e amigavel"
        assert raca_bd.temperamento == "Docil"
        assert raca_bd.expectativa_de_vida == "10-12 anos"
        assert raca_bd.porte == "Grande"

    def test_inserir_raca_campos_minimos(self, especie_gato_teste):
        """Deve inserir raca apenas com campos obrigatorios."""
        raca = Raca(
            id=0,
            id_especie=especie_gato_teste,
            nome="Persa Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id_inserido = raca_repo.inserir(raca)

        assert id_inserido > 0
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd is not None
        assert raca_bd.nome == "Persa Teste"
        assert raca_bd.descricao is None
        assert raca_bd.temperamento is None
        assert raca_bd.expectativa_de_vida is None
        assert raca_bd.porte is None

    def test_inserir_gera_id_sequencial(self, especie_cachorro_teste):
        """IDs devem ser gerados sequencialmente."""
        raca1 = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Bulldog Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        raca2 = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Poodle Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )

        id1 = raca_repo.inserir(raca1)
        id2 = raca_repo.inserir(raca2)

        assert id2 > id1


class TestRacaRepoObterPorId:
    """Testes para busca de raca por ID."""

    def test_obter_raca_existente_com_especie(self, especie_cachorro_teste):
        """Deve retornar raca com especie relacionada."""
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Golden Retriever Teste",
            descricao="Raca inteligente",
            temperamento="Amigavel",
            expectativa_de_vida="10-12 anos",
            porte="Grande"
        )
        id_inserido = raca_repo.inserir(raca)

        raca_bd = raca_repo.obter_por_id(id_inserido)

        assert raca_bd is not None
        assert raca_bd.id == id_inserido
        assert raca_bd.nome == "Golden Retriever Teste"
        assert raca_bd.especie is not None
        assert raca_bd.especie.nome == "Cachorro Raca"
        assert raca_bd.especie.descricao == "Canis lupus"

    def test_obter_raca_inexistente(self):
        """Deve retornar None para ID inexistente."""
        raca_bd = raca_repo.obter_por_id(99999)
        assert raca_bd is None

    def test_obter_raca_campos_opcionais_none(self, especie_gato_teste):
        """Deve retornar raca com campos opcionais None."""
        raca = Raca(
            id=0,
            id_especie=especie_gato_teste,
            nome="Siames Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id_inserido = raca_repo.inserir(raca)

        raca_bd = raca_repo.obter_por_id(id_inserido)

        assert raca_bd is not None
        assert raca_bd.descricao is None
        assert raca_bd.temperamento is None
        assert raca_bd.expectativa_de_vida is None
        assert raca_bd.porte is None


class TestRacaRepoObterTodos:
    """Testes para listagem de todas as racas."""

    def test_obter_todos_lista_racas(self, especie_cachorro_teste, especie_gato_teste):
        """Deve retornar todas as racas com suas especies."""
        raca1 = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Beagle Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Medio"
        )
        raca2 = Raca(
            id=0,
            id_especie=especie_gato_teste,
            nome="Maine Coon Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )
        raca3 = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Chihuahua Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Pequeno"
        )

        raca_repo.inserir(raca1)
        raca_repo.inserir(raca2)
        raca_repo.inserir(raca3)

        racas = raca_repo.obter_todos()

        assert len(racas) >= 3
        nomes = [r.nome for r in racas]
        assert "Beagle Teste" in nomes
        assert "Maine Coon Teste" in nomes
        assert "Chihuahua Teste" in nomes

        # Verificar que todas tem especie relacionada
        for raca in racas:
            assert raca.especie is not None

    def test_obter_todos_preserva_relacionamento_especie(self, especie_cachorro_teste):
        """Deve preservar relacionamento com especie em todas as racas."""
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Dalmata Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        raca_repo.inserir(raca)

        racas = raca_repo.obter_todos()

        raca_encontrada = next((r for r in racas if r.nome == "Dalmata Teste"), None)
        assert raca_encontrada is not None
        assert raca_encontrada.especie.nome == "Cachorro Raca"


class TestRacaRepoObterPorEspecie:
    """Testes para busca de racas por especie."""

    def test_obter_racas_por_especie(self, especie_cachorro_teste, especie_gato_teste):
        """Deve retornar apenas racas da especie solicitada."""
        # Criar racas de cachorro
        raca1 = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Pastor Alemao Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )
        raca2 = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Rottweiler Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )

        # Criar raca de gato
        raca3 = Raca(
            id=0,
            id_especie=especie_gato_teste,
            nome="Ragdoll Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )

        raca_repo.inserir(raca1)
        raca_repo.inserir(raca2)
        raca_repo.inserir(raca3)

        racas_cachorro = raca_repo.obter_por_especie(especie_cachorro_teste)

        assert len(racas_cachorro) == 2
        nomes = [r.nome for r in racas_cachorro]
        assert "Pastor Alemao Teste" in nomes
        assert "Rottweiler Teste" in nomes
        assert "Ragdoll Teste" not in nomes

    def test_obter_por_especie_sem_racas(self, especie_cachorro_teste):
        """Deve retornar lista vazia se especie nao tem racas."""
        racas = raca_repo.obter_por_especie(especie_cachorro_teste)
        assert racas == []

    def test_obter_por_especie_inexistente(self):
        """Deve retornar lista vazia para especie inexistente."""
        racas = raca_repo.obter_por_especie(99999)
        assert racas == []


class TestRacaRepoAtualizar:
    """Testes para atualizacao de racas."""

    def test_atualizar_raca_existente(self, especie_cachorro_teste):
        """Deve atualizar raca existente."""
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Boxer Update",
            descricao="Descricao antiga",
            temperamento="Brincalhao",
            expectativa_de_vida="8-10 anos",
            porte="Medio"
        )
        id_inserido = raca_repo.inserir(raca)

        raca_atualizada = Raca(
            id=id_inserido,
            id_especie=especie_cachorro_teste,
            nome="Boxer Alemao Update",
            descricao="Descricao nova",
            temperamento="Energetico",
            expectativa_de_vida="10-12 anos",
            porte="Grande"
        )
        resultado = raca_repo.atualizar(raca_atualizada)

        assert resultado is True
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd.nome == "Boxer Alemao Update"
        assert raca_bd.descricao == "Descricao nova"
        assert raca_bd.temperamento == "Energetico"
        assert raca_bd.expectativa_de_vida == "10-12 anos"
        assert raca_bd.porte == "Grande"

    def test_atualizar_raca_inexistente(self, especie_cachorro_teste):
        """Deve retornar False ao atualizar raca inexistente."""
        raca = Raca(
            id=99999,
            id_especie=especie_cachorro_teste,
            nome="Inexistente",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        resultado = raca_repo.atualizar(raca)
        assert resultado is False

    def test_atualizar_campos_para_none(self, especie_gato_teste):
        """Deve permitir atualizar campos opcionais para None."""
        raca = Raca(
            id=0,
            id_especie=especie_gato_teste,
            nome="Angora Update",
            descricao="Com descricao",
            temperamento="Docil",
            expectativa_de_vida="12-15 anos",
            porte="Medio"
        )
        id_inserido = raca_repo.inserir(raca)

        raca_atualizada = Raca(
            id=id_inserido,
            id_especie=especie_gato_teste,
            nome="Angora Turco Update",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        resultado = raca_repo.atualizar(raca_atualizada)

        assert resultado is True
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd.descricao is None
        assert raca_bd.temperamento is None
        assert raca_bd.expectativa_de_vida is None
        assert raca_bd.porte is None

    def test_atualizar_mudar_especie(self, especie_cachorro_teste, especie_gato_teste):
        """Deve permitir mudar especie de uma raca."""
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Raca Troca Especie",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id_inserido = raca_repo.inserir(raca)

        raca_atualizada = Raca(
            id=id_inserido,
            id_especie=especie_gato_teste,
            nome="Raca Troca Especie",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        resultado = raca_repo.atualizar(raca_atualizada)

        assert resultado is True
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd.id_especie == especie_gato_teste
        assert raca_bd.especie.nome == "Gato Raca"


class TestRacaRepoExcluir:
    """Testes para exclusao de racas."""

    def test_excluir_raca_sem_animais(self, especie_cachorro_teste):
        """Deve excluir raca que nao tem animais vinculados."""
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Akita Excluir",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id_inserido = raca_repo.inserir(raca)

        resultado = raca_repo.excluir(id_inserido)

        assert resultado is True
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd is None

    def test_excluir_raca_inexistente(self):
        """Deve retornar False ao excluir raca inexistente."""
        resultado = raca_repo.excluir(99999)
        assert resultado is False

    def test_excluir_raca_com_animais_vinculados(self, especie_cachorro_teste):
        """Deve lancar excecao ao excluir raca com animais."""
        # Criar raca
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Husky Vinculo",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id = raca_repo.inserir(raca)

        # Criar abrigo e animal vinculado
        with obter_conexao() as conn:
            cursor = conn.cursor()
            # Criar usuario abrigo
            cursor.execute(
                "INSERT INTO usuario (nome, email, senha, perfil) VALUES (?, ?, ?, ?)",
                ("Abrigo Raca Teste", "abrigo_raca@test.com", "hash", "ABRIGO")
            )
            id_usuario = cursor.lastrowid

            # Criar abrigo
            cursor.execute(
                "INSERT INTO abrigo (id_abrigo, responsavel) VALUES (?, ?)",
                (id_usuario, "Responsavel")
            )

            # Criar animal
            cursor.execute(
                """INSERT INTO animal (id_raca, id_abrigo, nome, sexo, data_entrada)
                   VALUES (?, ?, ?, ?, ?)""",
                (id, id_usuario, "Rex Raca", "M", "2024-01-01")
            )

        # Tentar excluir deve lancar excecao
        with pytest.raises(Exception) as exc_info:
            raca_repo.excluir(id)

        assert "Nao e possivel excluir esta raca" in str(exc_info.value)
        assert "1 animal(is) vinculado(s)" in str(exc_info.value)


class TestRacaRepoIntegracaoCRUD:
    """Testes de integracao das operacoes CRUD."""

    def test_ciclo_completo_crud(self, especie_cachorro_teste):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        raca = Raca(
            id=0,
            id_especie=especie_cachorro_teste,
            nome="Shih Tzu CRUD",
            descricao="Raca pequena",
            temperamento="Calmo",
            expectativa_de_vida="10-16 anos",
            porte="Pequeno"
        )
        id_inserido = raca_repo.inserir(raca)
        assert id_inserido > 0

        # READ
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd is not None
        assert raca_bd.nome == "Shih Tzu CRUD"
        assert raca_bd.especie is not None
        assert raca_bd.especie.nome == "Cachorro Raca"

        # UPDATE
        raca_bd.nome = "Shih Tzu Imperial CRUD"
        raca_bd.descricao = "Raca mini"
        resultado_update = raca_repo.atualizar(raca_bd)
        assert resultado_update is True

        raca_atualizada = raca_repo.obter_por_id(id_inserido)
        assert raca_atualizada.nome == "Shih Tzu Imperial CRUD"
        assert raca_atualizada.descricao == "Raca mini"

        # DELETE
        resultado_delete = raca_repo.excluir(id_inserido)
        assert resultado_delete is True

        raca_excluida = raca_repo.obter_por_id(id_inserido)
        assert raca_excluida is None

    def test_multiplas_racas_mesma_especie(self, especie_cachorro_teste):
        """Deve gerenciar multiplas racas da mesma especie."""
        racas_inseridas = []

        portes = ["Pequeno", "Medio", "Grande"]
        for i, porte in enumerate(portes):
            raca = Raca(
                id=0,
                id_especie=especie_cachorro_teste,
                nome=f"Raca Multi {i}",
                descricao=None,
                temperamento=None,
                expectativa_de_vida=None,
                porte=porte
            )
            id_inserido = raca_repo.inserir(raca)
            racas_inseridas.append(id_inserido)

        # Verificar que todas foram inseridas
        racas_especie = raca_repo.obter_por_especie(especie_cachorro_teste)
        assert len(racas_especie) == 3

        # Excluir uma no meio
        raca_repo.excluir(racas_inseridas[1])

        # Verificar que outras continuam
        racas_especie = raca_repo.obter_por_especie(especie_cachorro_teste)
        assert len(racas_especie) == 2
