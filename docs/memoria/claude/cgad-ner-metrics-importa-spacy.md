---
name: cgad-ner-metrics-importa-spacy
description: cgad.ner_metrics importa spacy no topo — não pode ser importado pelo backend web/
metadata: 
  node_type: memory
  type: project
  originSessionId: 1cd4e235-185c-4347-b894-a3b65dc1b907
  modified: 2026-08-11T17:45:01.057Z
---

`web/tools/cgad/cgad/ner_metrics.py` faz `import spacy` em escopo de módulo. Qualquer
`from cgad.ner_metrics import ...` dentro de `web/backend/app/` quebra o import da app
(`ModuleNotFoundError: No module named 'spacy'`) — spacy só está no ambiente dos
notebooks/experimentos, não no venv do backend.

**Why:** o pacote `cgad` é compartilhado entre o pipeline de ETL/experimentos e a API,
mas as dependências não são as mesmas. Reusar dali arrasta um NLP pesado para dentro do
container da API.

**How to apply:** para constantes pequenas (`ENTITY_LABELS`) e funções curtas
(`compute_iou_score`), reimplemente no lado do backend com um comentário apontando a
origem — foi o que `app/cgad/dataset/` faz. Só importe de `cgad.*` módulos que não
puxam spacy/langchain (ex.: `cgad.models`, `cgad.etl.staging`).

Relacionado: [[web-uv-workspace-all-packages]]
