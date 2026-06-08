"""Ingestão de pasta MMYYYY.txt → DataFrame canônico."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from frap.extratos import classifica as _classifica, extrator_pessoa, parser

_PERIODO_PATTERN = re.compile(r"^(\d{6})\.txt$")


def ingest_conta(pasta_conta: Path, conta: str) -> pd.DataFrame:
    """Lê todos os MMYYYY.txt de uma pasta-conta e devolve DataFrame canônico."""
    parts: list[pd.DataFrame] = []
    for arquivo in sorted(pasta_conta.glob("*.txt")):
        m = _PERIODO_PATTERN.match(arquivo.name)
        if not m:
            continue
        df = parser.parse_extrato(arquivo)
        if df.empty:
            continue
        df["periodo"] = m.group(1)
        parts.append(df)
    if not parts:
        return pd.DataFrame()

    df = pd.concat(parts, ignore_index=True)
    df["conta"] = conta

    df["dt_movimento"] = pd.to_datetime(df["dt_movimento"], errors="coerce", dayfirst=True)
    df["dt_balancete"] = pd.to_datetime(df["dt_balancete"], errors="coerce", dayfirst=True)
    df["doc_data"] = df["documento"].apply(_extrai_doc_data)
    df["seq_bb"] = df["documento"].apply(_extrai_seq_bb)
    df["categoria"] = df["historico"].apply(lambda h: _classifica.classifica(h).value)

    extracoes = df["descricao"].apply(extrator_pessoa.extrai_cpfcnpj)
    df["cpfcnpj_depositante"] = extracoes.apply(lambda t: t[0])
    df["cpfcnpj_ambiguo"] = extracoes.apply(lambda t: t[1])

    return df


def ingest_pasta(base: Path) -> pd.DataFrame:
    """Itera as subpastas-conta de `base` e devolve um DataFrame canônico consolidado."""
    parts: list[pd.DataFrame] = []
    for conta_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        df = ingest_conta(conta_dir, conta_dir.name)
        if not df.empty:
            parts.append(df)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def _extrai_doc_data(documento: str) -> pd.Timestamp | None:
    """Os 8 primeiros dígitos do `documento` (sem pontos) são YYYYMMDD."""
    if not documento:
        return None
    digitos = "".join(c for c in documento if c.isdigit())
    if len(digitos) < 8:
        return None
    return pd.to_datetime(digitos[:8], format="%Y%m%d", errors="coerce")


def _extrai_seq_bb(documento: str) -> str | None:
    """Últimos 7 dígitos do `documento` BB — autenticação sequencial do dia.
    Usado como chave de desempate quando há M OBs com mesma (data, valor)."""
    if not documento:
        return None
    digitos = "".join(c for c in documento if c.isdigit())
    if len(digitos) < 7:
        return None
    return digitos[-7:]
