from pydantic import BaseModel, field_validator
from typing import Optional
from dtos.validators import (
    validar_string_obrigatoria,
    validar_texto_longo_opcional,
    validar_id_positivo,
    validar_data_opcional,
    validar_sexo_animal,
    validar_status_animal
)

class CadastrarAnimalDTO(BaseModel):
    """DTO para cadastro de animal"""
    nome: str
    id_raca: int
    id_abrigo: int
    sexo: str
    data_nascimento: Optional[str] = None
    data_entrada: Optional[str] = None
    observacoes: Optional[str] = None
    status: str = "Disponível"

    _validar_nome = field_validator('nome')(
        validar_string_obrigatoria('Nome', tamanho_minimo=2, tamanho_maximo=100)
    )
    _validar_id_raca = field_validator('id_raca')(validar_id_positivo())
    _validar_id_abrigo = field_validator('id_abrigo')(validar_id_positivo())
    _validar_sexo = field_validator('sexo')(validar_sexo_animal())
    _validar_status = field_validator('status')(validar_status_animal())
    _validar_data_nascimento = field_validator('data_nascimento')(validar_data_opcional())
    _validar_data_entrada = field_validator('data_entrada')(validar_data_opcional())
    _validar_observacoes = field_validator('observacoes')(
        validar_texto_longo_opcional(tamanho_maximo=1000)
    )

class AlterarAnimalDTO(BaseModel):
    """DTO para alteração de animal"""
    id_animal: int
    nome: str
    id_raca: int
    id_abrigo: int
    sexo: str
    data_nascimento: Optional[str] = None
    data_entrada: Optional[str] = None
    observacoes: Optional[str] = None
    status: str

    _validar_id = field_validator('id_animal')(validar_id_positivo())
    # Mesmos validadores do CadastrarAnimalDTO

class AlterarStatusAnimalDTO(BaseModel):
    """DTO para alteração apenas do status do animal"""
    id_animal: int
    status: str

    _validar_id = field_validator('id_animal')(validar_id_positivo())
    _validar_status = field_validator('status')(validar_status_animal())