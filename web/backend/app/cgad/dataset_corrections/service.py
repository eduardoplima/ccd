"""In-memory orchestration for the dataset-corrections feature.

Loads the dataset, the cleanlab CSV, computes entity groups, and replays
persisted decisions on first use; everything is then kept in module-level
state guarded by a load lock.

Decisions are made per **entity group**, not per token. A group is either
the full gold NER span containing one or more flagged tokens, or — for
flagged tokens that don't fall in any gold span — a maximal contiguous
run of such tokens.
"""

from __future__ import annotations

import csv
import logging
import threading
from dataclasses import dataclass, field
from typing import Optional

from app.cgad.dataset_corrections import store
from app.cgad.dataset_corrections.dataset import (
    Dataset,
    Document,
    NerSpan,
    Token,
    available_bio_labels,
    load_dataset,
)
from app.cgad.dataset_corrections.paths import ERRORS_CSV
from app.cgad.dataset_corrections.store import (
    DecisionKind,
    LoadedDecisions,
    TokenDecision,
    UnmappedDecision,
    append_token_decisions,
    append_unmapped_decision,
    now_iso,
)


logger = logging.getLogger(__name__)


# Entity-level labels exposed for "custom" group decisions. The BIO sequence
# is generated from these (B-X for the first token, I-X for the rest, or
# all O when entity_label is "O").
ENTITY_LABELS = ["O", "MULTA", "OBRIGACAO", "RESSARCIMENTO", "RECOMENDACAO"]


@dataclass(frozen=True)
class ErrorRow:
    row_id: int
    sentenca_idx: int
    document_id: int
    token: str
    label_original: str
    label_sugerido: str
    confianca: float
    contexto: str
    token_idx_in_doc: int


@dataclass(frozen=True)
class EntityGroup:
    """A unit of decision: a contiguous range of tokens that the reviewer
    accepts/rejects/customises as a single entity."""

    group_id: str  # f"{document_id}:{first_token_idx}-{last_token_idx}"
    document_id: int
    first_token_idx: int
    last_token_idx: int
    char_start: int
    char_end: int
    flagged_row_ids: tuple[int, ...]
    gold_entity_label: Optional[str]  # None when the group is a "free" run


@dataclass
class State:
    dataset: Dataset
    documents_by_id: dict[int, Document]
    errors: list[ErrorRow]
    errors_by_row_id: dict[int, ErrorRow]
    errors_by_document: dict[int, list[int]]
    unmapped_row_ids: list[int]
    available_labels: list[str]
    groups_by_id: dict[str, EntityGroup]
    groups_by_document: dict[int, list[str]]
    decisions_by_token: dict[tuple[int, int], TokenDecision] = field(
        default_factory=dict
    )
    decisions_by_unmapped: dict[int, UnmappedDecision] = field(default_factory=dict)


_state: State | None = None
_load_lock = threading.Lock()


# ----- Token resolution (CSV → document) -----------------------------------


def _trigrams(text: str) -> set[str]:
    text = text.lower()
    return {text[i : i + 3] for i in range(len(text) - 2)} if len(text) >= 3 else set()


def _locate_token_in_doc(token: str, contexto: str, tokens: list[Token]) -> int:
    occurrences = [i for i, t in enumerate(tokens) if t.text == token]
    if not occurrences:
        return -1
    if len(occurrences) == 1:
        return occurrences[0]
    target_grams = _trigrams(contexto)
    if not target_grams:
        return occurrences[0]
    best_idx = occurrences[0]
    best_score = -1.0
    for i in occurrences:
        window = " ".join(t.text for t in tokens[max(0, i - 5) : i + 6])
        grams = _trigrams(window)
        if not grams:
            continue
        score = len(grams & target_grams) / len(grams | target_grams)
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx


def _parse_errors(dataset: Dataset) -> list[ErrorRow]:
    rows: list[ErrorRow] = []
    sentencas = dataset.sentencas_doc_ids
    docs_by_id = {d.document_id: d for d in dataset.documents}
    with ERRORS_CSV.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row_id, raw in enumerate(reader):
            sent_idx = int(raw["sentenca_idx"])
            try:
                conf = float(raw["confianca"])
            except (TypeError, ValueError):
                conf = 0.0
            token = raw["token"]
            contexto = raw.get("contexto") or ""
            doc_id = sentencas[sent_idx] if 0 <= sent_idx < len(sentencas) else -1
            doc = docs_by_id.get(doc_id) if doc_id >= 0 else None
            tok_idx = _locate_token_in_doc(token, contexto, doc.tokens) if doc else -1
            rows.append(
                ErrorRow(
                    row_id=row_id,
                    sentenca_idx=sent_idx,
                    document_id=doc_id if doc is not None else -1,
                    token=token,
                    label_original=raw["label_original"],
                    label_sugerido=raw["label_sugerido"],
                    confianca=conf,
                    contexto=contexto,
                    token_idx_in_doc=tok_idx,
                )
            )
    return rows


