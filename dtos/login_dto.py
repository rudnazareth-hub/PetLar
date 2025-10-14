from pydantic import BaseModel, Field, field_validator
import re

class LoginDTO(BaseModel):
    """DTO para validação de dados de login"""
    email: str
    senha: str

    @field_validator('email')
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError('E-mail é obrigatório')

        # Regex básico para validação de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('E-mail inválido')

        return v.strip().lower()

    @field_validator('senha')
    @classmethod
    def validar_senha(cls, v):
        """Valida que senha não está vazia"""
        if not v or not v.strip():
            raise ValueError('Senha é obrigatória')
        return v

class CadastroDTO(BaseModel):
    """DTO para validação de dados de cadastro"""
    nome: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    senha: str = Field(..., min_length=8, max_length=100)
    confirmar_senha: str = Field(..., min_length=8, max_length=100)

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        """Valida nome do usuário"""
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')

        if len(v.strip()) < 3:
            raise ValueError('Nome deve ter no mínimo 3 caracteres')

        return v.strip()

    @field_validator('email')
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError('E-mail é obrigatório')

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('E-mail inválido')

        return v.strip().lower()

    @field_validator('senha')
    @classmethod
    def validar_senha(cls, v):
        """Valida senha"""
        if not v or not v.strip():
            raise ValueError('Senha é obrigatória')

        if len(v) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')

        return v

    @field_validator('confirmar_senha')
    @classmethod
    def validar_confirmar_senha(cls, v):
        """Valida confirmação de senha"""
        if not v or not v.strip():
            raise ValueError('Confirmação de senha é obrigatória')
        return v

class RecuperacaoSenhaDTO(BaseModel):
    """DTO para validação de recuperação de senha"""
    email: str = Field(..., min_length=5, max_length=100)

    @field_validator('email')
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError('E-mail é obrigatório')

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('E-mail inválido')

        return v.strip().lower()

class RedefinirSenhaDTO(BaseModel):
    """DTO para validação de redefinição de senha"""
    token: str = Field(..., min_length=1)
    senha: str = Field(..., min_length=8, max_length=100)
    confirmar_senha: str = Field(..., min_length=8, max_length=100)

    @field_validator('token')
    @classmethod
    def validar_token(cls, v):
        """Valida token"""
        if not v or not v.strip():
            raise ValueError('Token é obrigatório')
        return v.strip()

    @field_validator('senha')
    @classmethod
    def validar_senha(cls, v):
        """Valida senha"""
        if not v or not v.strip():
            raise ValueError('Senha é obrigatória')

        if len(v) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')

        return v

    @field_validator('confirmar_senha')
    @classmethod
    def validar_confirmar_senha(cls, v):
        """Valida confirmação de senha"""
        if not v or not v.strip():
            raise ValueError('Confirmação de senha é obrigatória')
        return v
