from dataclasses import dataclass
from typing import Optional

from model.usuario_model import Usuario


@dataclass
class Endereco:
    """
    Model de endereço do sistema.

    Attributes:
        id_endereco: Identificador único do endereço
        id_usuario: ID do usuário (FK)
        titulo: Título do endereço (ex: Casa, Trabalho)
        logradouro: Rua/Avenida
        numero: Número do imóvel
        complemento: Complemento do endereço
        bairro: Bairro
        cidade: Cidade
        uf: Estado (UF)
        cep: CEP (formato: 00000-000)
        usuario: Objeto Usuario relacionado (opcional)
    """
    id_endereco: int
    id_usuario: int
    titulo: str
    logradouro: str
    numero: int
    complemento: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    usuario: Optional[Usuario] = None