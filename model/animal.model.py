from dataclasses import dataclass
from datetime import datetime


@dataclass

class Animal:
    id_animal: int
    id_raca: int
    id_abrigo: int
    data_nascimento: datetime
    data_entrada: datetime
    observacoes: str