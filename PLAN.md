# Plano de refactor — repositório CCD

Lista priorizada (maior retorno por esforço primeiro). Itens 1–4 estão sendo
implementados nesta passada; 5–8 ficam para iterações futuras.

## 1. Pacote instalável `ccd/`
Transformar `scripts/` em um pacote instalável (`pyproject.toml` +
`pip install -e .`) e renomear para `ccd/`. Elimina o `sys.path.append("..")`
dos notebooks e o "CWD trap" — `from ccd.db import get_connection` passa a
funcionar de qualquer diretório.

## 2. Caminhos a partir de `__file__`
Resolver caminhos a partir de `__file__`, não do CWD.
`load_dotenv(Path(__file__).resolve().parents[1] / ".env")`, e o mesmo para
`consultas/*.sql` e `templates/*.docx`. Mata silently-failing connections e
`FileNotFoundError` espúrios.

## 3. Conexão MSSQL unificada
Unificar as duas conexões e os dois esquemas de env vars. Hoje
`utils_ccd.get_connection` (SQLAlchemy Engine, `SQL_SERVER_*`) e
`automacao/antecedentes.get_connection` + `decisoes-etl/etl.py` (pymssql cru,
`SQLSERVER_*`) divergem. Um único helper que retorna Engine, com
`pd.read_sql(text(sql), engine, params=...)` em vez de `.format()` (corrige o
risco de SQL injection com CPF/nome/processo).

## 4. Modularizar `utils_ccd.py`
Quebrar `utils_ccd.py` em módulos coesos: `ccd/db.py`, `ccd/pdf.py`
(extract/merge/discover), `ccd/docs.py` (template render + LibreOffice/Word
com seleção automática por plataforma), `ccd/processo.py` (queries de
processo). Hoje as três responsabilidades convivem em 130 linhas e há
duplicação (`get_pdf_files_processo` × `get_informacoes_processo` repetem o
mesmo SQL).

## 5. Externalizar caminhos de rede
Mover `\\10.24.0.6\tce$\Informacoes_PDF`, `/mnt/informacoes_pdf`, host do
SQL e deployment do Azure para `.env` ou `settings.toml`. Hoje estão
espalhados como literais entre `utils_ccd.py`, `etl.py` e `tests.py`.

## 6. Padronizar a estrutura dos notebooks
Extrair o "prelude" repetido (`sys.path`, `load_dotenv`,
`AzureChatOpenAI(model_name="gpt-4o")`, `get_connection`) para
`ccd.notebook.setup()`. Os 20+ notebooks reproduzem as mesmas 5–10 linhas
iniciais.

## 7. Destino de `decisoes-etl/`
Resolvido — diretório removido do repo (lógica migrada para um repositório
separado).

## 8. Higiene de repo
Adicionar `~$*.docx`, `*/saidas/`, `*.xlsx` de saída ao `.gitignore`; rodar
`ruff` + `mypy` em CI; reabilitar (ou apagar) os testes de
`decisoes-etl/tests.py` que estão todos `@pytest.mark.skip`.

---

**Tradeoff principal**: itens 1–4 são um refactor único, com risco de quebrar
todos os notebooks de uma vez (caminhos relativos, imports). Itens 5–8 são
mudanças localizadas e podem ser feitas em qualquer ordem depois.
