from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.adotante_model import Adotante
from model.animal_model import Animal


@dataclass
class Adocao:
    id_adocao: int
    id_adotante: int
    id_animal: int
    data_solicitacao: datetime
    data_adocao: datetime
    status: str
    observacoes: str
    
    adotante: Optional[Adotante] 
    animal: Optional[Animal] 