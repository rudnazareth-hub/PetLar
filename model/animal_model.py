from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.abrigo_model import Abrigo
from model.raca_model import Raca


@dataclass
class Animal:
    """
    Model de animal do sistema.

    Attributes:
        id_animal: Identificador único do animal
        id_raca: ID da raça (FK)
        id_abrigo: ID do abrigo (FK)
        nome: Nome do animal
        sexo: Sexo do animal (Macho/Fêmea)
        data_nascimento: Data de nascimento do animal
        data_entrada: Data de entrada no abrigo
        observacoes: Observações sobre o animal
        status: Status do animal (Disponível/Em Processo/Adotado/Indisponível)
        foto: Caminho da foto do animal
        raca: Objeto Raca relacionado (opcional)
        abrigo: Objeto Abrigo relacionado (opcional)
        data_cadastro: Data de cadastro do animal
        data_atualizacao: Data da última atualização
    """
    id: int
    id_raca: int
    id_abrigo: int
    nome: str
    sexo: str
    data_nascimento: Optional[str] = None
    data_entrada: Optional[str] = None
    observacoes: Optional[str] = None
    status: str = "Disponível"
    foto: Optional[str] = None
    # Relacionamentos
    raca: Optional[Raca] = None
    abrigo: Optional[Abrigo] = None
    # Timestamps
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None

    # Propriedade para manter compatibilidade com código existente
    @property
    def id_animal(self) -> int:
        return self.id

    @id_animal.setter
    def id_animal(self, value: int):
        self.id = value
