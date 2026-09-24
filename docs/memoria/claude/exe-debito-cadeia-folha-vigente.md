---
name: exe-debito-cadeia-folha-vigente
description: "Na cadeia IdDebitoAnterior o débito vigente é a FOLHA, não a raiz — a convenção \"IdDebitoAnterior IS NULL = head\" usada no repo lê o débito original"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb93fc6a-281d-4f8b-ad84-5dba401aea89
  modified: 2026-08-14T16:49:09.966Z
---

`Exe_Debito.IdDebitoAnterior` encadeia versões do mesmo débito **para a frente**: registrar um
pagamento em X grava `ValorPago`/`dataBaixa` em X (status → 3) e **cria um filho** Y com o saldo
remanescente. Logo o débito vigente é a **folha** (`NOT EXISTS (SELECT 1 FROM Exe_Debito f WHERE
f.IdDebitoAnterior = d.IdDebito)`), e `IdDebitoAnterior IS NULL` devolve o **original**.

**Why:** o repo inteiro usa `e.IdDebitoAnterior IS NULL` comentado como "head do débito"
(`scripts/analise/carteira_ipsas.py`, `debitos_nereu.py`, `ccd/sql/processos_transito_nome.sql`,
`processos/projetos/nereu_desconto_folha/gerar.py`). Em 1.602 das cadeias (de 27.709 débitos / 17.115
raízes / 17.931 folhas) raiz ≠ folha e a leitura pela raiz pega status e saldo errados — ex.:
raiz 924 em status 3 cuja folha 17476 já é status 2 (Pago Integralmente).

**How to apply:** para saldo/status atual, filtrar pela folha. Para o valor da condenação
original, a raiz. `Exe_HistoricoDebito.dataInclusao` bate ao milissegundo com o `datainclusao`
do filho que a operação gerou — é assim que se reconstrói o que o operador fez. Folha com
`ValorPago` NULL e status 1 é o estado **normal** (10.674 casos); status 3 nessa posição é
defeito (13 casos, analisados em `docs/notas/ANALISE_CHAMADO_DEBITOS_STATUS3.md`).

**Corrigido em 14/08/2026 apenas em `scripts/analise/carteira_ipsas.py`**, com CTE recursiva que
agrega por cadeia: valor imputado da raiz, situação da folha, `SUM(ValorPago)` de todos os nós.
Efeito medido: ativo bruto 356,8 → 353,2 mi; provisão 88,50% → 83,89%; recuperação 5,16 → 7,81 mi
(+51%). Desempate de fork (200 cadeias, 546 folhas descartadas): folha mais profunda, depois
`datainclusao` mais recente — exposição de só R$ 7,6 mil ainda em aberto. Os demais pontos do repo
(`debitos_nereu.py`, `ccd/sql/processos_transito_nome.sql`, `processos/projetos/nereu_desconto_folha/gerar.py`)
**seguem lendo a raiz**.

Relacionado: [[exe-debito-valorapagar-vazio]], [[exe-parcelamento-semantica]],
[[ipsas-carteira-ccd]], [[relatorio-auditoria-financeira-ccd]].
