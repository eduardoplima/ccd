---
name: ccd-tramitacao-gabinete-bloqueada
description: "Desde 20/07/2026 a tramitação CCD→gabinetes é rejeitada (\"Setor interno não pode tramitar para setores externos\"); flag nao_tramita_setor_externo='S' na CCD"
metadata: 
  node_type: memory
  type: project
  originSessionId: d01ba2e0-bff5-4bad-a352-83f0750ead20
---

Em 20/07/2026 (à tarde, após deploys da Área Restrita às 14:37 e 15:17 — buildtime nos .js), a tramitação CCD → gabinete (GCAED etc.) passou a ser rejeitada pelo servidor com a mensagem em vermelho no frame de botões: **"Setor interno não pode tramitar para setores externos, e vice-versa."**

- A falha é **silenciosa** no fluxo requests ([[area-restrita-tramitar-flow]]): o POST `oculto=I` responde com a listagem de novo e o alert "Operação realizada com sucesso." — que é **JS estático** (aparece até em consulta); o único sinal confiável é o processo continuar na listagem. A mensagem real só aparece no frame `botoes` da UI.
- Confirmado com a UI real (Playwright, cliques reais): mesmo resultado.
- Evidência no banco: `Setor.nao_tramita_setor_externo = 'S'` **apenas na CCD** (DIP e gabinetes = NULL). CCD→DIP funcionou às 13:55 do mesmo dia; round_1 CCD→gabinetes funcionou em 13/07.
- Estado do processo (distribuído ou não) muda o sintoma: sem distribuição ele aparece no form de envio (M) e o I falha; distribuído ("em análise") ele nem é ecoado no form do M.
- Desbloqueio: chamado à TI (ajustar a regra/flag) ou rota permitida CCD→DIP.
