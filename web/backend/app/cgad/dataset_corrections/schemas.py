"""Pydantic DTOs for the dataset-corrections endpoints."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


DecisionStatus = Literal["pending", "accept", "reject", "custom", "mixed"]
DecisionKind = Literal["accept", "reject", "custom"]


class NerSpanDto(BaseModel):
    char_start: int
    char_end: int
    label: str


# ----- Tokens & groups (mapped errors) -----------------------------------


class TokenInGroup(BaseModel):
    """One token rendered inside an entity group. ``label_sugerido`` /
    ``confianca`` are present only for tokens that came from the cleanlab
    CSV; ``row_id`` lets the UI reference the underlying error row."""

    token_idx_in_doc: int
    text: str
    char_start: int
    char_end: int
    bio_original: str
    label_sugerido: Optional[str] = None
    confianca: Optional[float] = None
    row_id: Optional[int] = None
    is_flagged: bool


class EntityGroupDto(BaseModel):
    group_id: str
    document_id: int
    first_token_idx: int
    last_token_idx: int
    char_start: int
    char_end: int
    gold_entity_label: Optional[str] = (
        None  # MULTA / OBRIGACAO / ... or None for free groups
    )
    tokens: list[TokenInGroup]
    flagged_row_ids: list[int]
    status: DecisionStatus
    entity_label_final: Optional[str] = None  # filled for custom; "O" / "MULTA" / ...
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None


class GroupDecisionRequest(BaseModel):
    decision: DecisionKind
    entity_label: Optional[str] = Field(
        default=None,
        description=(
            "Required when decision == 'custom'. One of "
            "O / MULTA / OBRIGACAO / RESSARCIMENTO / RECOMENDACAO."
        ),
    )
    first_token_idx: Optional[int] = Field(
        default=None,
        description=(
            "Optional first token of the persisted entity. Only honoured for "
            "'custom' decisions; lets the reviewer extend or shrink the "
            "group's natural range. Must be paired with last_token_idx."
        ),
    )
    last_token_idx: Optional[int] = Field(
        default=None,
        description=(
            "Optional last token (inclusive) of the persisted entity. See "
            "first_token_idx."
        ),
    )


class GroupDecisionResponse(BaseModel):
    group_id: str
    status: DecisionStatus
    entity_label_final: Optional[str]
    decided_by: Optional[str]
    decided_at: Optional[str]


# ----- Document list / detail --------------------------------------------


class DocumentListItem(BaseModel):
    document_id: int
    text_preview: str
    group_count: int
    decided_group_count: int


class DocumentListPage(BaseModel):
    items: list[DocumentListItem]
    page: int
    page_size: int
    total: int


class DocumentToken(BaseModel):
    """One token from the document, surfaced so the UI can let the
    reviewer extend a group beyond its natural range."""

    token_idx_in_doc: int
    text: str
    char_start: int
    char_end: int
    bio: str


class DocumentDetail(BaseModel):
    document_id: int
    text: str
    ner_spans: list[NerSpanDto]
    groups: list[EntityGroupDto]
    tokens: list[DocumentToken]


# ----- Unmapped errors ---------------------------------------------------


class UnmappedError(BaseModel):
    row_id: int
    sentenca_idx: int
    token: str
    contexto: str
    label_original: str
    label_sugerido: str
    confianca: float
    status: DecisionStatus
    label_final: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None


class UnmappedListPage(BaseModel):
    items: list[UnmappedError]
    page: int
    page_size: int
    total: int


class UnmappedDecisionRequest(BaseModel):
    decision: DecisionKind
    label_final: Optional[str] = Field(
        default=None, description="Required when decision == 'custom'. BIO label."
    )


class UnmappedDecisionResponse(BaseModel):
    row_id: int
    status: DecisionStatus
    label_final: Optional[str]
    decided_by: Optional[str]
    decided_at: Optional[str]


# ----- Progress / labels -------------------------------------------------


class Progress(BaseModel):
    total: int
    decided: int
    accept: int
    reject: int
    custom: int
    mixed: int
    unmapped_total: int
    unmapped_decided: int


class LabelsResponse(BaseModel):
    labels: list[str]
    entity_labels: list[str]


# ----- Export ------------------------------------------------------------


class ExportSource(BaseModel):
    csv: str
    csv_mtime: float
    csv_rows: int
    json_path: str = Field(serialization_alias="json")


class ExportTokenChange(BaseModel):
    document_id: int
    token_idx_in_doc: int
    label_final: str
    decision: DecisionKind
    group_id: str
    row_id: Optional[int] = None
    decided_by: str
    decided_at: str


class ExportUnmappedChange(BaseModel):
    row_id: int
    sentenca_idx: int
    token: str
    label_original: str
    label_sugerido: str
    label_final: str
    decision: DecisionKind
    decided_by: str
    decided_at: str


class ExportSummary(BaseModel):
    groups_total: int
    groups_decided: int
    accept: int
    reject: int
    custom: int
    mixed: int
    token_changes: int
    unmapped_total: int
    unmapped_decided: int


class ExportPayload(BaseModel):
    version: Literal["2"] = "2"
    generated_at: str
    source: ExportSource
    token_changes: list[ExportTokenChange]
    unmapped_changes: list[ExportUnmappedChange]
    summary: ExportSummary
