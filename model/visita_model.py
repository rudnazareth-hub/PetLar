from dataclasses import dataclass
from datetime import datetime


@dataclass
class Visita:
    id_adotante: int
    id_abrigo: int
    data_agendada: datetime
    observacoes: str
    status: str