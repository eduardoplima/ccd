"""Align an extracted span (``descricao``) back to the source text.

Used by the review UI to highlight where a staged obligation / recommendation
came from in the full ``texto_acordao``. Pure, side-effect-free.
"""

from __future__ import annotations

from typing import Literal, Optional

from rapidfuzz import fuzz

_FUZZY_THRESHOLD = 90.0

SpanMatchStatus = Literal["exact", "fuzzy", "not_found"]


def find_span_offsets(
    descricao: str, texto_acordao: str
) -> tuple[Optional[int], Optional[int], SpanMatchStatus]:
    """Locate ``descricao`` inside ``texto_acordao`` and return the character
    offsets ``(start, end)`` plus how the match was found.

    Strategy:
      1. Exact case-sensitive substring → ``"exact"``.
      2. Case-insensitive substring → ``"exact"`` (same span, different casing).
      3. Fuzzy fallback via ``rapidfuzz.fuzz.partial_ratio`` with threshold 90
         → ``"fuzzy"``.
      4. Below threshold → ``(None, None, "not_found")``.
    """
    if not descricao or not texto_acordao:
        return None, None, "not_found"

    idx = texto_acordao.find(descricao)
    if idx != -1:
        return idx, idx + len(descricao), "exact"

    idx = texto_acordao.lower().find(descricao.lower())
    if idx != -1:
        return idx, idx + len(descricao), "exact"

    alignment = fuzz.partial_ratio_alignment(descricao, texto_acordao)
    if alignment is None or alignment.score < _FUZZY_THRESHOLD:
        return None, None, "not_found"

    start = alignment.dest_start
    end = alignment.dest_end
    if start is None or end is None or end <= start:
        return None, None, "not_found"
    return start, end, "fuzzy"


def find_span_with_status(
    descricao: str, texto_acordao: str
) -> tuple[Optional[str], SpanMatchStatus]:
    """Back-compat wrapper over ``find_span_offsets`` returning the matched
    substring (always sliced from ``texto_acordao``, never ``descricao``).
    """
    start, end, match_status = find_span_offsets(descricao, texto_acordao)
    if start is None or end is None:
        return None, match_status
    return texto_acordao[start:end], match_status


def find_span_in_text(descricao: str, texto_acordao: str) -> Optional[str]:
    """Back-compat wrapper returning only the matched substring."""
    span, _ = find_span_with_status(descricao, texto_acordao)
    return span
