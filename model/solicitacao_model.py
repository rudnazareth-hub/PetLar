from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.adotante_model import Adotante
from model.animal_model import Animal


@dataclass
class Solicitacao:
    id_solicitacao: int
    id_adotante: int
    id_animal: int
    data_solicitacao: datetime
    status: str
    observacoes: Optional[str] = None
    resposta_abrigo: Optional[str] = None
    # Relacionamentos
    adotante: Optional[Adotante] = None
    animal: Optional[Animal] = None
    