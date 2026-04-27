"""PDF text extraction and concatenation."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pypdf


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Read a PDF and return its concatenated text. Returns '' on failure."""
    try:
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            return "".join((page.extract_text() or "") for page in reader.pages)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""


def merge_pdfs(pdf_files: Iterable[str | Path], output_path: str | Path) -> None:
    """Concatenate `pdf_files` into a single PDF at `output_path`."""
    writer = pypdf.PdfWriter()
    for pdf_file in pdf_files:
        reader = pypdf.PdfReader(str(pdf_file))
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as fout:
        writer.write(fout)
