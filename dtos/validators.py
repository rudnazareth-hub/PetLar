"""
Módulo de validadores reutilizáveis para DTOs.

Este módulo contém funções de validação comuns que podem ser usadas
em múltiplos DTOs para evitar duplicação de código.

Uso:
    from dtos.validators import validar_email, validar_senha_forte

    class MeuDTO(BaseModel):
        email: str
        senha: str

        _validar_email = field_validator('email')(validar_email())
        _validar_senha = field_validator('senha')(validar_senha_forte())
"""

import re
from typing import Optional, Set, Callable, Any
from datetime import datetime
from pathlib import Path


# ===== VALIDAÇÕES DE CAMPOS DE TEXTO =====


def validar_string_obrigatoria(
    nome_campo: str = "Campo",
    tamanho_minimo: Optional[int] = None,
    tamanho_maximo: Optional[int] = None,
    truncar: bool = True,
) -> Callable[[Any, Any], Any]:
    """
    Valida string obrigatória com comprimento opcional.

    Args:
        nome_campo: Nome do campo para mensagens de erro
        tamanho_minimo: Comprimento mínimo (opcional)
        tamanho_maximo: Comprimento máximo (opcional)
        truncar: Se deve remover espaços das bordas

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_titulo = field_validator('titulo')(
            validar_string_obrigatoria('Título', tamanho_minimo=3, tamanho_maximo=100)
        )
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or (truncar and not v.strip()):
            raise ValueError(f"{nome_campo} é obrigatório.")

        valor = v.strip() if truncar else v

        if tamanho_minimo and len(valor) < tamanho_minimo:
            raise ValueError(
                f"{nome_campo} deve ter no mínimo {tamanho_minimo} caracteres."
            )

        if tamanho_maximo and len(valor) > tamanho_maximo:
            raise ValueError(
                f"{nome_campo} deve ter no máximo {tamanho_maximo} caracteres."
            )

        return valor

    return validator


def validar_comprimento(
    tamanho_minimo: Optional[int] = None,
    tamanho_maximo: Optional[int] = None,
    truncar: bool = True,
) -> Callable[[Any, Any], Any]:
    """
    Valida comprimento de string (permite vazia).

    Args:
        tamanho_minimo: Comprimento mínimo (opcional)
        tamanho_maximo: Comprimento máximo (opcional)
        truncar: Se deve remover espaços das bordas

    Returns:
        Função validadora para uso com field_validator
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v:
            return "" if truncar else v

        valor = v.strip() if truncar else v

        if tamanho_minimo and len(valor) < tamanho_minimo:
            raise ValueError(f"Deve ter no mínimo {tamanho_minimo} caracteres.")

        if tamanho_maximo and len(valor) > tamanho_maximo:
            raise ValueError(f"Deve ter no máximo {tamanho_maximo} caracteres.")

        return valor

    return validator


def validar_texto_minimo_palavras(
    min_palavras: int = 2,
    tamanho_maximo: int = 128,
    nome_campo: str = "Texto",
) -> Callable[[Any, Any], Any]:
    """
    Valida texto que deve conter um número mínimo de palavras.

    Args:
        min_palavras: Número mínimo de palavras
        tamanho_maximo: Comprimento máximo do texto
        nome_campo: Nome do campo para mensagens de erro

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_titulo = field_validator('titulo')(
            validar_texto_minimo_palavras(min_palavras=2, tamanho_maximo=128, nome_campo='Título')
        )
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError(f"{nome_campo} é obrigatório.")

        valor = v.strip()

        if len(valor.split()) < min_palavras:
            raise ValueError(
                f"{nome_campo} deve ter no mínimo {min_palavras} palavras."
            )

        if len(valor) > tamanho_maximo:
            raise ValueError(
                f"{nome_campo} deve ter no máximo {tamanho_maximo} caracteres."
            )

        return valor

    return validator


# ===== VALIDAÇÕES DE IDENTIFICAÇÃO PESSOAL =====


def validar_nome_pessoa(
    tamanho_minimo: Optional[int] = 4,
    min_palavras: Optional[int] = 2,
    tamanho_maximo: Optional[int] = 128,
) -> Callable[[Any, Any], Any]:
    """
    Valida nome de pessoa com opções flexíveis.

    Args:
        tamanho_minimo: Número mínimo de caracteres (opcional)
        min_palavras: Número mínimo de palavras (opcional)
        tamanho_maximo: Comprimento máximo

    Returns:
        Função validadora para uso com field_validator

    Example:
        # Nome simples (min 3 caracteres)
        _validar_nome = field_validator('nome')(validar_nome_pessoa(tamanho_minimo=3))

        # Nome completo (min 2 palavras)
        _validar_nome = field_validator('nome')(validar_nome_pessoa(min_palavras=2))
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("Nome é obrigatório.")

        valor = v.strip()

        if tamanho_minimo and len(valor) < tamanho_minimo:
            raise ValueError(f"Nome deve ter no mínimo {tamanho_minimo} caracteres.")

        if min_palavras and len(valor.split()) < min_palavras:
            raise ValueError(f"Nome deve ter no mínimo {min_palavras} palavras.")

        if tamanho_maximo and len(valor) > tamanho_maximo:
            raise ValueError(f"Nome deve ter no máximo {tamanho_maximo} caracteres.")

        return valor

    return validator


