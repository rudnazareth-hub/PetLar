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

class CadastrarEspecieDTO(BaseModel):
    """DTO para cadastro de espécie"""
    nome: str
    descricao: Optional[str] = None

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=50)
    )
    _validar_descricao = field_validator('descricao')(
        validar_comprimento(tamanho_maximo=200)
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
<<<<<<< HEAD
        validar_texto_longo_opcional(tamanho_maximo=200)
    )

=======
        validar_comprimento(tamanho_maximo=200)
    )
>>>>>>> 94b51611858862b1b07628a54fe3ccd46f45137a
