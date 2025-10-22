"""
Testes para o repositório de raças.

Testa todas as operações CRUD e validações do raca_repo,
incluindo models e SQLs relacionados, com relacionamentos com espécie.
"""

import pytest
from model.raca_model import Raca
from model.especie_model import Especie
from repo import raca_repo, especie_repo
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_racas():
    """Limpa tabelas de raças e espécies antes de cada teste."""
    # Criar tabelas se não existirem
    especie_repo.criar_tabela()
    raca_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM raca")
        cursor.execute("DELETE FROM especie")
        cursor.execute("PRAGMA foreign_keys = ON")
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DELETE FROM raca")
        cursor.execute("DELETE FROM especie")
        cursor.execute("PRAGMA foreign_keys = ON")


@pytest.fixture
def especie_cachorro():
    """Fixture que cria uma espécie Cachorro."""
    especie = Especie(id_especie=0, nome="Cachorro", descricao="Canis lupus")
    id_especie = especie_repo.inserir(especie)
    return id_especie


@pytest.fixture
def especie_gato():
    """Fixture que cria uma espécie Gato."""
    especie = Especie(id_especie=0, nome="Gato", descricao="Felis catus")
    id_especie = especie_repo.inserir(especie)
    return id_especie


class TestCriarTabela:
    """Testes para criação da tabela raca."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = raca_repo.criar_tabela()
        assert resultado is True

    def test_tabela_existe_apos_criacao(self):
        """Tabela deve existir após criação."""
        raca_repo.criar_tabela()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='raca'"
            )
            tabela = cursor.fetchone()
            assert tabela is not None
            assert tabela["name"] == "raca"


class TestInserir:
    """Testes para inserção de raças."""

    def test_inserir_raca_completa(self, especie_cachorro):
        """Deve inserir raça com todos os campos."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Labrador",
            descricao="Raça dócil e amigável",
            temperamento="Dócil",
            expectativa_de_vida="10-12 anos",
            porte="Grande"
        )
        id_inserido = raca_repo.inserir(raca)

        assert id_inserido > 0
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd is not None
        assert raca_bd.nome == "Labrador"
        assert raca_bd.descricao == "Raça dócil e amigável"
        assert raca_bd.temperamento == "Dócil"
        assert raca_bd.expectativa_de_vida == "10-12 anos"
        assert raca_bd.porte == "Grande"

    def test_inserir_raca_campos_minimos(self, especie_gato):
        """Deve inserir raça apenas com campos obrigatórios."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_gato,
            nome="Persa",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id_inserido = raca_repo.inserir(raca)

        assert id_inserido > 0
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd is not None
        assert raca_bd.nome == "Persa"
        assert raca_bd.descricao is None
        assert raca_bd.temperamento is None
        assert raca_bd.expectativa_de_vida is None
        assert raca_bd.porte is None

    def test_inserir_gera_id_sequencial(self, especie_cachorro):
        """IDs devem ser gerados sequencialmente."""
        raca1 = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Bulldog",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        raca2 = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Poodle",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )

        id1 = raca_repo.inserir(raca1)
        id2 = raca_repo.inserir(raca2)

        assert id2 > id1


class TestObterPorId:
    """Testes para busca de raça por ID."""

    def test_obter_raca_existente_com_especie(self, especie_cachorro):
        """Deve retornar raça com espécie relacionada."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Golden Retriever",
            descricao="Raça inteligente",
            temperamento="Amigável",
            expectativa_de_vida="10-12 anos",
            porte="Grande"
        )
        id_inserido = raca_repo.inserir(raca)

        raca_bd = raca_repo.obter_por_id(id_inserido)

        assert raca_bd is not None
        assert raca_bd.id_raca == id_inserido
        assert raca_bd.nome == "Golden Retriever"
        assert raca_bd.especie is not None
        assert raca_bd.especie.nome == "Cachorro"
        assert raca_bd.especie.descricao == "Canis lupus"

    def test_obter_raca_inexistente(self):
        """Deve retornar None para ID inexistente."""
        raca_bd = raca_repo.obter_por_id(99999)
        assert raca_bd is None

    def test_obter_raca_campos_opcionais_none(self, especie_gato):
        """Deve retornar raça com campos opcionais None."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_gato,
            nome="Siamês",
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


class TestObterTodos:
    """Testes para listagem de todas as raças."""

    def test_obter_todos_lista_vazia(self):
        """Deve retornar lista vazia quando não há raças."""
        racas = raca_repo.obter_todos()
        assert racas == []

    def test_obter_todos_lista_racas(self, especie_cachorro, especie_gato):
        """Deve retornar todas as raças com suas espécies."""
        raca1 = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Beagle",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Médio"
        )
        raca2 = Raca(
            id_raca=0,
            id_especie=especie_gato,
            nome="Maine Coon",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )
        raca3 = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Chihuahua",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Pequeno"
        )

        raca_repo.inserir(raca1)
        raca_repo.inserir(raca2)
        raca_repo.inserir(raca3)

        racas = raca_repo.obter_todos()

        assert len(racas) == 3
        nomes = [r.nome for r in racas]
        assert "Beagle" in nomes
        assert "Maine Coon" in nomes
        assert "Chihuahua" in nomes

        # Verificar que todas têm espécie relacionada
        for raca in racas:
            assert raca.especie is not None

    def test_obter_todos_preserva_relacionamento_especie(self, especie_cachorro):
        """Deve preservar relacionamento com espécie em todas as raças."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Dálmata",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        raca_repo.inserir(raca)

        racas = raca_repo.obter_todos()

        assert len(racas) == 1
        assert racas[0].especie.nome == "Cachorro"


