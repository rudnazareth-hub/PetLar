from dataclasses import dataclass
from typing import Optional
from datetime import datetime

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
        data_cadastro: Data de cadastro do endereço
        data_atualizacao: Data da última atualização
    """
    id: int
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
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None

    # Propriedade para manter compatibilidade com código existente
    @property
    def id_endereco(self) -> int:
        return self.id