# ----- Group computation --------------------------------------------------


def _entity_or_none(bio: str) -> str | None:
    if bio == "O" or not bio:
        return None
    if bio[:2] in ("B-", "I-"):
        return bio[2:]
    return bio


def _span_token_range(span: NerSpan, tokens: list[Token]) -> tuple[int, int] | None:
    """Token indices [first, last] (inclusive) of a gold span."""
    overlapping = [
        i
        for i, tok in enumerate(tokens)
        if tok.char_start < span.char_end and tok.char_end > span.char_start
    ]
    if not overlapping:
        return None
    return overlapping[0], overlapping[-1]


def _compute_groups_for_doc(doc: Document, errors: list[ErrorRow]) -> list[EntityGroup]:
    """Group flagged tokens into entity-level review units.

    Two ways a group is formed:

    1. **Gold span containing a flagged token** — the whole gold span (all
       its tokens, flagged or not) becomes one group. This preserves the
       reviewer's mental model of "review one named entity at a time"
       even when only part of the span is contested by cleanlab.
    2. **Free chains outside any gold span** — for tokens that don't belong
       to a gold span, we walk an "implied" label sequence (cleanlab's
       suggestion for flagged tokens, gold BIO for the rest, but here gold
       is always O since they're outside any span) and find maximal runs of
       non-O suggestions of the same entity, jumping across O suggestions.
       A chain becomes a group when it contains at least one flagged token.

    The free-chain bridging is what lets a doc whose flagged tokens all
    suggest ``I-MULTA`` collapse into one chain even when the underlying
    text has unflagged-O gaps — matching the reviewer's expectation that
    everything the model considered part of one entity should be reviewed
    as one entity.
    """
    flagged_idx_to_row: dict[int, list[int]] = {}
    error_by_idx: dict[int, ErrorRow] = {}
    for e in errors:
        if e.token_idx_in_doc < 0:
            continue
        flagged_idx_to_row.setdefault(e.token_idx_in_doc, []).append(e.row_id)
        error_by_idx.setdefault(e.token_idx_in_doc, e)
    if not flagged_idx_to_row:
        return []

    used_token_idxs: set[int] = set()
    groups: list[EntityGroup] = []

    # Phase 1 — gold-span groups
    for span in doc.ner_spans:
        rng = _span_token_range(span, doc.tokens)
        if rng is None:
            continue
        first, last = rng
        span_range = range(first, last + 1)
        flagged_in_span = [i for i in span_range if i in flagged_idx_to_row]
        if not flagged_in_span:
            continue
        flagged_rows = sorted(
            rid for i in flagged_in_span for rid in flagged_idx_to_row[i]
        )
        groups.append(
            EntityGroup(
                group_id=f"{doc.document_id}:{first}-{last}",
                document_id=doc.document_id,
                first_token_idx=first,
                last_token_idx=last,
                char_start=doc.tokens[first].char_start,
                char_end=doc.tokens[last].char_end,
                flagged_row_ids=tuple(flagged_rows),
                gold_entity_label=span.label,
            )
        )
        used_token_idxs.update(span_range)

    # Phase 2 — free chains, with O-suggestion bridging within the same entity
    def implied(i: int) -> str:
        return (
            error_by_idx[i].label_sugerido if i in error_by_idx else doc.tokens[i].bio
        )

    n = len(doc.tokens)
    i = 0
    while i < n:
        if i in used_token_idxs:
            i += 1
            continue
        if implied(i) == "O":
            i += 1
            continue
        entity = _entity_or_none(implied(i))
        if entity is None:
            i += 1
            continue
        start = i
        end = i
        j = i + 1
        while j < n and j not in used_token_idxs:
            ent = _entity_or_none(implied(j))
            if ent == entity:
                end = j
                j += 1
                continue
            if implied(j) == "O":
                # Look ahead through Os for another same-entity non-O.
                k = j + 1
                while k < n and k not in used_token_idxs and implied(k) == "O":
                    k += 1
                if (
                    k < n
                    and k not in used_token_idxs
                    and _entity_or_none(implied(k)) == entity
                ):
                    end = k
                    j = k + 1
                    continue
            break
        flagged_rows = sorted(
            rid
            for k in range(start, end + 1)
            if k in flagged_idx_to_row
            for rid in flagged_idx_to_row[k]
        )
        if flagged_rows:
            groups.append(
                EntityGroup(
                    group_id=f"{doc.document_id}:{start}-{end}",
                    document_id=doc.document_id,
                    first_token_idx=start,
                    last_token_idx=end,
                    char_start=doc.tokens[start].char_start,
                    char_end=doc.tokens[end].char_end,
                    flagged_row_ids=tuple(flagged_rows),
                    gold_entity_label=None,
                )
            )
        i = end + 1

    groups.sort(key=lambda g: g.first_token_idx)
    return groups


