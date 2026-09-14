"""DTOs for the dashboards API.

O único ``GET /dashboards/summary`` devolve um ``DashboardSummary`` com os
rankings, os treemaps e a lista completa das entidades aprovadas/enviadas —
o volume (centenas de linhas) cabe numa resposta e o filtro por clique nos
gráficos é feito no cliente.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_serializer

from app.cgad.review.schemas import _to_utc_iso


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


class TreemapBucket(BaseModel):
    nome: str
    total: int


class TreemapSet(BaseModel):
    """Contagens de um tipo de entidade por três dimensões. ``por_tipo`` e
    ``por_relator`` vêm do banco ``processo`` (Tipo/Relator do processo)."""

    por_orgao: list[TreemapBucket]
    por_tipo: list[TreemapBucket]
    por_relator: list[TreemapBucket]


class EntidadeCadastrada(BaseModel):
    """Uma linha aprovada/enviada do staging, já com as dimensões resolvidas
    (órgão, tipo de processo, relator, pessoa canônica) para o filtro por clique."""

    tipo: Literal["obrigacao", "recomendacao"]
    id: int  # PK do staging
    id_processo: int
    numero_processo: Optional[int] = None
    ano_processo: Optional[int] = None
    id_decisao: Optional[int] = None
    descricao: str
    status: Literal["approved", "dispatched"]
    revisor: Optional[str] = None
    data_revisao: Optional[datetime] = None
    data_envio: Optional[datetime] = None
    orgao: str
    tipo_processo: str
    relator: str
    pessoa: Optional[str] = None

    @field_serializer("data_revisao", "data_envio")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class DashboardSummary(BaseModel):
    top_orgaos: list[OrgaoBucket]
    top_pessoas: list[PessoaBucket]
    treemap_obrigacao: TreemapSet
    treemap_recomendacao: TreemapSet
    entidades: list[EntidadeCadastrada]
