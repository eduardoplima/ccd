---
name: monitoramento-desconto-folha-crud
description: "Planilha \"Monitoramento Desconto em Folha.xlsx\" aposentada — tabela FRAPMonitoramentoDescontoFolha + CRUD na webapp (26/08/2026)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 62edf4c8-fce4-4efe-9f39-9d3a6f740575
  modified: 2026-08-28T18:30:57.852Z
---

Em 26/08/2026 a planilha `docs/Monitoramento Desconto em Folha.xlsx` foi importada
para `BdDIP.dbo.FRAPMonitoramentoDescontoFolha` (migração alembic
`0018_monitoramento_desconto_folha`; 311 linhas: 255 GERAL + 13 ANTIGO + 43 NEREU).
**A fonte agora é o CRUD da webapp** (aba "Monitoramento", padrão, em
`/frap/desconto-folha`); a planilha está congelada.

- Chave única (filtrada por `Ativo=1`): `(Grupo, NumeroProcesso, CpfCnpj)` — um
  processo tem vários responsáveis. `IdFRAPDescontoFolha` é **BIGINT** (FK).
- Endpoints: `/api/v1/frap/desconto-folha/monitoramento[...]` + CRUD completo do
  cadastro manual (PATCH cadastro, POST/PATCH/DELETE parcela, GET detalhe) em
  `app/desconto_folha/monitoramento.py` e `service.py`.
- Reimport idempotente: `frap importar-monitoramento-tabela` (upsert; dry-run ok).
  28 órgãos não resolvidos pelo fuzzy ficaram com `IdOrgaoNotificado=NULL` (texto
  cru em `NomeOrgao`) — corrigir pela UI; muitos são federais/fora do RN.
- "Desconto implantado" no resumo = só `DescFolhaTexto LIKE 'S%'` (o vínculo por
  CPF a plano FRAP inflaria, pois Origem='S' é auto-populado).
- UI de conciliações OB/Boleto removida do frontend (página, hooks, api, schemas,
  menu); o backend `app/matches/` e o ETL ficaram intactos por decisão do usuário.
- Desde 28/08/2026 (commit bb413b4): CRUD do monitoramento aberto a **todos** os
  usuários (não só admin), e o modal Novo/Editar usa os campos do CGAD —
  `PessoaField` (select + modal de pessoas/cargos) alimentado por
  `GET .../monitoramento/pessoas-processo?processo=NNNNNN/AAAA`
  (Pro_ProcessosResponsavelDespesa + cargos via `_cargos_por_cpfs` do CGAD;
  cobre 310/311 processos monitorados) e `OrgaoField` (autocomplete
  `/cgad/reviews/orgaos`). Rota literal declarada ANTES de `/monitoramento/{id}`.
  Campo vazio = lista de pessoas vazia (degrada p/ input simples) — se "sumir",
  suspeitar de cache do browser/deploy em andamento antes de mexer no código.
- Testes de backend que dependem do fixture de auth (test_jobs, test_lancamentos,
  test_matches_ob) já estavam quebrados antes: `property 'NomeCompleto' of
  'Usuario' object has no setter`.
- Desde 28/08/2026: **job mensal de verificação SIAI** — `task_verificar_siai_folha`
  (`app/jobs/tasks.py`), primeiro `cron_jobs` do worker (dia 10, 07:00 UTC),
  materializa rubricas TCE/FRAP dos CPFs monitorados em
  `dbo.FRAPVerificacaoSiaiFolha` (migração 0019; delete+insert das 3 últimas
  competências — só rubrica SIAI, sem parcelas nem cruzamento FRAP). Fonte:
  `vwSiaiPessoalFolhaCompletaTodas`. Cron NÃO grava FRAPJob (IdUsuario NOT NULL);
  backfill manual: `POST /api/v1/frap/jobs/verificar-siai-folha?meses=N` (admin).
  UI: coluna/badge "SIAI" (última competência, valor no hover) via
  `siaiCompetencia`/`siaiValor` anexados no `listar`. Backfill 02–07/2026 rodado
  (252 linhas, ~39–45/mês). Campos manuais VerificadoSiaidp/Frap intocados.

Ligado a [[nereu-desconto-folha-progresso]] e [[web-consolidacao-ccd]].
