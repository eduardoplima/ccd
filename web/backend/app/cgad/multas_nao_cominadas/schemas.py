"""DTOs da lista de multas não cominadas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_serializer

from app.cgad.review.schemas import _to_utc_iso


class MultaNaoCominada(BaseModel):
    """Obrigação aprovada/enviada com multa cominatória prevista, cujo processo
    não tem débito do tipo 5 (multa cominatória) em ``Exe_Debito``."""

    id: int  # PK do staging
    id_processo: int
    numero_processo: Optional[int] = None
    ano_processo: Optional[int] = None
    id_decisao: Optional[int] = None
    descricao: str
    prazo: Optional[str] = None
    data_cumprimento: Optional[date] = None
    orgao: Optional[str] = None
    responsavel: Optional[str] = None
    documento: Optional[str] = None
    valor_dia: Optional[float] = None
    periodo: Optional[str] = None
    status: Literal["approved", "dispatched"]
    revisor: Optional[str] = None
    data_revisao: Optional[datetime] = None

    @field_serializer("data_revisao")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class MultasNaoCominadas(BaseModel):
    total_obrigacoes: int
    total_processos: int
    items: list[MultaNaoCominada]
