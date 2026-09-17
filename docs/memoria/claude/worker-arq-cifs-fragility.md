---
name: worker-arq-cifs-fragility
description: frap-worker morre de vez se o mount CIFS do share de PDFs falhar na criação do container (restart policy não cobre)
metadata: 
  node_type: memory
  type: project
  originSessionId: e2f96000-3088-450d-b5f9-6dd18cbf0eb9
---

O serviço `worker` (ARQ) do [[web-consolidacao-ccd]] monta o volume docker CIFS `informacoes_pdf` (`//10.24.0.6/tce$` em `/mnt/tce:ro`), usado só pela task `task_gerar_antecedentes`. As outras 4 tasks (extração CGAD `run_full_extraction`, conciliação FRAP, desconto em folha) **não** precisam do share, mas ficam reféns dele.

**Why:** falha de mount de volume acontece na **criação** do container, e `restart: unless-stopped` **só reinicia container que chegou a rodar** — então um blip transitório do CIFS no deploy mata o `frap-worker` **para sempre** (ficou Exited 255 por ~2 dias em jun/2026, enquanto front/back/redis subiram normais). Sintoma p/ o usuário: extração de obrigações ("revisão") "demorando" — na verdade o job fica enfileirado sem worker.

**How to apply:** recriar com `docker compose -f docker-compose.prod.yml up -d worker` (a partir de `/home/sudip/actions-runner/_work/ccd/ccd/web`) ressuscita na hora se o mount voltar. Resiliência durável **pendente** e limitada por não ter root no host ([[deploy-host-var-disk-tight]]): opção viável = cron do `sudip` rodando `docker compose up -d` a cada ~5min p/ ressuscitar containers mortos. Desacoplar de verdade (mount no host + bind, ou entrypoint que monta com `|| true`) exigiria root/`cap_add SYS_ADMIN`.
