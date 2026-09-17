---
name: llm-citacao-precisa-ser-conferida
description: DeepSeek inventa citação literal com confiança ALTA mesmo proibido no prompt; conferir o trecho contra o material em código
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 10c7a3d5-9049-4abe-b4ba-4ff6e921b851
  modified: 2026-09-04T14:44:09.324Z
---

Quando uma rotina pede ao modelo uma **citação literal** do documento (padrão usado em `crivo_monitoramento.py`, `monitoramento_obrigacoes.py`, antecedentes), o prompt sozinho não segura: o DeepSeek devolve o trecho inventado com `confianca=ALTA`.

Caso real: processo 000926/2022, primeira rodada da varredura de monitoramento — duas avaliações `CUMPRIDA`/`ALTA` citando um trecho que não existia em nenhuma das 8 peças lidas, apesar de o prompt mandar deixar o trecho vazio nesse caso.

**Why:** citação inventada com confiança alta é pior que resposta vazia — leva a CCD a arquivar caso vivo, e o auditor não tem como distinguir sem reabrir os PDFs.

**How to apply:** conferir em código, não em prompt. Normalizar (minúsculas, sem acento via `unicodedata`, espaços colapsados) e procurar um prefixo do trecho (~60 chars) no material que foi realmente enviado. Não achou ⇒ rebaixar o veredito para o valor neutro (`SEM_ELEMENTOS`), marcar `trecho_conferido=False` e registrar o descarte na saída. Ver `conferir_trechos` em `scripts/analise/monitoramento_obrigacoes.py`. Vale como check obrigatório de qualquer nova rotina que peça citação ao modelo.

Relacionados: [[monitoramento-obrigacoes-curadas]].
