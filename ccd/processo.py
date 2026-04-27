"""Domain helpers around the `processo` MSSQL database.

Queries are parameterized with named placeholders (`:processo`, `:nome`) so
callers never interpolate values into SQL strings. The PDF share path is
configurable via the `CCD_INFORMACOES_DIR` env var; the default points at the
TCE/RN Windows UNC share.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from ccd.db import get_connection
from ccd.pdf import extract_text_from_pdf

DEFAULT_INFORMACOES_DIR = r"\\10.24.0.6\tce$\Informacoes_PDF"


def _informacoes_dir() -> Path:
    return Path(os.getenv("CCD_INFORMACOES_DIR", DEFAULT_INFORMACOES_DIR))


def get_info_file_path(row: pd.Series | dict, dir_info: str | Path | None = None) -> Path:
    """Build the absolute path to an `Ata_Informacao` PDF on the share."""
    base = Path(dir_info) if dir_info is not None else _informacoes_dir()
    setor = row["setor"].strip()
    return base / setor / row["arquivo"]


_SQL_INFORMACOES_PROCESSO = """
SELECT concat(rtrim(inf.setor),'_',inf.numero_processo,'_',inf.ano_processo,'_',RIGHT(concat('0000',inf.ordem),4),'.pdf') as arquivo,
       ppe.SequencialProcessoEvento as evento,
       CONCAT(inf.numero_processo,'/', inf.ano_processo) as processo,
       inf.*
FROM processo.dbo.vw_ata_informacao inf
INNER JOIN processo.dbo.Pro_ProcessoEvento ppe
    ON inf.idinformacao = ppe.idinformacao
WHERE CONCAT(inf.numero_processo, '/', inf.ano_processo) = :processo
"""


def _query_informacoes(processo: str, conn: Engine | Any | None) -> pd.DataFrame:
    if conn is None:
        conn = get_connection()
    df = pd.read_sql(text(_SQL_INFORMACOES_PROCESSO), conn, params={"processo": processo})
    df["caminho_arquivo"] = df.apply(get_info_file_path, axis=1)
    return df


def get_pdf_files_processo(processo: str, conn: Engine | Any | None = None) -> list[Path]:
    """Return the list of PDF paths for a given processo (e.g. '002667/2025')."""
    return _query_informacoes(processo, conn)["caminho_arquivo"].tolist()


def get_informacoes_processo(processo: str, conn: Engine | Any | None = None) -> pd.DataFrame:
    """Return a DataFrame of all `Ata_Informacao` rows for a processo, with PDF text."""
    df = _query_informacoes(processo, conn)
    df["texto"] = df["caminho_arquivo"].apply(extract_text_from_pdf)
    return df


def download_processo(
    processo: str,
    dir_destino: str | Path,
    conn: Engine | Any | None = None,
) -> pd.DataFrame:
    """Copy every PDF for `processo` from the share into `dir_destino`."""
    infos = get_informacoes_processo(processo, conn)
    dir_destino = Path(dir_destino)
    dir_destino.mkdir(parents=True, exist_ok=True)

    for _, row in infos.iterrows():
        destino = dir_destino / row["arquivo"]
        origem = row["caminho_arquivo"]
        if origem.exists():
            destino.write_bytes(origem.read_bytes())
        else:
            print(f"Arquivo não encontrado: {origem}")

    return infos
