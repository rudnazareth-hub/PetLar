"""
DTOs para validação de dados da entidade Especie.
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_string_obrigatoria,
    validar_comprimento,
    validar_id_positivo
)

class CriarEspecieDTO(BaseModel):
    """DTO para criação de espécie"""
    nome: str
    descricao: str = ""

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_comprimento(tamanho_maximo=200)
    )

# Mantém compatibilidade com código existente
CadastrarEspecieDTO = CriarEspecieDTO

class AlterarEspecieDTO(BaseModel):
    """DTO para alteração de espécie"""
    id: int
    nome: str
    descricao: str = ""

    _validar_id = field_validator('id')(validar_id_positivo())
    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_comprimento(tamanho_maximo=200)
    )