"""Match de créditos do extrato com Exe_Debito via CPF/CNPJ do depositante."""
from __future__ import annotations

from enum import StrEnum

import pandas as pd


class StatusMatchPessoa(StrEnum):
    EXATO_PESSOA_VALOR = "EXATO_PESSOA_VALOR"  # 1 débito da mesma pessoa cujo valor casa
    AMBIGUO_PESSOA = "AMBIGUO_PESSOA"          # >1 débito casando
    SO_PESSOA = "SO_PESSOA"                    # cpfcnpj bate, mas nenhum valor casa
    SO_EXTRATO = "SO_EXTRATO"                  # cpfcnpj não aparece em débito


_VALOR_CAMPOS = ("ValorPago", "ValorAPagar", "valorOriginalDebito")
_TOLERANCIA = 0.005  # meio centavo


def match_pessoa(extrato_df: pd.DataFrame, debitos_df: pd.DataFrame) -> pd.DataFrame:
    """Cruza créditos do extrato com `dbo.Exe_Debito` quando o `cpfcnpj_depositante`
    do extrato coincide com `GenPessoa.Documento`.

    Match em duas etapas:
      1. Equi-join por `cpfcnpj_depositante == Documento`.
      2. Considera casado se `extrato.valor` bater com **pelo menos um** de
         {`ValorPago`, `ValorAPagar`, `valorOriginalDebito`} (tolerância de meio centavo).
         A coluna `valor_casado_em` (lista) registra qual(is) campo(s) bateram.

    Saída: linhas do extrato + colunas do débito candidato + `valor_casado_em` + `status_match`.
    """
    extrato = _filtra_extrato(extrato_df).copy()
    debitos = debitos_df.copy() if not debitos_df.empty else debitos_df

    if extrato.empty:
        return _vazio()

    if debitos.empty:
        extrato["status_match"] = StatusMatchPessoa.SO_EXTRATO.value
        extrato["valor_casado_em"] = [[] for _ in range(len(extrato))]
        return extrato

    debitos["Documento"] = debitos["Documento"].astype(str)
    for col in _VALOR_CAMPOS:
        if col in debitos.columns:
            debitos[col] = pd.to_numeric(debitos[col], errors="coerce")

    extrato["cpfcnpj_depositante"] = extrato["cpfcnpj_depositante"].astype(str)

    # 1) Equi-join por documento — preserva linhas-extrato sem candidata via outer.
    merged = extrato.merge(
        debitos,
        how="left",
        left_on="cpfcnpj_depositante",
        right_on="Documento",
        suffixes=("", "_debito"),
        indicator=True,
    )

    # 2) Para cada linha mesclada com candidata, calcula campos de valor que bateram.
    merged["valor_casado_em"] = merged.apply(_campos_que_batem, axis=1)
    merged["__valor_casa"] = merged["valor_casado_em"].apply(bool)

    # 3) Constrói status linha-a-linha.
    merged["status_match"] = ""
    merged.loc[merged["_merge"] == "left_only", "status_match"] = StatusMatchPessoa.SO_EXTRATO.value

    candidatos_validos = merged[(merged["_merge"] == "both") & (merged["__valor_casa"])]
    contagem = candidatos_validos.groupby("cpfcnpj_depositante").size()

    def _status_pessoa(row: pd.Series) -> str:
        if row["_merge"] == "left_only":
            return StatusMatchPessoa.SO_EXTRATO.value
        if not row["__valor_casa"]:
            return StatusMatchPessoa.SO_PESSOA.value
        n = int(contagem.get(row["cpfcnpj_depositante"], 0))
        return (
            StatusMatchPessoa.EXATO_PESSOA_VALOR.value
            if n == 1
            else StatusMatchPessoa.AMBIGUO_PESSOA.value
        )

    merged["status_match"] = merged.apply(_status_pessoa, axis=1)

    return merged.drop(columns=["_merge", "__valor_casa"])


def _campos_que_batem(row: pd.Series) -> list[str]:
    """Lista os nomes dos campos de valor do débito que batem com `row.valor`."""
    if row.get("_merge") == "left_only":
        return []
    valor_extrato = row["valor"]
    if pd.isna(valor_extrato):
        return []
    casados: list[str] = []
    for col in _VALOR_CAMPOS:
        v = row.get(col)
        if v is not None and not pd.isna(v) and abs(float(v) - float(valor_extrato)) <= _TOLERANCIA:
            casados.append(col)
    return casados


def _filtra_extrato(extrato_df: pd.DataFrame) -> pd.DataFrame:
    """Mantém apenas créditos com cpfcnpj_depositante extraído."""
    if extrato_df.empty:
        return extrato_df
    return extrato_df[
        (extrato_df["valor_dc"] == "C")
        & (extrato_df["cpfcnpj_depositante"].notna())
        & (extrato_df["cpfcnpj_depositante"].astype(str) != "")
    ]


def _vazio() -> pd.DataFrame:
    return pd.DataFrame(columns=["status_match", "valor_casado_em"])
