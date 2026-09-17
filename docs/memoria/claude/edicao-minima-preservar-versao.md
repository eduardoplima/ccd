---
name: edicao-minima-preservar-versao
description: Feedback forte do usuário — alterar SÓ os pontos pedidos e sempre preservar a versão anterior de arquivos gerados em outro arquivo (backup com timestamp)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c3f2290e-75db-49bb-aed7-9dc5b84fce5d
---

Ao alterar documentos/scripts, mexer **somente** nos pontos especificamente pedidos; nunca remover/reescrever trechos vizinhos por iniciativa própria. Antes de sobrescrever um arquivo gerado (.docx etc.), copiar a versão atual para `<nome>_YYYYmmdd_HHMMSS.<ext>`.

**Why:** Em 10/07/2026 regenerei um docx e alterei a conclusão além do pedido, sobrescrevendo a versão que o usuário queria manter — ele perdeu conteúdo e reclamou ("A versão anterior deve ser sempre mantida... Sempre só mexa em pontos específicos").

**How to apply:** Skill de projeto `.claude/skills/edicao-minima/SKILL.md` tem as regras completas e o bloco de backup padrão para scripts geradores (usar `shutil.copy2`, não `rename` — funciona com o arquivo aberto no Word; se o save falhar com PermissionError, pedir para fechar o Word, nunca matar o processo).
