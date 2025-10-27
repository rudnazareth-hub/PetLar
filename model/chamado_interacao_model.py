"""
Model para interações de chamados.

Representa cada mensagem/interação em um chamado, seja do usuário original,
do administrador, ou qualquer outra resposta subsequente.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TipoInteracao(Enum):
    """
    Tipos possíveis de interação em um chamado.

    - ABERTURA: Mensagem inicial que criou o chamado
    - RESPOSTA_USUARIO: Resposta/mensagem adicional do usuário
    - RESPOSTA_ADMIN: Resposta do administrador
    """
    ABERTURA = "Abertura"
    RESPOSTA_USUARIO = "Resposta do Usuário"
    RESPOSTA_ADMIN = "Resposta do Administrador"


@dataclass
class ChamadoInteracao:
    """
    Representa uma interação (mensagem) em um chamado.

    Cada interação armazena:
    - Qual chamado pertence
    - Quem escreveu (usuário ou admin)
    - O conteúdo da mensagem
    - Quando foi escrita
    - Tipo da interação
    - Status resultante do chamado após esta interação (se aplicável)
    """
    id: int
    chamado_id: int
    usuario_id: int
    mensagem: str
    tipo: TipoInteracao
    data_interacao: datetime
    status_resultante: Optional[str] = None
    # Campos do JOIN (para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None
