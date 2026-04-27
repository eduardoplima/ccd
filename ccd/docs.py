"""docx template rendering and docx → pdf conversion.

Two backends exist for docx → pdf: LibreOffice headless (cross-platform,
needs `soffice` on PATH) and Microsoft Word via COM (Windows only). Use
`docx_to_pdf()` to auto-pick by platform; force one with the explicit names.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Mapping

from docxtpl import DocxTemplate


def render_template(
    template_path: str | Path,
    context: Mapping[str, object],
    output_path: str | Path,
) -> Path:
    """Render a `.docx` Jinja-like template with `context` and save it."""
    doc = DocxTemplate(str(template_path))
    doc.render(dict(context))
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def docx_to_pdf_libreoffice(doc_path: str | Path, output_dir: str | Path) -> Path:
    """Convert `.docx` to `.pdf` using LibreOffice headless (`soffice`)."""
    doc_path = Path(doc_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(doc_path)]
    )
    return output_dir / (doc_path.stem + ".pdf")


def docx_to_pdf_word(doc_path: str | Path, output_dir: str | Path) -> Path:
    """Convert `.docx` to `.pdf` driving Microsoft Word via COM (Windows only)."""
    if sys.platform != "win32":
        raise RuntimeError("docx_to_pdf_word requires Windows + Microsoft Word.")
    import win32com.client  # noqa: PLC0415 — Windows-only import

    doc_path = Path(doc_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / (doc_path.stem + ".pdf")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(doc_path))
        doc.SaveAs(str(pdf_path), FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
    finally:
        word.Quit()
    return pdf_path


def docx_to_pdf(doc_path: str | Path, output_dir: str | Path) -> Path:
    """Convert `.docx` to `.pdf` using whichever backend fits the host.

    Windows → Word COM (matches the existing notebook expectations).
    Otherwise → LibreOffice headless.
    """
    if sys.platform == "win32":
        return docx_to_pdf_word(doc_path, output_dir)
    return docx_to_pdf_libreoffice(doc_path, output_dir)
