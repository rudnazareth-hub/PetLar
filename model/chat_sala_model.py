"""
Model para representar uma sala de chat entre dois usuários.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatSala:
    """
    Representa uma sala de chat privada entre dois usuários.

    O ID da sala segue o padrão: "menor_id_maior_id"
    Exemplo: Usuários com ID 3 e 7 sempre usam a sala "3_7"
    """
    id: str
    criada_em: datetime
    ultima_atividade: datetime
