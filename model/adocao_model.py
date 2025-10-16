from dataclasses import dataclass
from datetime import datetime


@dataclass
class Adocao:
    id_adocao: int
    id_adotante: int
    id_animal: int
    data_solicitacao: datetime
    data_adocao: datetime
    status: str
    observacoes: str
    