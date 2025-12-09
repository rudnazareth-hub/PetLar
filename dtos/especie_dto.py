from pydantic import BaseModel, field_validator

from dtos.validators import (
    validar_comprimento,
    validar_id_positivo,
    validar_string_obrigatoria,
)


class CriarEspecieDTO(BaseModel):
    """DTO para criar uma nova espécie."""

    nome: str
    descricao: str = ""

    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )


class AlterarEspecieDTO(BaseModel):
    """DTO para alterar uma espécie existente."""

    id: int
    nome: str
    descricao: str = ""

    _validar_id = field_validator("id")(validar_id_positivo("ID"))
    _validar_nome = field_validator("nome")(
        validar_string_obrigatoria("Nome", tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator("descricao")(
        validar_comprimento(tamanho_maximo=200)
    )
