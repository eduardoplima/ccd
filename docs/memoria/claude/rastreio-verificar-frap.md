---
name: rastreio-verificar-frap
description: Rastreio dos processos que precisam verificar depósitos no FRAP; ciclo de marcadores de desconto em folha (5953 = Verificar transferência FRAP)
metadata: 
  node_type: memory
  type: project
  originSessionId: f50ed0f7-0dfb-4a92-92fc-456e4e93c53c
  modified: 2026-08-18T16:56:00.437Z
---

Ciclo de marcadores de desconto em folha na CCD (Pro_Marcador, IdSetor 762): Implementar (5021/5022 Nereu) → SEAD desconta → **5953 "DESCONTO EM FOLHA - Verificar transferência FRAP"** → Fim <período> (6170–6174) / Finalizado (5907). Outros: 5469/5684 acompanhamento, 5963/5967 sem resposta, 6116 despacho, 6139 Nereu-substituir informação (fluxo próprio, não é FRAP).

`scripts/analise/rastreio_verificar_frap.py` (criado 18/08/2026) une dois sinais — marcador ativo da família OU notificação de desconto em folha + resposta via DE (caso do 000068/2026, eventos 73/74, que estava sem marcador nenhum) — e cruza por CPF do responsável: contracheque (BdSIAIPessoal rubrica TCE/FRAP), repasses (FRAPLancamento) e parcelas (FRAPDescontoFolhaParcela). Saída em `saidas/analise/rastreio_verificar_frap.xlsx`; em 18/08/2026: 97 processos, 8 já com 5953, **18 a marcar com 5953** (aplicação manual no sistema, pendente). Seção própria criada no AGRUPAMENTO_PROCESSOS.md (26 processos).

Informações geradas em 18/08/2026: `processos/verificacao_frap/gerar_informacoes.py` — uma por processo (docx+pdf em `processos/verificacao_frap/{completo|curso}/<num>_<ano>/`; `completo/` = desconto cessado há meses sem quitação: 005351/2017 (79% coberto, cessou 06/2025) e 003272/2023 (62%, cessou 02/2025) — set `COMPLETO` no script; cuidado: plano do FRAPDescontoFolha concluído NÃO significa dívida quitada, os planos são tranches menores que o débito), modelo_informacao.docx + quadros TCE/RN, base art. 25, § 1º, I e §§ 3º/4º da Res. 013/2015. Quatro variantes: conciliação (6), desconto sem repasse (8), repasse sem desconto visível no SIAI (1: 003051/2025), sem registros (11). Ressalva automática quando o mesmo CPF figura em mais de um processo do lote (ex.: 000068/000079/2026).

Armadilhas: `FRAPDescontoFolhaParcela` tem a MESMA parcela cadastrada até 5× (planos-tranche sobrepostos, ex. CPF da Daize 005351/2017: 127 registros → 56 reais) — sempre deduplicar por CpfCnpj+competência+ValorEsperado antes de somar; `FRAPLancamento.CpfCnpjDepositante` é NULL em ~98% e pode vir com zeros à esquerda (casar por `RIGHT(...,11)`); repasse confirmado é melhor detectado por `FRAPDescontoFolhaParcela.DataPagamentoParcela`. A atribuição por CPF não distribui valores entre processos do mesmo responsável (Nereu tem ~30 processos com o mesmo total). Ver [[nereu-desconto-folha-progresso]], [[frap-tables-in-bddip]].
