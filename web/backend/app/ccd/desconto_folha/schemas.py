"""DTOs do desconto em folha: cadastro → resposta do órgão → match FRAP.

JSON em camelCase (alias_generator); os modelos aceitam os dois nomes na
entrada. Datas saem como ISO sem fuso (MSSQL DATETIME é naive).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

StatusExtracao = Literal["PENDENTE", "OK", "SEM_RESPOSTA", "ERRO"]


class _Camel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# ----- leitura ---------------------------------------------------------------


class NotificacaoOut(_Camel):
    numero: Optional[str] = None  # "001940/2024"
    data: Optional[datetime] = None


class ArOut(_Camel):
    numero_postagem: Optional[str] = None
    data: Optional[datetime] = None


class RespostaOut(_Camel):
    processo: Optional[str] = None  # apensado, "300031/2025"
    evento: Optional[int] = None  # evento de apensamento no principal
    data: Optional[datetime] = None


class CadastroListItem(_Camel):
    id: int
    id_processo: int
    processo: str
    id_debito: Optional[int] = None
    id_pessoa: Optional[int] = None
    cpf_cnpj: Optional[str] = None
    responsavel: Optional[str] = None
    id_orgao: Optional[int] = None
    orgao: Optional[str] = None
    notificacao: NotificacaoOut
    ar: ArOut
    resposta: RespostaOut
    status_extracao: StatusExtracao
    valor_total: Optional[float] = None
    parcelado: bool = False
    qtd_valores: int = 0
    qtd_matches: int = 0


class CadastroListResponse(_Camel):
    items: list[CadastroListItem]
    total: int
    page: int
    size: int


class LancamentoOut(_Camel):
    id_lancamento: int
    dt_movimento: Optional[date] = None
    documento: Optional[str] = None
    historico: Optional[str] = None
    valor: float


class MatchOut(_Camel):
    id_match: int
    lancamento: LancamentoOut
    automatico: bool
    data_match: Optional[datetime] = None
    observacao: Optional[str] = None


class ValorOut(_Camel):
    id_valor: int
    numero_parcela: int
    mes: Optional[int] = None
    ano: Optional[int] = None
    valor: float
    origem: Literal["L", "M"]
    match: Optional[MatchOut] = None
    candidatos: list[LancamentoOut] = []


class CadastroDetalhe(CadastroListItem):
    trecho_resposta: Optional[str] = None
    arquivo_resposta: Optional[str] = None
    data_extracao: Optional[datetime] = None
    observacoes: Optional[str] = None
    valores: list[ValorOut] = []


# ----- lookup do processo (formulário) --------------------------------------


class DebitoLookup(_Camel):
    id_debito: int
    valor_original: Optional[float] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    cancelado: bool = False
    id_pessoa: Optional[int] = None
    nome_pessoa: Optional[str] = None
    documento: Optional[str] = None


class ProcessoLookup(_Camel):
    id_processo: int
    processo: str
    orgao: Optional[str] = None
    debitos: list[DebitoLookup]


# ----- escrita ---------------------------------------------------------------


class CadastroInput(_Camel):
    id_processo: int
    id_debito: Optional[int] = None
    id_pessoa: Optional[int] = None
    nome_orgao: Optional[str] = None
    observacoes: Optional[str] = None


class CadastroPatch(_Camel):
    id_debito: Optional[int] = None
    id_pessoa: Optional[int] = None
    nome_orgao: Optional[str] = None
    observacoes: Optional[str] = None


class ValorInput(_Camel):
    numero_parcela: int = Field(1, ge=1)
    mes: Optional[int] = Field(None, ge=1, le=12)
    ano: Optional[int] = Field(None, ge=2000, le=2100)
    valor: float = Field(gt=0)


class MatchInput(_Camel):
    id_lancamento: int
    observacao: Optional[str] = None


class MatchAutomaticoResultado(_Camel):
    vinculados: int
