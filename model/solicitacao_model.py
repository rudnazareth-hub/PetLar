from dataclasses import dataclass


@dataclass
class SolicitacaoModel:
    id_solicitacao: int
    id_adotante: int
    id_animal: str
    data_solicitacao: datatime
    status: str
    observacoes: int  