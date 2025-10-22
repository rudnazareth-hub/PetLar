"""
Testes para o repositório de espécies.

Testa todas as operações CRUD e validações do especie_repo,
incluindo models e SQLs relacionados.
"""

import pytest
from model.especie_model import Especie
from repo import especie_repo
from util.db_util import get_connection


@pytest.fixture(autouse=True)
def limpar_especies():
    """Limpa tabela de espécies antes de cada teste."""
    # Criar tabela se não existir
    especie_repo.criar_tabela()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM especie")
    yield
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM especie")


class TestCriarTabela:
    """Testes para criação da tabela especie."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = especie_repo.criar_tabela()
        assert resultado is True

    def test_tabela_existe_apos_criacao(self):
        """Tabela deve existir após criação."""
        especie_repo.criar_tabela()
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='especie'"
            )
            tabela = cursor.fetchone()
            assert tabela is not None
            assert tabela["name"] == "especie"


class TestInserir:
    """Testes para inserção de espécies."""

    def test_inserir_especie_completa(self):
        """Deve inserir espécie com todos os campos."""
        especie = Especie(
            id_especie=0,
            nome="Cachorro",
            descricao="Melhor amigo do homem"
        )
        id_inserido = especie_repo.inserir(especie)

        assert id_inserido > 0
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is not None
        assert especie_bd.nome == "Cachorro"
        assert especie_bd.descricao == "Melhor amigo do homem"

    def test_inserir_especie_sem_descricao(self):
        """Deve inserir espécie sem descrição (campo opcional)."""
        especie = Especie(
            id_especie=0,
            nome="Gato",
            descricao=None
        )
        id_inserido = especie_repo.inserir(especie)

        assert id_inserido > 0
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is not None
        assert especie_bd.nome == "Gato"
        assert especie_bd.descricao is None

    def test_inserir_gera_id_sequencial(self):
        """IDs devem ser gerados sequencialmente."""
        especie1 = Especie(id_especie=0, nome="Cachorro", descricao=None)
        especie2 = Especie(id_especie=0, nome="Gato", descricao=None)

        id1 = especie_repo.inserir(especie1)
        id2 = especie_repo.inserir(especie2)

        assert id2 > id1


class TestObterPorId:
    """Testes para busca de espécie por ID."""

    def test_obter_especie_existente(self):
        """Deve retornar espécie existente."""
        especie = Especie(id_especie=0, nome="Pássaro", descricao="Animal voador")
        id_inserido = especie_repo.inserir(especie)

        especie_bd = especie_repo.obter_por_id(id_inserido)

        assert especie_bd is not None
        assert especie_bd.id_especie == id_inserido
        assert especie_bd.nome == "Pássaro"
        assert especie_bd.descricao == "Animal voador"

    def test_obter_especie_inexistente(self):
        """Deve retornar None para ID inexistente."""
        especie_bd = especie_repo.obter_por_id(99999)
        assert especie_bd is None

    def test_obter_especie_sem_descricao(self):
        """Deve retornar espécie com descricao None."""
        especie = Especie(id_especie=0, nome="Réptil", descricao=None)
        id_inserido = especie_repo.inserir(especie)

        especie_bd = especie_repo.obter_por_id(id_inserido)

        assert especie_bd is not None
        assert especie_bd.descricao is None


class TestObterPorNome:
    """Testes para busca de espécie por nome."""

    def test_obter_especie_por_nome_existente(self):
        """Deve retornar espécie pelo nome."""
        especie = Especie(id_especie=0, nome="Hamster", descricao="Roedor pequeno")
        especie_repo.inserir(especie)

        especie_bd = especie_repo.obter_por_nome("Hamster")

        assert especie_bd is not None
        assert especie_bd.nome == "Hamster"
        assert especie_bd.descricao == "Roedor pequeno"

    def test_obter_especie_por_nome_inexistente(self):
        """Deve retornar None para nome inexistente."""
        especie_bd = especie_repo.obter_por_nome("Dinossauro")
        assert especie_bd is None

    def test_obter_especie_nome_case_sensitive(self):
        """Busca por nome deve ser case sensitive."""
        especie = Especie(id_especie=0, nome="Cachorro", descricao=None)
        especie_repo.inserir(especie)

        especie_upper = especie_repo.obter_por_nome("CACHORRO")
        assert especie_upper is None


class TestObterTodos:
    """Testes para listagem de todas as espécies."""

    def test_obter_todos_lista_vazia(self):
        """Deve retornar lista vazia quando não há espécies."""
        especies = especie_repo.obter_todos()
        assert especies == []

    def test_obter_todos_lista_especies(self):
        """Deve retornar todas as espécies cadastradas."""
        especie1 = Especie(id_especie=0, nome="Cachorro", descricao="Canis lupus")
        especie2 = Especie(id_especie=0, nome="Gato", descricao="Felis catus")
        especie3 = Especie(id_especie=0, nome="Pássaro", descricao=None)

        especie_repo.inserir(especie1)
        especie_repo.inserir(especie2)
        especie_repo.inserir(especie3)

        especies = especie_repo.obter_todos()

        assert len(especies) == 3
        nomes = [e.nome for e in especies]
        assert "Cachorro" in nomes
        assert "Gato" in nomes
        assert "Pássaro" in nomes

    def test_obter_todos_com_campos_opcionais_none(self):
        """Deve retornar espécies com campos opcionais None."""
        especie = Especie(id_especie=0, nome="Cobra", descricao=None)
        especie_repo.inserir(especie)

        especies = especie_repo.obter_todos()

        assert len(especies) == 1
        assert especies[0].nome == "Cobra"
        assert especies[0].descricao is None


class TestAtualizar:
    """Testes para atualização de espécies."""

    def test_atualizar_especie_existente(self):
        """Deve atualizar espécie existente."""
        especie = Especie(id_especie=0, nome="Cachorro", descricao="Descrição antiga")
        id_inserido = especie_repo.inserir(especie)

        especie_atualizada = Especie(
            id_especie=id_inserido,
            nome="Cachorro Doméstico",
            descricao="Descrição nova"
        )
        resultado = especie_repo.atualizar(especie_atualizada)

        assert resultado is True
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd.nome == "Cachorro Doméstico"
        assert especie_bd.descricao == "Descrição nova"

    def test_atualizar_especie_inexistente(self):
        """Deve retornar False ao atualizar espécie inexistente."""
        especie = Especie(
            id_especie=99999,
            nome="Inexistente",
            descricao="Teste"
        )
        resultado = especie_repo.atualizar(especie)
        assert resultado is False

    def test_atualizar_para_descricao_none(self):
        """Deve permitir atualizar descrição para None."""
        especie = Especie(id_especie=0, nome="Peixe", descricao="Com descrição")
        id_inserido = especie_repo.inserir(especie)

        especie_atualizada = Especie(
            id_especie=id_inserido,
            nome="Peixe Ornamental",
            descricao=None
        )
        resultado = especie_repo.atualizar(especie_atualizada)

        assert resultado is True
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd.descricao is None


class TestExcluir:
    """Testes para exclusão de espécies."""

    def test_excluir_especie_sem_racas(self):
        """Deve excluir espécie que não tem raças vinculadas."""
        especie = Especie(id_especie=0, nome="Tartaruga", descricao=None)
        id_inserido = especie_repo.inserir(especie)

        resultado = especie_repo.excluir(id_inserido)

        assert resultado is True
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is None

    def test_excluir_especie_inexistente(self):
        """Deve retornar False ao excluir espécie inexistente."""
        resultado = especie_repo.excluir(99999)
        assert resultado is False

    def test_excluir_especie_com_racas_vinculadas(self):
        """Deve lançar exceção ao excluir espécie com raças."""
        # Criar espécie
        especie = Especie(id_especie=0, nome="Cachorro", descricao=None)
        id_especie = especie_repo.inserir(especie)

        # Criar raça vinculada
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO raca (id_especie, nome) VALUES (?, ?)",
                (id_especie, "Labrador")
            )

        # Tentar excluir deve lançar exceção
        with pytest.raises(Exception) as exc_info:
            especie_repo.excluir(id_especie)

        assert "Não é possível excluir esta espécie" in str(exc_info.value)
        assert "1 raça(s) vinculada(s)" in str(exc_info.value)

    def test_excluir_especie_com_multiplas_racas(self):
        """Deve informar quantidade correta de raças vinculadas."""
        # Criar espécie
        especie = Especie(id_especie=0, nome="Gato", descricao=None)
        id_especie = especie_repo.inserir(especie)

        # Criar múltiplas raças vinculadas
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO raca (id_especie, nome) VALUES (?, ?)",
                (id_especie, "Persa")
            )
            cursor.execute(
                "INSERT INTO raca (id_especie, nome) VALUES (?, ?)",
                (id_especie, "Siamês")
            )
            cursor.execute(
                "INSERT INTO raca (id_especie, nome) VALUES (?, ?)",
                (id_especie, "Maine Coon")
            )

        with pytest.raises(Exception) as exc_info:
            especie_repo.excluir(id_especie)

        assert "3 raça(s) vinculada(s)" in str(exc_info.value)


class TestExisteNome:
    """Testes para verificação de existência de nome."""

    def test_existe_nome_true(self):
        """Deve retornar True se nome existe."""
        especie = Especie(id_especie=0, nome="Coelho", descricao=None)
        especie_repo.inserir(especie)

        existe = especie_repo.existe_nome("Coelho")
        assert existe is True

    def test_existe_nome_false(self):
        """Deve retornar False se nome não existe."""
        existe = especie_repo.existe_nome("Unicórnio")
        assert existe is False

    def test_existe_nome_excluindo_proprio_id(self):
        """Deve retornar False ao excluir próprio ID da verificação."""
        especie = Especie(id_especie=0, nome="Porco", descricao=None)
        id_inserido = especie_repo.inserir(especie)

        # Verificar sem excluir ID - deve retornar True
        existe_sem_excluir = especie_repo.existe_nome("Porco")
        assert existe_sem_excluir is True

        # Verificar excluindo o próprio ID - deve retornar False
        existe_excluindo = especie_repo.existe_nome("Porco", id_excluir=id_inserido)
        assert existe_excluindo is False

    def test_existe_nome_excluindo_id_diferente(self):
        """Deve retornar True se nome existe em ID diferente do excluído."""
        especie1 = Especie(id_especie=0, nome="Vaca", descricao=None)
        especie2 = Especie(id_especie=0, nome="Cavalo", descricao=None)

        id1 = especie_repo.inserir(especie1)
        id2 = especie_repo.inserir(especie2)

        # Verificar "Vaca" excluindo ID do Cavalo - deve retornar True
        existe = especie_repo.existe_nome("Vaca", id_excluir=id2)
        assert existe is True

    def test_existe_nome_case_sensitive(self):
        """Verificação de nome deve ser case sensitive."""
        especie = Especie(id_especie=0, nome="Ovelha", descricao=None)
        especie_repo.inserir(especie)

        existe_upper = especie_repo.existe_nome("OVELHA")
        assert existe_upper is False


class TestIntegracaoCRUD:
    """Testes de integração das operações CRUD."""

    def test_ciclo_completo_crud(self):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        especie = Especie(id_especie=0, nome="Rato", descricao="Roedor pequeno")
        id_inserido = especie_repo.inserir(especie)
        assert id_inserido > 0

        # READ
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is not None
        assert especie_bd.nome == "Rato"

        # UPDATE
        especie_bd.nome = "Rato Doméstico"
        especie_bd.descricao = "Pet de estimação"
        resultado_update = especie_repo.atualizar(especie_bd)
        assert resultado_update is True

        especie_atualizada = especie_repo.obter_por_id(id_inserido)
        assert especie_atualizada.nome == "Rato Doméstico"
        assert especie_atualizada.descricao == "Pet de estimação"

        # DELETE
        resultado_delete = especie_repo.excluir(id_inserido)
        assert resultado_delete is True

        especie_excluida = especie_repo.obter_por_id(id_inserido)
        assert especie_excluida is None

    def test_multiplas_especies_independentes(self):
        """Deve gerenciar múltiplas espécies independentemente."""
        especies_inseridas = []

        for i in range(5):
            especie = Especie(
                id_especie=0,
                nome=f"Especie{i}",
                descricao=f"Descrição {i}"
            )
            id_inserido = especie_repo.inserir(especie)
            especies_inseridas.append(id_inserido)

        # Verificar que todas foram inseridas
        todas = especie_repo.obter_todos()
        assert len(todas) == 5

        # Excluir uma no meio
        especie_repo.excluir(especies_inseridas[2])

        # Verificar que outras continuam
        todas = especie_repo.obter_todos()
        assert len(todas) == 4
        assert especie_repo.obter_por_id(especies_inseridas[0]) is not None
        assert especie_repo.obter_por_id(especies_inseridas[1]) is not None
        assert especie_repo.obter_por_id(especies_inseridas[2]) is None
        assert especie_repo.obter_por_id(especies_inseridas[3]) is not None
        assert especie_repo.obter_por_id(especies_inseridas[4]) is not None