class TestObterPorEspecie:
    """Testes para busca de raças por espécie."""

    def test_obter_racas_por_especie(self, especie_cachorro, especie_gato):
        """Deve retornar apenas raças da espécie solicitada."""
        # Criar raças de cachorro
        raca1 = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Pastor Alemão",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )
        raca2 = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Rottweiler",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )

        # Criar raça de gato
        raca3 = Raca(
            id_raca=0,
            id_especie=especie_gato,
            nome="Ragdoll",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte="Grande"
        )

        raca_repo.inserir(raca1)
        raca_repo.inserir(raca2)
        raca_repo.inserir(raca3)

        racas_cachorro = raca_repo.obter_por_especie(especie_cachorro)

        assert len(racas_cachorro) == 2
        nomes = [r.nome for r in racas_cachorro]
        assert "Pastor Alemão" in nomes
        assert "Rottweiler" in nomes
        assert "Ragdoll" not in nomes

    def test_obter_por_especie_sem_racas(self, especie_cachorro):
        """Deve retornar lista vazia se espécie não tem raças."""
        racas = raca_repo.obter_por_especie(especie_cachorro)
        assert racas == []

    def test_obter_por_especie_inexistente(self):
        """Deve retornar lista vazia para espécie inexistente."""
        racas = raca_repo.obter_por_especie(99999)
        assert racas == []


