"""Fallback LLM para inferência de órgão quando regex/alias/sigla falham.

Princípios:
- Chamada cara → cache em memória por chave normalizada (1 chamada por texto
  único no run do CLI).
- Pré-seleção: só passa ao LLM os top-N (~20) órgãos com sobreposição de
  tokens com o texto. Sem isso o prompt explode (milhares de órgãos na view).
- Resposta estruturada via Pydantic + with_structured_output. Se LLM retorna
  None / id inválido / exceção → cai para None silenciosamente.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable

from pydantic import BaseModel, Field

from frap.llm import get_llm_client
from frap.matching.inferencia_orgao import OrgaoIndex, _normaliza

logger = logging.getLogger(__name__)

_CACHE: dict[str, int | None] = {}
_TOP_N_CANDIDATOS = 20

_PROMPT_TEMPLATE = """Você recebe um trecho de extrato bancário do TCE-RN e uma lista de órgãos públicos candidatos do RN. O trecho descreve um depósito feito por algum desses órgãos (ou nenhum deles).

Trecho do extrato:
{texto}

Órgãos candidatos (id_orgao | nome | sigla):
{candidatos}

Retorne o id_orgao do órgão correspondente OU null se nenhum bater com confiança ALTA. Não invente ids — use apenas os listados acima. Em caso de dúvida, retorne null."""


class _LlmResposta(BaseModel):
    id_orgao: int | None = Field(default=None, description="IdOrgao do órgão correto, ou null.")


def _chave_cache(historico: str | None, descricao: str | None) -> str:
    texto = f"{historico or ''} {descricao or ''}"
    norm = _normaliza(texto)
    # remove sequências de dígitos (datas/CNPJs/valores) e tokens muito curtos
    norm = re.sub(r"\b\d+\b", "", norm)
    return " ".join(t for t in norm.split() if len(t) >= 3)


def _candidatos_top_n(texto_norm: str, indice: Iterable[OrgaoIndex]) -> list[OrgaoIndex]:
    tokens_texto = {t for t in texto_norm.split() if len(t) >= 4}
    if not tokens_texto:
        return []
    pontuados: list[tuple[int, OrgaoIndex]] = []
    for org in indice:
        tokens_org = set(org.nome_normalizado.split())
        if org.sigla_normalizada:
            tokens_org.add(org.sigla_normalizada)
        intersec = len(tokens_texto & tokens_org)
        if intersec > 0:
            pontuados.append((intersec, org))
    pontuados.sort(key=lambda x: (-x[0], len(x[1].nome_normalizado)))
    return [o for _, o in pontuados[:_TOP_N_CANDIDATOS]]


def infer_via_llm(
    historico: str | None,
    descricao: str | None,
    indice: list[OrgaoIndex],
) -> int | None:
    """Tenta inferir IdOrgao via Azure OpenAI. None se sem config / sem match."""
    chave = _chave_cache(historico, descricao)
    if not chave:
        return None
    if chave in _CACHE:
        return _CACHE[chave]

    client = get_llm_client()
    if client is None:
        _CACHE[chave] = None
        return None

    candidatos = _candidatos_top_n(chave, indice)
    if not candidatos:
        _CACHE[chave] = None
        return None

    candidatos_str = "\n".join(
        f"{o.id_orgao} | {o.nome} | {o.sigla or ''}" for o in candidatos
    )
    texto_full = f"{historico or ''} | {descricao or ''}"
    prompt = _PROMPT_TEMPLATE.format(texto=texto_full, candidatos=candidatos_str)

    try:
        structured = client.with_structured_output(_LlmResposta)
        resp: _LlmResposta = structured.invoke(prompt)
    except Exception as exc:
        logger.warning("LLM falhou para chave=%r: %s", chave[:80], exc)
        _CACHE[chave] = None
        return None

    id_orgao = resp.id_orgao
    ids_validos = {o.id_orgao for o in candidatos}
    if id_orgao is None or id_orgao not in ids_validos:
        _CACHE[chave] = None
        return None

    _CACHE[chave] = id_orgao
    return id_orgao


def limpar_cache() -> None:
    """Esvazia o cache. Usado em testes."""
    _CACHE.clear()
