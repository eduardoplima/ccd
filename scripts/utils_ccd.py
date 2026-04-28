"""Compatibility shim — the real code lives in the `ccd` package.

Notebooks under `scripts/<area>/*.ipynb` still do `from utils_ccd import ...`
after `sys.path.append("..")`. After `pip install -e .` at the repo root, you
can drop both lines and import from `ccd` directly.
"""
from ccd.db import get_connection
from ccd.docs import (
    docx_to_pdf_libreoffice as generate_pdf,
)
from ccd.docs import (
    docx_to_pdf_word as generate_pdf_office,
)
from ccd.pdf import extract_text_from_pdf, merge_pdfs
from ccd.processo import (
    DEFAULT_INFORMACOES_DIR as DIR_INFORMACOES,
)
from ccd.processo import (
    download_processo,
    get_info_file_path,
    get_informacoes_processo,
    get_pdf_files_processo,
)

__all__ = [
    "DIR_INFORMACOES",
    "download_processo",
    "extract_text_from_pdf",
    "generate_pdf",
    "generate_pdf_office",
    "get_connection",
    "get_info_file_path",
    "get_informacoes_processo",
    "get_pdf_files_processo",
    "merge_pdfs",
]
