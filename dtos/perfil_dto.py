from pydantic import BaseModel, field_validator, model_validator
import re
from pathlib import Path

class EditarPerfilDTO(BaseModel):
    """DTO para edição de dados do perfil"""
    nome: str
    email: str

    @field_validator('nome')
    @classmethod
    def validar_nome(cls, v):
        """Valida nome do usuário"""
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')

        if len(v.split()) < 2:
            raise ValueError('Nome deve ter no mínimo 2 palavras')

        if len(v.strip()) > 128:
            raise ValueError('Nome deve ter no máximo 128 caracteres')

        return v.strip()

    @field_validator('email')
    @classmethod
    def validar_email(cls, v):
        """Valida formato do e-mail"""
        if not v or not v.strip():
            raise ValueError('E-mail é obrigatório')

        if len(v.strip()) < 5:
            raise ValueError('E-mail deve ter no mínimo 5 caracteres')

        if len(v.strip()) > 128:
            raise ValueError('E-mail deve ter no máximo 128 caracteres')

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v.strip()):
            raise ValueError('E-mail inválido')

        return v.strip().lower()


class AlterarSenhaDTO(BaseModel):
    """DTO para alteração de senha"""
    senha_atual: str
    senha_nova: str
    confirmar_senha: str

    @field_validator('senha_atual')
    @classmethod
    def validar_senha_atual(cls, v):
        """Valida senha atual"""
        if not v or not v.strip():
            raise ValueError('Senha atual é obrigatória')
        return v

    @field_validator('senha_nova')
    @classmethod
    def validar_senha_nova(cls, v):
        """Valida força da senha nova"""
        if not v or not v.strip():
            raise ValueError('Nova senha é obrigatória')

        if len(v.strip()) < 8:
            raise ValueError('Nova senha deve ter no mínimo 8 caracteres')

        if len(v.strip()) > 128:
            raise ValueError('Nova senha deve ter no máximo 128 caracteres')

        if not re.search(r"[A-Z]", v):
            raise ValueError("Nova senha deve conter pelo menos uma letra maiúscula")

        if not re.search(r"[a-z]", v):
            raise ValueError("Nova senha deve conter pelo menos uma letra minúscula")

        if not re.search(r"\d", v):
            raise ValueError("Nova senha deve conter pelo menos um número")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Nova senha deve conter pelo menos um caractere especial")

        return v.strip()

    @field_validator('confirmar_senha')
    @classmethod
    def validar_confirmar_senha(cls, v):
        """Valida confirmação de senha"""
        if not v or not v.strip():
            raise ValueError('Confirmação de senha é obrigatória')

        if len(v.strip()) < 8:
            raise ValueError('Confirmação de senha deve ter no mínimo 8 caracteres')

        if len(v.strip()) > 128:
            raise ValueError('Confirmação de senha deve ter no máximo 128 caracteres')

        return v.strip()

    @model_validator(mode='after')
    def validar_senhas_coincidem(self):
        """Valida se senha nova e confirmação são iguais"""
        if self.senha_nova != self.confirmar_senha:
            raise ValueError('As senhas não coincidem')
        return self


class AtualizarFotoDTO(BaseModel):
    """DTO para validação de upload de foto"""
    filename: str
    size: int

    # Constantes para validação
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

    @field_validator('filename')
    @classmethod
    def validar_filename(cls, v):
        """Valida nome e extensão do arquivo"""
        if not v or not v.strip():
            raise ValueError('Nenhum arquivo selecionado')

        # Verificar extensão
        file_ext = Path(v).suffix.lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Formato não permitido. Use: {', '.join(cls.ALLOWED_EXTENSIONS)}")

        return v.strip()

    @field_validator('size')
    @classmethod
    def validar_size(cls, v):
        """Valida tamanho do arquivo"""
        if v <= 0:
            raise ValueError('Arquivo vazio')

        if v > cls.MAX_FILE_SIZE:
            max_mb = cls.MAX_FILE_SIZE // (1024 * 1024)
            raise ValueError(f'Arquivo muito grande. Tamanho máximo: {max_mb}MB')

        return v
