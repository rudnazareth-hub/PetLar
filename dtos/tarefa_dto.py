from pydantic import BaseModel, Field, field_validator

class CriarTarefaDTO(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    descricao: str = Field(default="", max_length=500)

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v):
        if not v or not v.strip():
            raise ValueError('Título é obrigatório')
        return v.strip()

class AlterarTarefaDTO(BaseModel):
    id: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=3, max_length=100)
    descricao: str = Field(default="", max_length=500)
    concluida: bool = False

    @field_validator('titulo')
    @classmethod
    def validar_titulo(cls, v):
        if not v or not v.strip():
            raise ValueError('Título é obrigatório')
        return v.strip()
