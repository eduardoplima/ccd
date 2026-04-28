"""Common notebook prelude.

Replaces the 5–10 boilerplate lines reproduced in every notebook
(`sys.path.append("..")`, `load_dotenv()`, `get_connection()`,
`AzureChatOpenAI(model_name="gpt-4o")`).

Usage in a new notebook:

    from ccd.notebook import setup
    ctx = setup()
    df = pd.read_sql(text("..."), ctx.engine)
    ctx.llm.invoke("...")

`langchain-openai` is an optional dependency: install with
`pip install -e ".[notebooks]"` or omit the `llm=True` flag.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from sqlalchemy.engine import Engine

from ccd.config import DEFAULT_AZURE_DEPLOYMENT, load_env
from ccd.db import get_connection


@dataclass
class NotebookContext:
    engine: Engine
    llm: Any | None  # AzureChatOpenAI when langchain-openai is installed


def setup(db: str = "processo", llm: bool = True) -> NotebookContext:
    """Load .env, open a MSSQL Engine, and (optionally) build the Azure LLM."""
    load_env()
    engine = get_connection(db)
    llm_instance: Any | None = None
    if llm:
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError as exc:
            raise ImportError(
                "langchain-openai is not installed. "
                'Install with: pip install -e ".[notebooks]"'
            ) from exc
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", DEFAULT_AZURE_DEPLOYMENT)
        llm_instance = AzureChatOpenAI(model=deployment)
    return NotebookContext(engine=engine, llm=llm_instance)
