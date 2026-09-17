"""Único ponto de construção de cliente LLM do repositório.

LGPD: texto de informação/despacho carrega dado pessoal de jurisdicionado, então
toda inferência sai pela Azure fornecida pelo SERPRO (Foundry) e por mais nenhum
provedor. `get_llm()` levanta se o endpoint configurado não for de um host
permitido — não existe fallback silencioso para OpenAI público, DeepSeek público
ou outra assinatura Azure.

O endpoint do Foundry é OpenAI-compatível (`.../openai/v1`), então o cliente é
`ChatOpenAI(base_url=...)`. `AzureChatOpenAI` **não** serve: contra essa base ele
ignora o deployment pedido e responde do default do recurso.
"""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlsplit

from ccd.config import load_env

# Sufixo de host da Azure do SERPRO. Override (raro, p.ex. domínio próprio) via
# CCD_LLM_HOST_ALLOWED.
FOUNDRY_HOST_SUFFIX = ".services.ai.azure.com"

# Deployment DeepSeek. Override via AZURE_OPENAI_DEPLOYMENT.
DEFAULT_LLM_MODEL = "DeepSeek-V4-Flash"


def _endpoint_permitido(endpoint: str) -> bool:
    host = urlsplit(endpoint).hostname or ""
    sufixo = os.getenv("CCD_LLM_HOST_ALLOWED", FOUNDRY_HOST_SUFFIX)
    return host.endswith(sufixo)


def get_llm(model: str | None = None, **kwargs: Any):
    """Cliente do DeepSeek no Foundry do SERPRO. Levanta se a config não bater."""
    load_env()
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    if not endpoint or not api_key:
        raise RuntimeError(
            "AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY ausentes — sem eles não há "
            "para onde mandar o texto dentro da Azure do SERPRO."
        )
    if not _endpoint_permitido(endpoint):
        raise RuntimeError(
            f"Endpoint LLM fora da Azure do SERPRO: {endpoint!r}. Por LGPD, todo "
            "processamento de texto de processo tem que sair pelo Foundry do SERPRO."
        )
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        base_url=endpoint,
        api_key=api_key,
        # `or` e não `getenv(..., default)`: o deploy escreve a linha sempre, então
        # a var pode vir presente-e-vazia — que o default de getenv não pega.
        model=model or os.getenv("AZURE_OPENAI_DEPLOYMENT") or DEFAULT_LLM_MODEL,
        temperature=kwargs.pop("temperature", 0.0),
        **kwargs,
    )


def structured(schema: Any, llm: Any | None = None, **kwargs: Any):
    """`get_llm().with_structured_output(schema)` com o método que o DeepSeek suporta.

    `method="function_calling"`: o `json_schema` nativo não é garantido nos
    deployments DeepSeek do Foundry.
    """
    return (llm or get_llm(**kwargs)).with_structured_output(
        schema, include_raw=False, method="function_calling"
    )


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
