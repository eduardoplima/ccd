from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Unidade = Literal["brl", "pct", "dias", "qtd"]
Sentido = Literal["maior", "menor"]  # qual direção é melhora


class Indicador(BaseModel):
    chave: str
    titulo: str
    unidade: Unidade
    sentido: Sentido
    explicacao: str  # como o número é calculado (hover do card)
    valores: dict[int, float | None]  # por ano; vazio p/ indicador só de retrato
    atual: float | None  # retrato de hoje (quando não há série)
    linha_base: float | None  # média dos dois anos anteriores ao corrente
    detalhe: str | None


class Painel(BaseModel):
    ano: int
    anos: list[int]
    indicadores: list[Indicador]
