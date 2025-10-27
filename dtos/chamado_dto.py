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
        prioridades_validas = ["Baixa", "Média", "Alta", "Urgente"]
        if v not in prioridades_validas:
            raise ValueError(
                f"Prioridade inválida. Use: {', '.join(prioridades_validas)}"
            )
        return v


class ResponderChamadoDTO(BaseModel):
    """
    DTO para resposta de administrador a um chamado.

    Usado quando administradores respondem e alteram status de chamados.
    """

    resposta: str
    status: str

    _validar_resposta = field_validator("resposta")(
        validar_string_obrigatoria(
            nome_campo="Resposta",
            tamanho_minimo=10,
            tamanho_maximo=2000
        )
    )

    @field_validator("status")
    @classmethod
    def validar_status(cls, v: str) -> str:
        """Valida se status está entre os valores permitidos."""
        status_validos = ["Aberto", "Em Análise", "Resolvido", "Fechado"]
        if v not in status_validos:
            raise ValueError(
                f"Status inválido. Use: {', '.join(status_validos)}"
            )
        return v
