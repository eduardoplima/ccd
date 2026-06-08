from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class DebitoLookupItem(BaseModel):
    matcher: Literal["PESSOA", "GUIA"]
    id_match: int = Field(serialization_alias="idMatch")
    status: str
    status_descricao: str | None = Field(default=None, serialization_alias="statusDescricao")
    conta: str
    periodo: str
    cpfcnpj: str | None = None
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    id_debito: int | None = Field(default=None, serialization_alias="idDebito")
    id_processo_execucao: int | None = Field(
        default=None, serialization_alias="idProcessoExecucao"
    )
    id_boleto: int | None = Field(default=None, serialization_alias="idBoleto")
    codigo_barras: str | None = Field(default=None, serialization_alias="codigoBarras")
    valor_pago: Decimal | None = Field(default=None, serialization_alias="valorPago")
    id_lancamento: int | None = Field(default=None, serialization_alias="idLancamento")
    dt_movimento: date | None = Field(default=None, serialization_alias="dtMovimento")
    valor_lancamento: Decimal | None = Field(default=None, serialization_alias="valorLancamento")

    model_config = {"populate_by_name": True}


class DebitoLookupResponse(BaseModel):
    items: list[DebitoLookupItem]
    total: int
    page: int
    size: int
