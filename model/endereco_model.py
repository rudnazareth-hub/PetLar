from dataclasses import dataclass


@dataclass
class Endereco:
    id_usuario: int
    titulo: str
    logradouro: str
    numero: int
    complemento: str
    bairro: str
    cidade: str
    UF: str
    CEP: int