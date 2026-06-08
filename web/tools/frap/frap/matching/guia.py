"""Match de créditos GUIA_RECEBIMENTO contra `Exe_Retorno_Boleto` por lote diário.

Regra real: cada crédito do extrato em D corresponde à **soma diária** de N boletos
pagos pelo cidadão em D-X (tipicamente D-1 ou D-2). O documento `documento` do
extrato é só um lote bancário (~6 dígitos), não bate com `RB.CodigoBarras` (44
dígitos), então o match é feito por `(soma_dia, dt_movimento - X dias)`.

Algoritmo:
  1. Computa `diaria[dpag] = sum(ValorPago)` agrupado por `DataPagamento`.
  2. Para cada crédito GUIA em ordem cronológica, procura `dpag` em
     `D, D-1, ..., D-janela_dias` cuja `diaria[dpag]` seja igual a `valor`.
     Pega a **primeira** (mais próxima) e marca a `dpag` como consumida.
  3. Para a `dpag` casada, emite **N linhas** (uma por boleto naquele dia)
     com `status=EXATO_LOTE` — todas compartilhando o mesmo lançamento.
  4. Crédito sem casamento → `SO_EXTRATO`. Boleto cuja `dpag` não foi
     consumida → `SO_PROCESSO`.
"""
from __future__ import annotations

from enum import StrEnum

import pandas as pd


class StatusMatchGuia(StrEnum):
    EXATO_LOTE = "EXATO_LOTE"     # soma diária de boletos em D-X = valor do crédito em D
    SO_EXTRATO = "SO_EXTRATO"     # crédito sem lote casando na janela
    SO_PROCESSO = "SO_PROCESSO"   # boleto pago cujo dia de pagamento não casou nenhum crédito


def match_guia(
    extrato_df: pd.DataFrame,
    retorno_boleto_df: pd.DataFrame,
    janela_dias: int = 5,
) -> pd.DataFrame:
    """Cruza créditos GUIA_RECEBIMENTO com boletos pagos pela regra do lote diário.

    `janela_dias` controla quantos dias para trás a partir de `dt_movimento` o
    matcher procura uma `dpag` candidata. Empiricamente 75% dos casos casam em
    D ou D-1; janela=5 cobre a vasta maioria.
    """
    extrato = _filtra_extrato(extrato_df)
    rb = retorno_boleto_df.copy() if not retorno_boleto_df.empty else retorno_boleto_df

    if extrato.empty and rb.empty:
        return pd.DataFrame(columns=["status_match"])

    if not rb.empty:
        rb["DataPagamento"] = pd.to_datetime(rb["DataPagamento"]).dt.normalize()
        rb["ValorPago"] = pd.to_numeric(rb["ValorPago"], errors="coerce")
        diaria = rb.groupby("DataPagamento")["ValorPago"].sum().to_dict()
    else:
        diaria = {}

    if not extrato.empty:
        extrato = extrato.sort_values("dt_movimento").reset_index(drop=True)
        extrato["dt_movimento"] = pd.to_datetime(extrato["dt_movimento"]).dt.normalize()

    rows: list[dict] = []
    dpag_consumida: set = set()

    for _, ex in extrato.iterrows():
        dt_mov = ex["dt_movimento"]
        valor = float(ex["valor"])
        encontrou = None
        for delta in range(0, janela_dias + 1):
            dpag = dt_mov - pd.Timedelta(days=delta)
            if dpag in dpag_consumida:
                continue
            soma = diaria.get(dpag)
            if soma is not None and abs(float(soma) - valor) < 0.005:
                encontrou = dpag
                break

        if encontrou is None:
            row = ex.to_dict()
            row["status_match"] = StatusMatchGuia.SO_EXTRATO.value
            rows.append(row)
        else:
            dpag_consumida.add(encontrou)
            boletos_lote = rb[rb["DataPagamento"] == encontrou]
            for _, b in boletos_lote.iterrows():
                row = ex.to_dict()
                for col, val in b.items():
                    row[col] = val
                row["status_match"] = StatusMatchGuia.EXATO_LOTE.value
                rows.append(row)

    if not rb.empty:
        sobras = rb[~rb["DataPagamento"].isin(dpag_consumida)]
        for _, b in sobras.iterrows():
            row = b.to_dict()
            row["status_match"] = StatusMatchGuia.SO_PROCESSO.value
            rows.append(row)

    return pd.DataFrame(rows)


def _filtra_extrato(extrato_df: pd.DataFrame) -> pd.DataFrame:
    if extrato_df.empty:
        return extrato_df
    return extrato_df[
        (extrato_df["categoria"] == "GUIA_RECEBIMENTO") & (extrato_df["valor_dc"] == "C")
    ]
