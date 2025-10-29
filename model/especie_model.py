from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Especie:
    id: int
    nome: str
    descricao: Optional[str] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None

    # Propriedade para manter compatibilidade com código existente
    @property
    def id_especie(self) -> int:
        return self.id