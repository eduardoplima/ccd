---
name: ipsas-carteira-ccd
description: Estudo de IPSAS (certificação ACCA) usando a carteira de créditos da CCD como laboratório
metadata: 
  node_type: memory
  type: project
  originSessionId: 17f7f05c-af83-4fb5-bfc7-452f55a91637
  modified: 2026-08-03T14:20:34.578Z
---

Objetivo em curso desde 03/08/2026: especialização em IPSAS para a certificação ACCA, usando os
dados da CCD como laboratório. Perspectiva escolhida: **o TCE/Estado como entidade que reporta**
(auditoria de convergência dos jurisdicionados foi explicitamente descartada).

Artefatos: `IPSAS_APLICACAO_CCD.md` (mapa norma → dado → exercício),
`scripts/analise/carteira_ipsas.py` (carteira + matriz de perda esperada) e
`PESQUISA_IPSAS_PUBLICACAO.md` (revisão de literatura + proposta de artigo).

Ângulo de publicação: a literatura trata TC como fiscal da contabilidade **alheia** (linha Lino &
Azevedo), nunca como entidade que reporta os créditos das próprias sanções. IPSAS 47 vigora desde
01/01/2026 e condiciona o reconhecimento à *enforceability* + *past experience*; STF Tema 899
(RE 636.886, 20/04/2020) tornou prescritível o ressarcimento de decisão de TC, dando choque exógeno
com multa como controle (já prescritível pela Lei 9.873/1999). Alvo: JPBAFM ou FAAM.

**Why:** a CCD administra uma carteira de créditos de transação sem contraprestação — objeto
literal da IPSAS 23 —, mas só a enxerga pela lente de cobrança. A lente contábil produz números que
ninguém tinha: provisão para perdas de 88,6% sobre R$ 356,7 mi reconhecidos, porque o Tribunal
recebe as dívidas pequenas (mediana R$ 600) e perde as grandes (mediana R$ 10.252).

**How to apply:** os 13 códigos de "Cancelada" do `Exe_StatusDivida` **não** são equivalentes —
separar perda de crédito (prescrição/perdão/óbito/extinção, calibra a provisão) de
desreconhecimento (decisão do relator/novo acórdão/judicial, é reversão de receita) de nunca-foi-ativo
(erro de cadastro/duplicidade/unificação/reabertura, sai da base). O grão é o débito, nunca a pessoa:
`Exe_DebitoPessoa` multiplicaria a carteira pelos solidários. Ver [[exe-debito-valorapagar-vazio]]
para a mensuração e [[exe-parcelamento-semantica]].
