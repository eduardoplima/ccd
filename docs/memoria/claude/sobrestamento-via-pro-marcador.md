---
name: sobrestamento-via-pro-marcador
description: "Sobrestamento não tem coluna própria — apurar por DUAS vias: marcador (Pro_Marcador LIKE '%sobrest%') E decisão do relator registrada como informação (nome/resumo 'Decis%sobrest%')"
metadata: 
  node_type: memory
  type: project
  originSessionId: 14cb1774-2e32-429b-909a-9c2c7d64a9ab
---

No banco `processo` não existe coluna/tabela de sobrestamento; o registro prático é por **marcador**: `Pro_MarcadorProcesso` (Numero_Processo/Ano_Processo, DataInclusao, DataExclusao) × `Pro_Marcador` (Descricao). Filtrar `Descricao LIKE '%sobrest%'`. Para o tema [[nereu-presidente-ipern]], o marcador é o 5846 "Nereu - SOBRESTADO" (setor 90/CCD, aplicado em 22–23/07/2025, DataExclusao NULL): em 10/07/2026 cobria 9 dos 92 processos do `gerar_info_nereu_ms.py`.

**O marcador sozinho NÃO basta** (erro grave detectado 13/07/2026): 22 dos 26 processos de carlos/protesto tinham decisão de sobrestamento do relator **sem marcador** — registrada só como informação do gabinete (nome/resumo "Decisão sobrestamento do processo de execução e da prescrição - NEREU", GCCTH 22/10/2025; ex.: evento 102 do 001391/2023). Apurar sempre pelas DUAS vias: marcador `%sobrest%` UNION `vw_ata_informacao` com `nome_informacao/resumo LIKE 'Decis%sobrest%'`. `fetch_sobrestados()` em `gerar_info_nereu_ms.py` já faz o UNION desde 13/07/2026.
