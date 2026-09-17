---
name: web-uv-workspace-all-packages
description: "web/ is a uv workspace — sync with `uv sync --all-packages`, never plain `uv sync`/`uv run` at the web root"
metadata: 
  node_type: memory
  type: project
  originSessionId: 13684a7b-ad24-4f40-b875-f69d9515d468
---

`web/` is a uv **workspace** (root `web/pyproject.toml` has `[tool.uv.workspace] members = ["backend", "tools/frap", "tools/cgad"]`); the workspace-root project `ccd-web-workspace` has **no dependencies of its own**.

**Why:** running plain `uv sync` (or `uv run ...`) from `web/` syncs only the empty root project and **prunes every workspace member** (`ccd-web-backend`/`tools`/`cgad`), emptying `web/.venv` — `app`, `frap`, etc. become un-importable. uv reports it as mass uninstalls (`- pkg==ver`).

**How to apply:** to install/repair the web env, always `uv sync --all-packages` (offline-restorable from uv cache). To run backend code use the venv python directly — `web/.venv/Scripts/python.exe -m ruff ...` — not `uv run`. Doing this at the **repo root** instead hits the separate pip-managed root `ccd` venv and a stray root `uv.lock`; the root venv restores with `pip install -r requirements.txt && pip install -e .`. Related: [[repo-moved-stale-editable-install]].
