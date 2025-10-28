from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_comprimento,
    validar_id_positivo,
)


class CriarCategoriaDTO(BaseModel):
    """DTO para criar uma nova categoria."""

    nome: str
    descricao: str = ""

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )


class AlterarCategoriaDTO(BaseModel):
    """DTO para alterar uma categoria existente."""

    id: int
    nome: str
    descricao: str = ""

    _validar_id = field_validator("id")(validar_id_positivo("ID"))
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=3, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )
