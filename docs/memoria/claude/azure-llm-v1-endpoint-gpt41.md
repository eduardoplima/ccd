---
name: azure-llm-v1-endpoint-gpt41
description: "LLM do repo: só via ccd.llm/frap.llm (DeepSeek no Foundry do SERPRO); endpoint /openai/v1 exige ChatOpenAI(base_url=), não AzureChatOpenAI"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e3b56875-ef2e-43b9-99a5-7178d4653e9c
  modified: 2026-08-21T14:15:39.197Z
---

`AZURE_OPENAI_ENDPOINT=https://projeto-dip-resource.services.ai.azure.com/openai/v1`
(mesmo valor em `scripts/.env` e `web/.env`) é o surface **OpenAI-compatível** do
Azure AI Foundry do SERPRO, não o Azure OpenAI clássico.

Desde 2026-08-21 há **um factory por árvore** e nada mais constrói cliente LLM
(exigência de LGPD — ver [[repo-moved-stale-editable-install]] para o setup):

- `ccd.llm.get_llm(model=None)` / `ccd.llm.structured(schema, llm=None)` — árvore raiz.
- `frap.llm.get_llm_client()` / `frap.llm.structured(...)` — árvore `web/` (backend,
  worker CGAD, cgad.dataset_pretag, handoff). Sem config → `None`; endpoint fora de
  `*.services.ai.azure.com` → `RuntimeError`.
- Default: `DeepSeek-V4-Flash` (override `AZURE_OPENAI_DEPLOYMENT`). `structured()`
  fixa `method="function_calling"` — `json_schema` não é garantido no DeepSeek.

Armadilhas que motivaram a centralização (ainda valem):

- `AzureChatOpenAI` contra esse endpoint dá 404 **ou** responde do deployment default
  ignorando o pedido — era o caso do worker CGAD, que "rodava deepseek" e rodava gpt-4o.
- Deployments verificados: `DeepSeek-V4-Flash` (em uso), `gpt-4.1`, `gpt-4.1-mini`.
  Listar reais: GET `${AZURE_OPENAI_ENDPOINT}/models` com `Authorization: Bearer <key>`.
