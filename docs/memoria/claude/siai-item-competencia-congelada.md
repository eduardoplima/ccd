---
name: siai-item-competencia-congelada
description: "ALRN congela CCI.MesReferencia do item ('7'/2025) em todas as folhas — matcher por competência do item dá falso NAO_DESCONTADA; view usa competência da FOLHA"
metadata: 
  node_type: memory
  type: project
  originSessionId: 03d98f55-c5ac-4afd-ab7a-2da3e5a2cd54
  modified: 2026-08-28T18:45:08.027Z
---

No SIAI Pessoal, a competência existe em dois níveis: **item**
(`SiaiDp_ContraChequeItem.MesReferencia/AnoReferencia`) e **folha**
(`SiaiDp_FolhaPagamento.Mes/Ano`). A ALRN (e possivelmente outros órgãos)
preenche a do item **congelada na 1ª parcela** (caso Edmilson Targino,
000731/2025: todos os itens vieram com Mes='7', Ano NULL ou '2025', de 07/2025
a 02/2026), enquanto a da folha está correta.

**Why:** o matcher `contracheque_descontos_tce` (web/tools/frap) filtra pela
competência do ITEM → falso `NAO_DESCONTADA`/match no mês errado. A view
`BdDIP.dbo.vwSiaiPessoalFolhaCompletaTodas` usa a competência da FOLHA →
correta (por isso o job `task_verificar_siai_folha` e a badge SIAI acertam).

**How to apply:** para conciliar/verificar desconto em folha, preferir a
competência da folha (ou `COALESCE(NULLIF(item), folha)`). Em 28/08/2026 o
usuário optou por NÃO corrigir o matcher; os 8 matches do caso foram gravados
manualmente (`FRAPMatchDescontoFolha`, status 41 DESCONTADA_SEM_REPASSE,
`IsManual=1` — preservados na republicação). Status manual sem lançamento:
INSERT direto; só IdFRAPDescontoFolhaParcela, IdStatusMatch, DataCalculo e
IsManual são NOT NULL.

Ligado a [[monitoramento-desconto-folha-crud]] e [[frap-tables-in-bddip]].
