"""Resolução de ids dos lookups FRAPConta, FRAPCategoria, FRAPStatusMatch.

Os lookups são pequenos e estáveis dentro de uma conexão — fazemos uma única
query por engine e mantemos os mapas em memória.
"""
from __future__ import annotations

from functools import lru_cache

import pandas as pd
from sqlalchemy import Engine, text


@lru_cache(maxsize=8)
def _mapa_conta(engine: Engine) -> dict[str, int]:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT IdConta, Conta FROM dbo.FRAPConta"), conn)
    return dict(zip(df["Conta"].astype(str), df["IdConta"].astype(int)))


@lru_cache(maxsize=8)
def _mapa_categoria(engine: Engine) -> dict[str, int]:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT IdCategoria, Codigo FROM dbo.FRAPCategoria"), conn)
    return dict(zip(df["Codigo"].astype(str), df["IdCategoria"].astype(int)))


@lru_cache(maxsize=8)
def _mapa_status(engine: Engine) -> dict[tuple[str, str], int]:
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT IdStatusMatch, Matcher, Codigo FROM dbo.FRAPStatusMatch"),
            conn,
        )
    return {
        (str(row["Matcher"]), str(row["Codigo"])): int(row["IdStatusMatch"])
        for _, row in df.iterrows()
    }


def get_id_conta(engine: Engine, conta: str) -> int:
    mapa = _mapa_conta(engine)
    if conta not in mapa:
        raise KeyError(f"Conta {conta!r} não cadastrada em dbo.FRAPConta")
    return mapa[conta]


def get_id_categoria(engine: Engine, codigo: str) -> int:
    mapa = _mapa_categoria(engine)
    if codigo not in mapa:
        raise KeyError(f"Categoria {codigo!r} não cadastrada em dbo.FRAPCategoria")
    return mapa[codigo]


def get_id_status_match(engine: Engine, matcher: str, codigo: str) -> int:
    mapa = _mapa_status(engine)
    chave = (matcher, codigo)
    if chave not in mapa:
        raise KeyError(
            f"Status (matcher={matcher!r}, codigo={codigo!r}) não cadastrado em dbo.FRAPStatusMatch"
        )
    return mapa[chave]


def reset_cache() -> None:
    """Limpa o cache de mapas — usar entre testes ou após alterar lookups."""
    _mapa_conta.cache_clear()
    _mapa_categoria.cache_clear()
    _mapa_status.cache_clear()
