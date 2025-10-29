from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Abrigo:
    """
    Model de abrigo do sistema.

    Relacionamento 1:1 com Usuario (id_abrigo = id do usuario)

    Attributes:
        id_abrigo: ID do abrigo (mesmo ID do usuário)
        responsavel: Nome do responsável pelo abrigo
        descricao: Descrição do abrigo
        data_abertura: Data de abertura do abrigo
        data_membros: Data de cadastro dos membros
        data_cadastro: Data de cadastro do abrigo
        data_atualizacao: Data da última atualização
    """
    id_abrigo: int
    responsavel: str
    descricao: Optional[str] = None
    data_abertura: Optional[str] = None
    data_membros: Optional[str] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
