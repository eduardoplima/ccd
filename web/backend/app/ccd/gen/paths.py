"""Localização em disco dos artefatos de geração de documentos do CCD.

Cada job tem um diretório próprio em `backend/.artifacts/ccd/<id_job>/`:

    input.json   — lista de processos selecionados (escrita no enfileiramento)
    *.docx/*.pdf — intermediários por processo (gerados pelo worker)
    final.pdf | final.zip — saída servida pelo endpoint de download

O diretório `.artifacts/` é gitignored.
"""

from __future__ import annotations

from pathlib import Path

# app/ccd/gen/paths.py -> parents[3] == web/backend
_BACKEND_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_ROOT = _BACKEND_ROOT / ".artifacts" / "ccd"


def artifact_dir(id_job: int) -> Path:
    """Diretório (criado on demand) com os artefatos do job `id_job`."""
    d = ARTIFACTS_ROOT / str(id_job)
    d.mkdir(parents=True, exist_ok=True)
    return d


def final_artifact(id_job: int) -> Path | None:
    """Retorna `final.pdf` ou `final.zip` do job, se já existir."""
    d = ARTIFACTS_ROOT / str(id_job)
    for nome in ("final.pdf", "final.zip"):
        p = d / nome
        if p.exists():
            return p
    return None
