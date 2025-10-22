"""
DTOs para validação de dados da entidade Raca.
"""

from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_inteiro_positivo


class RacaCriarDTO(BaseModel):
    """DTO para criação de raça."""
    id_especie: int
    nome: str
    descricao: str
    temperamento: str
    expectativa_de_vida: str
    porte: str  # Pequeno, Médio, Grande

    _validar_especie = field_validator('id_especie')(validar_inteiro_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_porte = field_validator('porte')(
        lambda v: v if v in ['Pequeno', 'Médio', 'Grande']
        else (_ for _ in ()).throw(ValueError('Porte deve ser: Pequeno, Médio ou Grande'))
    )


class RacaAlterarDTO(BaseModel):
    """DTO para alteração de raça."""
    id_especie: int
    nome: str
    descricao: str
    temperamento: str
    expectativa_de_vida: str
    porte: str

    _validar_especie = field_validator('id_especie')(validar_inteiro_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_porte = field_validator('porte')(
        lambda v: v if v in ['Pequeno', 'Médio', 'Grande']
        else (_ for _ in ()).throw(ValueError('Porte deve ser: Pequeno, Médio ou Grande'))
    )