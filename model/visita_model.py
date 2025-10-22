from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.abrigo_model import Abrigo
from model.adotante_model import Adotante


@dataclass
class Visita:
    id_visita: int
    id_adotante: int
    id_abrigo: int
    data_agendada: datetime
    observacoes: Optional[str] = None
    status: str = "Agendada"

    adotante: Optional[Adotante] = None
    abrigo: Optional[Abrigo] = None