def validar_email(
    tamanho_minimo: int = 5,
    tamanho_maximo: int = 254,  # RFC 5321
) -> Callable[[Any, Any], Any]:
    """
    Valida formato de e-mail.

    Args:
        tamanho_minimo: Comprimento mínimo
        tamanho_maximo: Comprimento máximo (padrão: 254 conforme RFC 5321)

    Returns:
        Função validadora para uso com field_validator
        Retorna e-mail em lowercase

    Example:
        _validar_email = field_validator('email')(validar_email())
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("E-mail é obrigatório.")

        valor = v.strip()

        if len(valor) < tamanho_minimo:
            raise ValueError(f"E-mail deve ter no mínimo {tamanho_minimo} caracteres.")

        if len(valor) > tamanho_maximo:
            raise ValueError(f"E-mail deve ter no máximo {tamanho_maximo} caracteres.")

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, valor):
            raise ValueError("Formato de e-mail inválido.")

        return valor.lower()

    return validator


def validar_cpf(formatar: bool = False) -> Callable[[Any, Any], Any]:
    """
    Valida CPF brasileiro com verificação de dígitos.

    Args:
        formatar: Se deve retornar CPF formatado (XXX.XXX.XXX-XX)

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_cpf = field_validator('cpf')(validar_cpf(formatar=True))
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("CPF é obrigatório.")

        # Remove caracteres não numéricos
        cpf = re.sub(r"\D", "", v.strip())

        if len(cpf) != 11:
            raise ValueError("CPF deve conter 11 dígitos.")

        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            raise ValueError("CPF inválido.")

        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial: str) -> str:
            soma = 0
            for i, digito in enumerate(cpf_parcial):
                soma += int(digito) * (len(cpf_parcial) + 1 - i)
            resto = soma % 11
            return "0" if resto < 2 else str(11 - resto)

        # Valida primeiro dígito
        if cpf[9] != calcular_digito(cpf[:9]):
            raise ValueError("CPF inválido.")

        # Valida segundo dígito
        if cpf[10] != calcular_digito(cpf[:10]):
            raise ValueError("CPF inválido.")

        if formatar:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

        return cpf

    return validator


