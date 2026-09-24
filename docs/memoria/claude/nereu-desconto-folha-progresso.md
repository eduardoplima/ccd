---
name: nereu-desconto-folha-progresso
description: Lote nereu_desconto_folha — 8 tramitados CCD→DIP em 17/08/2026; resta 002564/2024 (suspenso)
metadata: 
  node_type: memory
  type: project
  originSessionId: 85f8898a-22f6-4284-9819-a22111910675
  modified: 2026-08-26T13:03:31.236Z
---

Lote de desconto em folha do Nereu ([[nereu-presidente-ipern]]): 9 informações
assinadas em 07/08/2026 (gerador `processos/utils/gerar_informacoes_nereu_desconto_folha.py`).
Em **17/08/2026** os **8 não suspensos** foram tramitados **CCD → DIP** com providência
"Envio DE Nereu Desconto" (destino final = Diretoria de Expediente, sigla DE; a DIP é
intermediária) — verificado: saíram da listagem da CCD.

Pendências: **002564/2024** ficou de fora (débito 27187 **Suspenso**; há informação órfã
CCD_002564_2024_0060 não assinada a investigar); marcadores "Implementar Nereu" só saem
quando a SEAD implementar o desconto. Trilha distinta de [[nereu_baixa]] (processos já
pagos). Estado detalhado no HANDOFF.md do repo.

**Conciliação FRAP (verificada 26/08/2026, extrato carregado só até 31/07/2026):**
descontos SIAI (rubrica "FRAP TC", `BdSIAIPessoal`, duplicatas por reingestão — dedupe
por competência): 04/2026 R$ 1.117,83 · 05/2026 e 06/2026 R$ 5.291,22 cada ·
07/2026 R$ 7.188,72 (salto = novos débitos implantados). Ingresso: **só 1 crédito exato
R$ 5.291,22** (IdLancamento 14265, OB 29/07/2026, conta 700000-6) → cobre UMA das duas
competências de 5.291,22. **04/2026 sem repasse** (lag histórico é ~1 mês; janela vencida).
06 e 07/2026 podem estar em agosto, fora do extrato carregado. O cadastro
`FRAPDescontoFolha` do Nereu (plano 128, parcelas ~R$ 1,3k) está desatualizado vs os
descontos reais, e o `FRAPMatchDescontoFolha` foi calculado pela última vez em 12–14/05/2026
(tudo NAO_DESCONTADA — stale). Repasse do Nereu vem como OB própria no valor exato do
desconto (padrão do baseline `debitos_conciliados_nereu.xlsx`, congelado em 05/2025).
