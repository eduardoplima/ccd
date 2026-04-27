"""Extract decisions + PDF text from the `processo` DB into a JSON dataset.

Uses the unified `ccd.db.get_connection`. The PDF mount path can be overridden
via the `CCD_INFORMACOES_DIR` env var; default keeps the legacy Linux mount
(`/mnt/informacoes_pdf`) for this entrypoint.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pypdf
from sqlalchemy import text

from ccd.db import get_connection
from ccd.pdf import extract_text_from_pdf

DEFAULT_PDF_DIR = "/mnt/informacoes_pdf"

QUERY = """
SELECT
    p.numero_processo,
    p.ano_processo,
    p.codigo_tipo_processo,
    p.assunto,
    inf.setor,
    inf.resumo,
    inf.data_resumo,
    concat(rtrim(inf.setor),'_',inf.numero_processo,'_',inf.ano_processo,'_',RIGHT(concat('0000',inf.ordem),4),'.pdf') as arquivo
FROM processo.dbo.Ata_Informacao inf
INNER JOIN Processos p ON inf.numero_processo = p.numero_processo AND inf.ano_processo = p.ano_processo
WHERE inf.Decisao IS NOT NULL
  AND p.ano_processo > 2015
  AND year(inf.data_resumo) = :ano
"""


class ETL:
    def __init__(self, ano: int = 2024, pdf_dir: str | Path | None = None):
        self.engine = get_connection()
        self.ano = ano
        self.pdf_dir = Path(pdf_dir or os.getenv("CCD_INFORMACOES_DIR", DEFAULT_PDF_DIR))
        # Lazy docling import — heavy dependency, not always installed.
        self._docling = None

    def get_rows(self) -> list[dict]:
        with self.engine.connect() as conn:
            result = conn.execute(text(QUERY), {"ano": self.ano})
            return [dict(row) for row in result.mappings().all()]

    def get_file_path(self, row: dict) -> Path:
        return self.pdf_dir / row["setor"].strip() / row["arquivo"]

    def get_pdf_text(self, row: dict) -> list[str]:
        arquivo = self.get_file_path(row)
        print(f"File {arquivo} to pypdf text")
        try:
            pdf = pypdf.PdfReader(str(arquivo))
            return [page.extract_text() or "" for page in pdf.pages]
        except FileNotFoundError:
            print(f"File not found: {arquivo}")
            return []

    def get_docling_pdf_text(self, row: dict) -> str:
        if self._docling is None:
            from docling.document_converter import DocumentConverter  # noqa: PLC0415
            self._docling = DocumentConverter()
        arquivo = self.get_file_path(row)
        print(f"File {arquivo} to docling text")
        return self._docling.convert(str(arquivo)).document.export_to_text()

    def save_json(self, json_dicts: list[dict], filename: str | Path) -> None:
        Path(filename).write_text(json.dumps(json_dicts, ensure_ascii=False), encoding="utf-8")

    def execute(self, output_path: str | Path = "output.json") -> None:
        rows = self.get_rows()
        print(f"{len(rows)} rows returned.")
        for row in rows:
            row["texto"] = self.get_pdf_text(row)
            row["data_resumo"] = row["data_resumo"].strftime("%Y-%m-%d")
        self.save_json(rows, output_path)


if __name__ == "__main__":
    ETL().execute()
