"""Common notebook prelude.

Replaces the 5–10 boilerplate lines reproduced in every notebook
(`sys.path.append("..")`, `load_dotenv()`, `get_connection()`, construção do
cliente LLM — que agora vem só de `ccd.llm.get_llm()`).

Usage in a new notebook:

    from ccd.notebook import setup
    ctx = setup()
    df = pd.read_sql(text("..."), ctx.engine)
    ctx.llm.invoke("...")

`langchain-openai` is an optional dependency: install with
`pip install -e ".[notebooks]"` or omit the `llm=True` flag.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.engine import Engine

from ccd.config import load_env
from ccd.db import get_connection


@dataclass
class NotebookContext:
    engine: Engine
    llm: Any | None  # ChatOpenAI (DeepSeek no Foundry do SERPRO)


def setup(db: str = "processo", llm: bool = True) -> NotebookContext:
    """Load .env, open a MSSQL Engine, and (optionally) build the SERPRO LLM."""
    load_env()
    engine = get_connection(db)
    llm_instance: Any | None = None
    if llm:
        from ccd.llm import get_llm

        try:
            llm_instance = get_llm()
        except ImportError as exc:
            raise ImportError(
                "langchain-openai is not installed. "
                'Install with: pip install -e ".[notebooks]"'
            ) from exc
    return NotebookContext(engine=engine, llm=llm_instance)
