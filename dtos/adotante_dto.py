from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_id_positivo,
    validar_valor_monetario,
    validar_string_obrigatoria
)

class AlterarAdotanteDTO(BaseModel):
    """DTO para alteração de dados do adotante pelo admin"""
    id_adotante: int
    renda_media: float
    tem_filhos: bool
    estado_saude: str

    _validar_id = field_validator('id_adotante')(validar_id_positivo())
    _validar_renda = field_validator('renda_media')(validar_valor_monetario(minimo=0.0))
    _validar_estado_saude = field_validator('estado_saude')(
        validar_string_obrigatoria('Estado de Saúde', tamanho_minimo=3, tamanho_maximo=100)
    )