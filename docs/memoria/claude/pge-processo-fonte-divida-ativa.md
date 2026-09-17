---
name: pge-processo-fonte-divida-ativa
description: "Inscrição em dívida ativa (CDA, valor, status) vive em PGE_Processo; Exe_Debito.Status_PGE está vazio"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 12d2847c-fac0-466a-acba-81fda64d31d4
  modified: 2026-08-04T13:13:38.587Z
---

Para saber se um débito foi inscrito em dívida ativa, consultar `processo.dbo.PGE_Processo`
por `IdDebitoExecucao` — traz `NumeroCDA`, `ValorAtualizadoPGE`, `DataEnvioInscricaoDividaPGE`,
`HomologadoPGE` e os FKs `IdStatusProcessoPGE` (`PGE_StatusProcesso`: 1=Inscrito em Dívida
Ativa, 3=Quitado, 5=Cancelado…) e `IdStatusEnvio` (`PGE_StatusEnvio`: 2=Enviado Com Sucesso).

**Why:** `Exe_Debito.Status_PGE` / `Numero_OB_PGE` / `Status_Dfo` / `Status_Cfp` vêm **vazios**
mesmo em débitos comprovadamente inscritos — checá-los dá falso negativo. Visto em 04/08/2026
nos débitos 28815 e 28218 (execução 001393/2023): ambos com `Status_PGE` NULL e, ao mesmo
tempo, `PGE_Processo` 1518/1519 inscritos e homologados em 29/07/2026.

**How to apply:** O `ValorAtualizadoPGE` da CDA é um valor **datado e documentado** — preferir
esse ao `ccCorrecaoMonetaria` gravado em `Exe_Debito`, que é snapshot de data desconhecida.
Ver [[exe-debito-valorapagar-vazio]] e [[arrecadacao-multa-vs-pge]].
