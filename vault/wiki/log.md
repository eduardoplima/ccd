---
date: 2026-05-27
description: Log cronológico append-only da wiki CCD — ingests, queries e lints, com prefixo consistente para parsing simples.
tags:
  - log
---

# 🕒 Log da Wiki CCD

Registro append-only. Cada entrada começa com `## [AAAA-MM-DD] <tipo> | <fonte>`. Veja o [[index|índice]] para o catálogo de páginas.

## [2026-05-27] setup | criação do cofre

Estrutura inicial: schema ([[CLAUDE]]), [[Home]], [[index]], [[log]] e esqueleto de `wiki/` (`leis/`, `conceitos/`). Padrão [[llm-wiki]]. Fontes em `raw/leis/` e `raw/informacoes/`.

## [2026-05-27] ingest | raw/leis (7 normas)

Ingeridas as 7 normas de `raw/leis/` → 7 páginas em `wiki/leis/` e 18 páginas de conceito em `wiki/conceitos/`.

- Leis: [[LCE 464-2012 — Lei Orgânica do TCE-RN]], [[Regimento Interno do TCE-RN (Res 009-2012)]], [[Regulamento da SECEX (Res 042-2024)]], [[Resolução 028-2012 — Processo de execução]], [[Resolução 013-2015 — Execução de multas e ressarcimento]], [[Lei 9.492-1997 — Lei do Protesto]], [[Resolução 012-2020 — Provimento da Corregedoria]].
- Conceitos centrais: [[Coordenadoria de Controle de Decisões (CCD)]], [[Execução das decisões do TCE-RN]], [[CGAD — Cadastro Geral de Acompanhamento de Decisões]], [[Trânsito em julgado]], [[Multa]], [[Ressarcimento ao erário (débito)]].
- Achados de domínio: **CCD** é definida no art. 32 do Regulamento da SECEX (Res 42/2024), dentro da **DIP**, ao lado da **CIP** (= Coordenadoria de Instrução Processual, *não* o cadastro de créditos). O **TAG** dos despachos corresponde ao subcadastro CGTAG do CGAD.
- Extração: PDFs lidos via `pypdf` (venv) — a ferramenta Read recusa esses PDFs (protegidos por permissão).

## [2026-05-27] setup | busca qmd instalada e indexada

`@tobilu/qmd` 2.5.2 instalado (após adicionar o workload C++ "VCTools" ao VS Build Tools, necessário para compilar o `better-sqlite3`). Criado o índice `ccd-wiki` com a coleção `ccd-wiki` escopada a `vault/wiki/` (`**/*.md`): **29 documentos** indexados (BM25) + embeddings. Consulta: `qmd --index ccd-wiki query "<termo>"`. Reindexar após edições com `qmd --index ccd-wiki update` / `embed`.
