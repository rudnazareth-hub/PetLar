"""
DTOs para validação de dados da entidade Especie.
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_string_obrigatoria,
    validar_texto_longo_opcional,
    validar_id_positivo
)

class CadastrarEspecieDTO(BaseModel):
    """DTO para cadastro de espécie"""
    nome: str
    descricao: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_texto_longo_opcional(tamanho_maximo=200)
    )

class AlterarEspecieDTO(BaseModel):
    """DTO para alteração de espécie"""
    id_especie: int
    nome: str
    descricao: Optional[str] = None

    _validar_id = field_validator('id_especie')(validar_id_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_texto_longo_opcional(tamanho_maximo=200)
    )