class TestAtualizar:
    """Testes para atualização de raças."""

    def test_atualizar_raca_existente(self, especie_cachorro):
        """Deve atualizar raça existente."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Boxer",
            descricao="Descrição antiga",
            temperamento="Brincalhão",
            expectativa_de_vida="8-10 anos",
            porte="Médio"
        )
        id_inserido = raca_repo.inserir(raca)

        raca_atualizada = Raca(
            id_raca=id_inserido,
            id_especie=especie_cachorro,
            nome="Boxer Alemão",
            descricao="Descrição nova",
            temperamento="Energético",
            expectativa_de_vida="10-12 anos",
            porte="Grande"
        )
        resultado = raca_repo.atualizar(raca_atualizada)

        assert resultado is True
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd.nome == "Boxer Alemão"
        assert raca_bd.descricao == "Descrição nova"
        assert raca_bd.temperamento == "Energético"
        assert raca_bd.expectativa_de_vida == "10-12 anos"
        assert raca_bd.porte == "Grande"

    def test_atualizar_raca_inexistente(self, especie_cachorro):
        """Deve retornar False ao atualizar raça inexistente."""
        raca = Raca(
            id_raca=99999,
            id_especie=especie_cachorro,
            nome="Inexistente",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        resultado = raca_repo.atualizar(raca)
        assert resultado is False

    def test_atualizar_campos_para_none(self, especie_gato):
        """Deve permitir atualizar campos opcionais para None."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_gato,
            nome="Angorá",
            descricao="Com descrição",
            temperamento="Dócil",
            expectativa_de_vida="12-15 anos",
            porte="Médio"
        )
        id_inserido = raca_repo.inserir(raca)

        raca_atualizada = Raca(
            id_raca=id_inserido,
            id_especie=especie_gato,
            nome="Angorá Turco",
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

    def test_atualizar_mudar_especie(self, especie_cachorro, especie_gato):
        """Deve permitir mudar espécie de uma raça."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Raça Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id_inserido = raca_repo.inserir(raca)

        raca_atualizada = Raca(
            id_raca=id_inserido,
            id_especie=especie_gato,
            nome="Raça Teste",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        resultado = raca_repo.atualizar(raca_atualizada)

        assert resultado is True
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd.id_especie == especie_gato
        assert raca_bd.especie.nome == "Gato"


class TestExcluir:
    """Testes para exclusão de raças."""

    def test_excluir_raca_sem_animais(self, especie_cachorro):
        """Deve excluir raça que não tem animais vinculados."""
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Akita",
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
        """Deve retornar False ao excluir raça inexistente."""
        resultado = raca_repo.excluir(99999)
        assert resultado is False

    def test_excluir_raca_com_animais_vinculados(self, especie_cachorro):
        """Deve lançar exceção ao excluir raça com animais."""
        # Criar raça
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Husky",
            descricao=None,
            temperamento=None,
            expectativa_de_vida=None,
            porte=None
        )
        id_raca = raca_repo.inserir(raca)

        # Criar abrigo e animal vinculado
        with get_connection() as conn:
            cursor = conn.cursor()
            # Criar usuário abrigo
            cursor.execute(
                "INSERT INTO usuario (nome, email, senha, perfil) VALUES (?, ?, ?, ?)",
                ("Abrigo Teste", "abrigo@test.com", "hash", "ABRIGO")
            )
            id_usuario = cursor.lastrowid

            # Criar abrigo
            cursor.execute(
                "INSERT INTO abrigo (id_abrigo, responsavel) VALUES (?, ?)",
                (id_usuario, "Responsável")
            )

            # Criar animal
            cursor.execute(
                """INSERT INTO animal (id_raca, id_abrigo, nome, sexo, data_entrada)
                   VALUES (?, ?, ?, ?, ?)""",
                (id_raca, id_usuario, "Rex", "M", "2024-01-01")
            )

        # Tentar excluir deve lançar exceção
        with pytest.raises(Exception) as exc_info:
            raca_repo.excluir(id_raca)

        assert "Não é possível excluir esta raça" in str(exc_info.value)
        assert "1 animal(is) vinculado(s)" in str(exc_info.value)


class TestIntegracaoCRUD:
    """Testes de integração das operações CRUD."""

    def test_ciclo_completo_crud(self, especie_cachorro):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        raca = Raca(
            id_raca=0,
            id_especie=especie_cachorro,
            nome="Shih Tzu",
            descricao="Raça pequena",
            temperamento="Calmo",
            expectativa_de_vida="10-16 anos",
            porte="Pequeno"
        )
        id_inserido = raca_repo.inserir(raca)
        assert id_inserido > 0

        # READ
        raca_bd = raca_repo.obter_por_id(id_inserido)
        assert raca_bd is not None
        assert raca_bd.nome == "Shih Tzu"
        assert raca_bd.especie is not None
        assert raca_bd.especie.nome == "Cachorro"

        # UPDATE
        raca_bd.nome = "Shih Tzu Imperial"
        raca_bd.descricao = "Raça mini"
        resultado_update = raca_repo.atualizar(raca_bd)
        assert resultado_update is True

        raca_atualizada = raca_repo.obter_por_id(id_inserido)
        assert raca_atualizada.nome == "Shih Tzu Imperial"
        assert raca_atualizada.descricao == "Raça mini"

        # DELETE
        resultado_delete = raca_repo.excluir(id_inserido)
        assert resultado_delete is True

        raca_excluida = raca_repo.obter_por_id(id_inserido)
        assert raca_excluida is None

    def test_multiplas_racas_mesma_especie(self, especie_cachorro):
        """Deve gerenciar múltiplas raças da mesma espécie."""
        racas_inseridas = []

        portes = ["Pequeno", "Médio", "Grande"]
        for i, porte in enumerate(portes):
            raca = Raca(
                id_raca=0,
                id_especie=especie_cachorro,
                nome=f"Raça{i}",
                descricao=None,
                temperamento=None,
                expectativa_de_vida=None,
                porte=porte
            )
            id_inserido = raca_repo.inserir(raca)
            racas_inseridas.append(id_inserido)

        # Verificar que todas foram inseridas
        racas_especie = raca_repo.obter_por_especie(especie_cachorro)
        assert len(racas_especie) == 3

        # Excluir uma no meio
        raca_repo.excluir(racas_inseridas[1])

        # Verificar que outras continuam
        racas_especie = raca_repo.obter_por_especie(especie_cachorro)
        assert len(racas_especie) == 2
