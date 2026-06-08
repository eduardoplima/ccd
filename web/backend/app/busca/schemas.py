from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class PessoaItem(BaseModel):
    id_pessoa: int = Field(serialization_alias="idPessoa")
    cpfcnpj: str | None = None
    nome: str
    qtd_debitos: int = Field(serialization_alias="qtdDebitos")

    model_config = {"populate_by_name": True}


class PessoaListResponse(BaseModel):
    items: list[PessoaItem]
    total: int


class ProcessoHeader(BaseModel):
    id_processo: int = Field(serialization_alias="idProcesso")
    numero_processo: str = Field(serialization_alias="numeroProcesso")
    ano_processo: str = Field(serialization_alias="anoProcesso")
    assunto: str | None = None
    interessado: str | None = None
    valor: Decimal | None = None

    model_config = {"populate_by_name": True}


class ProcessoResultado(BaseModel):
    processo: ProcessoHeader
    tipo: Literal["origem", "execucao"]
    pessoas: list[PessoaItem]


class DebitoPessoaItem(BaseModel):
    id_debito: int = Field(serialization_alias="idDebito")
    id_processo_origem: int | None = Field(default=None, serialization_alias="idProcessoOrigem")
    id_processo_execucao: int | None = Field(default=None, serialization_alias="idProcessoExecucao")
    valor_original_debito: Decimal | None = Field(
        default=None, serialization_alias="valorOriginalDebito"
    )
    valor_pago: Decimal | None = Field(default=None, serialization_alias="valorPago")
    data_ato: date | None = Field(default=None, serialization_alias="dataAto")
    data_baixa: date | None = Field(default=None, serialization_alias="dataBaixa")
    matches_pessoa: int = Field(default=0, serialization_alias="matchesPessoa")
    matches_guia: int = Field(default=0, serialization_alias="matchesGuia")

    model_config = {"populate_by_name": True}


class DebitoPessoaListResponse(BaseModel):
    items: list[DebitoPessoaItem]
    total: int
