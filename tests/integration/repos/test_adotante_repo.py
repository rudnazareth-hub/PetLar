"""
Testes de integracao para o repositorio de adotantes.

Testa todas as operacoes CRUD do adotante_repo.
"""
import pytest
from model.adotante_model import Adotante
from model.usuario_model import Usuario
from repo import adotante_repo, usuario_repo
from util.db_util import obter_conexao
from util.security import criar_hash_senha
from util.perfis import Perfil


class TestAdotanteRepoCriarTabela:
    """Testes para criacao da tabela adotante."""

    def test_criar_tabela_retorna_true(self):
        """Deve retornar True ao criar tabela."""
        resultado = adotante_repo.criar_tabela()
        assert resultado is True


class TestAdotanteRepoInserir:
    """Testes para insercao de adotantes."""

    def test_inserir_adotante_completo(self, usuario_adotante_teste):
        """Deve inserir adotante com todos os campos."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=5000.00,
            tem_filhos=True,
            estado_saude="Excelente saude"
        )
        id_inserido = adotante_repo.inserir(adotante)

        assert id_inserido == usuario_adotante_teste
        adotante_bd = adotante_repo.obter_por_id(id_inserido)
        assert adotante_bd is not None
        assert adotante_bd.renda_media == 5000.00
        assert adotante_bd.tem_filhos is True
        assert adotante_bd.estado_saude == "Excelente saude"

    def test_inserir_adotante_sem_filhos(self, usuario_adotante_teste):
        """Deve inserir adotante sem filhos."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=3000.00,
            tem_filhos=False,
            estado_saude="Boa saude"
        )
        id_inserido = adotante_repo.inserir(adotante)

        assert id_inserido == usuario_adotante_teste
        adotante_bd = adotante_repo.obter_por_id(id_inserido)
        assert adotante_bd is not None
        assert adotante_bd.tem_filhos is False

    def test_inserir_usa_id_usuario(self, usuario_adotante_teste):
        """Deve usar ID do usuario como ID do adotante."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=4500.00,
            tem_filhos=True,
            estado_saude="Normal"
        )
        id_inserido = adotante_repo.inserir(adotante)

        assert id_inserido == usuario_adotante_teste

    def test_inserir_converte_boolean_para_int(self, usuario_adotante_teste):
        """Deve converter boolean tem_filhos para int no banco."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=2000.00,
            tem_filhos=True,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        # Verificar que foi armazenado como int no banco
        with obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tem_filhos FROM adotante WHERE id_adotante = ?",
                (usuario_adotante_teste,)
            )
            row = cursor.fetchone()
            assert row["tem_filhos"] in (0, 1)


class TestAdotanteRepoObterPorId:
    """Testes para busca de adotante por ID."""

    def test_obter_adotante_existente(self, usuario_adotante_teste):
        """Deve retornar adotante existente."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=6000.00,
            tem_filhos=True,
            estado_saude="Otima saude"
        )
        adotante_repo.inserir(adotante)

        adotante_bd = adotante_repo.obter_por_id(usuario_adotante_teste)

        assert adotante_bd is not None
        assert adotante_bd.id_adotante == usuario_adotante_teste
        assert adotante_bd.renda_media == 6000.00
        assert adotante_bd.tem_filhos is True
        assert adotante_bd.estado_saude == "Otima saude"

    def test_obter_adotante_inexistente(self):
        """Deve retornar None para ID inexistente."""
        adotante_bd = adotante_repo.obter_por_id(99999)
        assert adotante_bd is None

    def test_obter_converte_int_para_boolean(self, usuario_adotante_teste):
        """Deve converter int do banco para boolean."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=3500.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        adotante_bd = adotante_repo.obter_por_id(usuario_adotante_teste)

        assert isinstance(adotante_bd.tem_filhos, bool)
        assert adotante_bd.tem_filhos is False


class TestAdotanteRepoAtualizar:
    """Testes para atualizacao de adotantes."""

    def test_atualizar_adotante_existente(self, usuario_adotante_teste):
        """Deve atualizar adotante existente."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=3000.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        adotante_atualizado = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=5500.00,
            tem_filhos=True,
            estado_saude="Excelente"
        )
        resultado = adotante_repo.atualizar(adotante_atualizado)

        assert resultado is True
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante_teste)
        assert adotante_bd.renda_media == 5500.00
        assert adotante_bd.tem_filhos is True
        assert adotante_bd.estado_saude == "Excelente"

    def test_atualizar_adotante_inexistente(self):
        """Deve retornar False ao atualizar adotante inexistente."""
        adotante = Adotante(
            id_adotante=99999,
            renda_media=1000.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        resultado = adotante_repo.atualizar(adotante)
        assert resultado is False

    def test_atualizar_mudar_tem_filhos(self, usuario_adotante_teste):
        """Deve permitir alterar campo tem_filhos."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=4000.00,
            tem_filhos=False,
            estado_saude="Boa"
        )
        adotante_repo.inserir(adotante)

        adotante_atualizado = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=4000.00,
            tem_filhos=True,
            estado_saude="Boa"
        )
        resultado = adotante_repo.atualizar(adotante_atualizado)

        assert resultado is True
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante_teste)
        assert adotante_bd.tem_filhos is True