# ----- State assembly ------------------------------------------------------


def _build_state() -> State:
    dataset = load_dataset()
    errors = _parse_errors(dataset)

    docs_by_id = {d.document_id: d for d in dataset.documents}
    errors_by_row_id: dict[int, ErrorRow] = {e.row_id: e for e in errors}
    errors_by_document: dict[int, list[int]] = {}
    unmapped_row_ids: list[int] = []
    for e in errors:
        if e.document_id < 0 or e.token_idx_in_doc < 0:
            unmapped_row_ids.append(e.row_id)
        else:
            errors_by_document.setdefault(e.document_id, []).append(e.row_id)

    groups_by_id: dict[str, EntityGroup] = {}
    groups_by_document: dict[int, list[str]] = {}
    for doc_id, row_ids in errors_by_document.items():
        doc = docs_by_id[doc_id]
        doc_errors = [errors_by_row_id[rid] for rid in row_ids]
        for group in _compute_groups_for_doc(doc, doc_errors):
            groups_by_id[group.group_id] = group
            groups_by_document.setdefault(doc_id, []).append(group.group_id)

    try:
        loaded = store.load_decisions()
    except store.DecisionsStaleError as exc:
        logger.error("decisions.jsonl is stale: %s", exc)
        loaded = LoadedDecisions(by_token={}, by_unmapped_row={})

    return State(
        dataset=dataset,
        documents_by_id=docs_by_id,
        errors=errors,
        errors_by_row_id=errors_by_row_id,
        errors_by_document=errors_by_document,
        unmapped_row_ids=unmapped_row_ids,
        available_labels=available_bio_labels(dataset),
        groups_by_id=groups_by_id,
        groups_by_document=groups_by_document,
        decisions_by_token=loaded.by_token,
        decisions_by_unmapped=loaded.by_unmapped_row,
    )


def get_state() -> State:
    global _state
    if _state is None:
        with _load_lock:
            if _state is None:
                _state = _build_state()
    return _state


def reset_state_for_tests() -> None:
    global _state
    with _load_lock:
        _state = None


# ----- Group decision logic ----------------------------------------------


def _bio_for_position(entity_label: str, position_in_group: int) -> str:
    if entity_label == "O":
        return "O"
    return ("B-" if position_in_group == 0 else "I-") + entity_label


def _entity_of(bio: str) -> str | None:
    if bio == "O":
        return None
    if bio[:2] in ("B-", "I-"):
        return bio[2:]
    return None


def _fill_o_gaps_same_entity(sequence: list[str]) -> list[str]:
    """Fill ``O`` slots between non-O tokens of a single entity with ``I-X``.

    Cleanlab can suggest a fragmented sequence like
    ``B-MULTA O O I-MULTA O O I-MULTA`` for what is logically one entity.
    Accepting the suggestion verbatim would produce invalid BIO; this
    helper closes the gaps. Only applied when every non-O token shares
    the same entity — mixed entities are left untouched because the
    correct fill is ambiguous.
    """
    entities = [_entity_of(lab) for lab in sequence]
    non_o_indices = [i for i, e in enumerate(entities) if e is not None]
    if not non_o_indices:
        return list(sequence)
    unique = {entities[i] for i in non_o_indices if entities[i] is not None}
    if len(unique) != 1:
        return list(sequence)
    entity = next(iter(unique))
    first = non_o_indices[0]
    last = non_o_indices[-1]
    out = list(sequence)
    for i in range(first, last + 1):
        if out[i] == "O":
            out[i] = f"I-{entity}"
    return out


