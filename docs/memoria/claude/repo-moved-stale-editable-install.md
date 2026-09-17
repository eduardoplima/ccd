---
name: repo-moved-stale-editable-install
description: "Repo was moved out of Documents\\Dev; stale pip -e . finder breaks \"import ccd\""
metadata: 
  node_type: memory
  type: project
  originSessionId: 8ff4d5c1-638f-41bd-ba49-ca50bc1e617e
---

The repo was moved from `C:\Users\05911205424\Documents\Dev\ccd` to `C:\Users\05911205424\Dev\ccd`. The `pip install -e .` editable finder (`__editable___ccd_0_1_0_finder.py` in the venv) had a hardcoded MAPPING to the old `Documents\Dev` path, so `import ccd` only worked when CWD was the repo root (Python found `ccd/` via CWD, masking the broken finder) and failed everywhere else — e.g. notebooks in `scripts/analise/`.

**Why:** editable installs bake in an absolute path; moving the repo silently invalidates them. The error surfaces as `ModuleNotFoundError: No module named 'ccd'` only from non-root CWDs.

**How to apply:** if `import ccd` fails, check the finder's MAPPING path matches the current repo location; fix with `.venv\Scripts\python.exe -m pip install -e .` from the repo root. If other configs still reference `...\Documents\Dev\ccd`, they'll need the same correction. Also note there were two venvs (`.venv` real, `.venv-1` a stray duplicate, now deleted) and the notebooks must use the `.venv` kernel — VS Code had auto-picked the Microsoft Store Python.
