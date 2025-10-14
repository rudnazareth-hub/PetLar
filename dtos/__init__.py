"""DTOs - Data Transfer Objects para validação de dados"""

from .login_dto import LoginDTO, CadastroDTO, RecuperacaoSenhaDTO, RedefinirSenhaDTO
from .usuario_dto import CriarUsuarioDTO, AlterarUsuarioDTO
from .tarefa_dto import CriarTarefaDTO, AlterarTarefaDTO
from .perfil_dto import EditarPerfilDTO, AlterarSenhaDTO, AtualizarFotoDTO

__all__ = [
    'LoginDTO',
    'CadastroDTO',
    'RecuperacaoSenhaDTO',
    'RedefinirSenhaDTO',
    'CriarUsuarioDTO',
    'AlterarUsuarioDTO',
    'CriarTarefaDTO',
    'AlterarTarefaDTO',
    'EditarPerfilDTO',
    'AlterarSenhaDTO',
    'AtualizarFotoDTO',
]
