"""
DTOs para validação de dados da entidade Raca.
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_string_obrigatoria,
    validar_comprimento,
    validar_id_positivo
)

class CriarRacaDTO(BaseModel):
    """DTO para criação de raça"""
    nome: str
    id_especie: int
    descricao: str = ""

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_id_especie = field_validator('id_especie')(validar_id_positivo())
    _validar_descricao = field_validator('descricao')(
        validar_comprimento(tamanho_maximo=200)
    )

# Mantém compatibilidade com código existente
CadastrarRacaDTO = CriarRacaDTO

class AlterarRacaDTO(BaseModel):
    """DTO para alteração de raça"""
    id: int
    nome: str
    id_especie: int
    descricao: str = ""

    _validar_id = field_validator('id')(validar_id_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_id_especie = field_validator('id_especie')(validar_id_positivo())
    _validar_descricao = field_validator('descricao')(
        validar_comprimento(tamanho_maximo=200)
    )