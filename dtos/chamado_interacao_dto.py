"""
DTOs (Data Transfer Objects) para validação de interações de chamados.

Define os modelos Pydantic para validação de entrada de dados
relacionados a interações (mensagens) em chamados.
"""

from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria


class CriarInteracaoDTO(BaseModel):
    """
    DTO para criação de uma nova interação (mensagem) em um chamado.

    Usado tanto por usuários quanto por administradores ao responder.
    """

    mensagem: str

    _validar_mensagem = field_validator("mensagem")(
        validar_string_obrigatoria(
            nome_campo="Mensagem",
            tamanho_minimo=10,
            tamanho_maximo=2000
        )
    )
