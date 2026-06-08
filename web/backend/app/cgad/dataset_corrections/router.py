"""Admin-only endpoints for reviewing cleanlab token-level error flags.

Decisions are made at the entity-group level (a contiguous range of tokens
forming one named entity) rather than per token.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.cgad.dataset_corrections import schemas, service
from app.cgad.dataset_corrections.paths import ERRORS_CSV, LABELED_JSON, REPO_ROOT
from app.cgad.dataset_corrections.service import EntityGroup, ErrorRow, State
from app.deps import require_role
from cgad.models import UserORM


router = APIRouter(
    prefix="/api/v1/cgad/admin/dataset-corrections",
    tags=["dataset-corrections"],
    dependencies=[Depends(require_role("admin"))],
)


# ----- Helpers ------------------------------------------------------------


def _entity_labels_from_bio(bio_labels: list[str]) -> list[str]:
    seen: set[str] = {"O"}
    for lab in bio_labels:
        if lab == "O":
            continue
        if lab[:2] in ("B-", "I-"):
            seen.add(lab[2:])
    order = ["O", "MULTA", "OBRIGACAO", "RESSARCIMENTO", "RECOMENDACAO"]
    return [x for x in order if x in seen] + sorted(x for x in seen if x not in order)


def _text_preview(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "…"


def _group_to_dto(state: State, group: EntityGroup) -> schemas.EntityGroupDto:
    doc = state.documents_by_id[group.document_id]
    flagged_idx_to_error: dict[int, ErrorRow] = {
        state.errors_by_row_id[rid].token_idx_in_doc: state.errors_by_row_id[rid]
        for rid in group.flagged_row_ids
    }
    tokens: list[schemas.TokenInGroup] = []
    for idx in range(group.first_token_idx, group.last_token_idx + 1):
        if idx >= len(doc.tokens):
            break
        tok = doc.tokens[idx]
        err = flagged_idx_to_error.get(idx)
        tokens.append(
            schemas.TokenInGroup(
                token_idx_in_doc=idx,
                text=tok.text,
                char_start=tok.char_start,
                char_end=tok.char_end,
                bio_original=err.label_original if err is not None else tok.bio,
                label_sugerido=err.label_sugerido if err is not None else None,
                confianca=err.confianca if err is not None else None,
                row_id=err.row_id if err is not None else None,
                is_flagged=err is not None,
            )
        )
    status_str, entity_label, decided_by, decided_at = service.group_status(
        state, group
    )
    return schemas.EntityGroupDto(
        group_id=group.group_id,
        document_id=group.document_id,
        first_token_idx=group.first_token_idx,
        last_token_idx=group.last_token_idx,
        char_start=group.char_start,
        char_end=group.char_end,
        gold_entity_label=group.gold_entity_label,
        tokens=tokens,
        flagged_row_ids=list(group.flagged_row_ids),
        status=status_str,  # type: ignore[arg-type]
        entity_label_final=entity_label,
        decided_by=decided_by,
        decided_at=decided_at,
    )


def _group_max_confidence(state: State, group: EntityGroup) -> float:
    return max(
        (state.errors_by_row_id[rid].confianca for rid in group.flagged_row_ids),
        default=0.0,
    )


# ----- Documents list & detail -------------------------------------------


@router.get("/documents", response_model=schemas.DocumentListPage)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=2000),
    only_pending: bool = Query(False),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
) -> schemas.DocumentListPage:
    state = service.get_state()
    items: list[schemas.DocumentListItem] = []
    for doc_id, group_ids in state.groups_by_document.items():
        kept_groups = [
            state.groups_by_id[gid]
            for gid in group_ids
            if _group_max_confidence(state, state.groups_by_id[gid]) >= min_confidence
        ]
        if not kept_groups:
            continue
        decided = sum(
            1 for g in kept_groups if service.group_status(state, g)[0] != "pending"
        )
        if only_pending and decided >= len(kept_groups):
            continue
        doc = state.documents_by_id[doc_id]
        items.append(
            schemas.DocumentListItem(
                document_id=doc_id,
                text_preview=_text_preview(doc.text),
                group_count=len(kept_groups),
                decided_group_count=decided,
            )
        )
    items.sort(key=lambda x: x.document_id)
    total = len(items)
    page_items = items[(page - 1) * page_size : (page - 1) * page_size + page_size]
    return schemas.DocumentListPage(
        items=page_items, page=page, page_size=page_size, total=total
    )


@router.get("/documents/{document_id}", response_model=schemas.DocumentDetail)
def get_document(
    document_id: int,
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
) -> schemas.DocumentDetail:
    state = service.get_state()
    doc = state.documents_by_id.get(document_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="document not found"
        )
    group_ids = state.groups_by_document.get(document_id, [])
    groups = [
        _group_to_dto(state, state.groups_by_id[gid])
        for gid in group_ids
        if _group_max_confidence(state, state.groups_by_id[gid]) >= min_confidence
    ]
    return schemas.DocumentDetail(
        document_id=document_id,
        text=doc.text,
        ner_spans=[
            schemas.NerSpanDto(
                char_start=s.char_start, char_end=s.char_end, label=s.label
            )
            for s in doc.ner_spans
        ],
        groups=groups,
        tokens=[
            schemas.DocumentToken(
                token_idx_in_doc=i,
                text=tok.text,
                char_start=tok.char_start,
                char_end=tok.char_end,
                bio=tok.bio,
            )
            for i, tok in enumerate(doc.tokens)
        ],
    )


# ----- Group decision ----------------------------------------------------


@router.post("/groups/{group_id}/decide", response_model=schemas.GroupDecisionResponse)
def decide_group(
    group_id: str,
    body: schemas.GroupDecisionRequest,
    user: UserORM = Depends(require_role("admin")),
) -> schemas.GroupDecisionResponse:
    state = service.get_state()
    range_override: tuple[int, int] | None = None
    if body.first_token_idx is not None or body.last_token_idx is not None:
        if body.first_token_idx is None or body.last_token_idx is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="first_token_idx and last_token_idx must be provided together",
            )
        if body.decision != "custom":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="range override is only valid with decision='custom'",
            )
        range_override = (body.first_token_idx, body.last_token_idx)
    try:
        group = service.record_group_decision(
            state,
            group_id=group_id,
            decision=body.decision,
            entity_label=body.entity_label,
            decided_by=user.Email or user.NomeUsuario,
            range_override=range_override,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="group not found"
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    status_str, entity_label, decided_by, decided_at = service.group_status(
        state, group
    )
    return schemas.GroupDecisionResponse(
        group_id=group.group_id,
        status=status_str,  # type: ignore[arg-type]
        entity_label_final=entity_label,
        decided_by=decided_by,
        decided_at=decided_at,
    )


# ----- Unmapped errors ---------------------------------------------------


@router.get("/unmapped", response_model=schemas.UnmappedListPage)
def list_unmapped(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
) -> schemas.UnmappedListPage:
    state = service.get_state()
    filtered = [
        rid
        for rid in state.unmapped_row_ids
        if state.errors_by_row_id[rid].confianca >= min_confidence
    ]
    total = len(filtered)
    sliced = filtered[(page - 1) * page_size : (page - 1) * page_size + page_size]
    items: list[schemas.UnmappedError] = []
    for row_id in sliced:
        e = state.errors_by_row_id[row_id]
        rec = state.decisions_by_unmapped.get(row_id)
        items.append(
            schemas.UnmappedError(
                row_id=e.row_id,
                sentenca_idx=e.sentenca_idx,
                token=e.token,
                contexto=e.contexto,
                label_original=e.label_original,
                label_sugerido=e.label_sugerido,
                confianca=e.confianca,
                status=rec.decision if rec else "pending",
                label_final=rec.label_final if rec else None,
                decided_by=rec.decided_by if rec else None,
                decided_at=rec.decided_at if rec else None,
            )
        )
    return schemas.UnmappedListPage(
        items=items, page=page, page_size=page_size, total=total
    )


@router.post(
    "/unmapped/{row_id}/decide", response_model=schemas.UnmappedDecisionResponse
)
def decide_unmapped(
    row_id: int,
    body: schemas.UnmappedDecisionRequest,
    user: UserORM = Depends(require_role("admin")),
) -> schemas.UnmappedDecisionResponse:
    state = service.get_state()
    try:
        record = service.record_unmapped_decision(
            state,
            row_id=row_id,
            decision=body.decision,
            label_final=body.label_final,
            decided_by=user.Email or user.NomeUsuario,
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="row_id not found"
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return schemas.UnmappedDecisionResponse(
        row_id=record.row_id,
        status=record.decision,
        label_final=record.label_final,
        decided_by=record.decided_by,
        decided_at=record.decided_at,
    )


# ----- Progress + labels -------------------------------------------------


@router.get("/progress", response_model=schemas.Progress)
def progress() -> schemas.Progress:
    state = service.get_state()
    return schemas.Progress(**service.progress_counts(state))


@router.get("/labels", response_model=schemas.LabelsResponse)
def labels() -> schemas.LabelsResponse:
    state = service.get_state()
    return schemas.LabelsResponse(
        labels=state.available_labels,
        entity_labels=service.ENTITY_LABELS,
    )


# ----- Export -------------------------------------------------------------


@router.get("/export")
def export_decisions() -> JSONResponse:
    state = service.get_state()
    counts = {"accept": 0, "reject": 0, "custom": 0, "mixed": 0}
    decided_groups = 0
    for group in state.groups_by_id.values():
        gstatus, *_ = service.group_status(state, group)
        if gstatus == "pending":
            continue
        decided_groups += 1
        counts[gstatus] = counts.get(gstatus, 0) + 1

    token_changes = [
        schemas.ExportTokenChange(
            document_id=rec.document_id,
            token_idx_in_doc=rec.token_idx_in_doc,
            label_final=rec.label_final,
            decision=rec.decision,
            group_id=rec.group_id,
            row_id=rec.row_id,
            decided_by=rec.decided_by,
            decided_at=rec.decided_at,
        )
        for rec in sorted(
            state.decisions_by_token.values(),
            key=lambda r: (r.document_id, r.token_idx_in_doc),
        )
    ]
    unmapped_changes = [
        schemas.ExportUnmappedChange(
            row_id=rid,
            sentenca_idx=state.errors_by_row_id[rid].sentenca_idx,
            token=state.errors_by_row_id[rid].token,
            label_original=state.errors_by_row_id[rid].label_original,
            label_sugerido=state.errors_by_row_id[rid].label_sugerido,
            label_final=rec.label_final,
            decision=rec.decision,
            decided_by=rec.decided_by,
            decided_at=rec.decided_at,
        )
        for rid, rec in sorted(state.decisions_by_unmapped.items())
    ]

    payload = schemas.ExportPayload(
        version="2",
        generated_at=datetime.now(timezone.utc).isoformat(),
        source=schemas.ExportSource(
            csv=str(ERRORS_CSV.relative_to(REPO_ROOT)).replace("\\", "/"),
            csv_mtime=ERRORS_CSV.stat().st_mtime,
            csv_rows=len(state.errors),
            json_path=str(LABELED_JSON.relative_to(REPO_ROOT)).replace("\\", "/"),
        ),
        token_changes=token_changes,
        unmapped_changes=unmapped_changes,
        summary=schemas.ExportSummary(
            groups_total=len(state.groups_by_id),
            groups_decided=decided_groups,
            accept=counts["accept"],
            reject=counts["reject"],
            custom=counts["custom"],
            mixed=counts["mixed"],
            token_changes=len(token_changes),
            unmapped_total=len(state.unmapped_row_ids),
            unmapped_decided=len(state.decisions_by_unmapped),
        ),
    )
    return JSONResponse(
        content=payload.model_dump(by_alias=True),
        headers={
            "Content-Disposition": 'attachment; filename="dataset-corrections.json"'
        },
    )


# ----- Misc ---------------------------------------------------------------


_ = Optional  # silence unused import
