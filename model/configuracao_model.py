from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Configuracao:
    id: int
    chave: str
    valor: str
    descricao: Optional[str] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
