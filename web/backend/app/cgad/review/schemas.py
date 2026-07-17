"""DTOs for the review API.

``ObrigacaoReview`` / ``RecomendacaoReview`` are the payload schemas for
approvals — one reviewer-editable field per reviewer-editable column on the
final ORM. A schema-parity test pins this mapping so that when a column is
added to the final ORM, the DTO fails the test until it's updated (silent
data-loss guard).

All human-facing field names stay snake_case (Pydantic convention + matches
the stage-2 schemas in ``tools/schema.py``). The service layer translates to
the final ORM's PascalCase Portuguese columns.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


Kind = Literal["obrigacao", "recomendacao"]
ReviewStatusStr = Literal["pending", "approved", "rejected"]
SpanMatchStatusStr = Literal["exact", "fuzzy", "not_found"]


class SolidarioMulta(BaseModel):
    """One co-responsible person on a multa cominatória solidária. ``nome``
    comes from the LLM extraction; ``documento`` is filled by the reviewer
    (typically by picking from ``ReviewTexto.pessoas`` which lists everyone
    associated with the process)."""

    nome: str
    documento: Optional[str] = None


class Pessoa(BaseModel):
    """Person associated with the process — surfaced in ``ReviewTexto.pessoas``
    so the form can autocomplete ``documento`` when the reviewer types or
    picks a solidário by name."""

    nome: str
    documento: Optional[str] = None


def _to_utc_iso(dt: Optional[datetime]) -> Optional[str]:
    # MSSQL DateTime columns and ``datetime.utcnow()`` are naive; tag them
    # as UTC on the wire so the frontend's ISO-with-offset Zod check passes.
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


# ----- Approval payloads ---------------------------------------------------


class ObrigacaoReview(BaseModel):
    """Reviewer-editable fields, one-to-one with ``ObrigacaoORM`` (minus the
    auto-assigned ``IdObrigacao`` PK). The identity triple is accepted for
    round-trip convenience but is ignored by the service — the final row's
    triple is authoritative. Edited values land on the ``ObrigacaoStaging``
    audit row, never on the final ``Obrigacao`` row.
    """

    id_processo: Optional[int] = None
    id_composicao_pauta: Optional[int] = None
    id_voto_pauta: Optional[int] = None

    descricao_obrigacao: str
    de_fazer: Optional[bool] = True
    prazo: Optional[str] = None
    data_cumprimento: Optional[date] = None
    orgao_responsavel: Optional[str] = None
    id_orgao_responsavel: Optional[int] = None
    tem_multa_cominatoria: Optional[bool] = False
    nome_responsavel_multa_cominatoria: Optional[str] = None
    documento_responsavel_multa_cominatoria: Optional[str] = None
    id_pessoa_multa_cominatoria: Optional[int] = None
    valor_multa_cominatoria: Optional[float] = None
    periodo_multa_cominatoria: Optional[str] = None
    e_multa_cominatoria_solidaria: Optional[bool] = False
    solidarios_multa_cominatoria: Optional[list[SolidarioMulta]] = None


class RecomendacaoReview(BaseModel):
    """Reviewer-editable fields, one-to-one with ``RecomendacaoORM`` (minus
    the auto-assigned ``IdRecomendacao`` PK)."""

    id_processo: Optional[int] = None
    id_composicao_pauta: Optional[int] = None
    id_voto_pauta: Optional[int] = None

    descricao_recomendacao: Optional[str] = None
    prazo_cumprimento_recomendacao: Optional[str] = None
    data_cumprimento_recomendacao: Optional[date] = None
    nome_responsavel: Optional[str] = None
    id_pessoa_responsavel: Optional[int] = None
    orgao_responsavel: Optional[str] = None
    id_orgao_responsavel: Optional[int] = None
    cancelado: Optional[bool] = None


# ----- List / detail responses --------------------------------------------


class ReviewListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: Kind
    status: ReviewStatusStr
    descricao: str
    id_processo: int
    id_composicao_pauta: int
    id_voto_pauta: int
    # Resolved from ``processo.dbo.Processos`` so the list shows the
    # human-readable ``"<numero>/<ano>"``. Both may be ``None`` when the
    # MSSQL lookup fails — the frontend falls back to ``id_processo``.
    numero_processo: Optional[int] = None
    ano_processo: Optional[int] = None
    claimed_by: Optional[str] = None
    claimed_at: Optional[datetime] = None
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    @field_serializer("claimed_at", "reviewed_at")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class ReviewListPage(BaseModel):
    items: list[ReviewListItem]
    page: int
    page_size: int
    total: int


class AwaitingDispatchItem(BaseModel):
    """Approved staging row awaiting downstream dispatch.

    Fed by the union of ``ObrigacaoStaging`` + ``RecomendacaoStaging`` rows
    with ``Status=approved``. The frontend lists these so reviewers / admins
    can see what's been approved but not yet sent to downstream consumers.
    """

    id: int  # final-row id (IdObrigacao / IdRecomendacao)
    kind: Kind
    id_processo: int
    numero_processo: Optional[int] = None
    ano_processo: Optional[int] = None
    descricao: str
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    @field_serializer("reviewed_at")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class AwaitingDispatchPage(BaseModel):
    items: list[AwaitingDispatchItem]
    page: int
    page_size: int
    total: int


class ReviewDetail(BaseModel):
    id: int  # IdObrigacao / IdRecomendacao (final-table id)
    kind: Kind
    status: ReviewStatusStr

    id_processo: int
    id_composicao_pauta: int
    id_voto_pauta: int

    # Currently displayed values: pending → final-row fields; approved/rejected
    # → audit-row (reviewer-edited) fields.
    staged: dict[str, Any]
    # When status != pending, holds the immutable LLM extraction from the final
    # row so reviewers can compare what they edited against the original.
    original_payload: Optional[dict[str, Any]] = None

    claimed_by: Optional[str] = None
    claimed_at: Optional[datetime] = None
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None

    @field_serializer("claimed_at", "reviewed_at")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class ReviewTexto(BaseModel):
    """Full ``texto_acordao`` plus span-match metadata, fetched separately so
    the detail form can render before the (slow) MSSQL text query returns.

    ``numero_processo`` / ``ano_processo`` come from the same MSSQL query
    (Processos table) and are surfaced here so the reviewer-facing header can
    show the human-readable ``"<numero>/<ano>"`` instead of the internal
    ``IdProcesso``. Both may be ``None`` when the query fails or the row is
    missing — the frontend falls back to ``id_processo`` from ``ReviewDetail``.
    """

    texto_acordao: Optional[str] = None
    matched_span: Optional[str] = None
    span_match_status: SpanMatchStatusStr
    numero_processo: Optional[int] = None
    ano_processo: Optional[int] = None
    pessoas: list[Pessoa] = Field(default_factory=list)
    relatorio: Optional[str] = None
    fundamentacao_voto: Optional[str] = None
    conclusao: Optional[str] = None
    orgao_responsavel: Optional[str] = None
    orgao_origem: Optional[str] = None
    interessado: Optional[str] = None


# ----- Claim / reject -----------------------------------------------------


class ClaimResponse(BaseModel):
    claimed_by: str
    claimed_at: datetime
    expires_at: datetime

    @field_serializer("claimed_at", "expires_at")
    def _ser_dt(self, v: datetime) -> str:
        return _to_utc_iso(v)  # type: ignore[return-value]


class RejectRequest(BaseModel):
    review_notes: str = Field(min_length=10)
