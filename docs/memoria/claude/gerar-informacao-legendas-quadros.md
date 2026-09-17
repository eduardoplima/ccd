---
name: gerar-informacao-legendas-quadros
description: "Todo quadro/tabela em gerar_informacao.py (processos/<n>/) deve ter legenda \"Quadro N – título\" acima da tabela"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 353ff52b-1e70-4cf4-84f8-8525dd21a677
  modified: 2026-07-27T18:45:36.268Z
---

Em todo `gerar_informacao.py` de `processos/<numero_ano>/`: quadros (tabelas docx)
devem ter **legenda acima da tabela**, no formato "Quadro N – <título>", numerada
pela ordem em que aparecem no documento (não pela ordem de inserção no script).

**Why:** pedido de Eduardo em 27/07/2026 ao gerar a informação do 001454/2023;
padrão de peça jurídica — o texto referencia "o quadro a seguir" e a legenda dá
o vínculo formal.

**How to apply:** parágrafo centralizado, negrito, cor verde-escuro `#1A3D28`
(identidade [[tce-rn-identity]] — os quadros seguem o padrão TCE/RN: cabeçalho
`#2E5B3C` branco, alternância `#F2F2F2`, total `#1A3D28`), inserido entre o
parágrafo-âncora e a tabela. Implementação de referência: helper `_tabela_apos`
em `processos/001454_2023/gerar_informacao.py`. Incluir as legendas no
self-check (`assert trecho in texto_final`).
