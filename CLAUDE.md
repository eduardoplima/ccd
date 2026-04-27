# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Domain

Internal tooling for the **Coordenadoria de Controle de Decisões (CCD)** at a Tribunal de Contas (TCE). Most code reads from the `processo` MSSQL database (the court-case system) and produces analyses, despachos, and `.docx` documents for CCD workflows. Identifiers like `numero_processo/ano_processo`, `setor`, `Ata_Informacao`, `Pro_ProcessoEvento`, `Exe_Debito`, `GenPessoa`, `Processo_TransitoJulgado`, `CIP`, `DAP`, `PGE`, `nereu` are domain terms — preserve them verbatim.

## Environment & setup

- Python 3.12, single venv at `.venv/`. Install with:
  - `pip install -r requirements.txt` (pinned deps), then
  - `pip install -e .` (makes the `ccd` package importable from anywhere).
- Runtime config lives in `scripts/.env` (gitignored). `ccd.config.load_env()` finds it from `Path(__file__)`, not the CWD — it works regardless of where Python is launched. Both `<repo>/.env` and `<repo>/scripts/.env` are accepted; the first hit wins. Provided keys:
  - `SQL_SERVER_HOST` / `SQL_SERVER_USER` / `SQL_SERVER_PASS` / `SQL_SERVER_PORT` — MSSQL credentials (legacy `SQLSERVER_*` names are accepted as fallback).
  - `AZURE_OPENAI_API_KEY` / `AZURE_OPENAI_ENDPOINT` / `OPENAI_API_VERSION` — Azure OpenAI `gpt-4o` deployment used by every LLM notebook.
  - `CCD_INFORMACOES_DIR` (optional) — overrides the default PDF share path. Defaults to `\\10.24.0.6\tce$\Informacoes_PDF` for `ccd.processo`, and `/mnt/informacoes_pdf` for `decisoes-etl/etl.py`.

## Running things

- **Notebooks** (the primary surface): launch from anywhere. New notebooks should `from ccd.db import get_connection` etc. The legacy preamble (`sys.path.append("..")` + `from utils_ccd import ...`) still works because `scripts/utils_ccd.py` is a thin shim that re-exports the new package.
- **Antecedentes CLI**: `python -m scripts.automacao.antecedentes --nome "<nome LIKE pattern>" --json <context.json> --doc_name <out.docx>`. Note the parameter is `--nome`, not `--cpf` — the underlying SQL filters by responsável name.
- **Decisões ETL**: `python decisoes-etl/etl.py` — pulls `Ata_Informacao` rows for the configured year, extracts PDF text via `pypdf`, writes `output.json`.
- **Tests**: `pytest decisoes-etl/tests.py`. All marked `@pytest.mark.skip` (integration: need DB + PDF share); unskip selectively when running on a machine with both.

## Architecture

### `ccd/` — the package (importable from anywhere after `pip install -e .`)

- `ccd.config` — `PACKAGE_DIR`, `REPO_ROOT`, `SQL_DIR`, `load_env()`, `read_sql(name)`. All paths are resolved from `Path(__file__)`, killing the CWD trap.
- `ccd.db` — `get_connection(db='processo') -> Engine`, plus `run_query(sql, **params)` and `run_query_df(sql, **params)`. Always use **named parameters** (`:foo`) and pass values as kwargs — never `.format()` SQL with user input.
- `ccd.pdf` — `extract_text_from_pdf(path)`, `merge_pdfs(paths, out)`.
- `ccd.processo` — `get_info_file_path`, `get_pdf_files_processo`, `get_informacoes_processo`, `download_processo`. The processo SQL (a single parameterized query) lives inline in this module; the share path is overridable via `CCD_INFORMACOES_DIR`.
- `ccd.docs` — `render_template(template, ctx, out)`, `docx_to_pdf(doc, dir)` (auto-picks Word on Windows, LibreOffice elsewhere). Force a backend with `docx_to_pdf_word` / `docx_to_pdf_libreoffice`.
- `ccd/sql/` — bundled SQL files used by the package's API surface (`processo.sql`, `processos_transito_nome.sql`). Read with `ccd.config.read_sql("name.sql")`. **Note**: queries here use SQLAlchemy named placeholders (`:foo`); the older `.format()`-style files in `scripts/consultas/` are still used by notebooks and remain untouched.

### `scripts/` — notebooks and entrypoints

- `scripts/utils_ccd.py` — compatibility shim. Re-exports `get_connection`, `extract_text_from_pdf`, `merge_pdfs`, `get_info_file_path`, `get_pdf_files_processo`, `get_informacoes_processo`, `download_processo`, `generate_pdf` (= `docx_to_pdf_libreoffice`), `generate_pdf_office` (= `docx_to_pdf_word`), `DIR_INFORMACOES`. The 22 notebooks that do `from utils_ccd import ...` keep working unchanged.
- `scripts/automacao/antecedentes.py` — generates the antecedentes despacho. Uses `ccd.config.read_sql` + `ccd.db.run_query_df` with named params.
- `scripts/analise/` — exploratory notebooks (stats, LLM corpus analyses, ad-hoc downloads).
- `scripts/automacao/` — `.docx` deliverables built from `templates/*.docx` via `docxtpl.DocxTemplate`. Templates and per-notebook `saidas/` stay alongside their notebooks.
- `scripts/consultas/` — legacy `.sql` files loaded by notebooks via `open("../consultas/x.sql").read().format(...)`. Not migrated — modify here when changing notebook queries.
- `scripts/db/`, `scripts/docs/` — input spreadsheets/pickles.
- `scripts/erros/`, `scripts/json_antecedentes/` — auxiliary.

### `decisoes-etl/`

Standalone year-based extraction over `Ata_Informacao` joined with `Processos`. Now uses `ccd.db.get_connection` and parameterized SQL; the docling text path is lazy-imported (heavy dep). Output goes to `output.json` in the CWD.

## Conventions worth preserving

- New SQL must use named parameters (`:foo`) with `ccd.db.run_query_df(sql, **params)`. Don't extend the legacy `.format()` pattern in `scripts/consultas/`; if you touch one of those queries, migrate it to `ccd/sql/` and parameters at the same time.
- All user-facing strings (template variable names, LLM prompts, generated text) are in **Portuguese (pt-BR)**.
- `templates/~$*.docx` are Word lockfiles — never commit them. `scripts/<area>/saidas/` directories accumulate generated artifacts; check `git status` before staging.
- The PDF share path is the only "infra" address still hardcoded as a default (`\\10.24.0.6\tce$\Informacoes_PDF`). Override per-host via `CCD_INFORMACOES_DIR` rather than editing the source.
