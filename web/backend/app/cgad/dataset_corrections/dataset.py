"""Reconstruct the cleanlab notebook's per-document tokenisation.

The cleanlab analysis (``notebooks/aed_decicontas.ipynb``) loads
``dataset/labeled_data/decicontas.json`` via ``tools.dataset.get_decicontas_df``
(861 docs after the fewshot filter), tokenises each document with
``re.finditer(r'\\S+', text)``, and converts Label Studio spans to BIO tags
(MULTA_FIXA / MULTA_PERCENTUAL / OBRIGACAO_MULTA collapse to MULTA / OBRIGACAO).

The resulting ``sentencas`` list is one entry per non-empty document, and the
exported CSV's ``sentenca_idx`` indexes into that list. We mirror the same
construction here so the cleanlab error rows map directly onto documents.

The CONLL file is intentionally not used — it was produced by a different
tokenizer in a separate experiment and its sentence indices don't line up.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from app.cgad.dataset_corrections.paths import LABELED_JSON
from cgad.fewshot import FEWSHOT_DATASET_IDS


_TOKEN_RE = re.compile(r"\S+")

# Same as ``tools.dataset.translate_golden``: collapse fine-grained labels
# down to the four-class scheme cleanlab was trained on.
_LABEL_COLLAPSE = {
    "MULTA_FIXA": "MULTA",
    "MULTA_PERCENTUAL": "MULTA",
    "OBRIGACAO_MULTA": "OBRIGACAO",
}


@dataclass
class Token:
    text: str
    char_start: int
    char_end: int
    bio: str  # B-MULTA / I-OBRIGACAO / O / ...


@dataclass
class NerSpan:
    char_start: int
    char_end: int
    label: str  # collapsed


@dataclass
class Document:
    document_id: int
    text: str
    tokens: list[Token]
    ner_spans: list[NerSpan]


@dataclass
class Dataset:
    documents: list[Document]
    # ``sentencas[i]`` is the i-th document with at least one token —
    # this list's indexing matches the cleanlab CSV's sentenca_idx.
    sentencas_doc_ids: list[int]


def _collapse(label: str) -> str:
    return _LABEL_COLLAPSE.get(label, label)


def _build_document(raw_id: int, text: str, raw_spans: list[dict]) -> Document:
    spans: list[NerSpan] = []
    for s in raw_spans:
        start = s.get("start")
        end = s.get("end")
        labels = s.get("labels") or []
        if start is None or end is None or not labels:
            continue
        spans.append(
            NerSpan(
                char_start=int(start),
                char_end=int(end),
                label=_collapse(labels[0]),
            )
        )
    spans.sort(key=lambda s: (s.char_start, s.char_end))

    tokens: list[Token] = [
        Token(text=m.group(), char_start=m.start(), char_end=m.end(), bio="O")
        for m in _TOKEN_RE.finditer(text or "")
    ]

    # The notebook's BIO assignment is keyed per span (first overlapping
    # token gets B-, subsequent overlapping tokens get I-) so we walk spans,
    # not tokens.
    for span in spans:
        first = True
        for tok in tokens:
            if tok.char_start < span.char_end and tok.char_end > span.char_start:
                tok.bio = ("B-" if first else "I-") + span.label
                first = False

    return Document(document_id=raw_id, text=text or "", tokens=tokens, ner_spans=spans)


def _extract_raw_spans(item: dict) -> list[dict]:
    spans: list[dict] = []
    for ann in item.get("annotations", []) or []:
        for r in ann.get("result", []) or []:
            value = r.get("value") or {}
            if "start" in value and "end" in value and "labels" in value:
                spans.append(
                    {
                        "start": value["start"],
                        "end": value["end"],
                        "labels": value["labels"],
                    }
                )
    return spans


def load_dataset(path: Path = LABELED_JSON) -> Dataset:
    """Load the dataset using the same filter+tokenisation as the cleanlab
    notebook so ``sentenca_idx`` from the CSV maps directly onto an entry
    in the returned ``documents`` list.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    fewshot = set(FEWSHOT_DATASET_IDS)

    docs: list[Document] = []
    sentencas_doc_ids: list[int] = []
    for item in raw:
        doc_id = item.get("id")
        if doc_id is None or doc_id in fewshot:
            continue
        text = (item.get("data", {}) or {}).get("text", "") or ""
        raw_spans = _extract_raw_spans(item)
        document = _build_document(int(doc_id), text, raw_spans)
        docs.append(document)
        # The notebook's loop appends to ``sentencas`` only when ``tokens``
        # is non-empty — mirror that for index alignment.
        if document.tokens:
            sentencas_doc_ids.append(document.document_id)

    return Dataset(documents=docs, sentencas_doc_ids=sentencas_doc_ids)


def available_bio_labels(dataset: Dataset) -> list[str]:
    """Sorted union of BIO labels observed across all documents, plus ``O``.
    Drives the "label custom" select in the UI."""
    labels: set[str] = {"O"}
    for d in dataset.documents:
        for tok in d.tokens:
            labels.add(tok.bio)
    return sorted(labels, key=lambda x: (x != "O", x))
