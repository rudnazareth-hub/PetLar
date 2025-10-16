from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.especie_model import Especie


@dataclass
class Raca:
    id_raca: int
    id_especie: int
    nome: str
    descricao: str
    temperamento: str
    expectativa_de_vida: str
    porte: str 
    # relacionamentos
    especie: Optional[Especie]  