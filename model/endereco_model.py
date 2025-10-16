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
    Uf: str
    CEP: int