def validar_cnpj(formatar: bool = False) -> Callable[[Any, Any], Any]:
    """
    Valida CNPJ brasileiro com verificação de dígitos.

    Args:
        formatar: Se deve retornar CNPJ formatado (XX.XXX.XXX/XXXX-XX)

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_cnpj = field_validator('cnpj')(validar_cnpj(formatar=True))
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("CNPJ é obrigatório.")

        # Remove caracteres não numéricos
        cnpj = re.sub(r"\D", "", v.strip())

        if len(cnpj) != 14:
            raise ValueError("CNPJ deve conter 14 dígitos.")

        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            raise ValueError("CNPJ inválido.")

        # Validação dos dígitos verificadores
        def calcular_digito(cnpj_parcial: str, pesos: list[int]) -> str:
            soma = sum(int(digito) * peso for digito, peso in zip(cnpj_parcial, pesos))
            resto = soma % 11
            return "0" if resto < 2 else str(11 - resto)

        # Pesos para validação
        pesos_primeiro = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos_segundo = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        # Valida primeiro dígito
        if cnpj[12] != calcular_digito(cnpj[:12], pesos_primeiro):
            raise ValueError("CNPJ inválido.")

        # Valida segundo dígito
        if cnpj[13] != calcular_digito(cnpj[:13], pesos_segundo):
            raise ValueError("CNPJ inválido.")

        if formatar:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

        return cnpj

    return validator


# ===== VALIDAÇÕES DE CONTATO =====


def validar_telefone_br(formatar: bool = False) -> Callable[[Any, Any], Any]:
    """
    Valida telefone brasileiro (celular ou fixo).

    Formatos aceitos:
    - Celular: (11) 91234-5678 ou 11912345678
    - Fixo: (11) 1234-5678 ou 1112345678

    Args:
        formatar: Se deve retornar telefone formatado

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_telefone = field_validator('telefone')(validar_telefone_br(formatar=True))
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("Telefone é obrigatório.")

        # Remove caracteres não numéricos
        telefone = re.sub(r"\D", "", v.strip())

        # Valida comprimento (10 dígitos para fixo, 11 para celular)
        if len(telefone) not in [10, 11]:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos.")

        # Valida DDD
        ddd = int(telefone[:2])
        if ddd < 11 or ddd > 99:
            raise ValueError("DDD inválido.")

        # Valida celular (deve começar com 9)
        if len(telefone) == 11 and telefone[2] != "9":
            raise ValueError("Número de celular deve começar com 9.")

        if formatar:
            if len(telefone) == 11:  # Celular
                return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
            else:  # Fixo
                return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"

        return telefone

    return validator


def validar_cep(formatar: bool = True) -> Callable[[Any, Any], Any]:
    """
    Valida CEP brasileiro.

    Args:
        formatar: Se deve retornar CEP formatado (XXXXX-XXX)

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_cep = field_validator('cep')(validar_cep(formatar=True))
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("CEP é obrigatório.")

        # Remove caracteres não numéricos
        cep = re.sub(r"\D", "", v.strip())

        if len(cep) != 8:
            raise ValueError("CEP deve conter 8 dígitos.")

        if formatar:
            return f"{cep[:5]}-{cep[5:]}"

        return cep

    return validator


# ===== VALIDAÇÕES DE SEGURANÇA =====


def validar_senha_forte(
    tamanho_minimo: int = 8,
    tamanho_maximo: int = 128,
    requer_maiuscula: bool = True,
    requer_minuscula: bool = True,
    requer_numero: bool = True,
    requer_especial: bool = True,
    caracteres_especiais: str = r"[!@#$%^&*(),.?\":{}|<>]",
) -> Callable[[Any, Any], Any]:
    """
    Valida força de senha com múltiplos critérios.

    Args:
        tamanho_minimo: Comprimento mínimo
        tamanho_maximo: Comprimento máximo
        requer_maiuscula: Se deve exigir letra maiúscula
        requer_minuscula: Se deve exigir letra minúscula
        requer_numero: Se deve exigir número
        requer_especial: Se deve exigir caractere especial
        caracteres_especiais: Regex para caracteres especiais aceitos

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_senha = field_validator('senha')(validar_senha_forte())
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("Senha é obrigatória.")

        valor = v.strip()

        if len(valor) < tamanho_minimo:
            raise ValueError(f"Senha deve ter no mínimo {tamanho_minimo} caracteres.")

        if len(valor) > tamanho_maximo:
            raise ValueError(f"Senha deve ter no máximo {tamanho_maximo} caracteres.")

        if requer_maiuscula and not re.search(r"[A-Z]", valor):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula.")

        if requer_minuscula and not re.search(r"[a-z]", valor):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula.")

        if requer_numero and not re.search(r"\d", valor):
            raise ValueError("Senha deve conter pelo menos um número.")

        if requer_especial and not re.search(caracteres_especiais, valor):
            raise ValueError("Senha deve conter pelo menos um caractere especial.")

        return valor

    return validator


