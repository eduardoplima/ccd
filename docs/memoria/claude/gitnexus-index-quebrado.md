---
name: gitnexus-index-quebrado
description: Índice GitNexus do repo ccd inoperante (storage v41 vs build v40); reanálise segfaulta
metadata: 
  node_type: memory
  type: project
  originSessionId: 904823ad-5b92-4a9b-8dff-342af4c5be94
  modified: 2026-08-28T18:35:23.546Z
---

Desde 28/08/2026 as ferramentas GitNexus (impact, query, detect_changes) falham no repo ccd: "Database file version: 41, Current build storage version: 40" — o índice foi escrito por uma versão mais nova do que o binário atual. `node .gitnexus/run.cjs analyze` morre com exit 139 (segfault). Enquanto não for corrigido (atualizar o gitnexus ou apagar `.gitnexus`/índice e reindexar), as regras "MUST run impact/detect_changes" do CLAUDE.md são inexecutáveis — fazer análise de impacto manualmente por leitura/grep e avisar o usuário.

**Why:** evitar repetir tentativas de reindexação que travam a sessão.
**How to apply:** se as ferramentas voltarem a responder, apagar esta memória.
