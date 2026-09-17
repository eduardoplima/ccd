---
name: frontend-src-lib-gitignored
description: "root .gitignore `lib/` silently ignores web/frontend/src/lib/ — new files there need the negation in web/.gitignore"
metadata: 
  node_type: memory
  type: project
  originSessionId: 13684a7b-ad24-4f40-b875-f69d9515d468
---

The repo-root `.gitignore` line `lib/` matches **any** directory named `lib` anywhere, including the Next.js `web/frontend/src/lib/`.

**Why:** existing files under `src/lib/` (api-client.ts, api/ccd.ts, …) are tracked only because they were force-added (`git add -f`) earlier; git keeps tracking already-tracked files but **silently drops new files** added to that directory — they never show up in `git status` / `git add`.

**How to apply:** `web/.gitignore` now re-includes the tree with `!frontend/src/lib/` + `!frontend/src/lib/**` (the directory must be negated before the files, per git's parent-dir rule). Verify a new file is trackable with `git check-ignore -v <path>`. If adding a new `lib/`-named dir elsewhere in the web app, expect the same trap.
