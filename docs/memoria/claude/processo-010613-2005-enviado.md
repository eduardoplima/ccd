---
name: processo-010613-2005-enviado
description: 010613/2005 (CM Santana do Matos) — informação CCD enviada à DIP 28/08/2026; descontos IPERN aparecem na folha SEAD do SIAI DP; Acórdão 135/2026 tem dispositivo impresso contaminado
metadata: 
  node_type: memory
  type: project
  originSessionId: fb50ee58-9879-4b4c-8fcf-7173b04e07c9
  modified: 2026-08-28T14:56:36.728Z
---

Processo 010613/2005 (DCD, CM Santana do Matos; Acórdão 239/2012, trânsito 29/05/2012; responsável Maria das Dores B. Assunção, CPF 00906234441): informação da CCD (`processos/informacoes/010613_2005/gerar_informacao.py`, ordem 0063) cadastrada, assinada e tramitada CCD→DIP em 28/08/2026, providência "ENVIO A GCREN". Sugestões: notificar a SEAD (repasse de 4×R$ 391,96 = R$ 1.567,84 descontadas e não repassadas ao FRAP) e deliberar sobre prescrição (multas art. 115; ressarcimento via Tema 899).

Achados reutilizáveis:

- **Desconto "implantado no IPERN" aparece na folha da SEAD** no SIAI Despesa com Pessoal (`vwSiaiDPFolhaResumida`, BdDIP): sem rubrica nominal TCE/FRAP — o desconto fica embutido na rubrica agregada "Descontos diversos"; detectar pelo degrau exato do valor da parcela (aqui +391,96 em ago/2016, −391,96 em jun/2017).
- **Acórdão nº 135/2026 – 2ª Câmara (proc. 006457/2016)**: a ementa e o voto aplicam o Tema 899/STF (prescrição de ressarcimento, marcos do art. 115 LC 464/2012 por analogia) — citação segura. MAS o dispositivo impresso (`RelAcordao.rpt`, secsc_006457_2016_0026.pdf) está **contaminado**: itens a–c são de outro acórdão da mesma sessão (proc. 2870/2002, Francisco Artur de Souza). Ao citar, ancorar na ementa/voto (GCGIL_006457_2016_0022.pdf).
- No fluxo Área Restrita, o mojibake "EXECUĮÃO" no output do `assinar_informacoes` é só exibição do terminal — o resumo gravado sai correto (conferir via `AreaRestrita._consultar_digitar`, que lista ordem/resumo/assinado).
