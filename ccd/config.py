"""Path resolution and .env loading.

Every path the package needs is computed from `Path(__file__)` so importing
`ccd` works from any current working directory — no `sys.path.append("..")`,
no silently-empty env vars when a notebook is launched from the wrong place.
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR: Path = Path(__file__).resolve().parent
REPO_ROOT: Path = PACKAGE_DIR.parent
SQL_DIR: Path = PACKAGE_DIR / "sql"

_ENV_CANDIDATES = (
    REPO_ROOT / ".env",
    REPO_ROOT / "scripts" / ".env",
)

_env_loaded: Path | None = None


def load_env(override: bool = False) -> Path | None:
    """Load the project's .env file. Returns the path that was loaded, or None.

    Searches REPO_ROOT/.env first, then scripts/.env (legacy location).
    Idempotent: subsequent calls are no-ops unless override=True.
    """
    global _env_loaded
    if _env_loaded is not None and not override:
        return _env_loaded
    for candidate in _ENV_CANDIDATES:
        if candidate.exists():
            load_dotenv(candidate, override=override)
            _env_loaded = candidate
            return candidate
    return None


def read_sql(name: str) -> str:
    """Read a bundled SQL file from ccd/sql/<name>."""
    path = SQL_DIR / name
    return path.read_text(encoding="utf-8")
