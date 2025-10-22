"""
DTOs para autenticação e gerenciamento de acesso.

Contém validações para login, cadastro, recuperação e redefinição de senha.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from dtos.validators import (
    validar_email,
    validar_perfil_usuario,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_string_obrigatoria,
    validar_senhas_coincidem,
)
from util.perfis import Perfil


class LoginDTO(BaseModel):
    """DTO para validação de dados de login."""

    email: str = Field(..., description="E-mail do usuário", examples=["usuario@exemplo.com"])
    senha: str = Field(..., description="Senha do usuário", min_length=8, max_length=128)

    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())


class CadastroDTO(BaseModel):
    """DTO para validação de dados de cadastro de novo usuário."""

    perfil: str = Field(..., description="Perfil/Role do usuário", examples=["Cliente", "Vendedor"])
    nome: str = Field(..., description="Nome completo do usuário", min_length=4, max_length=128)
    email: str = Field(..., description="E-mail do usuário", examples=["usuario@exemplo.com"])
    senha: str = Field(..., description="Senha do usuário", min_length=8, max_length=128)
    confirmar_senha: str = Field(..., description="Confirmação da senha", min_length=8, max_length=128)

    _validar_perfil = field_validator("perfil")(validar_perfil_usuario(Perfil))
    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(
        validar_string_obrigatoria(
            "Confirmação de Senha", tamanho_minimo=8, tamanho_maximo=128
        )
    )

    _validar_senhas_match = model_validator(mode="after")(validar_senhas_coincidem())


class EsqueciSenhaDTO(BaseModel):
    """DTO para validação de solicitação de recuperação de senha."""

    email: str = Field(..., description="E-mail cadastrado do usuário", examples=["usuario@exemplo.com"])

    _validar_email = field_validator("email")(validar_email())


class RedefinirSenhaDTO(BaseModel):
    """DTO para validação de redefinição de senha via token."""

    token: str = Field(..., description="Token de redefinição recebido por e-mail", min_length=1)
    senha: str = Field(..., description="Nova senha do usuário", min_length=8, max_length=128)
    confirmar_senha: str = Field(..., description="Confirmação da nova senha", min_length=8, max_length=128)

    _validar_token = field_validator("token")(
        validar_string_obrigatoria("Token", tamanho_minimo=1)
    )
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(
        validar_string_obrigatoria()
    )

    _validar_senhas_match = model_validator(mode="after")(validar_senhas_coincidem())
