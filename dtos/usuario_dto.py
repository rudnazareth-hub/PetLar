from pydantic import BaseModel, field_validator
from util.perfis import Perfil
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_id_positivo,
    validar_perfil_usuario,
    validar_cpf,
    validar_telefone_br,
    validar_data,
    validar_data_passada
)


class UsuarioCadastroDTO(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: str
    data_nascimento: Optional[str] = None
    numero_documento: Optional[str] = None
    telefone: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=3, tamanho_maximo=100)
    )
    _validar_email = field_validator('email')(validar_email())
    _validar_senha = field_validator('senha')(validar_senha_forte())
    _validar_perfil = field_validator('perfil')(lambda v: Perfil.validar(v))

    # Novos validadores
    _validar_data_nascimento = field_validator('data_nascimento')(
        validar_data_passada(campo='Data de Nascimento', obrigatorio=False)
    )
    _validar_cpf = field_validator('numero_documento')(
        validar_cpf(obrigatorio=False)
    )
    _validar_telefone = field_validator('telefone')(
        validar_telefone_br(obrigatorio=False)
    )

class AlterarUsuarioDTO(BaseModel):
    """DTO para alteração de usuário"""

    id: int
    nome: str
    email: str
    perfil: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_perfil = field_validator("perfil")(validar_perfil_usuario(Perfil))
