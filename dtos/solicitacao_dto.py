
from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import validar_id_positivo, validar_texto_longo_opcional

class AprovarSolicitacaoDTO(BaseModel):
    """DTO para aprovação de solicitação"""
    id_solicitacao: int
    resposta_abrigo: Optional[str] = None

    _validar_id = field_validator('id_solicitacao')(validar_id_positivo())
    _validar_resposta = field_validator('resposta_abrigo')(
        validar_texto_longo_opcional(tamanho_maximo=500)
    )

class RejeitarSolicitacaoDTO(BaseModel):
    """DTO para rejeição de solicitação"""
    id_solicitacao: int
    resposta_abrigo: str

    _validar_id = field_validator('id_solicitacao')(validar_id_positivo())
    _validar_resposta = field_validator('resposta_abrigo')(
        validar_string_obrigatoria('Motivo da rejeição', tamanho_minimo=10, tamanho_maximo=500)
    )
