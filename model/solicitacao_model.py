from dataclasses import dataclass
from datetime import datetime


@dataclass
class Solicitacao:
    id_solicitacao: int
    id_adotante: int
    id_animal: int
    data_solicitacao: datetime
    status: str
    observacoes: str  