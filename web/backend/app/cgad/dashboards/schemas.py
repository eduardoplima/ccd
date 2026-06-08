"""DTOs for the dashboards API.

The single ``GET /dashboards/summary`` endpoint returns one ``DashboardSummary``
with three sub-blocks: KPIs, top órgãos and top pessoas. Sized for one page
render — no pagination, top-N is server-controlled.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class KpiBlock(BaseModel):
    """High-level numbers for the period plus current pending snapshot.

    ``pendentes_*`` are a snapshot of the inbox (not date-filtered) — final
    rows without a staging audit row. The remaining counters are filtered by
    ``DataRevisao`` ∈ [start_date, end_date] on the staging row.
    """

    pendentes_obrigacao: int
    pendentes_recomendacao: int
    revisadas_periodo: int
    aprovadas_periodo: int
    percent_aprovacao: float  # 0.0 – 1.0
    obrigacoes_com_multa: int
    ticket_medio_multa: Optional[float] = None


class OrgaoBucket(BaseModel):
    nome: str
    obrigacoes: int
    recomendacoes: int
    total: int


class PessoaBucket(BaseModel):
    nome: str
    documento: Optional[str] = None
    obrigacoes: int
    recomendacoes: int
    total: int


class DashboardSummary(BaseModel):
    kpis: KpiBlock
    top_orgaos: list[OrgaoBucket]
    top_pessoas: list[PessoaBucket]