def _normalize_bio(sequence: list[str]) -> list[str]:
    """Ensure each entity run starts with ``B-X`` and continues with ``I-X``.

    Cleanlab can produce orphaned ``I-`` tokens (especially when every
    flagged token in a chain is suggested as ``I-X`` with no ``B-X``
    anywhere). After fill, this rewrites each non-O run so the first
    token is ``B-X`` and the rest are ``I-X``. Os are left as Os.
    """
    out = list(sequence)
    prev_entity: str | None = None
    for i, lab in enumerate(out):
        if lab == "O":
            prev_entity = None
            continue
        ent = _entity_of(lab)
        if ent is None:
            prev_entity = None
            continue
        out[i] = ("B-" if ent != prev_entity else "I-") + ent
        prev_entity = ent
    return out


def _validate_entity_label(label: str) -> None:
    if label not in ENTITY_LABELS:
        raise ValueError(f"entity_label must be one of {ENTITY_LABELS}, got {label!r}")


def compute_group_token_labels(
    state: State,
    group: EntityGroup,
    decision: DecisionKind,
    entity_label: str | None,
    range_override: tuple[int, int] | None = None,
) -> dict[int, str]:
    """Return ``{token_idx_in_doc: new_bio_label}`` for the tokens that
    should be persisted under this decision.

    - ``accept``: each flagged token gets its ``label_sugerido``;
      non-flagged tokens carry their gold label into the resulting
      sequence. The sequence is then post-processed to fill O slots that
      sit between non-O tokens of a single entity, so a fragmented
      suggestion like ``B-MULTA O O I-MULTA O O I-MULTA`` becomes a
      coherent ``B-MULTA I-MULTA …`` entity. Tokens whose final label
      differs from the gold are persisted (along with every flagged token,
      so the group is marked decided).
    - ``reject``: only flagged tokens are recorded (each kept at its
      ``label_original``) so the group is marked decided.
    - ``custom``: every token in the group's range gets the new BIO derived
      from ``entity_label``; non-flagged tokens are written too so the
      downstream applier rewrites the whole entity.
    """
    doc = state.documents_by_id[group.document_id]
    flagged_by_idx: dict[int, ErrorRow] = {
        state.errors_by_row_id[rid].token_idx_in_doc: state.errors_by_row_id[rid]
        for rid in group.flagged_row_ids
    }
    out: dict[int, str] = {}

    if decision == "accept":
        indices = [
            i
            for i in range(group.first_token_idx, group.last_token_idx + 1)
            if i < len(doc.tokens)
        ]
        sequence = [
            flagged_by_idx[i].label_sugerido
            if i in flagged_by_idx
            else doc.tokens[i].bio
            for i in indices
        ]
        normalized = _normalize_bio(_fill_o_gaps_same_entity(sequence))
        for offset, idx in enumerate(indices):
            new_label = normalized[offset]
            gold = doc.tokens[idx].bio
            # Always record flagged tokens (so the group is decided);
            # also record any non-flagged token whose label was filled.
            if idx in flagged_by_idx or new_label != gold:
                out[idx] = new_label
    elif decision == "reject":
        for idx, error in flagged_by_idx.items():
            out[idx] = error.label_original
    elif decision == "custom":
        if entity_label is None:
            raise ValueError("custom decision requires entity_label")
        _validate_entity_label(entity_label)
        if range_override is not None:
            first, last = range_override
            if first < 0 or last < 0 or first > last:
                raise ValueError(
                    "invalid range_override: first must be <= last and both >= 0"
                )
            if last >= len(doc.tokens):
                raise ValueError(
                    f"last_token_idx {last} is past the document's last token "
                    f"(idx {len(doc.tokens) - 1})"
                )
        else:
            first = group.first_token_idx
            last = group.last_token_idx
        # If the new range shrinks below the group's natural range, tokens
        # excluded from the new range that were previously written under
        # this group's custom decision need to be reset to their gold BIO
        # so the export reflects the resize.
        for idx in range(group.first_token_idx, group.last_token_idx + 1):
            if idx >= len(doc.tokens):
                continue
            if idx < first or idx > last:
                out[idx] = doc.tokens[idx].bio
        for offset, idx in enumerate(range(first, last + 1)):
            if idx >= len(doc.tokens):
                continue
            out[idx] = _bio_for_position(entity_label, offset)
    else:
        raise ValueError(f"unknown decision: {decision}")
    return out


