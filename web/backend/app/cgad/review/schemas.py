"""DTOs for the decision-level review API.

The review unit is one decision (``NERDecisao``), which carries N entities of
four types: multa, obrigação, recomendação, ressarcimento. The reviewer edits
or rejects each entity, may add new ones, and approves the whole decision in
one POST — the service persists everything in a single transaction as
``*Staging`` audit rows.

All human-facing field names stay snake_case (Pydantic convention + matches
the stage-2 schemas in ``cgad/schema.py``). The service layer translates to
the staging ORMs' PascalCase Portuguese columns.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator


Tipo = Literal["multa", "obrigacao", "recomendacao", "ressarcimento"]
ReviewStatusStr = Literal["pending", "approved", "rejected"]
SpanMatchStatusStr = Literal["exact", "fuzzy", "not_found"]


class SolidarioMulta(BaseModel):
    """One co-responsible person on a multa solidária. ``nome`` comes from the
    LLM extraction; ``documento`` is filled by the reviewer (typically by
    picking from ``DecisaoTexto.pessoas``)."""

    nome: str
    documento: Optional[str] = None


class PessoaCargo(BaseModel):
    """One cargo found for a pessoa in the external bases — Anexo 42 (BdSIAI,
    gestores de unidade jurisdicionada) or SIAI Pessoal (BdSIAIPessoal, folha)."""

    fonte: Literal["anexo42", "siai_pessoal"]
    cargo: str
    orgao: Optional[str] = None
    inicio: Optional[date] = None
    fim: Optional[date] = None


class Pessoa(BaseModel):
    """Person associated with the process — surfaced in ``DecisaoTexto.pessoas``
    so forms can autocomplete ``documento``."""

    nome: str
    documento: Optional[str] = None
    cargos: list[PessoaCargo] = []


class OrgaoOut(BaseModel):
    """Órgão de ``processo.dbo.Orgaos`` — opções do campo Órgão responsável."""

    id: int
    nome: str


def _to_utc_iso(dt: Optional[datetime]) -> Optional[str]:
    # MSSQL DateTime columns and ``datetime.utcnow()`` are naive; tag them
    # as UTC on the wire so the frontend's ISO-with-offset Zod check passes.
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


# ----- Per-type editable fields --------------------------------------------


class ObrigacaoFields(BaseModel):
    """Reviewer-editable fields, one-to-one with ``ObrigacaoStagingORM``."""

    tipo: Literal["obrigacao"] = "obrigacao"

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


class RecomendacaoFields(BaseModel):
    tipo: Literal["recomendacao"] = "recomendacao"

    descricao_recomendacao: str
    prazo_cumprimento_recomendacao: Optional[str] = None
    data_cumprimento_recomendacao: Optional[date] = None
    nome_responsavel: Optional[str] = None
    id_pessoa_responsavel: Optional[int] = None
    orgao_responsavel: Optional[str] = None
    id_orgao_responsavel: Optional[int] = None
    cancelado: Optional[bool] = None


class MultaFields(BaseModel):
    tipo: Literal["multa"] = "multa"

    descricao_multa: str
    valor_fixo: Optional[float] = None
    percentual: Optional[float] = None
    base_calculo: Optional[float] = None
    nome_responsavel: Optional[str] = None
    documento_responsavel: Optional[str] = None
    e_multa_solidaria: Optional[bool] = False
    solidarios: Optional[list[SolidarioMulta]] = None


class RessarcimentoFields(BaseModel):
    tipo: Literal["ressarcimento"] = "ressarcimento"

    descricao_ressarcimento: str
    valor_dano: Optional[float] = None
    percentual_imputado: Optional[float] = None
    valor_imputado: Optional[float] = None
    nome_responsavel: Optional[str] = None
    documento_responsavel: Optional[str] = None


EntidadeFields = Union[MultaFields, ObrigacaoFields, RecomendacaoFields, RessarcimentoFields]


# ----- Approval payload -----------------------------------------------------


class EntidadeReview(BaseModel):
    """One entity inside the decision approve payload.

    ``id_ner`` is the NER-row id; ``None`` means the reviewer added this
    entity by selecting a span the extractor missed (only valid with
    ``resultado="approved"``). Rejections may carry an optional motive in
    ``observacoes`` and don't need ``campos``.
    """

    tipo: Tipo
    id_ner: Optional[int] = None
    resultado: Literal["approved", "rejected"]
    observacoes: Optional[str] = None
    campos: Optional[EntidadeFields] = Field(None, discriminator="tipo")

    @model_validator(mode="after")
    def _check(self) -> "EntidadeReview":
        if self.campos is not None and self.campos.tipo != self.tipo:
            raise ValueError("campos.tipo diverge de tipo")
        if self.resultado == "approved" and self.campos is None:
            raise ValueError("entidade aprovada exige campos")
        if self.resultado == "rejected" and self.id_ner is None:
            raise ValueError("entidade adicionada não pode ser rejeitada")
        return self


class DecisaoReviewPayload(BaseModel):
    entidades: list[EntidadeReview]


# ----- List / detail responses ----------------------------------------------


class DecisaoListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int  # IdNerDecisao
    id_processo: int
    id_composicao_pauta: int
    id_voto_pauta: int
    numero_processo: Optional[int] = None
    ano_processo: Optional[int] = None
    # Número do acórdão/decisão colegiada (numeroResultado/anoResultado da
    # vw_ia_votos_acordaos_decisoes); tipo: "A" = Acórdão, "D" = Decisão.
    numero_acordao: Optional[str] = None
    ano_acordao: Optional[str] = None
    tipo_acordao: Optional[str] = None
    data_extracao: Optional[datetime] = None
    multas: int
    obrigacoes: int
    recomendacoes: int
    ressarcimentos: int
    claimed_by: Optional[str] = None
    claimed_at: Optional[datetime] = None

    @field_serializer("data_extracao", "claimed_at")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class DecisaoListPage(BaseModel):
    items: list[DecisaoListItem]
    page: int
    page_size: int
    total: int


class EntidadeOut(BaseModel):
    """One entity of the decision as shown to the reviewer.

    ``campos`` uses the snake_case field names of the matching ``*Fields``
    model. For obrigação/recomendação they come from the stage-2 final row
    when it exists; multa/ressarcimento start with just the NER description
    (stage-1 extracts no structured fields for them). Entities already
    reviewed (``status != pending``) are rendered read-only by the frontend
    and must not appear in the approve payload.
    """

    tipo: Tipo
    id_ner: int
    descricao: str
    status: ReviewStatusStr
    campos: dict[str, Any]
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    observacoes: Optional[str] = None

    @field_serializer("reviewed_at")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class DecisaoDetail(BaseModel):
    id: int
    id_processo: int
    id_composicao_pauta: int
    id_voto_pauta: int
    data_extracao: Optional[datetime] = None
    claimed_by: Optional[str] = None
    claimed_at: Optional[datetime] = None
    revisado_por: Optional[str] = None
    data_revisao: Optional[datetime] = None
    entidades: list[EntidadeOut]
    # Preenchido apenas pelo approve: a próxima decisão da fila (sem revisão e
    # sem reserva ativa), para o revisor emendar uma na outra.
    proximo_id: Optional[int] = None

    @field_serializer("data_extracao", "claimed_at", "data_revisao")
    def _ser_dt(self, v: Optional[datetime]) -> Optional[str]:
        return _to_utc_iso(v)


class EntidadeSpan(BaseModel):
    """Character offsets of one entity's description inside ``texto_acordao``,
    re-derived at read time (nothing persisted). ``not_found`` → offsets are
    ``None`` and the entity is only shown in the side panel."""

    id_ner: int
    tipo: Tipo
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    match_status: SpanMatchStatusStr


class DecisaoTexto(BaseModel):
    """Full ``texto_acordao`` plus per-entity span offsets, fetched separately
    so the detail screen can render before the (slow) MSSQL text query
    returns."""

    texto_acordao: Optional[str] = None
    numero_processo: Optional[int] = None
    ano_processo: Optional[int] = None
    numero_acordao: Optional[str] = None
    ano_acordao: Optional[str] = None
    tipo_acordao: Optional[str] = None
    pessoas: list[Pessoa] = Field(default_factory=list)
    relatorio: Optional[str] = None
    fundamentacao_voto: Optional[str] = None
    conclusao: Optional[str] = None
    orgao_responsavel: Optional[str] = None
    orgao_origem: Optional[str] = None
    interessado: Optional[str] = None
    spans: list[EntidadeSpan] = Field(default_factory=list)


# ----- Awaiting dispatch -----------------------------------------------------


class AwaitingDispatchItem(BaseModel):
    """Approved staging row awaiting downstream dispatch — union of the four
    ``*Staging`` tables with ``Status=approved``. ``id`` is the staging PK."""

    id: int
    tipo: Tipo
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


# ----- Claim ------------------------------------------------------------------


class ClaimResponse(BaseModel):
    claimed_by: str
    claimed_at: datetime
    expires_at: datetime

    @field_serializer("claimed_at", "expires_at")
    def _ser_dt(self, v: datetime) -> str:
        return _to_utc_iso(v)  # type: ignore[return-value]
