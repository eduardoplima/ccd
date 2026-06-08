from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


# ---------- Lista ----------


class MatchResumo(BaseModel):
    matcher: Literal["OB", "PESSOA", "GUIA", "DESCONTO_FOLHA"]
    status: str
    quantidade: int


class LancamentoListItem(BaseModel):
    id_lancamento: int = Field(serialization_alias="idLancamento")
    conta: str
    periodo: str
    dt_movimento: date = Field(serialization_alias="dtMovimento")
    dt_balancete: date | None = Field(default=None, serialization_alias="dtBalancete")
    ag_origem: str | None = Field(default=None, serialization_alias="agOrigem")
    lote: str | None = None
    historico: str
    documento: str | None = None
    doc_data: date | None = Field(default=None, serialization_alias="docData")
    valor: Decimal
    valor_dc: Literal["C", "D"] = Field(serialization_alias="valorDC")
    descricao: str | None = None
    categoria: str
    cpfcnpj_depositante: str | None = Field(default=None, serialization_alias="cpfcnpjDepositante")
    matches_resumo: list[MatchResumo] = Field(
        default_factory=list, serialization_alias="matchesResumo"
    )

    model_config = {"populate_by_name": True}


class LancamentoListResponse(BaseModel):
    items: list[LancamentoListItem]
    total: int
    page: int
    size: int


# ---------- Detalhe ----------


class _MatchBase(BaseModel):
    id_match: int = Field(serialization_alias="idMatch")
    status: str
    status_descricao: str | None = Field(default=None, serialization_alias="statusDescricao")

    model_config = {"populate_by_name": True}


class MatchOB(_MatchBase):
    matcher: Literal["OB"] = "OB"
    ano_sigef: int | None = Field(default=None, serialization_alias="anoSigef")
    cd_unidade_gestora: int | None = Field(default=None, serialization_alias="cdUnidadeGestora")
    cd_gestao: int | None = Field(default=None, serialization_alias="cdGestao")
    nu_ordem_bancaria: str | None = Field(default=None, serialization_alias="nuOrdemBancaria")
    data_pagamento: date | None = Field(default=None, serialization_alias="dataPagamento")
    valor_ob: Decimal | None = Field(default=None, serialization_alias="valorOB")
    cd_credor: str | None = Field(default=None, serialization_alias="cdCredor")
    nm_credor: str | None = Field(default=None, serialization_alias="nmCredor")
    nu_preparacao_pagamento: str | None = Field(
        default=None, serialization_alias="nuPreparacaoPagamento"
    )
    nu_nota_empenho: str | None = Field(default=None, serialization_alias="nuNotaEmpenho")


class MatchPessoa(_MatchBase):
    matcher: Literal["PESSOA"] = "PESSOA"
    id_debito: int | None = Field(default=None, serialization_alias="idDebito")
    id_processo_execucao: int | None = Field(default=None, serialization_alias="idProcessoExecucao")
    cpfcnpj: str | None = None
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    valor_pago: Decimal | None = Field(default=None, serialization_alias="valorPago")
    valor_a_pagar: Decimal | None = Field(default=None, serialization_alias="valorAPagar")
    valor_original_debito: Decimal | None = Field(
        default=None, serialization_alias="valorOriginalDebito"
    )
    valor_casado_em: str | None = Field(default=None, serialization_alias="valorCasadoEm")


class MatchGuia(_MatchBase):
    matcher: Literal["GUIA"] = "GUIA"
    id_boleto: int | None = Field(default=None, serialization_alias="idBoleto")
    id_debito: int | None = Field(default=None, serialization_alias="idDebito")
    id_processo_execucao: int | None = Field(default=None, serialization_alias="idProcessoExecucao")
    codigo_barras: str | None = Field(default=None, serialization_alias="codigoBarras")
    data_pagamento: date | None = Field(default=None, serialization_alias="dataPagamento")
    valor_pago: Decimal | None = Field(default=None, serialization_alias="valorPago")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    cpfcnpj: str | None = None


class MatchDescontoFolha(_MatchBase):
    matcher: Literal["DESCONTO_FOLHA"] = "DESCONTO_FOLHA"
    id_parcela: int | None = Field(default=None, serialization_alias="idParcela")
    numero_parcela: int | None = Field(default=None, serialization_alias="numeroParcela")
    mes_referencia: int | None = Field(default=None, serialization_alias="mesReferencia")
    ano_referencia: int | None = Field(default=None, serialization_alias="anoReferencia")
    valor_esperado: Decimal | None = Field(default=None, serialization_alias="valorEsperado")
    cpfcnpj: str | None = None
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    id_contracheque_item: int | None = Field(default=None, serialization_alias="idContrachequeItem")
    valor_contracheque: Decimal | None = Field(
        default=None, serialization_alias="valorContracheque"
    )


Match = Annotated[
    Union[MatchOB, MatchPessoa, MatchGuia, MatchDescontoFolha],
    Field(discriminator="matcher"),
]


class LancamentoDetail(BaseModel):
    id_lancamento: int = Field(serialization_alias="idLancamento")
    conta: str
    periodo: str
    dt_movimento: date = Field(serialization_alias="dtMovimento")
    dt_balancete: date | None = Field(default=None, serialization_alias="dtBalancete")
    ag_origem: str | None = Field(default=None, serialization_alias="agOrigem")
    lote: str | None = None
    historico: str
    documento: str | None = None
    doc_data: date | None = Field(default=None, serialization_alias="docData")
    valor: Decimal
    valor_dc: Literal["C", "D"] = Field(serialization_alias="valorDC")
    descricao: str | None = None
    categoria: str
    cpfcnpj_depositante: str | None = Field(default=None, serialization_alias="cpfcnpjDepositante")
    cpfcnpj_ambiguo: bool = Field(serialization_alias="cpfcnpjAmbiguo")
    nome_arquivo: str | None = Field(default=None, serialization_alias="nomeArquivo")
    matches: list[Match] = Field(default_factory=list)

    model_config = {"populate_by_name": True}
