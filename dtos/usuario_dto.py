from pydantic import BaseModel, field_validator
import re
from util.perfis import Perfil


class CriarUsuarioDTO(BaseModel):
    """DTO para criação de usuário"""

    nome: str
    email: str
    senha: str
    perfil: str

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v):
        """Valida nome do usuário"""
        if not v or not v.strip():
            raise ValueError("Nome é obrigatório")

        if len(v.strip()) < 3:
            raise ValueError("Nome deve ter no mínimo 3 caracteres")

        if len(v.strip()) > 128:
            raise ValueError("Nome deve ter no máximo 128 caracteres")

        return v.strip()

    @field_validator("email")
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError("E-mail é obrigatório")

        if len(v.strip()) < 5:
            raise ValueError("E-mail deve ter no mínimo 5 caracteres")

        if len(v.strip()) > 128:
            raise ValueError("E-mail deve ter no máximo 128 caracteres")

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, v.strip()):
            raise ValueError("E-mail inválido")

        return v.strip().lower()

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v):
        """Valida força da senha"""
        if not v or not v.strip():
            raise ValueError("Senha é obrigatória")

        if len(v.strip()) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")

        if len(v.strip()) > 128:
            raise ValueError("Senha deve ter no máximo 128 caracteres")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")

        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")

        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Senha deve conter pelo menos um caractere especial")

        return v.strip()

    @field_validator("perfil")
    @classmethod
    def validar_perfil(cls, v):
        """
        Valida perfil do usuário usando o Enum Perfil.

        Fonte única da verdade: util.perfis.Perfil
        """
        if not Perfil.existe(v):
            perfis_validos = ", ".join([f"'{p}'" for p in Perfil.valores()])
            raise ValueError(
                f'Perfil inválido: "{v}". ' f"Valores válidos: {perfis_validos}"
            )
        return v


class AlterarUsuarioDTO(BaseModel):
    """DTO para alteração de usuário"""

    id: int
    nome: str
    email: str
    perfil: str

    @field_validator("id")
    @classmethod
    def validar_id(cls, v):
        """Valida ID do usuário"""
        if not isinstance(v, int) or v <= 0:
            raise ValueError("ID deve ser um número positivo")
        return v

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v):
        """Valida nome do usuário"""
        if not v or not v.strip():
            raise ValueError("Nome é obrigatório")

        if len(v.split()) < 2:
            raise ValueError("Nome deve ter no mínimo 2 palavras")

        if len(v.strip()) > 128:
            raise ValueError("Nome deve ter no máximo 128 caracteres")

        return v.strip()

    @field_validator("email")
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError("E-mail é obrigatório")

        if len(v.strip()) < 5:
            raise ValueError("E-mail deve ter no mínimo 5 caracteres")

        if len(v.strip()) > 128:
            raise ValueError("E-mail deve ter no máximo 128 caracteres")

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, v.strip()):
            raise ValueError("E-mail inválido")

        return v.strip().lower()

    @field_validator("perfil")
    @classmethod
    def validar_perfil(cls, v):
        """
        Valida perfil do usuário usando o Enum Perfil.

        Fonte única da verdade: util.perfis.Perfil
        """
        if not Perfil.existe(v):
            perfis_validos = ", ".join([f"'{p}'" for p in Perfil.valores()])
            raise ValueError(
                f'Perfil inválido: "{v}". ' f"Valores válidos: {perfis_validos}"
            )
        return v
