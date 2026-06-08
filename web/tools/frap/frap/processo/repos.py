"""Queries em `processo` — débitos de execução e boletos pagos."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date

import pandas as pd
from sqlalchemy import Engine, bindparam, text

# Caminho de join para casar créditos por boleto:
#
#   Exe_Retorno_Boleto  ⨝  Exe_Boleto         por IdBoleto
#                       ⨝  Exe_DebitoBoleto   por IdBoleto
#                       ⨝  Exe_Debito         por IdDebito
#                       ⨝  Exe_StatusDivida   (lookup)
#
# Caminho para identificar débito por pessoa:
#
#   Exe_Debito          ⨝  Exe_DebitoPessoa   por IdDebito
#                       ⨝  GenPessoa          por IdPessoa


_SQL_DEBITOS_POR_PESSOAS = """
SELECT
    ED.IdDebito,
    ED.IdProcessoExecucao,
    ED.valorOriginalDebito,
    ED.ValorAPagar,
    ED.ValorPago,
    ED.dataAto,
    ED.dataBaixa,
    ED.TipodeBaixa,
    ED.CodigoStatusDivida,
    GP.IdPessoa,
    GP.Documento                          AS DocumentoOriginal,
    REPLACE(REPLACE(REPLACE(REPLACE(
        GP.Documento, '.', ''), '-', ''), '/', ''), ' ', '')
                                          AS Documento,
    GP.Nome                               AS Nome
FROM dbo.Exe_Debito ED
JOIN dbo.Exe_DebitoPessoa EDP ON EDP.IDDebito = ED.IdDebito
JOIN dbo.GenPessoa GP         ON EDP.IDPessoa = GP.IdPessoa
WHERE
    ED.DataCancelamento IS NULL
    AND REPLACE(REPLACE(REPLACE(REPLACE(
        GP.Documento, '.', ''), '-', ''), '/', ''), ' ', '') IN :documentos
"""

_FILTRO_ANOS = " AND YEAR(ED.dataAto) IN :anos"


def debitos_por_pessoas(
    engine: Engine,
    documentos: Iterable[str],
    anos: tuple[int, ...] = (),
) -> pd.DataFrame:
    """Débitos de execução vinculados a pessoas cujo `GenPessoa.Documento` (normalizado
    para só dígitos) está em `documentos`.

    `documentos` deve conter strings com somente dígitos (a normalização é responsabilidade
    do chamador — `extrai_cpfcnpj` já devolve assim).
    """
    docs = tuple({d for d in documentos if d})
    if not docs:
        return pd.DataFrame()

    sql = _SQL_DEBITOS_POR_PESSOAS
    params = {"documentos": docs}
    bindparams = [bindparam("documentos", expanding=True)]

    if anos:
        sql += _FILTRO_ANOS
        params["anos"] = tuple(anos)
        bindparams.append(bindparam("anos", expanding=True))

    stmt = text(sql).bindparams(*bindparams)
    with engine.connect() as conn:
        return pd.read_sql(stmt, conn, params=params)


_SQL_BOLETOS_PAGOS = """
SELECT
    RB.IdBoleto,
    RB.CodigoBarras,
    RB.DataPagamento,
    RB.ValorPago,
    DB.IdDebito,
    ED.IdProcessoExecucao,
    ED.valorOriginalDebito,
    ED.TipodeBaixa,
    GP.Nome                               AS Nome,
    REPLACE(REPLACE(REPLACE(REPLACE(
        GP.Documento, '.', ''), '-', ''), '/', ''), ' ', '')
                                          AS Documento
FROM dbo.Exe_Retorno_Boleto RB
JOIN dbo.Exe_Boleto B         ON B.IdBoleto = RB.IdBoleto
JOIN dbo.Exe_DebitoBoleto DB  ON DB.IdBoleto = B.IdBoleto
JOIN dbo.Exe_Debito ED        ON ED.IdDebito = DB.IdDebito
LEFT JOIN dbo.Exe_DebitoPessoa EDP ON EDP.IDDebito = ED.IdDebito
LEFT JOIN dbo.GenPessoa GP    ON EDP.IDPessoa = GP.IdPessoa
WHERE
    RB.DataPagamento BETWEEN :inicio AND :fim
    AND ED.TipodeBaixa = 1
"""


def boletos_pagos(engine: Engine, inicio: date, fim: date) -> pd.DataFrame:
    """Boletos pagos no intervalo, com FK até `Exe_Debito` (filtra `TipodeBaixa = 1`)."""
    with engine.connect() as conn:
        return pd.read_sql(
            text(_SQL_BOLETOS_PAGOS),
            conn,
            params={"inicio": inicio, "fim": fim},
        )


# Caminho de join do desconto folha (cadastro + parcelas mensais previstas):
#
#   Exe_DescontoFolha  ─→ Exe_Debito          (por IdDebito)
#                      ─→ Exe_Parcelamento    (por IdDebito)
#                      ─→ Exe_Parcela         (por IdParcelamento → N parcelas mensais)
#                      ─→ Exe_DebitoPessoa    (por IdDebito)
#                      ─→ GenPessoa           (por IdPessoa)
#
# Pessoa não está em Exe_DescontoFolha.IdPessoa (sempre NULL nos ativos) — vem
# por Exe_DebitoPessoa, mesmo caminho usado pelo matcher de pessoa.

_SQL_DESCONTOS_FOLHA = """
SELECT
    DF.IdDescontoFolha,
    DF.IdProcesso,
    DF.IdDebito,
    DF.DataInclusao              AS DataInclusaoDesconto,
    DF.Ativo,
    PP.IdParcelamento,
    PP.NumeroParcelas            AS QtdParcelasPlanejadas,
    PP.SituacaoParcelamento,
    EDP.IDPessoa                 AS IdPessoa,
    REPLACE(REPLACE(REPLACE(REPLACE(GP.Documento,'.',''),'-',''),'/',''),' ','') AS CpfCnpj,
    GP.Nome                      AS NomePessoa,
    ED.valorOriginalDebito,
    P.IdParcela,
    P.NumeroParcela,
    P.DataVencimentoParcela,
    P.DataPagamentoParcela,
    P.ValorOriginalParcela,
    P.ValorPago,
    P.SituacaoParcela,
    P.TipoDeBaixa
FROM dbo.Exe_DescontoFolha DF
LEFT JOIN dbo.Exe_Debito         ED  ON ED.IdDebito       = DF.IdDebito
LEFT JOIN dbo.Exe_Parcelamento   PP  ON PP.IdDebito       = DF.IdDebito
LEFT JOIN dbo.Exe_Parcela        P   ON P.IdParcelamento  = PP.IdParcelamento
LEFT JOIN dbo.Exe_DebitoPessoa   EDP ON EDP.IDDebito      = DF.IdDebito
LEFT JOIN dbo.GenPessoa          GP  ON GP.IdPessoa       = EDP.IDPessoa
WHERE DF.Ativo = 1
ORDER BY DF.IdDescontoFolha, P.NumeroParcela
"""


def descontos_folha_cadastrados(engine: Engine) -> pd.DataFrame:
    """Cadastros ativos de desconto em folha + parcelas mensais previstas.

    Retorna formato long: 1 linha por (desconto, parcela). Para descontos sem
    parcela vinculada (parcelamento não criado), retorna 1 linha com colunas
    de parcela em NULL.
    """
    with engine.connect() as conn:
        return pd.read_sql(text(_SQL_DESCONTOS_FOLHA), conn)
