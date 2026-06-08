"""Filesystem layout for dataset correction artifacts.

Resolved relative to the repo root so the backend works whether launched
from ``backend/`` or the repo root.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT: Path = Path(__file__).resolve().parents[3]

DATASET_DIR: Path = REPO_ROOT / "dataset"
LABELED_JSON: Path = DATASET_DIR / "labeled_data" / "decicontas.json"
ERRORS_CSV: Path = DATASET_DIR / "errors" / "erros_anotacao_decicontas.csv"
DECISIONS_JSONL: Path = DATASET_DIR / "errors" / "decisions.jsonl"
