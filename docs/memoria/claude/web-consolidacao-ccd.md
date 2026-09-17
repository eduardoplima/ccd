---
name: web-consolidacao-ccd
description: "Webapp consolidada em web/ (módulos CCD/CGAD/FRAP); estado, decisões e o que falta"
metadata: 
  node_type: memory
  type: project
  originSessionId: 50232e1a-1d81-48e2-bde8-03de4ac9dee5
---

Consolidação de `repos/frap-controle` (→ módulo FRAP) e `repos/decicontas.app` (→ módulo CGAD) numa única webapp em **`web/`** na raiz do repo ccd. 3 módulos: CCD (placeholder, interfaces p/ scripts — a definir), CGAD, FRAP. Tema = frap-controle (verde/dourado, Roboto). Iniciado 2026-06-08.

**Stack** (idêntica nos dois): FastAPI + uv workspace (`web/backend` + `web/tools/frap`), Next.js 15 + Tailwind 4 + shadcn/ui (`web/frontend`, pnpm), JWT, ARQ/Redis, MSSQL BdDIP (pyodbc).

**Decisões fixas:**
- Auth lê **só `dbo.Usuarios`** (+ `TokensRenovacao`). `FRAPUsuario`/`FRAPRefreshToken` abandonadas. ORM em `app/auth/models.py`: classe `Usuario`→tabela Usuarios, `Login`=synonym de `NomeUsuario`, `NomeCompleto`=property(=NomeUsuario), `TokenHash`=synonym de `HashToken`; aliases `FRAPUsuario`/`FRAPRefreshToken` mantêm imports legados. eduardo=IdUsuario 2 (admin), admin=1.
- Todos os usuários autenticados veem os 3 módulos; `Papel=='admin'` gateia admin/ETL.
- API namespchada: FRAP em `/api/v1/frap/*`, CCD `/api/v1/ccd/*`, auth/usuarios compartilhados. Frontend: páginas FRAP movidas p/ `(app)/frap/*`, TopBar com switcher de módulo.
- Alembic: frap usa version_table **`FRAPAlembicVersion`** (head 0013), separado do `alembic_version` (decicontas, head b8a3e7c1d562) — não colidem. Migração nova `0014_repoint_user_fks` repointa FKs de FRAPJob.IdUsuario e FRAPMatchDescontoFolha.IdUsuarioConcilia de FRAPUsuario→Usuarios (e remapeia dados 1→2).

**Fase 1 (esqueleto) — FEITA e verificada** end-to-end: login/auth em Usuarios, FRAP reads namespchados retornam dados, CCD placeholder, frontend 3-módulos (tsc + next build compilam 14 páginas). `web/.env` gerado de `scripts/.env`.

**Fase 1 + migração 0014 + Fase 2 — FEITAS (2026-06-08).**
- Migração `0014` aplicada em prod (FRAPAlembicVersion=0014): FKs de FRAPJob/FRAPMatchDescontoFolha agora → Usuarios, dados remapeados 1→2 (eduardo). FRAP writes OK.
- **Fase 2 CGAD feita**: `web/tools/cgad` (pacote `cgad`, pyodbc, sql/ em web/tools/cgad/sql); routers `app/cgad/{review,etl,dashboards,dataset_corrections}` em `/api/v1/cgad/*` (etl `_QUEUE_NAME="arq:queue"` p/ um worker só); `app/cgad/tasks.py` = orquestrador `run_full_extraction` no `worker.py`; CGAD usa **web** `app.deps`/`app.auth` (UserOut: `papel`/`login`, não role/username); `cgad.models.UserORM` existe mas não é usado. Frontend `(app)/cgad/{reviews,etl,dashboards,admin}` + libs `*-api.ts`/hooks/schemas copiados, paths→`/api/v1/cgad`, links→`/cgad/*`, `.role→.papel`/`.username→.login`, format helpers add em `lib/format.ts`. Verificado: reviews 1333 obrig/901 recom, dashboards, etl 3 runs; tsc OK; rotas 200.

**Módulo CCD — página Início (FEITA):** lista processos do banco `processo` com `setor_atual='CCD'` e `IdProcessoApensador IS NULL` (533), paginada 100. Colunas Processo/Marcador/Origem/Relator/Tipo/Assunto; filtros marcador(dropdown)/relator(dropdown por codigo)/assunto(LIKE). Backend: `app/db.get_processo_engine` + `deps.get_processo_session`, `app/ccd/{schemas,service,router}.py` (`GET /api/v1/ccd/processos` e `/processos/filtros`). Marcador = mais recente de origem CCD (`Pro_Marcador.IdSetor=762`, `Pro_MarcadorProcesso` ativo, ROW_NUMBER). Setor CCD idSetor=762. Frontend: `schemas/ccd.ts`, `lib/api/ccd.ts`, `hooks/use-ccd-processos.ts`, `(app)/ccd/page.tsx` (substituiu o seletor de módulos). Verificado 533/100, filtros combinam.

**PENDENTE:**
- ETL run (CGAD) só executa com Redis + Azure OpenAI ativos; não rodado fim-a-fim. `dataset_corrections`/cleanlab-review (admin) depende de arquivos de dataset que não existem em web — tool experimental, pode falhar em runtime.
- **Fase 3 — CCD**: interfaces reais p/ scripts do repo.
- Testes do backend (`web/backend/tests/*`) ainda usam `NomeCompleto=`/`FRAPUsuario` — quebram; ajustar quando rodar pytest.

Build standalone falha no Windows (symlink EPERM) e fonts precisam de [[node-fetch-tls-corporate-mitm]] (`NODE_EXTRA_CA_CERTS`); `pnpm dev` funciona. Auth FRAP é o [[cit-citacoes-authoritative-source]] domínio; DB é [[mssql-plain-ip-not-named-instance]].
