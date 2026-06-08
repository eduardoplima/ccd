"""Extrai CPF/CNPJ do depositante a partir do campo `descricao` do extrato."""
from __future__ import annotations

import re

# Formatos com pontuação têm prioridade — eliminam falsos positivos com
# códigos de barras embutidos no campo `documento` (que podem ter 14 dígitos).
_CNPJ_FMT = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")
_CPF_FMT = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
# Crú: 11 ou 14 dígitos isolados por limites de palavra (evita pegar
# substring em sequência maior tipo código de barras de 47 dígitos).
_RAW = re.compile(r"\b\d{14}\b|\b\d{11}\b")


def extrai_cpfcnpj(descricao: str) -> tuple[str | None, bool]:
    """Tenta extrair um CPF ou CNPJ do `descricao` do extrato.

    Retorna `(documento_normalizado, ambiguo)`. `documento_normalizado` é só os
    dígitos. `ambiguo=True` indica que havia mais de um candidato — devolvemos
    o primeiro mas o consumidor pode querer auditar.
    """
    if not descricao:
        return (None, False)

    matches = _CNPJ_FMT.findall(descricao) + _CPF_FMT.findall(descricao)
    if not matches:
        matches = _RAW.findall(descricao)
    if not matches:
        return (None, False)

    primeiro = "".join(c for c in matches[0] if c.isdigit())
    return (primeiro, len(matches) > 1)
