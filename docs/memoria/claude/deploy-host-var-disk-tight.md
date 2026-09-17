---
name: deploy-host-var-disk-tight
description: "Host de deploy 10.24.0.197: /var agora é 24GB (não mais apertado); deploy via runner GitHub Actions no push à main; sem root"
metadata:
  node_type: memory
  type: project
  originSessionId: 101b17d3-322c-4726-a8b6-2f2406658d76
---

Fatos do host de deploy da webapp [[web-consolidacao-ccd]] (`10.24.0.197`, Debian 13), verificados em 2026-06-15:

- **`/var` agora tem 24 GB** (≈20% usado, ~19 GB livres) — foi redimensionado; o aperto antigo de 4,1 GB que enchia no build do backend (LibreOffice+ODBC) **não é mais problema**. (Histórico: a imagem do backend instala LibreOffice + msodbcsql18; correção sustentável ainda válida = `apt-get clean` no RUN do apt do `web/backend/Dockerfile`.)
- **Deploy é automático via self-hosted GitHub Actions runner** no push à `main`. Working dir real: `/home/sudip/actions-runner/_work/ccd/ccd/web`, compose project **`frap-controle`** (`docker-compose.prod.yml`), rede externa `frap-controle_default`. Containers: `frap-frontend/backend/worker/caddy/redis`. O `web/deploy/deploy_remote.py` + `~/frap-controle` é caminho **manual legado/não usado** (a pasta nem existe no host).
- **`sudip` não tem root** (não há binário `sudo` no host) — opera só pelo grupo docker. Logo CIFS/mounts de host (fstab/systemd) **não são viáveis**; o único jeito de montar o share `//10.24.0.6/tce$` é via **volume docker** (o daemon monta como root). Mount funciona com `vers=2.0`/`2.1`/`sec=ntlmssp` e as credenciais atuais (sem precisar de `domain`); **`vers=3.0` falha**.
- Rodar scripts SSH com `PYTHONUTF8=1` p/ não quebrar com `UnicodeEncodeError` (cp1252) nos caracteres de caixa do `docker compose`.
