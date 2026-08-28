"""Único ponto de construção de cliente LLM da árvore `web/` (FRAP, CGAD, backend).

LGPD: texto de decisão/informação carrega dado pessoal, então toda inferência sai
pela Azure fornecida pelo SERPRO (Foundry) e por mais nenhum provedor.

Duas regras, deliberadamente diferentes:

- **Sem configuração** (`AZURE_OPENAI_ENDPOINT`/`AZURE_OPENAI_API_KEY` vazios) →
  `None`: o caller cai em "sem LLM", que não vaza nada.
- **Configuração apontando para fora do SERPRO** → `RuntimeError`: isso é violação,
  não indisponibilidade.

O endpoint do Foundry é OpenAI-compatível (`.../openai/v1`), então o cliente é
`ChatOpenAI(base_url=...)`. `AzureChatOpenAI` **não** serve: contra essa base ele
ignora o deployment pedido e responde do default do recurso — era por isso que o
CGAD achava que rodava DeepSeek e rodava gpt-4o.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any
from urllib.parse import urlsplit

from frap.config import load_dotenv

logger = logging.getLogger(__name__)

# Sufixo de host da Azure do SERPRO. Override via FRAP_LLM_HOST_ALLOWED.
FOUNDRY_HOST_SUFFIX = ".services.ai.azure.com"

# Deployment DeepSeek. Override via AZURE_OPENAI_DEPLOYMENT.
DEFAULT_LLM_MODEL = "DeepSeek-V4-Flash"


def _endpoint_permitido(endpoint: str) -> bool:
    host = urlsplit(endpoint).hostname or ""
    sufixo = os.environ.get("FRAP_LLM_HOST_ALLOWED", FOUNDRY_HOST_SUFFIX)
    return host.endswith(sufixo)


@lru_cache(maxsize=1)
def get_llm_client(model: str | None = None, **kwargs: Any) -> Any | None:
    """Cliente do DeepSeek no Foundry do SERPRO, ou `None` se não configurado.

    Cache=1 — o cliente é stateless e o ChatOpenAI cria sua HTTP pool; reuso
    é desejado dentro de um run do CLI.
    """
    load_dotenv()
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()
    if not endpoint or not api_key:
        logger.warning(
            "AZURE_OPENAI_API_KEY / AZURE_OPENAI_ENDPOINT ausentes — LLM desativado."
        )
        return None
    if not _endpoint_permitido(endpoint):
        raise RuntimeError(
            f"Endpoint LLM fora da Azure do SERPRO: {endpoint!r}. Por LGPD, todo "
            "processamento de texto de processo tem que sair pelo Foundry do SERPRO."
        )
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        logger.warning(
            "langchain_openai não instalado — instale com `uv pip install -e \"./tools[llm]\"`."
        )
        return None
    return ChatOpenAI(
        base_url=endpoint,
        api_key=api_key,
        # `or` e não `get(..., default)`: o deploy escreve a linha sempre, então a
        # var pode vir presente-e-vazia — que o default de get não pega.
        model=model or os.environ.get("AZURE_OPENAI_DEPLOYMENT") or DEFAULT_LLM_MODEL,
        temperature=kwargs.pop("temperature", 0.0),
        timeout=kwargs.pop("timeout", 15),
        # max_retries alto: o Azure devolve 429 em rajada e o SDK respeita o
        # Retry-After. Com o default (2) metade da rodada se perde.
        max_retries=kwargs.pop("max_retries", 8),
        **kwargs,
    )


def structured(schema: Any, llm: Any | None = None, **kwargs: Any) -> Any | None:
    """`with_structured_output` com o método que o DeepSeek suporta.

    `method="function_calling"`: o `json_schema` nativo não é garantido nos
    deployments DeepSeek do Foundry. Devolve `None` quando não há LLM configurado.
    """
    llm = llm or get_llm_client(**kwargs)
    if llm is None:
        return None
    return llm.with_structured_output(schema, include_raw=False, method="function_calling")


def _demo() -> None:
    """Self-check da guarda de host — sem rede."""
    assert _endpoint_permitido("https://projeto-dip-resource.services.ai.azure.com/openai/v1")
    for proibido in (
        "https://api.openai.com/v1",
        "https://api.deepseek.com",
        "https://qualquer-coisa.openai.azure.com/",
        "https://services.ai.azure.com.evil.example/openai/v1",
        "",
    ):
        assert not _endpoint_permitido(proibido), proibido
    print("ok: guarda de host do LLM")


if __name__ == "__main__":
    _demo()
