"""Integration smoke tests — require live MSSQL + the PDF share mount."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pypdf
import pytest
from sqlalchemy import text

from ccd.db import get_connection

QUERY = """
SELECT
    RTRIM(setor) as setor,
    resumo,
    data_resumo,
    Decisao,
    concat(rtrim(setor),'_',numero_processo,'_',ano_processo,'_',RIGHT(concat('0000',ordem),4),'.pdf') as arquivo
FROM processo.dbo.Ata_Informacao
WHERE Decisao IS NOT NULL
  AND year(data_resumo) = :ano
"""


@pytest.fixture
def engine():
    return get_connection()


@pytest.mark.skip(reason="integration: needs DB")
def test_conn(engine):
    with engine.connect() as conn:
        rows = conn.execute(text(QUERY), {"ano": 2024}).mappings().all()
    assert len(rows) > 0


@pytest.mark.skip(reason="integration: needs DB + PDF share")
def test_pdf(engine, tmp_path: Path):
    pdf_dir = Path(os.getenv("CCD_INFORMACOES_DIR", "/mnt/informacoes_pdf"))
    assert pdf_dir.exists()

    with engine.connect() as conn:
        rows = conn.execute(text(QUERY), {"ano": 2024}).mappings().all()
    row = dict(rows[2])

    arquivo = pdf_dir / row["setor"].strip() / row["arquivo"]
    pdf = pypdf.PdfReader(str(arquivo))
    row["texto"] = [page.extract_text() or "" for page in pdf.pages]
    row["data_resumo"] = row["data_resumo"].strftime("%Y-%m-%d")

    (tmp_path / "output.json").write_text(json.dumps([row], ensure_ascii=False), encoding="utf-8")
    assert len(rows) > 0
