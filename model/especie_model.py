from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Especie:
    """
    Representa uma espécie de algo do projeto.

    Atributos:
        id: Identificador único da espécie
        nome: Nome da espécie (ex: "Tecnologia")
        descricao: Descrição opcional da espécie
        data_cadastro: Data/hora de criação do registro
        data_atualizacao: Data/hora da última atualização
    """
    id: Optional[int] = None
    nome: str = ""
    descricao: str = ""
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    especie: Optional["Especie"] = None
    