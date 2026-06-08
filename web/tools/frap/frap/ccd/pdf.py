"""Extrai texto de PDFs do share de informações do TCE."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)

# Share Windows com PDFs das informações dos processos. Estrutura por setor:
# `\\10.24.0.6\tce$\Informacoes_PDF\<SETOR>\<arquivo>`.
DEFAULT_INFORMACOES_DIR = r"\\10.24.0.6\tce$\Informacoes_PDF"


def informacoes_dir() -> Path:
    """Diretório base. Override via env var `CCD_INFORMACOES_DIR`."""
    return Path(os.environ.get("CCD_INFORMACOES_DIR", DEFAULT_INFORMACOES_DIR))


def extract_text_from_pdf(file_path: Path) -> str:
    """Lê texto de todas as páginas do PDF. Retorna '' em qualquer falha."""
    try:
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        logger.warning("Erro lendo PDF %s: %s", file_path, e)
        return ""
