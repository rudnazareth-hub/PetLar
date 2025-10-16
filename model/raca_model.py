from dataclasses import dataclass
from datetime import datetime


@dataclass
class Raca:
    id_raca: int
    id_especie: int
    nome: str
    descricao: str
    temperamento: str
    expectativa_de_vida: str
    porte: str
    