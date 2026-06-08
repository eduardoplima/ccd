"""Queries SIGEF Oracle — OBs cujo credor é o FRAP ou o TCE-RN.

SIGEF de anos 2026+ está em Oracle (host TCE-RN, instância `sigef`). Schemas
por ano (`SIGEF2026`, `SIGEF2027`, ...) com as tabelas operacionais. A tabela
de credores (`EADMCREDOR`) é global no schema `SIGEF`.
"""
from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import Engine, text

from frap.config import FRAP_CNPJ, TCE_CNPJ


def _sql_ob_frap_ou_tce(schema_ano: str) -> str:
    return f"""
SELECT
    UGG.CDUNIDADEGESTORATCE       AS CodigoLRF_UGPagadora,
    UN.NMUNIDADEGESTORA           AS UGNome,
    OB.CDUNIDADEGESTORA,
    OB.CDGESTAO,
    OB.NUORDEMBANCARIA            AS OB_Sigef,
    OB.DTPAGAMENTO                AS DataPagamento,
    OB.VLTOTAL                    AS ValorOB,
    OB.CDTIPOORDEMBANCARIA        AS TipoOB,
    OB.CDSITUACAOORDEMBANCARIA    AS Situacao,
    OB.DEOBSERVACAO               AS Observacao,
    DBUG.CDBANCO                  AS BancoOrigem,
    DBUG.CDAGENCIA                AS AgenciaOrigem,
    DBUG.NUCONTA                  AS ContaOrigem,
    PP.NUPREPARACAOPAGAMENTO      AS PP,
    PP.NUDOCUMENTOORIGINAL        AS DocOriginal,
    PP.NUNOTAEMPENHO              AS Empenho,
    PP.NURETENCAO                 AS Retencao,
    PP.VLPREPARACAOPAGAMENTO      AS ValorPP,
    C.CDCREDOR,
    C.NMCREDOR                    AS Credor,
    C.NUCPF                       AS CredorCPF,
    C.NUCNPJ                      AS CredorCNPJ,
    CASE C.NUCNPJ
        WHEN :frap_cnpj THEN 'FRAP'
        WHEN :tce_cnpj  THEN 'TCE'
    END                           AS CredorTipo
FROM {schema_ano}.EFINORDEMBANCARIA OB
LEFT JOIN {schema_ano}.EFINPREPARACAOPAGAMENTO PP
       ON PP.CDUNIDADEGESTORAOB = OB.CDUNIDADEGESTORA
      AND PP.CDGESTAOOB         = OB.CDGESTAO
      AND PP.NUORDEMBANCARIA    = OB.NUORDEMBANCARIA
LEFT JOIN SIGEF.EADMCREDOR C
       ON PP.CDCREDOR = C.CDCREDOR
LEFT JOIN {schema_ano}.EADMUGGESTAO UGG
       ON UGG.CDUNIDADEGESTORA = OB.CDUNIDADEGESTORA
      AND UGG.CDGESTAO         = OB.CDGESTAO
LEFT JOIN {schema_ano}.EADMUNIDADEGESTORA UN
       ON UN.CDUNIDADEGESTORA = OB.CDUNIDADEGESTORA
LEFT JOIN {schema_ano}.EADMDOMICILIOBANCARIOUGGESTAO DBUG
       ON DBUG.CDUNIDADEGESTORA = OB.CDUNIDADEGESTORA
      AND DBUG.CDGESTAO         = OB.CDGESTAO
      AND DBUG.NUSEQDOMICILIO   = OB.NUSEQDOMICILIOUGGESTAO
WHERE C.NUCNPJ IN (:frap_cnpj, :tce_cnpj)
  AND OB.DTPAGAMENTO BETWEEN :inicio AND :fim
ORDER BY OB.DTPAGAMENTO, OB.NUORDEMBANCARIA
"""


def schema_sigef_oracle(ano: int) -> str:
    return f"SIGEF{ano}"


def ob_para_frap_ou_tce_periodo(
    engine: Engine, inicio: date, fim: date, ano: int | None = None
) -> pd.DataFrame:
    """OBs do SIGEF Oracle cujo credor é FRAP ou TCE-RN, pagas entre inicio e fim.

    Uma OB com múltiplas PPs aparece em múltiplas linhas (uma por PP). Para
    cruzamento em nível de OB, agrupar por OB_Sigef em pandas.
    """
    schema = schema_sigef_oracle(ano or inicio.year)
    with engine.connect() as conn:
        df = pd.read_sql(
            text(_sql_ob_frap_ou_tce(schema)),
            conn,
            params={"frap_cnpj": FRAP_CNPJ, "tce_cnpj": TCE_CNPJ, "inicio": inicio, "fim": fim},
        )
    rename = {
        "codigolrf_ugpagadora": "CodigoLRF_UGPagadora",
        "ugnome": "UGNome",
        "cdunidadegestora": "CDUnidadeGestora",
        "cdgestao": "CDGestao",
        "ob_sigef": "OB_Sigef",
        "datapagamento": "DataPagamento",
        "valorob": "ValorOB",
        "tipoob": "TipoOB",
        "situacao": "Situacao",
        "observacao": "Observacao",
        "bancoorigem": "BancoOrigem",
        "agenciaorigem": "AgenciaOrigem",
        "contaorigem": "ContaOrigem",
        "pp": "PP",
        "docoriginal": "DocOriginal",
        "empenho": "Empenho",
        "retencao": "Retencao",
        "valorpp": "ValorPP",
        "cdcredor": "CDCredor",
        "credor": "Credor",
        "credorcpf": "CredorCPF",
        "credorcnpj": "CredorCNPJ",
        "credortipo": "CredorTipo",
    }
    return df.rename(columns=rename)
