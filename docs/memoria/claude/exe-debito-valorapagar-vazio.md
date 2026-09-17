---
name: exe-debito-valorapagar-vazio
description: "Exe_Debito.ValorAPagar está NULL em 99,9% dos débitos em aberto — usar valorOriginalDebito como mensuração"
metadata: 
  node_type: memory
  type: project
  originSessionId: 17f7f05c-af83-4fb5-bfc7-452f55a91637
  modified: 2026-08-03T13:43:13.341Z
---

`Exe_Debito.ValorAPagar` **não** é o saldo devedor: está NULL em 10.144 dos 10.155 débitos
`Em Aberto` (medido em 03/08/2026). `CorrecaoApagar` e `JurosApagar` idem. `ValorPago` só é
preenchido onde o `CodigoStatusDivida` já diz pago (integral ou parcial) — não há receita escondida
em débitos abertos.

**Why:** a query legada `ccd/sql/processos_transito_nome.sql` expõe `ValorAPagar` como
"valor_atualizado", o que sugere um saldo corrigido que o sistema nunca alimentou. Somar essa coluna
dá R$ 134 mil onde `valorOriginalDebito` dá R$ 632 milhões.

**How to apply:** mensurar por `valorOriginalDebito`, subtraindo `ValorPago` para obter o saldo.
A carteira sai a valor histórico, sem correção monetária — registrar a limitação. Ver
[[ipsas-carteira-ccd]] e `scripts/analise/carteira_ipsas.py`.

Outra armadilha na mesma tabela: `Status_PGE` é `bit` (flag), não FK — o join com
`PGE_StatusProcesso` na query legada funciona por acidente (1 → "Inscrito em Dívida Ativa").
