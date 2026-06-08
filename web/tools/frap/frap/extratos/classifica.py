"""Classificação de `historico` em categoria controlada."""
from __future__ import annotations

import unicodedata
from enum import StrEnum


class Categoria(StrEnum):
    OB_RECEBIDA = "OB_RECEBIDA"              # crédito; bate com SIGEF
    GUIA_RECEBIMENTO = "GUIA_RECEBIMENTO"    # crédito; bate com Exe_Debito/boleto
    TRANSFERENCIA = "TRANSFERENCIA"          # crédito sem fonte interna
    APLICACAO_RESGATE = "APLICACAO_RESGATE"  # movimento de aplicação automática
    SALDO = "SALDO"                          # linhas de saldo (ignorar)
    OUTROS = "OUTROS"                        # warning para investigação


# Casamento por substring sobre `historico` normalizado (sem acento, lowercase).
# A ordem importa: regras mais específicas vêm antes para não serem absorvidas
# por uma mais genérica (ex.: "saldo anterior" antes do "saldo" puro).
_REGRAS: tuple[tuple[str, Categoria], ...] = (
    ("ordem bancaria", Categoria.OB_RECEBIDA),
    ("ordem banc", Categoria.OB_RECEBIDA),  # truncado: "Ordem Banc 12 Sec Tes Nac"
    ("recebimento de guias", Categoria.GUIA_RECEBIMENTO),
    ("recebimentos diversos", Categoria.GUIA_RECEBIMENTO),
    ("deposito online", Categoria.GUIA_RECEBIMENTO),
    ("transferencia recebida", Categoria.TRANSFERENCIA),
    ("transferencia enviada", Categoria.TRANSFERENCIA),
    ("ted-credito", Categoria.TRANSFERENCIA),
    ("ted-deposito", Categoria.TRANSFERENCIA),
    ("ted-debito", Categoria.TRANSFERENCIA),
    ("pix", Categoria.TRANSFERENCIA),
    ("transferido da poupanca", Categoria.APLICACAO_RESGATE),
    ("bb rf sim", Categoria.APLICACAO_RESGATE),
    ("bb cp ", Categoria.APLICACAO_RESGATE),  # cobre "automatico" e "admin diferenciado"
    ("aplicacao", Categoria.APLICACAO_RESGATE),
    ("resgate", Categoria.APLICACAO_RESGATE),
    ("saldo anterior", Categoria.SALDO),
    ("s a l d o", Categoria.SALDO),
    ("saldo", Categoria.SALDO),
)


def _normaliza(s: str) -> str:
    n = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return n.lower().strip()


def classifica(historico: str) -> Categoria:
    """Mapeia o `historico` do BB para uma `Categoria` controlada.

    Casamento por substring (case- e accent-insensitive). Sem regra → `OUTROS`,
    sinalizando que o histórico precisa virar regra nova ou ser investigado.
    """
    if not historico:
        return Categoria.OUTROS
    norm = _normaliza(historico)
    for trecho, cat in _REGRAS:
        if trecho in norm:
            return cat
    return Categoria.OUTROS
