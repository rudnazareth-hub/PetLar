"""
DTOs (Data Transfer Objects) para validação de chamados.

Define os modelos Pydantic para validação de entrada de dados
relacionados a chamados, usando validators reutilizáveis.
"""

from pydantic import BaseModel, field_validator
from dtos.validators import (
    validar_string_obrigatoria,
    validar_comprimento,
)
from model.chamado_model import StatusChamado, PrioridadeChamado


class CriarChamadoDTO(BaseModel):
    """
    DTO para criação de um novo chamado.

    Usado quando usuários não-administradores abrem chamados.
    """

    titulo: str
    descricao: str
    prioridade: str = "Média"

    _validar_titulo = field_validator("titulo")(
        validar_string_obrigatoria(
            nome_campo="Título",
            tamanho_minimo=10,
            tamanho_maximo=200
        )
    )

    _validar_descricao = field_validator("descricao")(
        validar_string_obrigatoria(
            nome_campo="Descrição",
            tamanho_minimo=20,
            tamanho_maximo=2000
        )
    )

    @field_validator("prioridade")
    @classmethod
    def validar_prioridade(cls, v: str) -> str:
        """Valida se prioridade está entre os valores permitidos."""
        prioridades_validas = [p.value for p in PrioridadeChamado]
        if v not in prioridades_validas:
            raise ValueError(
                f"Prioridade inválida. Use: {', '.join(prioridades_validas)}"
            )
        return v


class AlterarStatusDTO(BaseModel):
    """
    DTO para alteração de status de um chamado.

    Usado quando administradores alteram o status sem adicionar mensagem.
    """

    status: str

    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida se status está entre os valores permitidos."""
        status_validos = [s.value for s in StatusChamado]
        if v not in status_validos:
            raise ValueError(
                f"Status inválido. Use: {', '.join(status_validos)}"
            )
        return v
