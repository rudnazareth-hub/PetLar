from dataclasses import dataclass
from typing import Optional

@dataclass
class Tarefa:
    id: int
    titulo: str
    descricao: str
    concluida: bool
    usuario_id: int
    data_criacao: Optional[str] = None
    data_conclusao: Optional[str] = None
