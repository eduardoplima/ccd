---
name: tag-sao-bento-cadernos-1323-1325
description: "Cadernos do TAG 04/2018 (São Bento do Trairí, Acórdão 293/2023): 001323/2024 (Prefeito José Aracleide) e 001325/2024 (Juliana, Educação) — defesas TEMPESTIVAS; informações de mérito enviadas 03/09/2026 e SUBSTITUÍDAS no mesmo dia por declínio de atribuição à CIP; 001324 (Márcia) foi revelia, tramitada 27/08"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8f7ac60a-eca8-44b1-b736-de76e2519fd2
  modified: 2026-09-03T16:40:20.270Z
---

Três cadernos irmãos do Acórdão 293/2023-TC (Proc. 006775/2018), relator George Montenegro (cód. 19), MPC pediu conversão em execução (multa Cláusula Sétima, R$ 10 mil/mês):
- **001324/2024** Márcia Cristina (Assist. Social): defesa INTEMPESTIVA (03/08, prazo até 29/07) → informação de revelia, tramitada 27/08/2026.
- **001323/2024** José Aracleide de Araújo (Prefeito; o Assunto grafa "Aracieide", errado): AR 10/07, prazo 13/07–07/08, defesa 05/08 → TEMPESTIVA. Informação em `processos/informacoes/001323_2024/` gerada 02/09/2026 → **ENVIADA 03/09/2026** (CCD_001323_2024_0022, assinada Web PKI, tramitada CCD→DIP "ENVIO A GCGEO").
- **001325/2024** Juliana Patrícia de Oliveira Pessoa Dantas (Educação): AR 01/07, prazo 02/07–29/07, defesa 29/07 (último dia) → TEMPESTIVA. Tese do 1º Termo Aditivo não homologado tem respaldo no voto do Acórdão 293/2023 (só o TAG do ev. 11 foi homologado). Informação em `processos/informacoes/001325_2024/` (docx regerado 03/09 10:00) → **ENVIADA 03/09/2026** (CCD_001325_2024_0021, assinada, tramitada CCD→DIP "ENVIO A GCGEO").

**Virada de 03/09/2026 — análise de defesa NÃO é atribuição da CCD.** Os cadernos com
defesa (1323 e 1325) são da **CIP**: art. 31 da Res. 042/2024-TCE dá a ela o exame e a
instrução de processos de controle externo em sede de defesa ou recurso; o art. 32
reserva à CCD só obrigações/recomendações, cobrança executiva e apoio à
indisponibilidade. As informações de mérito foram substituídas por uma informação
curta de declínio, gerada por `processos/utils/gerar_informacao_cip.py` (um script para os
dois; saídas `informacao_cip_00132X_2024.docx/pdf` nas pastas de cada processo, sem
tocar nos geradores de mérito). O texto invoca o art. 31 **como um todo**, nunca o
inciso I, para não tomar posição sobre haver ou não análise preliminar anterior da
unidade técnica. O 001324 (revelia, sem defesa a examinar) não foi tocado.

Ciclo do declínio concluído em 03/09/2026: distribuição própria → cadastro
(`CCD_001323_2024_0023` ordem 47; `CCD_001325_2024_0022` ordem 45) → assinatura A3 →
substituição (ordem 44→47 e 42→45) → tramitação CCD→DIP com providência
**"ENVIO A CIP"** (não há CIP em `GABINETES`, use `--providencia` explícita). Como
substituída e substituta têm o mesmo autor e a mesma data, `substituir` **exige
`--ordem` da antiga** — sem ela o script elege a nova como substituída e inverte o
par; descubra as ordens rodando `substituir --autor ZZZ --dry-run`, que lista todas.

**How to apply:** sugestões nos tempestivos = conhecer defesa + vista ao MPC (art. 37 §5º LC 464 / art. 200 §4º RI) + retomar conversão. Reusar os scripts como base para outros signatários (Rayres, Anesiano etc.) se aparecerem na CCD. Ver [[cit-certidao-situacao-21-ambigua]].
