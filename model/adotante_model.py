from dataclasses import dataclass

@dataclass
class Adotante:
    id_adotante: int
    renda_media: float
    tem_filhos: bool
    estado_saude: str