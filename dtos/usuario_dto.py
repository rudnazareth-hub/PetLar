from pydantic import BaseModel, Field, field_validator, EmailStr
from util.perfis import Perfil

class CriarUsuarioDTO(BaseModel):
    """DTO para criação de usuário"""
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(...)
    senha: str = Field(..., min_length=8)
    perfil: str = Field(...)

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()

    @field_validator('perfil')
    @classmethod
    def validar_perfil(cls, v):
        if not Perfil.existe(v):
            raise ValueError(f'Perfil inválido. Use: {", ".join(Perfil.valores())}')
        return v

class AlterarUsuarioDTO(BaseModel):
    """DTO para alteração de usuário"""
    id: int = Field(..., gt=0)
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(...)
    perfil: str = Field(...)

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()

    @field_validator('perfil')
    @classmethod
    def validar_perfil(cls, v):
        if not Perfil.existe(v):
            raise ValueError(f'Perfil inválido. Use: {", ".join(Perfil.valores())}')
        return v
