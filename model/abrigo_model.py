from dataclasses import dataclass
from typing import Optional

@dataclass
class Abrigo:
    id_abrigo: int  # Mesmo ID do usuario
    responsavel: str
    descricao: Optional[str] = None
    data_abertura: Optional[str] = None  # YYYY-MM-DD
    data_membros: Optional[str] = None  # JSON com lista de membros