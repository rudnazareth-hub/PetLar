from typing import Set
from pydantic import BaseModel, field_validator, model_validator
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_string_obrigatoria,
    validar_extensao_arquivo,
    validar_tamanho_arquivo,
)


class EditarPerfilDTO(BaseModel):
    """DTO para edição de dados do perfil"""

    nome: str
    email: str

    _validar_nome = field_validator("nome")(validar_nome_pessoa(min_palavras=2))
    _validar_email = field_validator("email")(validar_email())


class AlterarSenhaDTO(BaseModel):
    """DTO para alteração de senha"""

    senha_atual: str
    senha_nova: str
    confirmar_senha: str

    _validar_senha_atual = field_validator("senha_atual")(
        validar_string_obrigatoria("Senha atual")
    )
    _validar_senha_nova = field_validator("senha_nova")(validar_senha_forte())
    _validar_confirmar = field_validator("confirmar_senha")(
        validar_string_obrigatoria(
            "Confirmação de senha", tamanho_minimo=8, tamanho_maximo=128
        )
    )

    @model_validator(mode="after")
    def validar_senhas_coincidem(self) -> "AlterarSenhaDTO":
        """Valida se senha nova e confirmação são iguais"""
        if self.senha_nova != self.confirmar_senha:
            raise ValueError("As senhas não coincidem")
        return self


class AtualizarFotoDTO(BaseModel):
    """DTO para validação de upload de foto"""

    filename: str
    size: int

    # Constantes para validação
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    _validar_filename = field_validator("filename")(
        validar_extensao_arquivo({".jpg", ".jpeg", ".png", ".gif", ".webp"}, "Foto")
    )
    _validar_size = field_validator("size")(
        validar_tamanho_arquivo(5 * 1024 * 1024, "Foto")  # 5MB
    )
