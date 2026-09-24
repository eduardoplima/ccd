---
name: nereu-ms-auditoria-verbas-saude
description: Auditoria nereu_ms (verbas transitórias saúde) — bugs 1/2 corrigidos 23/07/2026; bug 3 aberto (keyword sem semântica deu OK ao 003070/2022, que é errado); listas de suspeitos
metadata: 
  node_type: memory
  type: project
  originSessionId: 63725b44-9f07-4395-98f4-cbc7f5f5a90c
  modified: 2026-07-24T15:17:25.864Z
---

Auditoria `scripts/analise/verificar_verbas_saude_nereu.py` (saídas em
`output/analise/verificacao_verbas_saude_nereu.{xlsx,md}`). Dois bugs corrigidos
em 23/07/2026:

1. Regra "órgão da origem é da saúde" dava OK sem exigir verba **transitória**
   (falso-negativo apontado pelo usuário no 001390/2023).
2. **`vw_ata_informacao.IdProcesso` vem NULL nas informações mais novas** — o
   filtro por IdProcesso perdia DAP_BENs (177→622 infos ao filtrar por
   número/ano). Causou falsos "NAO_SAUDE" (002038/2024 "sem DAP_BEN";
   011525/2009 e 003070/2022 avaliados só pelas infos de 2016).

Resultado final (168 OK / 5 NAO_SAUDE / 3 MANUAL):
- **NAO_SAUDE (5)**: 000119/2022, 000134/2022, 003006/2022 (FUNDASE),
  003709/2022 (SEEC), **003673/2022 (round 1, ADTS = permanente)**.
- **MANUAL (3, todos round 1, relator Carlos Thompson os 2 primeiros+001390)**:
  **001390/2023** (confirmado errado pelo usuário: erro de cálculo de
  proventos, origem 007239/2017), 003691/2022 (mesmo padrão), 003663/2022
  (perda de objeto por óbito).
- 011525/2009: falso positivo da auditoria antiga — usuário confirmou (evento
  58 = DAP_BEN ordem 59, insalubridade+noturno); OK.
- **003070/2022 é ERRADO** (usuário, 24/07/2026), apesar do OK da auditoria.
  Origem 007245/2017 (Maria Gamelo, SESAP): mesmo padrão do 001390/2023 — erro
  de cálculo de proventos (média das 80% maiores contribuições, Lei
  10.887/2004), não verba transitória. **Bug 3 (não corrigido)**: a regra
  determinística "órgão saúde + keyword transitóri" deu OK porque a info de
  monitoramento (DAP_BEN ordem 36) chama a irregularidade, imprecisamente, de
  "vantagens transitórias"; a conclusiva (ordem 3) e a Decisão 2493/2020-TC
  falam só em cálculo. Keyword match não é semântica e o LLM só rodava nos
  AMBIGUO. **Corrigido em 24/07/2026**: LLM roda em TODAS as origens; keywords/
  órgão viraram cross-check; prompt exclui explicitamente erro de cálculo
  (média das 80%, Lei 10.887/2004).

**002564/2024 (24/07/2026)**: usuário resgatou do GCAED à CCD; informação de
correção gerada (`output/automacao/nereu_ms_correcao/002564_2024.pdf`, template
modelo_nereu_correcao) e cadastrada como CCD_002564_2024_0060 — **pendente de
assinatura** (usuário pediu só cadastrar). Após assinar: substituir a
instrutiva errada de 15/07 e decidir tramitação.

**Rodada 24/07/2026 (LLM em todas as 176 origens): 165 OK / 10 NAO_SAUDE /
1 MANUAL.** Além dos já conhecidos: **002564/2024 (round 1!, origem
002785/2017 SESAP — erro de cálculo do vencimento básico)** é suspeito novo;
003380/2024 (round 2, origem 101636/2019) saiu NAO_SAUDE pelo LLM ("servidor
do IPERN") mas o **usuário confirmou em 24/07/2026 que está CORRETO** (falso
positivo do LLM) — tramitado à DIP em 24/07 (ENVIO A GCAED; estava na CCD,
não foi no lote de 21/07);
001390/2023 e 003691/2022 (origem 012468/2015, média das 80%) migraram
MANUAL→NAO_SAUDE; 003663/2022 segue MANUAL (origem 018341/2016 só monitora/
remete pensão). 013166/2017 (no GCCTH) e 011525/2009 = OK. **019033/2017 TEM débito**
(28033: origem 019033/2017, execução 002162/2025 — ambos nas listas; o
"sem débito" era artefato do dedup por processo_ccd, corrigido no script em
24/07); a origem foi auditada OK (insalubridade, SESAP).

Round 1 = informações já cadastradas ([[nereu-ms-envio-progresso]]); dos
suspeitos round 1 só 011525/2009 tinha sido tramitado (GCCTH) e ele é OK — os
errados (001390/2023, 003673/2022, 003691/2022, 003663/2022) estão na CCD.

002038/2024 revertido em 23/07/2026: correção de 21/07 substituída de volta
pela informação nereu_ms (recadastrada como CCD_002038_2024_0058 — exigiu
redistribuir antes; assinatura+substituição feitas à mão pelo usuário) e
tramitado CCD→DIP com providência "ENVIO A GCAED" (via DIP funciona; direto
a gabinete segue bloqueado).

**Why:** as informações nereu_ms afirmam débito decorrente de verba transitória
de servidor da saúde; cadastrar fora desse perfil é erro material na peça.

**How to apply:** ao consultar `vw_ata_informacao`, nunca filtrar por
IdProcesso (usar numero/ano). Antes de gerar/enviar lote nereu_ms, rodar a
auditoria e excluir NAO_SAUDE/MANUAL.
