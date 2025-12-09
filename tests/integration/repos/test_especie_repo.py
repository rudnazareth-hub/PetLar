"""
Testes de integracao para o repositorio de especies.

Testa todas as operacoes CRUD e validacoes do especie_repo.

NOTA: Estes testes estao desabilitados ate que o aluno implemente
model/especie_model.py, repo/especie_repo.py e sql/especie_sql.py
"""
import pytest

# Skip todo o modulo ate que especie_model e especie_repo sejam implementados
pytest.skip(
    "Modulo especie_model e especie_repo ainda nao implementados",
    allow_module_level=True
)

from model.especie_model import Especie
from repo import especie_repo
from util.db_util import obter_conexao


@pytest.fixture
def especie_teste():
    """Cria uma especie de teste."""
    especie = Especie(id=0, nome="Cachorro", descricao="Canis lupus")
    id_inserido = especie_repo.inserir(especie)
    return id_inserido


class TestEspecieRepoCriarTabela:
    """Testes para criacao da tabela especie."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = especie_repo.criar_tabela()
        assert resultado is True

    def test_tabela_existe_apos_criacao(self):
        """Tabela deve existir apos criacao."""
        especie_repo.criar_tabela()
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='especie'"
            )
            tabela = cursor.fetchone()
            assert tabela is not None
            assert tabela["name"] == "especie"


class TestEspecieRepoInserir:
    """Testes para insercao de especies."""

    def test_inserir_especie_completa(self):
        """Deve inserir especie com todos os campos."""
        especie = Especie(
            id=0,
            nome="Cachorro Teste",
            descricao="Melhor amigo do homem"
        )
        id_inserido = especie_repo.inserir(especie)

        assert id_inserido > 0
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is not None
        assert especie_bd.nome == "Cachorro Teste"
        assert especie_bd.descricao == "Melhor amigo do homem"

    def test_inserir_especie_sem_descricao(self):
        """Deve inserir especie sem descricao (campo opcional)."""
        especie = Especie(
            id=0,
            nome="Gato Teste",
            descricao=None
        )
        id_inserido = especie_repo.inserir(especie)

        assert id_inserido > 0
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is not None
        assert especie_bd.nome == "Gato Teste"
        assert especie_bd.descricao is None

    def test_inserir_gera_id_sequencial(self):
        """IDs devem ser gerados sequencialmente."""
        especie1 = Especie(id=0, nome="Cachorro Seq", descricao=None)
        especie2 = Especie(id=0, nome="Gato Seq", descricao=None)

        id1 = especie_repo.inserir(especie1)
        id2 = especie_repo.inserir(especie2)

        assert id2 > id1


class TestEspecieRepoObterPorId:
    """Testes para busca de especie por ID."""

    def test_obter_especie_existente(self):
        """Deve retornar especie existente."""
        especie = Especie(id=0, nome="Passaro Teste", descricao="Animal voador")
        id_inserido = especie_repo.inserir(especie)

        especie_bd = especie_repo.obter_por_id(id_inserido)

        assert especie_bd is not None
        assert especie_bd.id == id_inserido
        assert especie_bd.nome == "Passaro Teste"
        assert especie_bd.descricao == "Animal voador"

    def test_obter_especie_inexistente(self):
        """Deve retornar None para ID inexistente."""
        especie_bd = especie_repo.obter_por_id(99999)
        assert especie_bd is None

    def test_obter_especie_sem_descricao(self):
        """Deve retornar especie com descricao None."""
        especie = Especie(id=0, nome="Reptil Teste", descricao=None)
        id_inserido = especie_repo.inserir(especie)

        especie_bd = especie_repo.obter_por_id(id_inserido)

        assert especie_bd is not None
        assert especie_bd.descricao is None


class TestEspecieRepoObterPorNome:
    """Testes para busca de especie por nome."""

    def test_obter_especie_por_nome_existente(self):
        """Deve retornar especie pelo nome."""
        especie = Especie(id=0, nome="Hamster Teste", descricao="Roedor pequeno")
        especie_repo.inserir(especie)

        especie_bd = especie_repo.obter_por_nome("Hamster Teste")

        assert especie_bd is not None
        assert especie_bd.nome == "Hamster Teste"
        assert especie_bd.descricao == "Roedor pequeno"

    def test_obter_especie_por_nome_inexistente(self):
        """Deve retornar None para nome inexistente."""
        especie_bd = especie_repo.obter_por_nome("Dinossauro")
        assert especie_bd is None

    def test_obter_especie_nome_case_sensitive(self):
        """Busca por nome deve ser case sensitive."""
        especie = Especie(id=0, nome="CachorroCase", descricao=None)
        especie_repo.inserir(especie)

        especie_upper = especie_repo.obter_por_nome("CACHORROCASE")
        assert especie_upper is None


class TestEspecieRepoObterTodos:
    """Testes para listagem de todas as especies."""

    def test_obter_todos_lista_especies(self):
        """Deve retornar todas as especies cadastradas."""
        especie1 = Especie(id=0, nome="Cachorro Lista", descricao="Canis lupus")
        especie2 = Especie(id=0, nome="Gato Lista", descricao="Felis catus")
        especie3 = Especie(id=0, nome="Passaro Lista", descricao=None)

        especie_repo.inserir(especie1)
        especie_repo.inserir(especie2)
        especie_repo.inserir(especie3)

        especies = especie_repo.obter_todos()

        assert len(especies) >= 3
        nomes = [e.nome for e in especies]
        assert "Cachorro Lista" in nomes
        assert "Gato Lista" in nomes
        assert "Passaro Lista" in nomes

    def test_obter_todos_com_campos_opcionais_none(self):
        """Deve retornar especies com campos opcionais None."""
        especie = Especie(id=0, nome="Cobra Teste", descricao=None)
        especie_repo.inserir(especie)

        especies = especie_repo.obter_todos()

        especie_encontrada = next(
            (e for e in especies if e.nome == "Cobra Teste"), None
        )
        assert especie_encontrada is not None
        assert especie_encontrada.descricao is None


class TestEspecieRepoAtualizar:
    """Testes para atualizacao de especies."""

    def test_atualizar_especie_existente(self):
        """Deve atualizar especie existente."""
        especie = Especie(id=0, nome="CachorroUpdate", descricao="Descricao antiga")
        id_inserido = especie_repo.inserir(especie)

        especie_atualizada = Especie(
            id=id_inserido,
            nome="Cachorro Domestico Update",
            descricao="Descricao nova"
        )
        resultado = especie_repo.atualizar(especie_atualizada)

        assert resultado is True
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd.nome == "Cachorro Domestico Update"
        assert especie_bd.descricao == "Descricao nova"

    def test_atualizar_especie_inexistente(self):
        """Deve retornar False ao atualizar especie inexistente."""
        especie = Especie(
            id=99999,
            nome="Inexistente",
            descricao="Teste"
        )
        resultado = especie_repo.atualizar(especie)
        assert resultado is False

    def test_atualizar_para_descricao_none(self):
        """Deve permitir atualizar descricao para None."""
        especie = Especie(id=0, nome="Peixe Update", descricao="Com descricao")
        id_inserido = especie_repo.inserir(especie)

        especie_atualizada = Especie(
            id=id_inserido,
            nome="Peixe Ornamental Update",
            descricao=None
        )
        resultado = especie_repo.atualizar(especie_atualizada)

        assert resultado is True
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd.descricao is None


class TestEspecieRepoExcluir:
    """Testes para exclusao de especies."""

    def test_excluir_especie_sem_racas(self):
        """Deve excluir especie que nao tem racas vinculadas."""
        especie = Especie(id=0, nome="Tartaruga Excluir", descricao=None)
        id_inserido = especie_repo.inserir(especie)

        resultado = especie_repo.excluir(id_inserido)

        assert resultado is True
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is None

    def test_excluir_especie_inexistente(self):
        """Deve retornar False ao excluir especie inexistente."""
        resultado = especie_repo.excluir(99999)
        assert resultado is False

    def test_excluir_especie_com_racas_vinculadas(self):
        """Deve lancar excecao ao excluir especie com racas."""
        # Criar especie
        especie = Especie(id=0, nome="Cachorro Vinculo", descricao=None)
        id = especie_repo.inserir(especie)

        # Criar raca vinculada
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO raca (id_especie, nome) VALUES (?, ?)",
                (id, "Labrador Vinculo")
            )

        # Tentar excluir deve lancar excecao
        with pytest.raises(Exception) as exc_info:
            especie_repo.excluir(id)

        assert "Nao e possivel excluir esta especie" in str(exc_info.value)
        assert "1 raca(s) vinculada(s)" in str(exc_info.value)


class TestEspecieRepoExisteNome:
    """Testes para verificacao de existencia de nome."""

    def test_existe_nome_true(self):
        """Deve retornar True se nome existe."""
        especie = Especie(id=0, nome="Coelho Existe", descricao=None)
        especie_repo.inserir(especie)

        existe = especie_repo.existe_nome("Coelho Existe")
        assert existe is True

    def test_existe_nome_false(self):
        """Deve retornar False se nome nao existe."""
        existe = especie_repo.existe_nome("Unicornio")
        assert existe is False

    def test_existe_nome_excluindo_proprio_id(self):
        """Deve retornar False ao excluir proprio ID da verificacao."""
        especie = Especie(id=0, nome="Porco Existe", descricao=None)
        id_inserido = especie_repo.inserir(especie)

        # Verificar sem excluir ID - deve retornar True
        existe_sem_excluir = especie_repo.existe_nome("Porco Existe")
        assert existe_sem_excluir is True

        # Verificar excluindo o proprio ID - deve retornar False
        existe_excluindo = especie_repo.existe_nome("Porco Existe", id_excluir=id_inserido)
        assert existe_excluindo is False

    def test_existe_nome_excluindo_id_diferente(self):
        """Deve retornar True se nome existe em ID diferente do excluido."""
        especie1 = Especie(id=0, nome="Vaca Existe", descricao=None)
        especie2 = Especie(id=0, nome="Cavalo Existe", descricao=None)

        id1 = especie_repo.inserir(especie1)
        id2 = especie_repo.inserir(especie2)

        # Verificar "Vaca Existe" excluindo ID do Cavalo - deve retornar True
        existe = especie_repo.existe_nome("Vaca Existe", id_excluir=id2)
        assert existe is True

    def test_existe_nome_case_sensitive(self):
        """Verificacao de nome deve ser case sensitive."""
        especie = Especie(id=0, nome="Ovelha Case", descricao=None)
        especie_repo.inserir(especie)

        existe_upper = especie_repo.existe_nome("OVELHA CASE")
        assert existe_upper is False


class TestEspecieRepoIntegracaoCRUD:
    """Testes de integracao das operacoes CRUD."""

    def test_ciclo_completo_crud(self):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        especie = Especie(id=0, nome="Rato CRUD", descricao="Roedor pequeno")
        id_inserido = especie_repo.inserir(especie)
        assert id_inserido > 0

        # READ
        especie_bd = especie_repo.obter_por_id(id_inserido)
        assert especie_bd is not None
        assert especie_bd.nome == "Rato CRUD"

        # UPDATE
        especie_bd.nome = "Rato Domestico CRUD"
        especie_bd.descricao = "Pet de estimacao"
        resultado_update = especie_repo.atualizar(especie_bd)
        assert resultado_update is True

        especie_atualizada = especie_repo.obter_por_id(id_inserido)
        assert especie_atualizada.nome == "Rato Domestico CRUD"
        assert especie_atualizada.descricao == "Pet de estimacao"

        # DELETE
        resultado_delete = especie_repo.excluir(id_inserido)
        assert resultado_delete is True

        especie_excluida = especie_repo.obter_por_id(id_inserido)
        assert especie_excluida is None

    def test_multiplas_especies_independentes(self):
        """Deve gerenciar multiplas especies independentemente."""
        especies_inseridas = []

        for i in range(5):
            especie = Especie(
                id=0,
                nome=f"Especie Multi {i}",
                descricao=f"Descricao {i}"
            )
            id_inserido = especie_repo.inserir(especie)
            especies_inseridas.append(id_inserido)

        # Verificar que todas foram inseridas
        todas = especie_repo.obter_todos()
        assert len(todas) >= 5

        # Excluir uma no meio
        especie_repo.excluir(especies_inseridas[2])

        # Verificar que outras continuam
        assert especie_repo.obter_por_id(especies_inseridas[0]) is not None
        assert especie_repo.obter_por_id(especies_inseridas[1]) is not None
        assert especie_repo.obter_por_id(especies_inseridas[2]) is None
        assert especie_repo.obter_por_id(especies_inseridas[3]) is not None
        assert especie_repo.obter_por_id(especies_inseridas[4]) is not None
