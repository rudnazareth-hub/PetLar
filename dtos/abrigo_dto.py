"""
DTOs para validação de dados da entidade Especie.
"""

from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria


class EspecieCriarDTO(BaseModel):
    """DTO para criação de espécie."""
    nome: str
    descricao: str

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )


class EspecieAlterarDTO(BaseModel):
    """DTO para alteração de espécie."""
    nome: str
    descricao: str

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )

    