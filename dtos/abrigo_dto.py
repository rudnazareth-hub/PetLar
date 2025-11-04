"""
DTOs para validação de dados da entidade Abrigo.
"""

from typing import Optional
from pydantic import BaseModel, field_validator
from dtos.validators import validar_comprimento, validar_string_obrigatoria


class CadastrarAbrigoDTO(BaseModel):
    """DTO para cadastro de abrigo"""
    nome: str
    descricao: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_comprimento(tamanho_maximo=200)
    )
class AlterarAbrigoDTO(BaseModel):
    """DTO para alteração de abrigo"""
    nome: str
    descricao: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_comprimento(tamanho_maximo=200)
    )