class TestAdotanteRepoExcluir:
    """Testes para exclusao de adotantes."""

    def test_excluir_adotante_existente(self, usuario_adotante_teste):
        """Deve excluir adotante existente."""
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=2500.00,
            tem_filhos=False,
            estado_saude="Normal"
        )
        adotante_repo.inserir(adotante)

        resultado = adotante_repo.excluir(usuario_adotante_teste)

        assert resultado is True
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante_teste)
        assert adotante_bd is None

    def test_excluir_adotante_inexistente(self):
        """Deve retornar False ao excluir adotante inexistente."""
        resultado = adotante_repo.excluir(99999)
        assert resultado is False


class TestAdotanteRepoIntegracaoCRUD:
    """Testes de integracao das operacoes CRUD."""

    def test_ciclo_completo_crud(self, usuario_adotante_teste):
        """Deve executar ciclo completo: criar, ler, atualizar, excluir."""
        # CREATE
        adotante = Adotante(
            id_adotante=usuario_adotante_teste,
            renda_media=4000.00,
            tem_filhos=True,
            estado_saude="Boa saude"
        )
        id_inserido = adotante_repo.inserir(adotante)
        assert id_inserido == usuario_adotante_teste

        # READ
        adotante_bd = adotante_repo.obter_por_id(usuario_adotante_teste)
        assert adotante_bd is not None
        assert adotante_bd.renda_media == 4000.00
        assert adotante_bd.tem_filhos is True

        # UPDATE
        adotante_bd.renda_media = 6000.00
        adotante_bd.tem_filhos = False
        adotante_bd.estado_saude = "Excelente saude"
        resultado_update = adotante_repo.atualizar(adotante_bd)
        assert resultado_update is True

        adotante_atualizado = adotante_repo.obter_por_id(usuario_adotante_teste)
        assert adotante_atualizado.renda_media == 6000.00
        assert adotante_atualizado.tem_filhos is False
        assert adotante_atualizado.estado_saude == "Excelente saude"

        # DELETE
        resultado_delete = adotante_repo.excluir(usuario_adotante_teste)
        assert resultado_delete is True

        adotante_excluido = adotante_repo.obter_por_id(usuario_adotante_teste)
        assert adotante_excluido is None

    def test_multiplos_adotantes_independentes(self):
        """Deve gerenciar multiplos adotantes independentemente."""
        usuarios = []

        # Criar 3 usuarios e adotantes
        for i in range(3):
            usuario = Usuario(
                id=0,
                nome=f"Adotante {i}",
                email=f"adotante_multi{i}@test.com",
                senha=criar_hash_senha("Senha@123"),
                perfil=Perfil.ADOTANTE.value
            )
            id_usuario = usuario_repo.inserir(usuario)
            usuarios.append(id_usuario)

            adotante = Adotante(
                id_adotante=id_usuario,
                renda_media=3000.00 + (i * 1000),
                tem_filhos=i % 2 == 0,
                estado_saude=f"Saude {i}"
            )
            adotante_repo.inserir(adotante)

        # Verificar que todos foram inseridos
        for id_usuario in usuarios:
            adotante_bd = adotante_repo.obter_por_id(id_usuario)
            assert adotante_bd is not None

        # Excluir um no meio
        adotante_repo.excluir(usuarios[1])

        # Verificar que outros continuam
        assert adotante_repo.obter_por_id(usuarios[0]) is not None
        assert adotante_repo.obter_por_id(usuarios[1]) is None
        assert adotante_repo.obter_por_id(usuarios[2]) is not None

    def test_diferentes_valores_renda(self, usuario_adotante_teste, usuario_adotante2_teste):
        """Deve suportar diferentes valores de renda."""
        rendas = [1200.50, 10000.00, 500.00, 15000.99]

        for renda in rendas:
            # Limpar antes de cada teste de renda
            adotante_repo.excluir(usuario_adotante_teste)

            adotante = Adotante(
                id_adotante=usuario_adotante_teste,
                renda_media=renda,
                tem_filhos=False,
                estado_saude="Normal"
            )
            adotante_repo.inserir(adotante)

            adotante_bd = adotante_repo.obter_por_id(usuario_adotante_teste)
            assert adotante_bd.renda_media == renda
