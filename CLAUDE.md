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
  - `AZURE_OPENAI_API_KEY` / `AZURE_OPENAI_ENDPOINT` / `OPENAI_API_VERSION` — Azure OpenAI credentials used by every LLM notebook.
  - `AZURE_OPENAI_DEPLOYMENT` (optional) — Azure deployment name. Defaults to `gpt-4o` (`ccd.config.DEFAULT_AZURE_DEPLOYMENT`).
  - `CCD_INFORMACOES_DIR` (optional) — overrides the default PDF share path. Defaults to `\\10.24.0.6\tce$\Informacoes_PDF` (`ccd.config.DEFAULT_INFORMACOES_DIR`); resolve at runtime with `ccd.config.informacoes_dir()`.

## Running things

- **Notebooks** (the primary surface): launch from anywhere. New notebooks should use `from ccd.notebook import setup; ctx = setup()` to get an `engine` + `llm` ready to go (replaces the boilerplate `sys.path` + `load_dotenv` + `AzureChatOpenAI(...)` block). Or, for finer control, import from the submodules directly: `from ccd.db import get_connection`, `from ccd.config import informacoes_dir`. The legacy preamble (`sys.path.append("..")` + `from utils_ccd import ...`) still works because `scripts/utils_ccd.py` is a thin shim that re-exports the new package.
- **Antecedentes CLI**: `python -m scripts.automacao.antecedentes --nome "<nome LIKE pattern>" --json <context.json> --doc_name <out.docx>`. Note the parameter is `--nome`, not `--cpf` — the underlying SQL filters by responsável name.
- **CI**: GitHub Actions runs `ruff check` + `mypy ccd` on push/PR (see `.github/workflows/ci.yml`). No test suite at the moment.

## Architecture

### `ccd/` — the package (importable from anywhere after `pip install -e .`)

- `ccd.config` — `PACKAGE_DIR`, `REPO_ROOT`, `SQL_DIR`, `DEFAULT_INFORMACOES_DIR`, `DEFAULT_AZURE_DEPLOYMENT`, `load_env()`, `read_sql(name)`, `informacoes_dir()`. All paths are resolved from `Path(__file__)`, killing the CWD trap. Single source of truth for env-var-overridable infra paths/names.
- `ccd.notebook` — `setup(db='processo', llm=True) -> NotebookContext` with `engine` and (optionally) `llm`. Replaces the per-notebook prelude. Requires the `notebooks` extra (`pip install -e ".[notebooks]"`) for the LLM path.
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

## Conventions worth preserving

- New SQL must use named parameters (`:foo`) with `ccd.db.run_query_df(sql, **params)`. Don't extend the legacy `.format()` pattern in `scripts/consultas/`; if you touch one of those queries, migrate it to `ccd/sql/` and parameters at the same time.
- All user-facing strings (template variable names, LLM prompts, generated text) are in **Portuguese (pt-BR)**.
- `templates/~$*.docx` are Word lockfiles — never commit them. `scripts/<area>/saidas/` directories accumulate generated artifacts; check `git status` before staging.
- The PDF share path and Azure deployment name live in `ccd/config.py` as `DEFAULT_INFORMACOES_DIR` / `DEFAULT_AZURE_DEPLOYMENT`. Override per-host via `CCD_INFORMACOES_DIR` / `AZURE_OPENAI_DEPLOYMENT` env vars rather than editing the source.
- Commits: use **mensagens curtas** (uma linha, estilo dos commits recentes) e **sem `Co-Authored-By: Claude`** no rodapé.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ccd** (7495 symbols, 11873 relationships, 259 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ccd/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ccd/clusters` | All functional areas |
| `gitnexus://repo/ccd/processes` | All execution flows |
| `gitnexus://repo/ccd/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
