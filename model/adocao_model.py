from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.adotante_model import Adotante
from model.animal_model import Animal


@dataclass
class Adocao:
    id: int
    id_adotante: int
    id_animal: int
    data_solicitacao: datetime
    data_adocao: Optional[datetime] = None
    status: str = "Concluída"
    observacoes: Optional[str] = None
    data_atualizacao: Optional[datetime] = None

    adotante: Optional[Adotante] = None
    animal: Optional[Animal] = None 

    # Propriedade para manter compatibilidade com código existente
    @property
    def id_adocao(self) -> int:
        return self.id