"""Queries SIGEF — Ordens Bancárias cujo credor é o FRAP."""
from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import Engine, text

from frap.config import FRAP_CNPJ

# Template SQL aprovado para o match de OB. Roda em BdCargaSigef{ano}.
# Match estrito por (DTPAGAMENTO, VLTOTAL, credor=FRAP). Conta destino do extrato
# (700000-6 / 600000-2) NÃO é filtro: o que define a OB do FRAP é o credor.
SQL_OB_FRAP = """
SELECT
    UGG.CDUNIDADEGESTORATCE         AS CodigoLRF_UGPagadora,
    OB.CDUNIDADEGESTORA,
    OB.CDGESTAO,
    OB.NUORDEMBANCARIA              AS OB_Sigef,
    OB.DTPAGAMENTO                  AS DataPagamento,
    OB.VLTOTAL                      AS ValorOB,
    OB.CDTIPOORDEMBANCARIA          AS TipoOB,
    OB.CDSITUACAOORDEMBANCARIA      AS Situacao,
    OB.DEOBSERVACAO                 AS Observacao,
    DBUG.CDBANCO                    AS BancoOrigem,
    DBUG.CDAGENCIA                  AS AgenciaOrigem,
    DBUG.NUCONTA                    AS ContaOrigem,
    PP.NUPREPARACAOPAGAMENTO        AS PP,
    PP.NUDOCUMENTOORIGINAL          AS DocOriginal,
    PP.NUNOTAEMPENHO                AS Empenho,
    PP.NURETENCAO                   AS Retencao,
    PP.VLPREPARACAOPAGAMENTO        AS ValorPP,
    C.CDCREDOR,
    C.NMCREDOR                      AS Credor,
    C.NUCPF                         AS CredorCPF,
    C.NUCNPJ                        AS CredorCNPJ
FROM
    EFINORDEMBANCARIA OB
    LEFT JOIN EFINPREPARACAOPAGAMENTO PP
           ON PP.CDUNIDADEGESTORAOB = OB.CDUNIDADEGESTORA
          AND PP.CDGESTAOOB         = OB.CDGESTAO
          AND PP.NUORDEMBANCARIA    = OB.NUORDEMBANCARIA
    LEFT JOIN EADMCREDOR C
           ON PP.CDCREDOR = C.CDCREDOR
    LEFT JOIN EADMUGGESTAO UGG
           ON UGG.CDUNIDADEGESTORA = OB.CDUNIDADEGESTORA
          AND UGG.CDGESTAO         = OB.CDGESTAO
    LEFT JOIN EADMDOMICILIOBANCARIOUGGESTAO DBUG
           ON DBUG.CDUNIDADEGESTORA = OB.CDUNIDADEGESTORA
          AND DBUG.CDGESTAO         = OB.CDGESTAO
          AND DBUG.NUSEQDOMICILIO   = OB.NUSEQDOMICILIOUGGESTAO
WHERE
        C.NUCNPJ       = :frap_cnpj
    AND OB.DTPAGAMENTO BETWEEN :inicio AND :fim
ORDER BY
    OB.DTPAGAMENTO, OB.NUORDEMBANCARIA;
"""


def ob_para_frap_periodo(engine: Engine, inicio: date, fim: date) -> pd.DataFrame:
    """OBs do SIGEF cujo credor é o FRAP, pagas entre `inicio` e `fim` (inclusive).

    O `engine` precisa apontar para o banco do ano correspondente
    (use `frap.config.banco_sigef(ano)` + `build_engine(...)`).
    """
    with engine.connect() as conn:
        return pd.read_sql(
            text(SQL_OB_FRAP),
            conn,
            params={"frap_cnpj": FRAP_CNPJ, "inicio": inicio, "fim": fim},
        )
