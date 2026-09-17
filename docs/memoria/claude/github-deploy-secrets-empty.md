---
name: github-deploy-secrets-empty
description: Deploy lê /home/sudip/.env (não secrets do GitHub); migração fora do git derruba o backend em todo deploy
metadata: 
  node_type: memory
  type: project
  originSessionId: 91e3c779-914c-4c28-9168-6b38c222a2e0
  modified: 2026-08-31T12:54:50.879Z
---

O `deploy.yml` foi corrigido: escreve `web/.env` a partir de `/home/sudip/.env` no host (runner roda como sudip) e **não usa mais os secrets do repo GitHub** (que continuam vazios). Valida as vars obrigatórias e persiste `JWT_SECRET_KEY` gerado no próprio arquivo.

**Incidente 31/08/2026**: backend de produção ficou dias fora do ar (502) porque a migração `0019_verificacao_siai_folha.py` foi aplicada/carimbada no BdDIP de produção mas ficou **untracked** no repo — todo deploy falhava no `alembic upgrade` com "Can't locate revision". Corrigido commitando o arquivo (`9ce56b9`).

**Why:** rodar migração em produção a partir da working tree local sem commitar o arquivo quebra silenciosamente todos os deploys seguintes; o run falho deixa o backend derrubado.

**How to apply:** ao criar migração nova, commitar o arquivo em `web/backend/app/migrations/versions/` no mesmo momento em que ela é aplicada em produção. Se deploy falhar com "Can't locate revision", procurar migração untracked (`git status web/backend/app/migrations/versions/`). Deploy manual: workflow tem `workflow_dispatch` (`gh workflow run deploy.yml`); o `gh` local autentica com o token do Windows Credential Manager (`git credential fill`). SSH `sudip@10.24.0.197` (host `prd-dip01`) aceita a chave local `~/.ssh/id_ed25519` desde 31/08/2026 — dá para ver logs (`docker logs frap-backend`), ressuscitar o worker (`docker compose up -d worker` em `~/actions-runner/_work/ccd/ccd/web`, projeto `frap-controle`) e restart sem rebuild. Ver [[deploy-host-var-disk-tight]].
