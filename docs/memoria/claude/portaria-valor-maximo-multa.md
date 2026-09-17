---
name: portaria-valor-maximo-multa
description: "Portaria anual da Presidência fixa o valor máximo da multa do art. 107, II da LC 464/2012; 2021 = Portaria 009/2021-GP/TCE (R$ 16.054,81); como achar as de outros anos"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7a8f70b9-3722-49e3-be45-14c2985fc471
  modified: 2026-08-28T18:32:29.438Z
---

O valor máximo da multa do art. 107, II, da LC 464/2012 (e art. 323, II do Regimento) é atualizado anualmente por portaria da Presidência (art. 107, §4º), publicada em janeiro no Diário Eletrônico.

- **2021**: Portaria nº 009/2021-GP/TCE, de 14/01/2021 — R$ 16.054,81. Publicada no DOE nº 2740, de 18/01/2021 (`DOE18012021164715.pdf`).
- Outros anos conhecidos: 104/2017 (R$ ~13.908), 012/2018 (R$ 14.272,55), 021/2020.

**Como achar a de qualquer ano**: API aberta do SISDOCS — `https://sisdocs.tce.rn.gov.br/api/v1/DiarioEletronico/BuscarDiariosAntigos` lista todos os diários antigos (json com `numero`, `dataPublicacao`, `arquivo`); PDF em `https://www.tce.rn.gov.br/as/DOE/OUTROS/<arquivo>`. O servidor derruba conexões do curl com UA padrão — usar User-Agent de navegador. Baixar os diários de janeiro e grepar "valor máximo da multa". Config da SPA (bases de API) em `https://diario.tce.rn.gov.br/assets/config.json`.

Relacionado: [[multas-resolucao-004-2013-gradacao]] (percentuais aplicados sobre esse teto).
