from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class _Common(BaseModel):
    id_match: int = Field(serialization_alias="idMatch")
    status: str
    status_descricao: str | None = Field(default=None, serialization_alias="statusDescricao")
    conta: str
    periodo: str

    model_config = {"populate_by_name": True}


class _LancamentoCtx(BaseModel):
    id_lancamento: int | None = Field(default=None, serialization_alias="idLancamento")
    dt_movimento: date | None = Field(default=None, serialization_alias="dtMovimento")
    valor_lancamento: Decimal | None = Field(default=None, serialization_alias="valorLancamento")
    valor_dc: str | None = Field(default=None, serialization_alias="valorDC")
    historico: str | None = None
    documento_extrato: str | None = Field(default=None, serialization_alias="documentoExtrato")


class MatchOBListItem(_Common, _LancamentoCtx):
    matcher: Literal["OB"] = "OB"
    ano_sigef: int = Field(serialization_alias="anoSigef")
    nu_ordem_bancaria: str | None = Field(default=None, serialization_alias="nuOrdemBancaria")
    cd_unidade_gestora: int | None = Field(default=None, serialization_alias="cdUnidadeGestora")
    data_pagamento: date | None = Field(default=None, serialization_alias="dataPagamento")
    valor_ob: Decimal | None = Field(default=None, serialization_alias="valorOB")
    cd_credor: str | None = Field(default=None, serialization_alias="cdCredor")
    nm_credor: str | None = Field(default=None, serialization_alias="nmCredor")


class MatchPessoaListItem(_Common, _LancamentoCtx):
    matcher: Literal["PESSOA"] = "PESSOA"
    id_debito: int | None = Field(default=None, serialization_alias="idDebito")
    cpfcnpj: str | None = None
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    valor_pago: Decimal | None = Field(default=None, serialization_alias="valorPago")
    valor_a_pagar: Decimal | None = Field(default=None, serialization_alias="valorAPagar")
    valor_casado_em: str | None = Field(default=None, serialization_alias="valorCasadoEm")


class MatchGuiaListItem(_Common, _LancamentoCtx):
    matcher: Literal["GUIA"] = "GUIA"
    id_boleto: int | None = Field(default=None, serialization_alias="idBoleto")
    id_debito: int | None = Field(default=None, serialization_alias="idDebito")
    codigo_barras: str | None = Field(default=None, serialization_alias="codigoBarras")
    data_pagamento: date | None = Field(default=None, serialization_alias="dataPagamento")
    valor_pago: Decimal | None = Field(default=None, serialization_alias="valorPago")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    cpfcnpj: str | None = None


class MatchDescontoFolhaListItem(BaseModel):
    matcher: Literal["DESCONTO_FOLHA"] = "DESCONTO_FOLHA"
    id_match: int = Field(serialization_alias="idMatch")
    status: str
    status_descricao: str | None = Field(default=None, serialization_alias="statusDescricao")
    id_parcela: int | None = Field(default=None, serialization_alias="idParcela")
    numero_parcela: int | None = Field(default=None, serialization_alias="numeroParcela")
    mes_referencia: int | None = Field(default=None, serialization_alias="mesReferencia")
    ano_referencia: int | None = Field(default=None, serialization_alias="anoReferencia")
    valor_esperado: Decimal | None = Field(default=None, serialization_alias="valorEsperado")
    cpfcnpj: str | None = None
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    valor_contracheque: Decimal | None = Field(
        default=None, serialization_alias="valorContracheque"
    )
    id_lancamento: int | None = Field(default=None, serialization_alias="idLancamento")
    dt_movimento: date | None = Field(default=None, serialization_alias="dtMovimento")
    valor_lancamento: Decimal | None = Field(default=None, serialization_alias="valorLancamento")

    model_config = {"populate_by_name": True}


class MatchOBListResponse(BaseModel):
    items: list[MatchOBListItem]
    total: int
    page: int
    size: int


class MatchPessoaListResponse(BaseModel):
    items: list[MatchPessoaListItem]
    total: int
    page: int
    size: int


class MatchGuiaListResponse(BaseModel):
    items: list[MatchGuiaListItem]
    total: int
    page: int
    size: int


class MatchDescontoFolhaListResponse(BaseModel):
    items: list[MatchDescontoFolhaListItem]
    total: int
    page: int
    size: int
