from pydantic import BaseModel, field_validator, model_validator
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
    nome: str
    email: str
    senha: str
    confirmar_senha: str

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        """Valida nome do usuário"""
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')

        if len(v.strip()) < 3:
            raise ValueError('Nome deve ter no mínimo 3 caracteres')

        if len(v.strip()) > 100:
            raise ValueError('Nome deve ter no máximo 100 caracteres')

        return v.strip()

    @field_validator('email')
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError('E-mail é obrigatório')

        if len(v.strip()) < 5:
            raise ValueError('E-mail deve ter no mínimo 5 caracteres')

        if len(v.strip()) > 100:
            raise ValueError('E-mail deve ter no máximo 100 caracteres')

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('E-mail inválido')

        return v.strip().lower()

    @field_validator('senha')
    @classmethod
    def validar_senha(cls, v):
        """Valida força da senha"""
        if not v or not v.strip():
            raise ValueError('Senha é obrigatória')

        if len(v) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')

        if len(v) > 100:
            raise ValueError('Senha deve ter no máximo 100 caracteres')

        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")

        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")

        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")

        return v

    @field_validator('confirmar_senha')
    @classmethod
    def validar_confirmar_senha(cls, v):
        """Valida confirmação de senha"""
        if not v or not v.strip():
            raise ValueError('Confirmação de senha é obrigatória')

        if len(v) < 8:
            raise ValueError('Confirmação de senha deve ter no mínimo 8 caracteres')

        if len(v) > 100:
            raise ValueError('Confirmação de senha deve ter no máximo 100 caracteres')

        return v

    @model_validator(mode='after')
    def validar_senhas_coincidem(self):
        """Valida se senha e confirmação são iguais"""
        if self.senha != self.confirmar_senha:
            raise ValueError('As senhas não coincidem')
        return self

class RecuperacaoSenhaDTO(BaseModel):
    """DTO para validação de recuperação de senha"""
    email: str

    @field_validator('email')
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError('E-mail é obrigatório')

        if len(v.strip()) < 5:
            raise ValueError('E-mail deve ter no mínimo 5 caracteres')

        if len(v.strip()) > 100:
            raise ValueError('E-mail deve ter no máximo 100 caracteres')

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('E-mail inválido')

        return v.strip().lower()

class RedefinirSenhaDTO(BaseModel):
    """DTO para validação de redefinição de senha"""
    token: str
    senha: str
    confirmar_senha: str

    @field_validator('token')
    @classmethod
    def validar_token(cls, v):
        """Valida token"""
        if not v or not v.strip():
            raise ValueError('Token é obrigatório')

        if len(v.strip()) < 1:
            raise ValueError('Token inválido')

        return v.strip()

    @field_validator('senha')
    @classmethod
    def validar_senha(cls, v):
        """Valida força da senha"""
        if not v or not v.strip():
            raise ValueError('Senha é obrigatória')

        if len(v) < 8:
            raise ValueError('Senha deve ter no mínimo 8 caracteres')

        if len(v) > 100:
            raise ValueError('Senha deve ter no máximo 100 caracteres')

        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")

        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")

        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")

        return v

    @field_validator('confirmar_senha')
    @classmethod
    def validar_confirmar_senha(cls, v):
        """Valida confirmação de senha"""
        if not v or not v.strip():
            raise ValueError('Confirmação de senha é obrigatória')

        if len(v) < 8:
            raise ValueError('Confirmação de senha deve ter no mínimo 8 caracteres')

        if len(v) > 100:
            raise ValueError('Confirmação de senha deve ter no máximo 100 caracteres')

        return v

    @model_validator(mode='after')
    def validar_senhas_coincidem(self):
        """Valida se senha e confirmação são iguais"""
        if self.senha != self.confirmar_senha:
            raise ValueError('As senhas não coincidem')
        return self
