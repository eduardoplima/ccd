---
name: wiki-module-web
description: "Módulo WIKI da webapp — páginas .md em web/backend/wiki/, overrides de edição via WIKI_EDITS_DIR"
metadata: 
  node_type: memory
  type: project
  originSessionId: 26955de6-cf2c-4e27-86f0-ca96308c855a
  modified: 2026-08-20T14:48:12.394Z
---

Módulo WIKI da webapp consolidada (criado 20/08/2026), ao lado de FRAP na topbar. Ver [[web-consolidacao-ccd]].

- Conteúdo: `.md` versionados em `web/backend/wiki/` (entram na imagem via `COPY backend/`; editar+push → deploy). Procedimentos enquadrados como **POPs conforme ISO 10013:2021** (20/08/2026): POP-CCD-001..012 em `procedimentos/*` (010 Reabertura de Parcelamento é MINUTA a validar — fluxo sem previsão normativa, proposto do modelo de dados; 011 verificação FRAP; 012 baixa/saldo residual); `marcadores` e `rotinas-mensais` são documentos de apoio; 8 POPs pendentes listados no `index.md` (DAP, anotação CGAD, certidão de quitação, informação instrutiva, Área Restrita/e-Contas, triagem do passivo, chamados/erros, inviabilidade).
- Backend: `app/wiki/router.py` (`/api/v1/wiki`) — pages/search/PUT/DELETE override. Edições da UI: dev grava direto no repo (`wiki_edits_dir` vazio); prod grava no volume `wiki_edits` (`WIKI_EDITS_DIR=/data/wiki_edits`) como overlay — badge "editado na UI", reconciliar copiando ao repo + DELETE override.
- Frontend: `(app)/wiki/` + `components/wiki/markdown.tsx` (react-markdown + remark-gfm + @tailwindcss/typography; links relativos resolvidos p/ `/wiki/<slug>`).

**Armadilhas locais:** o `Button` do projeto não tem `asChild` (usar `buttonVariants` + `Link`); `pnpm build` local precisa de `NODE_EXTRA_CA_CERTS=~/.qmd-ca-bundle.pem` ([[node-fetch-tls-corporate-mitm]]) e falha no passo standalone por EPERM de symlink no Windows (só no Docker/Linux completa).
