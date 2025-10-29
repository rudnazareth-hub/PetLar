from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Adotante:
    id_adotante: int
    renda_media: float
    tem_filhos: bool
    estado_saude: str
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None