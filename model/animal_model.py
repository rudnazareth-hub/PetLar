from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.abrigo_model import Abrigo
from model.raca_model import Raca


@dataclass

class Animal:
    id_animal: int
    id_raca: int
    id_abrigo: int
    data_nascimento: datetime
    data_entrada: datetime
    observacoes: str
    # Relacionamentos
    raca: Optional[Raca]
    abrigo: Optional[Abrigo]