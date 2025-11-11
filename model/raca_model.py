from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# from model.especie_model import Especie  # REMOVIDO: O aluno deverá criar este modelo


@dataclass
class Raca:
    id: int
    id_especie: int
    nome: str
    descricao: Optional[str] = None
    temperamento: Optional[str] = None
    expectativa_de_vida: Optional[str] = None
    porte: Optional[str] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    # relacionamentos
    # especie: Optional[Especie] = None  # REMOVIDO: O aluno deverá criar o modelo Especie

    # Propriedade para manter compatibilidade com código existente
    @property
    def id_raca(self) -> int:
        return self.id  