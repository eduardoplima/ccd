---
name: monitoramento-obrigacoes-curadas
description: Acervo curado do CGAD (staging approved) vive fora do CGR; CGR parado desde 02/2025; rotina de monitoramento sob NBASP 100
metadata: 
  node_type: memory
  type: project
  originSessionId: 10c7a3d5-9049-4abe-b4ba-4ff6e921b851
  modified: 2026-09-04T14:43:58.234Z
---

O acervo **curado** do CGAD são as linhas `Status='approved'` de `BdDIP.dbo.ObrigacaoStaging` e `RecomendacaoStaging` — a existência da linha de staging É o registro da revisão humana (revisor, data, `PayloadOriginal` com o que o LLM propôs antes da edição). Não existe `ObrigacoesStaging` no plural, e o nome é singular: `ObrigacaoStaging`.

**Medições de 04/09/2026** (o acervo cresce a cada revisão — em 3h passou de 737 para 813 itens, então nunca fixar o número em documento):

- 813 itens curados (520 obrigações + 293 recomendações) em 538 processos.
- Apenas **16** pertenciam a processo com registro no CGR (`processo.dbo.Obg_Obrigacao`).
- `Obg_Obrigacao` estava **sem alimentação desde 07/02/2025**.
- 216 itens em processos já **arquivados**; só 31 em processo com `setor_atual='CCD'`.

Ou seja: "triagem dos processos na CCD" não pode significar `setor_atual='CCD'` — a competência do art. 32 da Res. 042/2024 segue a decisão, não a tramitação.

**Entrega**: `scripts/analise/monitoramento_obrigacoes.py` + `ccd/sql/obrigacoes_curadas.sql` + POP-CCD-013 (`web/backend/wiki/procedimentos/monitoramento-obrigacoes.md`, minuta). Triagem determinística em 4 buckets, varredura LLM das peças posteriores à decisão, ficha `.md` por processo. Sem módulo web, sem tabela, sem migração.

**Âncora normativa**: NBASP 100 (ISSAI 100), seção "Monitoramento" (número do item ainda não conferido no PDF do IRB — citar pelo nome da seção); NBASP 300 item 42; adesão do TCE/RN pela **Res. 010/2020-TCE de 07/07/2020**. O art. 32, I e II da Res. 042/2024 reproduz o vocabulário da NBASP 100 ("implicações mais amplas" + "relatório adicional"), e o prompt do `crivo_monitoramento.py` já operava esse critério sem citar a norma.

Relacionados: [[cgad-stage2-dedup-orphan-finals]], [[llm-citacao-precisa-ser-conferida]], [[fila-prioridade-ccd-inicio]].
