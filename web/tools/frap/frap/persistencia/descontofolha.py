"""Persistência de FRAPDescontoFolha + FRAPDescontoFolhaParcela + FRAPMatchDescontoFolha.

Estratégia: substituição por desconto (atomicidade do desconto+parcelas) e
substituição por mês/ano nos matches.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import Engine, text

# ---------------------------------------------------------------------------
# Cadastro: FRAPDescontoFolha + FRAPDescontoFolhaParcela
# ---------------------------------------------------------------------------

_SQL_UPSERT_DESCONTO = """
MERGE dbo.FRAPDescontoFolha AS tgt
USING (SELECT :id_desconto_folha AS IdDescontoFolha) AS src
ON tgt.IdDescontoFolha = src.IdDescontoFolha
WHEN MATCHED THEN
    UPDATE SET
        Origem                 = 'P',
        IdProcesso             = :id_processo,
        IdDebito               = :id_debito,
        IdParcelamento         = :id_parcelamento,
        IdPessoa               = :id_pessoa,
        CpfCnpj                = :cpfcnpj,
        NomePessoa             = :nome_pessoa,
        QtdParcelasPlanejadas  = :qtd_parcelas,
        ValorTotalEsperado     = :valor_total,
        SituacaoParcelamento   = :situacao_parcelamento,
        Ativo                  = :ativo,
        DataInclusao           = :data_inclusao,
        DataIngestao           = SYSUTCDATETIME()
WHEN NOT MATCHED THEN
    INSERT (IdDescontoFolha, Origem, IdProcesso, IdDebito, IdParcelamento, IdPessoa,
            CpfCnpj, NomePessoa, QtdParcelasPlanejadas, ValorTotalEsperado,
            SituacaoParcelamento, Ativo, DataInclusao)
    VALUES (:id_desconto_folha, 'P', :id_processo, :id_debito, :id_parcelamento, :id_pessoa,
            :cpfcnpj, :nome_pessoa, :qtd_parcelas, :valor_total,
            :situacao_parcelamento, :ativo, :data_inclusao)
OUTPUT inserted.IdFRAPDescontoFolha;
"""

_SQL_DELETE_PARCELAS = (
    "DELETE FROM dbo.FRAPDescontoFolhaParcela WHERE IdFRAPDescontoFolha = :id_pai;"
)

_SQL_INSERT_PARCELA = """
INSERT INTO dbo.FRAPDescontoFolhaParcela
    (IdFRAPDescontoFolha, IdParcela, NumeroParcela, MesReferencia, AnoReferencia,
     ValorEsperado, DataVencimento, DataPagamentoParcela, SituacaoParcela, TipoDeBaixa)
VALUES
    (:id_pai, :id_parcela, :numero_parcela, :mes, :ano,
     :valor, :dt_venc, :dt_pgto, :situacao, :tipo_baixa);
