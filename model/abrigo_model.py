from dataclasses import dataclass
from datetime import datetime


@dataclass
class Abrigo:
    id_abrigo: int
    responsavel: str
    data_abertura: datetime
    