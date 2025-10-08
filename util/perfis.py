from enum import Enum

class Perfil(str, Enum):
    """Enum centralizado para perfis de usuário"""
    ADMIN = "admin"
    CLIENTE = "cliente"

    @classmethod
    def valores(cls):
        """Retorna lista de todos os valores de perfis"""
        return [perfil.value for perfil in cls]

    @classmethod
    def existe(cls, valor: str) -> bool:
        """Verifica se um perfil existe"""
        return valor in cls.valores()
