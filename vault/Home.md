---
date: 2026-05-27
description: Porta de entrada do cofre — wiki CCD mantida por LLM no padrão llm-wiki, com legislação e informações da Coordenadoria de Controle de Decisões.
tags:
  - moc
---

# 🏛️ Wiki CCD

Segundo cérebro da **Coordenadoria de Controle de Decisões (CCD)** do TCE-RN. Fontes brutas em `raw/`; páginas mantidas pelo LLM em `wiki/`. Convenções em [`CLAUDE.md`](CLAUDE.md).

## Navegação

- [[index|📑 Índice (catálogo da wiki)]]
- [[log|🕒 Log (cronológico)]]

## Camadas

- **`raw/`** — fontes imutáveis: `raw/leis/` (legislação), `raw/informacoes/` (despachos/processos do setor).
- **`wiki/`** — `leis/`, `conceitos/`, e (futuro) `processos/`, `relatores/`, `informacoes/`.

## Como usar

- **Ingerir** uma fonte: aponte um arquivo de `raw/` e peça o ingest.
- **Perguntar**: faça uma pergunta; a resposta pode virar página.
- **Revisar (lint)**: peça uma checagem de saúde (órfãos, contradições, cruzamentos faltando).
