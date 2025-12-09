from pydantic import BaseModel, field_validator
from typing import Optional

from dtos.validators import (
    validar_cep,
    validar_comprimento,
    validar_id_positivo,
    validar_string_obrigatoria,
)


UFS_VALIDAS = {
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
}


def validar_uf():
    """Valida UF brasileira (2 letras maiusculas)."""
    def validator(cls, v):
        if not v or not v.strip():
            raise ValueError("UF é obrigatória.")

        valor = v.strip().upper()

        if len(valor) != 2:
            raise ValueError("UF deve ter exatamente 2 caracteres.")

        if valor not in UFS_VALIDAS:
            raise ValueError(f"UF inválida: {valor}")

        return valor
    return validator


def validar_numero():
    """Valida numero do endereco (inteiro positivo ou S/N)."""
    def validator(cls, v):
        if v is None:
            return None

        # Se for string, pode ser "S/N" ou um numero
        if isinstance(v, str):
            valor = v.strip().upper()
            if valor in ('S/N', 'SN', ''):
                return 0  # S/N como 0
            try:
                return int(valor)
            except ValueError:
                raise ValueError("Número deve ser um valor inteiro ou 'S/N'.")

        if isinstance(v, int):
            if v < 0:
                raise ValueError("Número não pode ser negativo.")
            return v

        raise ValueError("Número inválido.")
    return validator


class CriarEnderecoDTO(BaseModel):
    """DTO para criar um novo endereco."""

    titulo: str
    logradouro: str
    numero: Optional[int] = None
    complemento: str = ""
    bairro: str
    cidade: str
    uf: str
    cep: str

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria("Título", tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_logradouro = field_validator("logradouro")(
        validar_string_obrigatoria("Logradouro", tamanho_minimo=3, tamanho_maximo=200)
    )
    _validar_numero = field_validator("numero", mode="before")(validar_numero())
    _validar_complemento = field_validator("complemento")(
        validar_comprimento(tamanho_maximo=100)
    )
    _validar_bairro = field_validator("bairro")(
        validar_string_obrigatoria("Bairro", tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_cidade = field_validator("cidade")(
        validar_string_obrigatoria("Cidade", tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_uf = field_validator("uf")(validar_uf())
    _validar_cep = field_validator("cep")(validar_cep(formatar=True))


class AlterarEnderecoDTO(BaseModel):
    """DTO para alterar um endereco existente."""

    id: int
    titulo: str
    logradouro: str
    numero: Optional[int] = None
    complemento: str = ""
    bairro: str
    cidade: str
    uf: str
    cep: str

    _validar_id = field_validator("id")(validar_id_positivo("ID"))
    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria("Título", tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_logradouro = field_validator("logradouro")(
        validar_string_obrigatoria("Logradouro", tamanho_minimo=3, tamanho_maximo=200)
    )
    _validar_numero = field_validator("numero", mode="before")(validar_numero())
    _validar_complemento = field_validator("complemento")(
        validar_comprimento(tamanho_maximo=100)
    )
    _validar_bairro = field_validator("bairro")(
        validar_string_obrigatoria("Bairro", tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_cidade = field_validator("cidade")(
        validar_string_obrigatoria("Cidade", tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_uf = field_validator("uf")(validar_uf())
    _validar_cep = field_validator("cep")(validar_cep(formatar=True))
