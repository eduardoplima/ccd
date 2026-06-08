"""Append-only JSONL store for admin decisions.

Two record kinds, distinguished by which key fields are present:

- ``token``: keyed by ``(document_id, token_idx_in_doc)`` — used when the
  decision applies to a token that resolved to a document. A single group
  decision writes one of these per token in the group's range, so non-flagged
  tokens that get relabeled by a custom group decision are persisted too.
- ``unmapped``: keyed by ``row_id`` — used for cleanlab errors whose
  document/token couldn't be located. The reviewer decides directly on the
  CSV row.

Both record types share ``decision``, ``label_final``, ``decided_by``,
``decided_at``. The first line of the file is a header carrying the
cleanlab CSV mtime — if the CSV has been regenerated since the JSONL was
written, ``load_decisions`` raises ``DecisionsStaleError`` because row ids
would no longer line up.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal, Optional

from app.cgad.dataset_corrections.paths import DECISIONS_JSONL, ERRORS_CSV


logger = logging.getLogger(__name__)


DecisionKind = Literal["accept", "reject", "custom"]


class DecisionsStaleError(RuntimeError):
    """Raised when the JSONL header's csv_mtime doesn't match the current
    cleanlab CSV — row ids would be inconsistent."""


@dataclass(frozen=True)
class TokenDecision:
    document_id: int
    token_idx_in_doc: int
    label_final: str
    decision: DecisionKind
    group_id: str
    decided_by: str
    decided_at: str
    row_id: Optional[int] = None  # original CSV row id, if this token was flagged

    def to_jsonl_line(self) -> str:
        payload = {
            "kind": "token",
            "document_id": self.document_id,
            "token_idx_in_doc": self.token_idx_in_doc,
            "label_final": self.label_final,
            "decision": self.decision,
            "group_id": self.group_id,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at,
        }
        if self.row_id is not None:
            payload["row_id"] = self.row_id
        return json.dumps(payload, ensure_ascii=False) + "\n"


@dataclass(frozen=True)
class UnmappedDecision:
    row_id: int
    label_final: str
    decision: DecisionKind
    decided_by: str
    decided_at: str

    def to_jsonl_line(self) -> str:
        return (
            json.dumps(
                {
                    "kind": "unmapped",
                    "row_id": self.row_id,
                    "label_final": self.label_final,
                    "decision": self.decision,
                    "decided_by": self.decided_by,
                    "decided_at": self.decided_at,
                },
                ensure_ascii=False,
            )
            + "\n"
        )


@dataclass
class LoadedDecisions:
    by_token: dict[tuple[int, int], TokenDecision]
    by_unmapped_row: dict[int, UnmappedDecision]


_lock = threading.Lock()


def _csv_mtime() -> float:
    return ERRORS_CSV.stat().st_mtime if ERRORS_CSV.exists() else 0.0


def _ensure_header(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    header = json.dumps({"_header": True, "csv_mtime": _csv_mtime()}) + "\n"
    path.write_text(header, encoding="utf-8")


def _iter_records(path: Path) -> Iterator[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except ValueError:
                logger.warning(
                    "decisions.jsonl: skipping malformed line: %r", line[:80]
                )


def load_decisions(path: Path = DECISIONS_JSONL) -> LoadedDecisions:
    """Replay the JSONL into the latest decision per token / unmapped row.

    Raises ``DecisionsStaleError`` if the header's csv_mtime is missing or
    differs from the current CSV's mtime.
    """
    if not path.exists():
        return LoadedDecisions(by_token={}, by_unmapped_row={})

    records = list(_iter_records(path))
    if not records:
        return LoadedDecisions(by_token={}, by_unmapped_row={})

    head, *body = records
    if not head.get("_header"):
        body = records
    else:
        stored = head.get("csv_mtime")
        current = _csv_mtime()
        if stored is None or abs(float(stored) - current) > 1e-6:
            raise DecisionsStaleError(
                f"decisions.jsonl was written for csv_mtime={stored!r}, "
                f"but current cleanlab CSV mtime is {current!r}. "
                "Reset the JSONL or regenerate the CSV in sync."
            )

    by_token: dict[tuple[int, int], TokenDecision] = {}
    by_unmapped: dict[int, UnmappedDecision] = {}
    for rec in body:
        kind = rec.get("kind")
        try:
            if kind == "token":
                key = (int(rec["document_id"]), int(rec["token_idx_in_doc"]))
                by_token[key] = TokenDecision(
                    document_id=key[0],
                    token_idx_in_doc=key[1],
                    label_final=rec["label_final"],
                    decision=rec["decision"],
                    group_id=rec["group_id"],
                    decided_by=rec["decided_by"],
                    decided_at=rec["decided_at"],
                    row_id=rec.get("row_id"),
                )
            elif kind == "unmapped":
                row_id = int(rec["row_id"])
                by_unmapped[row_id] = UnmappedDecision(
                    row_id=row_id,
                    label_final=rec["label_final"],
                    decision=rec["decision"],
                    decided_by=rec["decided_by"],
                    decided_at=rec["decided_at"],
                )
            else:
                logger.warning("decisions.jsonl: unknown kind %r — skipping", kind)
        except (KeyError, TypeError, ValueError):
            logger.warning("decisions.jsonl: skipping invalid record: %r", rec)
    return LoadedDecisions(by_token=by_token, by_unmapped_row=by_unmapped)


def append_token_decisions(
    records: list[TokenDecision], path: Path = DECISIONS_JSONL
) -> None:
    """Atomic batch write — used when committing a group decision."""
    if not records:
        return
    with _lock:
        _ensure_header(path)
        with path.open("a", encoding="utf-8") as fh:
            for record in records:
                fh.write(record.to_jsonl_line())


def append_unmapped_decision(
    record: UnmappedDecision, path: Path = DECISIONS_JSONL
) -> None:
    with _lock:
        _ensure_header(path)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(record.to_jsonl_line())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
