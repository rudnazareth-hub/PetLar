"""
Configuracao especifica para testes de repositorios.

Fornece fixtures reutilizaveis para testes de repos.
A criacao de tabelas e feita pela fixture criar_tabelas_integracao
no conftest.py do nivel de integracao.
"""
import pytest

from repo import (
    usuario_repo, chamado_repo, chamado_interacao_repo,
    abrigo_repo, adotante_repo, endereco_repo, visita_repo
)
from model.usuario_model import Usuario
from model.abrigo_model import Abrigo
from model.adotante_model import Adotante
from model.chamado_model import Chamado, StatusChamado, PrioridadeChamado
from model.chamado_interacao_model import ChamadoInteracao, TipoInteracao
from util.security import criar_hash_senha
from util.perfis import Perfil


# ============================================================================
# FIXTURES REUTILIZAVEIS PARA TESTES DE REPOS
# ============================================================================


@pytest.fixture(scope="function")
def usuario_repo_teste():
    """
    Cria um usuario para associar a entidades que requerem FK de usuario.

    Returns:
        int: ID do usuario criado
    """
    usuario = Usuario(
        id=0,
        nome="Usuario Repo Teste",
        email="usuario_repo@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.ADOTANTE.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture(scope="function")
def admin_repo_teste():
    """
    Cria um usuario admin para testes que requerem perfil administrativo.

    Returns:
        int: ID do admin criado
    """
    usuario = Usuario(
        id=0,
        nome="Admin Repo Teste",
        email="admin_repo@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.ADMIN.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture(scope="function")
def chamado_repo_teste(usuario_repo_teste):
    """
    Cria um chamado de teste associado a um usuario.

    Args:
        usuario_repo_teste: Fixture que fornece ID do usuario

    Returns:
        int: ID do chamado criado
    """
    chamado = Chamado(
        id=0,
        titulo="Chamado Repo Teste",
        status=StatusChamado.ABERTO,
        prioridade=PrioridadeChamado.MEDIA,
        usuario_id=usuario_repo_teste
    )
    chamado_id = chamado_repo.inserir(chamado)
    return chamado_id


@pytest.fixture(scope="function")
def interacao_repo_teste(chamado_repo_teste, usuario_repo_teste):
    """
    Cria uma interacao de teste para um chamado.

    Args:
        chamado_repo_teste: Fixture que fornece ID do chamado
        usuario_repo_teste: Fixture que fornece ID do usuario

    Returns:
        int: ID da interacao criada
    """
    interacao = ChamadoInteracao(
        id=0,
        chamado_id=chamado_repo_teste,
        usuario_id=usuario_repo_teste,
        mensagem="Mensagem de teste",
        tipo=TipoInteracao.ABERTURA,
        data_interacao=None,
        status_resultante=StatusChamado.ABERTO.value
    )
    interacao_id = chamado_interacao_repo.inserir(interacao)
    return interacao_id


# ============================================================================
# FIXTURES PARA TESTES DE ABRIGO
# ============================================================================


@pytest.fixture(scope="function")
def usuario_abrigo_teste():
    """
    Cria um usuario com perfil ABRIGO para testes.

    Returns:
        int: ID do usuario criado
    """
    usuario = Usuario(
        id=0,
        nome="Abrigo Teste",
        email="abrigo_teste@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.ABRIGO.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture(scope="function")
def usuario_abrigo2_teste():
    """
    Cria um segundo usuario com perfil ABRIGO para testes.

    Returns:
        int: ID do usuario criado
    """
    usuario = Usuario(
        id=0,
        nome="Abrigo Teste 2",
        email="abrigo_teste2@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.ABRIGO.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture(scope="function")
def abrigo_teste(usuario_abrigo_teste):
    """
    Cria um abrigo de teste associado a um usuario.

    Args:
        usuario_abrigo_teste: Fixture que fornece ID do usuario

    Returns:
        int: ID do abrigo criado
    """
    abrigo = Abrigo(
        id_abrigo=usuario_abrigo_teste,
        responsavel="Responsavel Teste",
        descricao="Abrigo de teste",
        data_abertura="2020-01-01",
        data_membros="Equipe teste"
    )
    abrigo_repo.inserir(abrigo)
    return usuario_abrigo_teste


# ============================================================================
# FIXTURES PARA TESTES DE ADOTANTE
# ============================================================================


@pytest.fixture(scope="function")
def usuario_adotante_teste():
    """
    Cria um usuario com perfil ADOTANTE para testes.

    Returns:
        int: ID do usuario criado
    """
    usuario = Usuario(
        id=0,
        nome="Adotante Teste",
        email="adotante_teste@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.ADOTANTE.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture(scope="function")
def usuario_adotante2_teste():
    """
    Cria um segundo usuario com perfil ADOTANTE para testes.

    Returns:
        int: ID do usuario criado
    """
    usuario = Usuario(
        id=0,
        nome="Adotante Teste 2",
        email="adotante_teste2@example.com",
        senha=criar_hash_senha("Senha@123"),
        perfil=Perfil.ADOTANTE.value
    )
    usuario_id = usuario_repo.inserir(usuario)
    return usuario_id


@pytest.fixture(scope="function")
def adotante_teste(usuario_adotante_teste):
    """
    Cria um adotante de teste associado a um usuario.

    Args:
        usuario_adotante_teste: Fixture que fornece ID do usuario

    Returns:
        int: ID do adotante criado
    """
    adotante = Adotante(
        id_adotante=usuario_adotante_teste,
        renda_media=5000.00,
        tem_filhos=False,
        estado_saude="Excelente"
    )
    adotante_repo.inserir(adotante)
    return usuario_adotante_teste


# ============================================================================
# FIXTURES PARA TESTES DE VISITA
# ============================================================================


@pytest.fixture(scope="function")
def setup_visita_teste(usuario_adotante_teste, usuario_abrigo_teste):
    """
    Cria estrutura completa para testes de visita.

    Args:
        usuario_adotante_teste: Fixture que fornece ID do adotante
        usuario_abrigo_teste: Fixture que fornece ID do abrigo

    Returns:
        dict: IDs do adotante e abrigo
    """
    # Criar adotante
    adotante = Adotante(
        id_adotante=usuario_adotante_teste,
        renda_media=3000.00,
        tem_filhos=False,
        estado_saude="Boa"
    )
    adotante_repo.inserir(adotante)

    # Criar abrigo
    abrigo = Abrigo(
        id_abrigo=usuario_abrigo_teste,
        responsavel="Resp Visitas",
        descricao=None,
        data_abertura=None,
        data_membros=None
    )
    abrigo_repo.inserir(abrigo)

    return {
        "id_adotante": usuario_adotante_teste,
        "id_abrigo": usuario_abrigo_teste
    }
