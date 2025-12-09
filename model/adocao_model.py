from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Adocao:
    """
    Model de adoção do sistema.

    Attributes:
        id: Identificador único da adoção
        id_adotante: ID do adotante (FK para Usuario)
        id_animal: ID do animal (FK para Animal)
        data_adocao: Data e hora da conclusão da adoção
        observacoes: Observações sobre a adoção
        data_cadastro: Data de cadastro do registro
        data_atualizacao: Data da última atualização
        animal_nome: Nome do animal (do JOIN)
        animal_foto: Foto do animal (do JOIN)
        adotante_nome: Nome do adotante (do JOIN)
        adotante_email: Email do adotante (do JOIN)
    """
    id: int
    id_adotante: int
    id_animal: int
    data_adocao: Optional[datetime] = None
    observacoes: Optional[str] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    # Campos do JOIN (opcionais)
    animal_nome: Optional[str] = None
    animal_foto: Optional[str] = None
    animal_sexo: Optional[str] = None
    raca_nome: Optional[str] = None
    especie_nome: Optional[str] = None
    abrigo_nome: Optional[str] = None
    adotante_nome: Optional[str] = None
    adotante_email: Optional[str] = None

    @property
    def id_adocao(self) -> int:
        """Compatibilidade com código existente."""
        return self.id
