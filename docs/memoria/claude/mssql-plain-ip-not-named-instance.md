---
name: mssql-plain-ip-not-named-instance
description: "MSSQL connect needs plain IP + static port 59678, NOT host\\instance"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8ff4d5c1-638f-41bd-ba49-ca50bc1e617e
---

The `processo` MSSQL server is reachable at `10.24.0.77` on **static port 59678**. In `scripts/.env`, `SQL_SERVER_HOST` must be the **plain IP `10.24.0.77`** (no `\ControleExterno` instance suffix) together with `SQL_SERVER_PORT=59678`. Empirically tested: plain-IP + port connects; `10.24.0.77\ControleExterno` + port and instance-only (SQL Browser) both fail with DB-Lib 20009 "Adaptive Server is unavailable".

**Why:** pymssql/FreeTDS can't combine a named instance with a static port — the instance name routes the request to the SQL Browser service (UDP 1434), overriding/ignoring the static port. This contradicts the comment in `ccd/db.py` (~lines 53-59), which keeps `host\instance` + port via `connect_args` expecting it to work; for this server it does not.

**How to apply:** keep `SQL_SERVER_HOST=10.24.0.77` (don't "restore" the instance name). After editing `.env`, **restart the kernel** — `ccd.config.load_env()` is cached and uses `override=False`, so a running process keeps the stale value. Don't edit `db.py` to strip instances globally; it could break other hosts. Related: [[repo-moved-stale-editable-install]].
