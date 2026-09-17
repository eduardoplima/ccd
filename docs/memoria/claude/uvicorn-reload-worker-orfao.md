---
name: uvicorn-reload-worker-orfao
description: "Windows: matar o supervisor do uvicorn --reload deixa worker órfão segurando a porta com código antigo; usar taskkill /T"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9f348462-5915-40f4-b2a8-b21413f9c79c
  modified: 2026-08-31T14:02:29.555Z
---

No Windows, o `uvicorn --reload` (backend local em `web/backend`, porta 8000) spawna um worker via multiprocessing. `taskkill /PID <supervisor> /F` sem `/T` deixa o worker órfão vivo, segurando o socket e servindo o **código antigo** — e netstat/Get-NetTCPConnection atribuem o socket ao PID morto do pai (parece fantasma; tasklist não acha o PID).

**Why:** Em 31/08/2026 isso mascarou um deploy local: a API respondia HTTP 200 com schema desatualizado e parecia que "o backend não rodava".

**How to apply:** Para matar o backend local use `taskkill /PID <pid> /T /F`. Se a 8000 responder com código velho e o PID do netstat não existir, procure o órfão: `Get-CimInstance Win32_Process` filtrando CommandLine por `multiprocessing.spawn`/`uvicorn`. Para subir o backend fora da sessão do Claude: `Start-Process uv -ArgumentList "run","uvicorn","app.main:app","--reload","--port","8000" -WorkingDirectory web\backend -WindowStyle Minimized` (background task do harness morre com a sessão).
