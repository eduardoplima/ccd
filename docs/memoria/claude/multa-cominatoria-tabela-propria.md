---
name: multa-cominatoria-tabela-propria
description: "Detalhe da multa diária está em Exe_Debito_MultaCominatoria; nº de diárias vem do total, não da diferença de datas"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 12d2847c-fac0-466a-acba-81fda64d31d4
  modified: 2026-08-04T13:13:45.841Z
---

Multa cominatória (multa diária) = `Exe_Debito.CodigoTipoDebito` **5**, com o detalhe em
`processo.dbo.Exe_Debito_MultaCominatoria` (1:1 por `IdDebito`): `ValorMultaCominatoria`
(valor/dia), `CcTotalMultaCominatoria` (montante apurado), `LimiteValor` (teto aplicado),
`DataInicioImputacaoMultaCominatoria` / `DataFinalImputacaoMultaCominatoria`.

**Why:** o nº de diárias **não** é a diferença de datas. No débito 28815 o intervalo
25/11/2022–22/05/2023 tem 179 dias corridos, mas o sistema imputou **178** diárias
(R$ 17.800,00 ÷ R$ 100,00). Calcular por data gera texto que não bate com o valor.
`ImplementadaProcessoExecucao` é inútil como indicador — NULL em 214 dos 217 registros.

**How to apply:** derivar `DIAS = round(CcTotalMultaCominatoria / ValorMultaCominatoria)` e
travar com assert. O teto costuma ser o do art. 323, II, "b", do RITCE, atualizado por
portaria da Presidência (ex.: R$ 17.728,31 pela Portaria nº 014/2022-GP/TCE).
Exemplo em `processos/002166_2024/gerar_informacao.py`.
