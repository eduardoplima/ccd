---
name: cgad-stage2-dedup-orphan-finals
description: "Stage-2 CGAD dedup é por IdNerObrigacao+staging, não pelo texto na tabela final — re-rodar NER duplica contra finais órfãos"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5965ce80-3fd4-4783-8e99-5c545d6eb3a8
---

O dedup do stage-2 CGAD (`obligations_nonprocessed.sql` / `recommendations_nonprocessed.sql`) filtra por `NOT EXISTS` em `ObrigacaoProcessada`/`RecomendacaoProcessada` (chave `IdNerObrigacao`/`IdNerRecomendacao`) **e** em `*Staging` (status pending/approved). NÃO checa o texto já presente na tabela final `Obrigacao`/`Recomendacao`.

**Consequência:** se um processo já tem finais "órfãos" (sem linha de bridge `*Processada` e nunca revisados — ex.: de uma rodada antiga cujas linhas NER sumiram), re-rodar o stage-1 (NER) gera novos `IdNer*` e o stage-2 **duplica** os mesmos itens na tabela final. Aconteceu no processo 5202/2020 (IdProcesso 540767): #2204-2206/#984 novos duplicaram #32-34/#69 órfãos.

**Como aplicar:** antes de rodar stage-2 num processo, confira finais pré-existentes (`SELECT ... FROM BdDIP.dbo.Obrigacao WHERE IdProcesso=...`) e se têm bridge em `*Processada`. Órfãos sem bridge não bloqueiam re-extração. Driver é gated por `Pro_ProcessosResponsavelDespesa` (INNER JOIN) — processos sem responsável de despesa retornam 0 linhas; troquei por LEFT JOIN no script manual. Ver [[web-consolidacao-ccd]].
