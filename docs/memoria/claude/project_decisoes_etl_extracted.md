---
name: decisoes-etl moved to its own repo
description: The decisoes-etl/ directory was deliberately removed in 2026-04 because the logic now lives in a separate repository.
type: project
originSessionId: f2749754-07d7-476e-9e9b-9ebd0bf283bd
---
`decisoes-etl/` (year-based corpus export over `Ata_Informacao`) was removed
from the `ccd` repo in 2026-04. The user migrated that logic to a separate
repository.

**Why:** Different lifecycle from the CCD tooling — it's a one-off corpus
export pipeline, not part of the day-to-day CCD despacho/análise workflow.
Keeping it here was confusing the architecture (item 7 of PLAN.md).

**How to apply:**
- Don't recreate `decisoes-etl/` here. If a notebook needs the same export,
  point at the external repo or build a focused helper in `ccd/`.
- The `ccd/` package no longer has any consumers of pytest infrastructure
  in this repo — CI runs ruff + mypy only.
- `ccd.config.informacoes_dir()` is still the canonical PDF-share resolver
  (originally factored out partly to serve etl.py); it stays.
