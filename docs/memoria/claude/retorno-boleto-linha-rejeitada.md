---
name: retorno-boleto-linha-rejeitada
description: "Pagamento creditado pelo BB pode não baixar o crédito — a rotina de importação rejeita a linha com \"Boleto ID = N já está com status pago\""
metadata: 
  node_type: memory
  type: project
  originSessionId: b6a1cb85-1e03-43da-be2d-0731a7c78c66
  modified: 2026-09-03T16:46:22.255Z
---

O arquivo de retorno do BB traz o detalhe boleto a boleto do crédito diário
("617 Recebimento de guias" no extrato do FRAP). `Exe_Retorno` guarda o total
**declarado** (`ValorTotal`, `QtdBoletos`); `Exe_Retorno_Boleto`, só as linhas
**aceitas**. Quando os dois não batem, entrou dinheiro na conta sem baixar o crédito.
`Exe_Retorno_Log` guarda a linha CNAB crua e o motivo da recusa.

Apurado em 03/09/2026 sobre toda a série 2020–2026: 6.205 linhas rejeitadas, mas
**6.184 são benignas** (o banco reenvia um arquivo já importado e o boleto já tem o
pagamento certo). Só há perda quando `SUM(Exe_Retorno_Boleto.ValorPago)` do boleto é
**menor que `Exe_Boleto.ValorTotalAPagar`** ou é NULL — **4 casos, R$ 5.960,95**:

| arquivo | boleto | título | registrado | processo |
|---|---|---|---|---|
| 21/10/2021 | 20526 | 237,69 | — | 015141/2014 |
| 28/02/2026 | 36991 | 948,27 | 2,02 | 004164/2020 (déb. 23232) |
| 16/04/2026 | 38259 | 1.481,87 | — | 000550/2019 (déb. 28484) |
| 14/05/2026 | 38688 | 3.293,11 | — | 000745/2020 (déb. 27695) |

**Gatilho do caso 004164/2020**: em 06/02/2026 dois créditos irrisórios com
`FormaPagamento=4` (R$ 1,01 no boleto 36977 / 004424-2020 e R$ 2,02 no 36991) marcaram
os boletos como pagos. Em 27/02 o responsável pagou os R$ 948,27 de verdade; o crédito
entrou no arquivo `rcb001.bco001.28022601180287` (60 boletos, R$ 24.843,18, creditado
02/03/2026) e a **linha 41 foi rejeitada** — o arquivo importou 59 boletos e
R$ 23.894,91, exatamente R$ 948,27 a menos. Esses dois são os **únicos** pagamentos
abaixo de 5% do título em toda a base: padrão de sonda, não de erro.

Script: `scripts/analise/retornos_boleto_nao_importados.py` (`--self-check` offline).
Ver [[frap-extrato-bb-armadilhas]], [[arrecadacao-multa-vs-pge]],
[[exe-parcelamento-semantica]].
