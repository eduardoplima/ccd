"""Match estrito de OBs (crédito no extrato) contra SIGEF.

Chave de match: (`doc_data`, `valor`) do extrato vs (`DataPagamento`, `ValorOB`)
do SIGEF. Quando a chave tem cardinalidade M:N >1 em ao menos um lado, faz
desempate por ordem cronológica: extrato ordenado por `seq_bb` (autenticação
sequencial diária do BB, 7 últimos dígitos do `documento`) e SIGEF por
`OB_Sigef`. Ambos sobem em ordem monotônica dentro do mesmo dia — validado
empiricamente — então pareamento posição-a-posição é confiável.
"""
from __future__ import annotations

from enum import StrEnum

import pandas as pd

from frap.config import ANOS_SIGEF


class StatusMatchOB(StrEnum):
    EXATO = "EXATO"
    EXATO_POR_ORDEM = "EXATO_POR_ORDEM"   # M:N pareado por seq_bb × OB_Sigef
    AMBIGUO = "AMBIGUO"                   # legado; novos matches não emitem
    SO_EXTRATO = "SO_EXTRATO"             # extrato sem contraparte SIGEF
    SO_SIGEF = "SO_SIGEF"                 # SIGEF sem contraparte no extrato
    SEM_FONTE_SIGEF = "SEM_FONTE_SIGEF"   # ano fora de 2023..2025 (sem carga)


def match_ob(extrato_df: pd.DataFrame, sigef_df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Cruza créditos `OB_RECEBIDA` do extrato com OBs do SIGEF.

    Saída: linhas extrato + colunas SIGEF + `status_match`. Em chave (data, valor)
    com M:N, o pareamento por ordem produz `EXATO_POR_ORDEM`; sobras de qualquer
    lado viram `SO_EXTRATO` ou `SO_SIGEF`.
    """
    if ano not in ANOS_SIGEF:
        sub = _filtra_ob(extrato_df).copy()
        sub["status_match"] = StatusMatchOB.SEM_FONTE_SIGEF.value
        return sub

    extrato_ob = _filtra_ob(extrato_df).copy()

    sigef = sigef_df.copy()
    if not sigef.empty:
        sigef["DataPagamento"] = pd.to_datetime(sigef["DataPagamento"], errors="coerce")
        sigef["ValorOB"] = sigef["ValorOB"].astype(float)

    extrato_cols = list(extrato_ob.columns)
    sigef_cols = [c for c in sigef.columns if c not in extrato_cols]

    chaves: set[tuple] = set()
    if not extrato_ob.empty:
        chaves |= set(zip(extrato_ob["doc_data"], extrato_ob["valor"]))
    if not sigef.empty:
        chaves |= set(zip(sigef["DataPagamento"], sigef["ValorOB"]))

    linhas: list[dict] = []
    for dt, val in chaves:
        lado_ext = (
            extrato_ob[(extrato_ob["doc_data"] == dt) & (extrato_ob["valor"] == val)]
            .sort_values("seq_bb", na_position="last")
            if not extrato_ob.empty else extrato_ob
        )
        lado_sig = (
            sigef[(sigef["DataPagamento"] == dt) & (sigef["ValorOB"] == val)]
            .sort_values("OB_Sigef", na_position="last")
            if not sigef.empty else sigef
        )
        m = min(len(lado_ext), len(lado_sig))
        modo_par = (
            StatusMatchOB.EXATO.value if (m == 1 and len(lado_ext) == 1 and len(lado_sig) == 1)
            else StatusMatchOB.EXATO_POR_ORDEM.value
        )
        for i in range(m):
            d = {c: lado_ext.iloc[i][c] for c in extrato_cols}
            for c in sigef_cols:
                d[c] = lado_sig.iloc[i][c]
            d["status_match"] = modo_par
            linhas.append(d)
        for i in range(m, len(lado_ext)):
            d = {c: lado_ext.iloc[i][c] for c in extrato_cols}
            for c in sigef_cols:
                d[c] = pd.NA
            d["status_match"] = StatusMatchOB.SO_EXTRATO.value
            linhas.append(d)
        for i in range(m, len(lado_sig)):
            d = {c: pd.NA for c in extrato_cols}
            for c in sigef_cols:
                d[c] = lado_sig.iloc[i][c]
            d["status_match"] = StatusMatchOB.SO_SIGEF.value
            linhas.append(d)

    if not linhas:
        return pd.DataFrame(columns=[*extrato_cols, *sigef_cols, "status_match"])
    return pd.DataFrame(linhas)


def _filtra_ob(extrato_df: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas créditos classificados como OB_RECEBIDA."""
    return extrato_df[
        (extrato_df["categoria"] == "OB_RECEBIDA") & (extrato_df["valor_dc"] == "C")
    ]
