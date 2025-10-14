from pydantic import BaseModel, field_validator


class CriarTarefaDTO(BaseModel):
    """DTO para criação de tarefa"""

    titulo: str
    descricao: str = ""

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, v):
        """Valida título da tarefa"""
        if not v or not v.strip():
            raise ValueError("Título é obrigatório")

        if len(v.split()) < 2:
            raise ValueError("Título deve ter no mínimo 2 palavras")

        if len(v.strip()) > 128:
            raise ValueError("Título deve ter no máximo 128 caracteres")

        return v.strip()

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, v):
        """Valida descrição da tarefa"""
        if v and len(v.strip()) > 500:
            raise ValueError("Descrição deve ter no máximo 500 caracteres")
        return v.strip() if v else ""


class AlterarTarefaDTO(BaseModel):
    """DTO para alteração de tarefa"""

    id: int
    titulo: str
    descricao: str = ""
    concluida: bool = False

    @field_validator("id")
    @classmethod
    def validar_id(cls, v):
        """Valida ID da tarefa"""
        if not isinstance(v, int) or v <= 0:
            raise ValueError("ID deve ser um número positivo")
        return v

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, v):
        """Valida título da tarefa"""
        if not v or not v.strip():
            raise ValueError("Título é obrigatório")

        if len(v.split()) < 2:
            raise ValueError("Título deve ter no mínimo 2 palavras")

        if len(v.strip()) > 128:
            raise ValueError("Título deve ter no máximo 128 caracteres")

        return v.strip()

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, v):
        """Valida descrição da tarefa"""
        if v and len(v) > 500:
            raise ValueError("Descrição deve ter no máximo 500 caracteres")
        return v.strip() if v else ""
