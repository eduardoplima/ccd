---
name: relatorio-auditoria-financeira-ccd
description: Relatório-diagnóstico à gestão do TCE/RN que enquadra a carteira da CCD e o FRAP sob NBASP/NBC TASP
metadata: 
  node_type: memory
  type: project
  originSessionId: ea2b76ec-9de0-4760-94f1-edbf603e7a9e
  modified: 2026-08-14T16:49:25.154Z
---

Produzido em 14/08/2026: `docs/notas/RELATORIO_AUDITORIA_FINANCEIRA_CCD.md`, gerado em .docx/.pdf
por `python -m scripts.automacao.gerar_relatorio_docx <md>` — usa `templates/modelo_informacao.docx`
como base (cabeçalho DIP/CCD) e acrescenta rodapé "Página X de Y", que o modelo não tem.

Tese: os três trabalhos já existentes da CCD — carteira IPSAS, baixa de débitos, conciliação FRAP —
são, na verdade, reconhecimento, desreconhecimento e realização em caixa do mesmo ativo financeiro.
Nomeados assim, viram um diagnóstico único endereçável pela gestão. Postura acordada com o usuário:
"oportunidade de aprimoramento", nunca "deficiência/achado".

**Why:** o argumento institucional que sustenta o relatório é a assimetria — o Tribunal exige dos
jurisdicionados índice de recebibilidade e política formalizada de ajuste para perdas (MCASP), e não
aplica nenhum dos dois aos créditos que ele próprio gera.

**How to apply:** números-âncora em 14/08/2026 — ativo bruto R$ 353,2 mi (9.565), provisão 83,89%,
líquido R$ 56,9 mi, contingente R$ 286,7 mi (1.409), recuperado R$ 7,81 mi; caixa FRAP 2021–jun/2026
R$ 8,87 mi com **62,7% de cobertura** (37,3% entra sem vínculo com o crédito); 85,3% do ativo bruto
sem protesto nem dívida ativa. Correspondência normativa conferida no CFC: IPSAS 23→NBC TSP 01,
IPSAS 19→**NBC TSP 03 (R1)** (não a 19, que é Acordos em Conjunto), IPSAS 41→NBC TSP 31 (R1),
IPSAS 30→NBC TSP 33; NBASP 200/2000 publicadas pelo IRB em 30/11/2023; NBC TASP = Res. CFC
1.601/2020. Reproduzir com `carteira_ipsas` + `conciliacao_competencia_caixa` (ambos têm
`--self-check` sem banco). Ver [[exe-debito-cadeia-folha-vigente]] e [[ipsas-carteira-ccd]].
