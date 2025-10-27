from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Chamado:
    """
    Modelo de dados para um chamado de suporte.

    Representa um ticket/chamado aberto por um usuário para ser
    respondido por administradores do sistema.
    """
    id: int
    titulo: str
    descricao: str
    status: str  # Aberto, Em Análise, Resolvido, Fechado
    prioridade: str  # Baixa, Média, Alta, Urgente
    usuario_id: int
    data_abertura: Optional[datetime] = None
    data_fechamento: Optional[datetime] = None
    resposta_admin: Optional[str] = None
    admin_id: Optional[int] = None  # ID do admin que respondeu
    data_resposta: Optional[datetime] = None  # Data/hora da resposta
    usuario_nome: Optional[str] = None  # Nome do usuário (do JOIN)
    usuario_email: Optional[str] = None  # Email do usuário (do JOIN)
    admin_nome: Optional[str] = None  # Nome do admin que respondeu (do JOIN)
