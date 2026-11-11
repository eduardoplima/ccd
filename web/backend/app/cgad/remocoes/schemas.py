"""DTOs da remoção de obrigações/recomendações curadas por acórdão."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_serializer

from app.cgad.review.schemas import _to_utc_iso

TipoItem = Literal["obrigacao", "recomendacao"]


class Acordao(BaseModel):
    id_composicao_pauta: int
    numero: Optional[str] = None
    ano: Optional[str] = None
    tipo: Optional[str] = None  # "A" acórdão, "D" decisão
    data_sessao: Optional[date] = None


class ItemCurado(BaseModel):
    tipo: TipoItem
    id: int  # PK do staging
    id_composicao_pauta: int  # decisão de origem
    descricao: str
    orgao: Optional[str] = None
    status: Literal["approved", "dispatched", "removed"]
    id_composicao_pauta_remocao: Optional[int] = None
    justificativa_remocao: Optional[str] = None
    removido_por: Optional[str] = None
    data_remocao: Optional[datetime] = None

    @field_serializer("data_remocao")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class Consulta(BaseModel):
    id_processo: int
    processo: str
    acordaos: list[Acordao]
    itens: list[ItemCurado]


class ItemRef(BaseModel):
    tipo: TipoItem
    id: int


class RemocaoPayload(BaseModel):
    id_processo: int
    id_composicao_pauta_remocao: int
    justificativa: str = Field(min_length=1)
    itens: list[ItemRef] = Field(min_length=1)


class RemocaoResultado(BaseModel):
    removidos: int