def record_group_decision(
    state: State,
    *,
    group_id: str,
    decision: DecisionKind,
    entity_label: str | None,
    decided_by: str,
    range_override: tuple[int, int] | None = None,
) -> EntityGroup:
    group = state.groups_by_id.get(group_id)
    if group is None:
        raise KeyError(group_id)

    new_labels = compute_group_token_labels(
        state, group, decision, entity_label, range_override=range_override
    )
    flagged_row_for_idx: dict[int, int] = {
        state.errors_by_row_id[rid].token_idx_in_doc: rid
        for rid in group.flagged_row_ids
    }
    timestamp = now_iso()
    records: list[TokenDecision] = []
    for idx, label_final in new_labels.items():
        records.append(
            TokenDecision(
                document_id=group.document_id,
                token_idx_in_doc=idx,
                label_final=label_final,
                decision=decision,
                group_id=group.group_id,
                decided_by=decided_by,
                decided_at=timestamp,
                row_id=flagged_row_for_idx.get(idx),
            )
        )
    append_token_decisions(records)
    for rec in records:
        state.decisions_by_token[(rec.document_id, rec.token_idx_in_doc)] = rec
    return group


# ----- Unmapped decision logic -------------------------------------------


def record_unmapped_decision(
    state: State,
    *,
    row_id: int,
    decision: DecisionKind,
    label_final: str | None,
    decided_by: str,
) -> UnmappedDecision:
    error = state.errors_by_row_id.get(row_id)
    if error is None:
        raise KeyError(row_id)
    if decision == "accept":
        final = error.label_sugerido
    elif decision == "reject":
        final = error.label_original
    elif decision == "custom":
        if not label_final or label_final not in set(state.available_labels):
            raise ValueError("custom decision requires a known BIO label_final")
        final = label_final
    else:
        raise ValueError(f"unknown decision: {decision}")
    record = UnmappedDecision(
        row_id=row_id,
        label_final=final,
        decision=decision,
        decided_by=decided_by,
        decided_at=now_iso(),
    )
    append_unmapped_decision(record)
    state.decisions_by_unmapped[row_id] = record
    return record


# ----- Group status helper ------------------------------------------------


def group_status(
    state: State, group: EntityGroup
) -> tuple[str, Optional[str], Optional[str], Optional[str]]:
    """Return ``(status, entity_label, decided_by, decided_at)``.

    Status is ``pending`` if any flagged token in the group has no decision
    yet, otherwise the shared ``decision`` value (``accept``/``reject``/
    ``custom``). ``mixed`` is returned when the same group has flagged
    tokens with different decisions (legacy data).
    """
    decisions: list[TokenDecision] = []
    for rid in group.flagged_row_ids:
        idx = state.errors_by_row_id[rid].token_idx_in_doc
        rec = state.decisions_by_token.get((group.document_id, idx))
        if rec is None:
            return "pending", None, None, None
        decisions.append(rec)

    kinds = {d.decision for d in decisions}
    if len(kinds) > 1:
        return "mixed", None, None, None
    only = next(iter(kinds))
    entity_label: Optional[str] = None
    if only == "custom":
        # Recover entity label from the BIO labels recorded across the group.
        labels = {d.label_final for d in decisions}
        if labels == {"O"}:
            entity_label = "O"
        else:
            stripped = {lab[2:] if lab[:2] in ("B-", "I-") else lab for lab in labels}
            entity_label = next(iter(stripped)) if len(stripped) == 1 else None
    last = max(decisions, key=lambda d: d.decided_at)
    return only, entity_label, last.decided_by, last.decided_at


def progress_counts(state: State) -> dict[str, int]:
    """Group-level progress: total groups, decided groups, and per-decision
    counts."""
    counts = {"accept": 0, "reject": 0, "custom": 0, "mixed": 0}
    decided = 0
    total = len(state.groups_by_id)
    for group in state.groups_by_id.values():
        status, *_ = group_status(state, group)
        if status == "pending":
            continue
        decided += 1
        counts[status] = counts.get(status, 0) + 1
    return {
        "total": total,
        "decided": decided,
        "accept": counts["accept"],
        "reject": counts["reject"],
        "custom": counts["custom"],
        "mixed": counts["mixed"],
        "unmapped_total": len(state.unmapped_row_ids),
        "unmapped_decided": len(state.decisions_by_unmapped),
    }