def validar_senhas_coincidem(
    campo_senha: str = "senha",
    campo_confirmacao: str = "confirmar_senha",
    mensagem_erro: str = "As senhas não coincidem.",
) -> Callable[[Any], Any]:
    """
    Valida se dois campos de senha são iguais (model validator).

    Esta é uma função factory que retorna um model_validator para
    verificar se dois campos de senha coincidem.

    Args:
        campo_senha: Nome do campo com a senha (padrão: "senha")
        campo_confirmacao: Nome do campo com a confirmação (padrão: "confirmar_senha")
        mensagem_erro: Mensagem de erro customizada

    Returns:
        Função validadora para uso com @model_validator(mode="after")

    Example:
        class MeuDTO(BaseModel):
            senha: str
            confirmar_senha: str

            _validar_match = model_validator(mode="after")(
                validar_senhas_coincidem()
            )

        # Para campos com nomes diferentes:
        class AlterarSenhaDTO(BaseModel):
            senha_nova: str
            confirmar_senha: str

            _validar_match = model_validator(mode="after")(
                validar_senhas_coincidem("senha_nova", "confirmar_senha")
            )
    """

    def validator(model: Any) -> Any:  # noqa: ANN401
        senha = getattr(model, campo_senha, None)
        confirmacao = getattr(model, campo_confirmacao, None)

        if senha != confirmacao:
            raise ValueError(mensagem_erro)

        return model

    return validator


# ===== VALIDAÇÕES DE IDENTIFICADORES =====


def validar_id_positivo(nome_campo: str = "Identificador") -> Callable[[Any, Any], Any]:
    """
    Valida ID como número inteiro positivo.

    Args:
        nome_campo: Nome do campo para mensagens de erro

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_id = field_validator('id')(validar_id_positivo('ID'))
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{nome_campo} deve ser um número positivo.")
        return v

    return validator


def validar_inteiro_positivo(nome_campo: str = "Valor") -> Callable[[Any, Any], Any]:
    """
    Valida número inteiro positivo (alias para validar_id_positivo).

    Args:
        nome_campo: Nome do campo para mensagens de erro

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_especie = field_validator('id_especie')(validar_inteiro_positivo('ID da Espécie'))
    """
    return validar_id_positivo(nome_campo)


def validar_slug(tamanho_maximo: int = 128) -> Callable[[Any, Any], Any]:
    """
    Valida slug (URL-friendly string).

    Args:
        tamanho_maximo: Comprimento máximo

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_slug = field_validator('slug')(validar_slug())
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("Slug é obrigatório.")

        valor = v.strip().lower()

        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", valor):
            raise ValueError(
                "Slug deve conter apenas letras minúsculas, números e hífens."
            )

        if len(valor) > tamanho_maximo:
            raise ValueError(f"Slug deve ter no máximo {tamanho_maximo} caracteres.")

        return valor

    return validator


# ===== VALIDAÇÕES DE ARQUIVOS =====


def validar_extensao_arquivo(
    extensoes_permitidas: Set[str],
    nome_campo: str = "Arquivo",
) -> Callable[[Any, Any], Any]:
    """
    Valida extensão de arquivo.

    Args:
        extensoes_permitidas: Set de extensões permitidas (ex: {'.jpg', '.png'})
        nome_campo: Nome do campo para mensagens de erro

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_imagem = field_validator('filename')(
            validar_extensao_arquivo({'.jpg', '.png', '.gif'}, 'Imagem')
        )
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError(f"Nenhum {nome_campo.lower()} selecionado.")

        file_ext = Path(v.strip()).suffix.lower()

        if file_ext not in extensoes_permitidas:
            extensoes_str = ", ".join(sorted(extensoes_permitidas))
            raise ValueError(f"Formato não permitido. Use: {extensoes_str}.")

        return v.strip()

    return validator


def validar_tamanho_arquivo(
    tamanho_max_bytes: int,
    nome_campo: str = "Arquivo",
) -> Callable[[Any, Any], Any]:
    """
    Valida tamanho de arquivo.

    Args:
        tamanho_max_bytes: Tamanho máximo em bytes
        nome_campo: Nome do campo para mensagens de erro

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_tamanho = field_validator('size')(
            validar_tamanho_arquivo(5 * 1024 * 1024, 'Imagem')  # 5MB
        )
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if v <= 0:
            raise ValueError(f"{nome_campo} vazio.")

        if v > tamanho_max_bytes:
            max_mb = tamanho_max_bytes // (1024 * 1024)
            raise ValueError(f"{nome_campo} muito grande. Tamanho máximo: {max_mb}MB.")

        return v

    return validator


# ===== VALIDAÇÕES DE TIPOS ESPECÍFICOS =====


