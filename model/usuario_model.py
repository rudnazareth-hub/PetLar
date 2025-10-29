from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from util.perfis import Perfil

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    data_nascimento: Optional[str] = None  # Formato: YYYY-MM-DD
    numero_documento: Optional[str] = None  # CPF ou CNPJ
    telefone: Optional[str] = None  # Formato: (00) 00000-0000
    confirmado: bool = False  # Email confirmado?
    token_redefinicao: Optional[str] = None
    data_token: Optional[datetime] = None
    data_cadastro: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
