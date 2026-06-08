"""Cliente LLM para inferência fuzzy de órgão via Azure OpenAI.

Opt-out por configuração: se `AZURE_OPENAI_API_KEY` ou `AZURE_OPENAI_ENDPOINT`
estão vazios, ou se `langchain_openai` não está instalado, `get_llm_client()`
retorna `None` e o caller cai silenciosamente em "sem LLM".
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any

from frap.config import load_dotenv

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm_client() -> Any | None:
    """Devolve um `AzureChatOpenAI` configurado ou `None` se faltar config/dep.

    Cache=1 — o cliente é stateless e o ChatOpenAI cria sua HTTP pool; reuso
    é desejado dentro de um run do CLI.
    """
    load_dotenv()
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    api_version = os.environ.get("OPENAI_API_VERSION", "2025-03-01-preview").strip()
    if not api_key or not endpoint:
        logger.warning(
            "AZURE_OPENAI_API_KEY / AZURE_OPENAI_ENDPOINT ausentes — LLM desativado."
        )
        return None
    try:
        from langchain_openai import AzureChatOpenAI
    except ImportError:
        logger.warning(
            "langchain_openai não instalado — instale com `uv pip install -e \"./tools[llm]\"`."
        )
        return None
    return AzureChatOpenAI(
        azure_deployment="gpt-5.4-nano",
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
        temperature=0.0,
        timeout=15,
        max_retries=1,
    )