def validar_data(
    formato: str = "%Y-%m-%d",
    data_minima: Optional[datetime] = None,
    data_maxima: Optional[datetime] = None,
) -> Callable[[Any, Any], Any]:
    """
    Valida data com formato e range opcional.

    Args:
        formato: Formato da data (padrão: YYYY-MM-DD)
        data_minima: Data mínima permitida
        data_maxima: Data máxima permitida

    Returns:
        Função validadora para uso com field_validator
        Retorna string da data validada

    Example:
        _validar_data = field_validator('data_nascimento')(
            validar_data(data_maxima=datetime.now())
        )
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("Data é obrigatória.")

        try:
            data = datetime.strptime(v.strip(), formato)
        except ValueError:
            raise ValueError(f"Data inválida. Use o formato: {formato}.")

        if data_minima and data < data_minima:
            raise ValueError(
                f"Data deve ser posterior a {data_minima.strftime(formato)}."
            )

        if data_maxima and data > data_maxima:
            raise ValueError(
                f"Data deve ser anterior a {data_maxima.strftime(formato)}."
            )

        return v.strip()

    return validator


def validar_url(requer_protocolo: bool = True) -> Callable[[Any, Any], Any]:
    """
    Valida URL.

    Args:
        requer_protocolo: Se deve exigir http:// ou https://

    Returns:
        Função validadora para uso com field_validator

    Example:
        _validar_site = field_validator('site')(validar_url())
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        if not v or not v.strip():
            raise ValueError("URL é obrigatória.")

        valor = v.strip()

        if requer_protocolo:
            url_regex = r"^https?://[^\s/$.?#].[^\s]*$"
            if not re.match(url_regex, valor, re.IGNORECASE):
                raise ValueError("URL inválida. Deve começar com http:// ou https://.")
        else:
            url_regex = r"^(?:https?://)?[^\s/$.?#].[^\s]*$"
            if not re.match(url_regex, valor, re.IGNORECASE):
                raise ValueError("URL inválida.")

        return valor

    return validator


def validar_tipo(nome_campo: str, tipo_enum: Any) -> Callable[[Any, Any], Any]:
    """
    Valida tipo usando um Enum.

    Args:
        tipo_enum: Classe Enum com método existe() e valores()

    Returns:
        Função validadora para uso com field_validator

    Example:
        from model.chamado_model import StatusChamado
        _validar_status = field_validator('status')(validar_tipo(StatusChamado))
    """

    def validator(cls: Any, v: Any) -> Any:  # noqa: N805
        valores_validos = [t.value for t in tipo_enum]
        if v not in valores_validos:
            tipos_validos = ", ".join([f"'{t.value}'" for t in tipo_enum])
            raise ValueError(
                f"{nome_campo} deve ter um valor válido. Valores válidos: {tipos_validos}."
            )
        return v

    return validator


def validar_sexo_animal():
    """Valida sexo do animal (Macho/Fêmea)"""
    def validator(cls, v: str) -> str:
        valores_validos = {'Macho', 'Fêmea'}
        if v not in valores_validos:
            raise ValueError(f"Sexo deve ser 'Macho' ou 'Fêmea', recebido: '{v}'")
        return v
    return validator

def validar_status_animal():
    """Valida status do animal"""
    def validator(cls, v: str) -> str:
        valores_validos = {'Disponível', 'Em Processo', 'Adotado', 'Indisponível'}
        if v not in valores_validos:
            raise ValueError(f"Status inválido: '{v}'")
        return v
    return validator

def validar_valor_monetario(minimo: float = 0.0):
    """Valida valores monetários"""
    def validator(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < minimo:
            raise ValueError(f"Valor deve ser maior ou igual a R$ {minimo:.2f}")
        return v
    return validator

def validar_data_opcional():
    """Valida datas opcionais no formato YYYY-MM-DD ou dd/mm/yyyy"""
    def validator(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == '':
            return None

        # Tentar formato ISO (YYYY-MM-DD)
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            pass

        # Tentar formato brasileiro (dd/mm/yyyy)
        try:
            dt = datetime.strptime(v, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Data deve estar no formato YYYY-MM-DD ou dd/mm/yyyy")

    return validator

def validar_status_solicitacao():
    """Valida status da solicitação"""
    def validator(cls, v: str) -> str:
        valores_validos = {'Pendente', 'Aprovada', 'Rejeitada', 'Cancelada'}
        if v not in valores_validos:
            raise ValueError(f"Status inválido: '{v}'")
        return v
    return validator