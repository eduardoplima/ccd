---
name: processo-005090-2018-citacao-frustrada
description: "005090/2018 na CCD com marcador \"EXECUÇÃO - Instaurar processo\", mas sem prova de citação; informação sugere completar o art. 46, §2º antes do edital"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3e1d34c4-ef4f-47a2-9338-1fcda2ab1b97
  modified: 2026-08-24T17:45:39.774Z
---

Processo 005090/2018-TC (IdProcesso 478246), denúncia contra a Câmara de Monte das Gameleiras. Acórdão 137/2025, trânsito em 25/08/2025: Welington Ferreira da Silva (IdPessoa 13118) condenado a R$ 79.460,00 de ressarcimento (credor: a **Câmara**, IdOrgao 99) e R$ 1.000,00 de multa. Débitos 28345 e 28346, `IdProcessoExecucao` ainda NULL.

**A citação de execução nunca se aperfeiçoou.** O AR da citação 002614/2025 voltou "AO REMETENTE" ("Mudou-se"/"Não Procurado", uma só tentativa) — ver [[ar-baixa-entregue-pode-ser-devolucao]]. Logo falta a **prova de citação** que o art. 24 da Res. 013/2015 exige para constituir a execução, e a CCD está impedida de instaurar apesar do marcador 5031.

**Why:** os três despachos de execução do gabinete (28/11/2025, 12/06/2026, 21/07/2026) são fórmulas "de ordem" idênticas; o pedido de edital da DE (Evento 100) nunca foi apreciado.

**Estado em 24/08/2026: ENVIADO.** Informação CCD_005090_2018_0066 cadastrada, assinada e tramitada CCD→DIP com providência "ENVIO A GCGEO". O script reproduz a versão revisada de punho próprio pelo Coordenador (que suprimiu o quadro de débitos, os valores no corpo, o parágrafo sobre a baixa espúria de 21/01/2026 e o da prescrição, e pôs as sugestões em alíneas de 2º nível). Ressalva: o texto final chama a fonte dos vínculos de "SIAI Pessoal", mas os dados vêm de `SiaiDp_*` — ver [[siai-despesa-pessoal-vs-siai-pessoal]].

**How to apply:** a informação gerada (`processos/005090_2018/gerar_informacao.py`) sugere completar o art. 46, §2º da LC 464/2012 antes do edital — a DE notificou CAERN e COSERN, mas **não os órgãos de vínculo**, que o SIAI DP comprova: Câmara e Prefeitura de Monte das Gameleiras (2013–2020) e **Prefeitura de Serra de São Bento** (professor, 2017–2019). Cuidado com o **homônimo** IdPessoa 23176 (CPF 851.106.474-53, Brejinho/RN), citado por erro em 2024. Pendente também a multa cominatória do item "b" do acórdão (R$ 1.000/dia), nunca apurada.
