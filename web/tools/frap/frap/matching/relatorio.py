"""Consolida resultados dos matchers em um Excel multi-aba."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# Status que contam como "conciliado de fato" para fins de identificar
# o complemento (créditos não conciliados).
_EXATOS = {
    "EXATO",
    "EXATO_POR_ORDEM",
    "EXATO_PESSOA_VALOR",
    "EXATO_LOTE",
}
_AMBIGUOS = {"AMBIGUO", "AMBIGUO_PESSOA"}

# Categorias que não vão para "nao_conciliados" porque não geram contrapartida
# externa por design (saldo informativo, aplicação automática).
_CATEGORIAS_INFORMATIVAS = {"SALDO", "APLICACAO_RESGATE"}

# Chave usada para identificar um lançamento do extrato em qualquer matcher.
_CHAVE_LANC = ("conta", "periodo", "valor", "documento")


def relatorio_mensal(
    matches_ob: pd.DataFrame,
    matches_pessoa: pd.DataFrame,
    matches_guia: pd.DataFrame,
    extrato: pd.DataFrame,
    destino: Path,
) -> Path:
    """Gera Excel multi-aba com a conciliação consolidada.

    Abas:
      - `resumo`: contagem por status em cada matcher.
      - `ob_status`, `pessoa_status`, `guia_status`: detalhe linha-a-linha.
      - `nao_conciliados`: créditos do extrato que nenhum matcher fechou (fora as
        categorias informativas como SALDO/APLICACAO_RESGATE).
      - `ambiguos`: candidatos múltiplos para revisão manual, vindos de qualquer matcher.
    """
    resumo = _resumo([
        ("ob", matches_ob),
        ("pessoa", matches_pessoa),
        ("guia", matches_guia),
    ])

    chaves_conciliadas = _chaves_exatas([matches_ob, matches_pessoa, matches_guia])
    nao_conciliados = _nao_conciliados(extrato, chaves_conciliadas)
    ambiguos = _ambiguos([
        ("ob", matches_ob),
        ("pessoa", matches_pessoa),
        ("guia", matches_guia),
    ])

    destino.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(destino, engine="openpyxl") as writer:
        resumo.to_excel(writer, sheet_name="resumo")
        _to_sheet(matches_ob, writer, "ob_status")
        _to_sheet(matches_pessoa, writer, "pessoa_status")
        _to_sheet(matches_guia, writer, "guia_status")
        _to_sheet(nao_conciliados, writer, "nao_conciliados")
        _to_sheet(ambiguos, writer, "ambiguos")

    return destino


def _resumo(pares: list[tuple[str, pd.DataFrame]]) -> pd.DataFrame:
    series = {}
    for nome, df in pares:
        if df.empty or "status_match" not in df.columns:
            series[nome] = pd.Series(dtype=int)
        else:
            series[nome] = df["status_match"].value_counts()
    return pd.DataFrame(series).fillna(0).astype(int)


def _chaves_exatas(matches: list[pd.DataFrame]) -> set[tuple]:
    chaves: set[tuple] = set()
    for df in matches:
        if df.empty or "status_match" not in df.columns:
            continue
        ok = df[df["status_match"].isin(_EXATOS)]
        for _, row in ok.iterrows():
            chave = tuple(row.get(c) for c in _CHAVE_LANC)
            chaves.add(chave)
    return chaves


def _nao_conciliados(extrato: pd.DataFrame, chaves_ok: set[tuple]) -> pd.DataFrame:
    if extrato.empty:
        return extrato

    creditos = extrato[
        (extrato["valor_dc"] == "C") & (~extrato["categoria"].isin(_CATEGORIAS_INFORMATIVAS))
    ].copy()
    if creditos.empty:
        return creditos

    chaves = creditos[list(_CHAVE_LANC)].apply(tuple, axis=1)
    return creditos[~chaves.isin(chaves_ok)]


def _ambiguos(pares: list[tuple[str, pd.DataFrame]]) -> pd.DataFrame:
    parts = []
    for nome, df in pares:
        if df.empty or "status_match" not in df.columns:
            continue
        sub = df[df["status_match"].isin(_AMBIGUOS)].copy()
        if sub.empty:
            continue
        sub.insert(0, "_matcher", nome)
        parts.append(sub)
    if not parts:
        return pd.DataFrame(columns=["_matcher", "status_match"])
    return pd.concat(parts, ignore_index=True)


def _to_sheet(df: pd.DataFrame, writer: pd.ExcelWriter, sheet: str) -> None:
    """`pandas.to_excel` não lida bem com DataFrame totalmente vazio — escrevemos
    uma aba placeholder neste caso, para o arquivo não ficar quebrado."""
    if df is None or df.empty:
        pd.DataFrame({"info": ["sem linhas"]}).to_excel(writer, sheet_name=sheet, index=False)
        return
    df.to_excel(writer, sheet_name=sheet, index=False)
