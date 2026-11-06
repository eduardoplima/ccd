"""DTOs do cadastro de TAGs (CGTAG). JSON em camelCase."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

SituacaoTag = Literal["VIGENTE", "CUMPRIDO", "RESCINDIDO", "PRORROGADO"]
SituacaoObrigacao = Literal["PENDENTE", "CUMPRIDA", "DESCUMPRIDA", "PRORROGADA"]


class _Camel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class ObrigacaoOut(_Camel):
    id: int
    ordem: int
    clausula: str
    descricao: str
    prazo_texto: Optional[str] = None
    data_limite: Optional[date] = None
    situacao: SituacaoObrigacao
    data_cumprimento: Optional[date] = None
    evento_comprovacao: Optional[int] = None
    observacoes: Optional[str] = None


class TagListItem(_Camel):
    id: int
    id_processo: int
    processo: str  # "014254/2015"
    evento: int
    url_evento: Optional[str] = None
    numero: str
    orgao: str
    responsavel: str
    prazo: Optional[date] = None
    situacao: SituacaoTag
    revisado: bool
    qtd_obrigacoes: int
    proxima_data_limite: Optional[date] = None  # menor data-limite pendente
    data_inclusao: Optional[datetime] = None


class TagListResponse(_Camel):
    items: list[TagListItem]
    total: int


class TagDetalhe(TagListItem):
    id_informacao: Optional[int] = None
    cargo_responsavel: Optional[str] = None
    cpf_responsavel: Optional[str] = None
    compromissario: Optional[str] = None
    data_celebracao: Optional[date] = None
    homologacao: Optional[str] = None
    valor_multa_descumprimento: Optional[float] = None
    observacoes: Optional[str] = None
    texto_ocr: Optional[str] = None
    obrigacoes: list[ObrigacaoOut] = []


# ----- escrita ---------------------------------------------------------------


class ExtrairInput(_Camel):
    processo: str = Field(pattern=r"^\d{1,6}/\d{4}$", description="numero/ano, ex.: 14254/2015")
    evento: int = Field(ge=1)


class TagPatch(_Camel):
    """Campos do cabeçalho; só o que vier não-nulo é alterado."""

    numero: Optional[str] = Field(None, max_length=40)
    orgao: Optional[str] = Field(None, max_length=255)
    responsavel: Optional[str] = Field(None, max_length=255)
    cargo_responsavel: Optional[str] = Field(None, max_length=255)
    cpf_responsavel: Optional[str] = Field(None, max_length=14)
    compromissario: Optional[str] = Field(None, max_length=255)
    data_celebracao: Optional[date] = None
    prazo: Optional[date] = None
    homologacao: Optional[str] = Field(None, max_length=120)
    valor_multa_descumprimento: Optional[float] = None
    situacao: Optional[SituacaoTag] = None
    revisado: Optional[bool] = None
    observacoes: Optional[str] = None


class ObrigacaoInput(_Camel):
    clausula: str = Field(max_length=80)
    descricao: str = Field(min_length=1)
    prazo_texto: Optional[str] = Field(None, max_length=255)
    data_limite: Optional[date] = None
    situacao: SituacaoObrigacao = "PENDENTE"
    data_cumprimento: Optional[date] = None
    evento_comprovacao: Optional[int] = None
    observacoes: Optional[str] = None


class ObrigacoesInput(_Camel):
    obrigacoes: list[ObrigacaoInput]
