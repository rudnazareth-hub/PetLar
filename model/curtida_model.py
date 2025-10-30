from dataclasses import dataclass
from datetime import datetime


@dataclass
class Curtida:
    id: int
    id_usuario: int
    id_animal: int
    data_curtida: datetime
    