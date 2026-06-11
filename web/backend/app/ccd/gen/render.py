"""Render de template `.docx` (docxtpl) + conversão para PDF + empacotamento.

Espelha o que os notebooks fazem com `DocxTemplate(...).render(ctx)` +
`generate_pdf_office`, mas isolado do CWD: os templates vivem em
`app/ccd/gen/templates/` e a conversão escolhe o backend pela plataforma
(Word no Windows via `docx2pdf`, LibreOffice headless caso contrário).
"""

from __future__ import annotations

import locale
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

from docxtpl import DocxTemplate

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def set_pt_br_locale() -> None:
    """Best-effort pt-BR locale (para num2words/locale.currency nas features)."""
    for name in ("pt_BR.UTF-8", "pt_BR.utf8", "Portuguese_Brazil.1252", "pt_BR"):
        try:
            locale.setlocale(locale.LC_ALL, name)
            return
        except locale.Error:
            continue


def render_docx(template_name: str, context: dict[str, Any], out_path: Path) -> Path:
    """Renderiza `templates/<template_name>` com `context` e salva em `out_path`."""
    template = TEMPLATES_DIR / template_name
    if not template.exists():
        raise FileNotFoundError(f"template não encontrado: {template}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = DocxTemplate(str(template))
    doc.render(context)
    doc.save(str(out_path))
    return out_path


def docx_to_pdf(docx_path: Path, out_dir: Path | None = None) -> Path:
    """Converte um `.docx` em `.pdf` no mesmo diretório (ou em `out_dir`).

    Windows → MS Word (docx2pdf). Outras plataformas → LibreOffice headless.
    Levanta `RuntimeError` se a conversão não produzir o PDF.
    """
    docx_path = Path(docx_path)
    out_dir = Path(out_dir) if out_dir else docx_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / (docx_path.stem + ".pdf")

    if sys.platform.startswith("win"):
        from docx2pdf import convert  # import tardio: usa win32com só no Windows

        convert(str(docx_path), str(pdf_path))
    else:
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(out_dir),
                str(docx_path),
            ],
            check=True,
            capture_output=True,
        )

    if not pdf_path.exists():
        raise RuntimeError(f"conversão para PDF falhou: {pdf_path}")
    return pdf_path


def montar_saida(pdfs: list[Path], out_dir: Path) -> Path:
    """Empacota os PDFs gerados em `final.pdf` (1) ou `final.zip` (vários).

    Retorna o caminho do artefato final. Levanta `ValueError` se a lista
    estiver vazia.
    """
    pdfs = [Path(p) for p in pdfs if p and Path(p).exists()]
    if not pdfs:
        raise ValueError("nenhum PDF foi gerado")

    if len(pdfs) == 1:
        final = out_dir / "final.pdf"
        final.write_bytes(pdfs[0].read_bytes())
        return final

    final = out_dir / "final.zip"
    with zipfile.ZipFile(final, "w", zipfile.ZIP_DEFLATED) as zf:
        for pdf in pdfs:
            zf.write(pdf, arcname=pdf.name)
    return final