"""


def publica_desconto_folha(engine: Engine, df: pd.DataFrame) -> dict[int, int]:
    """Publica cadastro + parcelas. `df` é o long format de descontos_folha_cadastrados.

    Retorna mapa `{IdDescontoFolha: IdFRAPDescontoFolha}` para uso posterior.
    """
    if df.empty:
        return {}

    mapa: dict[int, int] = {}
    df = df.copy()

    with engine.begin() as conn:
        for id_df, grupo in df.groupby("IdDescontoFolha", sort=True):
            cabeca = grupo.iloc[0]
            id_pai = conn.execute(
                text(_SQL_UPSERT_DESCONTO),
                {
                    "id_desconto_folha": int(id_df),
                    "id_processo": _int_or_none(cabeca.get("IdProcesso")),
                    "id_debito": _int_or_none(cabeca.get("IdDebito")),
                    "id_parcelamento": _int_or_none(cabeca.get("IdParcelamento")),
                    "id_pessoa": _int_or_none(cabeca.get("IdPessoa")),
                    "cpfcnpj": _str_or_none(cabeca.get("CpfCnpj")),
                    "nome_pessoa": _str_or_none(cabeca.get("NomePessoa")),
                    "qtd_parcelas": _int_or_none(cabeca.get("QtdParcelasPlanejadas")),
                    "valor_total": _float_or_none(cabeca.get("valorOriginalDebito")),
                    "situacao_parcelamento": _str_or_none(cabeca.get("SituacaoParcelamento")),
                    "ativo": bool(cabeca.get("Ativo", True)),
                    "data_inclusao": _date(cabeca.get("DataInclusaoDesconto")),
                },
            ).scalar_one()
            mapa[int(id_df)] = int(id_pai)

            conn.execute(text(_SQL_DELETE_PARCELAS), {"id_pai": int(id_pai)})
            parcelas = grupo[grupo["NumeroParcela"].notna()]
            if parcelas.empty:
                continue
            params = []
            for _, p in parcelas.iterrows():
                dt_venc = _date(p.get("DataVencimentoParcela"))
                if dt_venc is None:
                    continue
                params.append(
                    {
                        "id_pai": int(id_pai),
                        "id_parcela": _int_or_none(p.get("IdParcela")),
                        "numero_parcela": int(p["NumeroParcela"]),
                        "mes": int(dt_venc.month),
                        "ano": int(dt_venc.year),
                        "valor": float(p.get("ValorOriginalParcela") or 0),
                        "dt_venc": dt_venc,
                        "dt_pgto": _date(p.get("DataPagamentoParcela")),
                        "situacao": _str_or_none(p.get("SituacaoParcela")),
                        "tipo_baixa": _int_or_none(p.get("TipoDeBaixa")),
                    }
                )
            if params:
                conn.execute(text(_SQL_INSERT_PARCELA), params)

    return mapa


# ---------------------------------------------------------------------------
# Match: FRAPMatchDescontoFolha (substituição por mês/ano)
# ---------------------------------------------------------------------------

_SQL_DELETE_MATCH = """
DELETE M FROM dbo.FRAPMatchDescontoFolha M
JOIN dbo.FRAPDescontoFolhaParcela P ON P.IdFRAPDescontoFolhaParcela = M.IdFRAPDescontoFolhaParcela
WHERE P.MesReferencia = :mes AND P.AnoReferencia = :ano AND M.IsManual = 0;
"""

_SQL_INSERT_MATCH = """
INSERT INTO dbo.FRAPMatchDescontoFolha
    (IdFRAPDescontoFolhaParcela, IdContraChequeItem, IdRubrica, ValorContracheque,
     IdLancamentoFRAP, IdStatusMatch)
VALUES
    (:id_parcela, :id_cci, :id_rubrica, :valor_cc, :id_lanc, :id_status);
"""


def publica_match_desconto_folha(
    engine: Engine,
    df: pd.DataFrame,
    mes: int,
    ano: int,
    id_status_por_codigo: dict[str, int],
) -> int:
    """Substitui o match de DESCONTO_FOLHA do mês/ano. `id_status_por_codigo` mapeia
    `status_match` -> `IdStatusMatch` (resolver via lookup antes de chamar).
    """
    with engine.begin() as conn:
        conn.execute(text(_SQL_DELETE_MATCH), {"mes": int(mes), "ano": int(ano)})
        if df.empty:
            return 0
        params = []
        for _, r in df.iterrows():
            params.append(
                {
                    "id_parcela": int(r["IdFRAPDescontoFolhaParcela"]),
                    "id_cci": _int_or_none(r.get("IdContraChequeItem")),
                    "id_rubrica": _int_or_none(r.get("IdRubrica")),
                    "valor_cc": _float_or_none(r.get("ValorContracheque")),
                    "id_lanc": _int_or_none(r.get("IdLancamentoFRAP")),
                    "id_status": int(id_status_por_codigo[str(r["status_match"])]),
                }
            )
        conn.execute(text(_SQL_INSERT_MATCH), params)
        return len(params)


# ---------------------------------------------------------------------------


def _int_or_none(v):
    if v is None or pd.isna(v):
        return None
    return int(v)


def _float_or_none(v):
    if v is None or pd.isna(v):
        return None
    return float(v)


def _str_or_none(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None


def _date(v):
    if v is None or pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.date()
    return v
