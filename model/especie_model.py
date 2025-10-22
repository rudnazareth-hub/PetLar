from dataclasses import dataclass
from typing import Optional


@dataclass
class Especie:
    id_especie: int
    nome: str
    descricao: Optional[str] = None