# CLAUDE.md — backend

Convenções específicas do serviço FastAPI.

## Regras

- **Sem trabalho longo em handlers HTTP.** LLM, scraping, qualquer coisa > poucos segundos vai pela ARQ. Endpoints enfileiram e retornam `202` com job id e URL de status.
- **DI para sessões DB** via `app.deps.get_db_session`. Não instancie `Engine`/`Session` em escopo de módulo.
- **Settings via `pydantic-settings`**, carregadas uma vez no startup com `@lru_cache get_settings()`. Não leia `os.environ` ad hoc. `env_file="../.env"` para o `.env` ser compartilhado pelo workspace.
- **Auth**: OAuth2 password flow, JWT access (curto, default 60 min) + refresh (default 7 dias). Refresh tokens são persistidos como **hash SHA-256** (não bcrypt — JWT já tem entropia alta; bcrypt é para senhas de baixa entropia). Bcrypt para senhas de usuário, com **rejeição explícita acima de 72 bytes** (não truncar silenciosamente). Rotação a cada `/refresh`. Use `python-jose`.
- **Papéis**: pelo menos `user` e `admin`. Enforce com `Depends(require_role("admin"))`.
- **Transporte de token**: `Authorization: Bearer …` por enquanto. Migração para HTTP-only cookie é dívida documentada.
- **Erros seguem RFC 7807** (`detail` em inglês, voltado a desenvolvedor). Frontend localiza por código.
- **Alembic**: migrações manuais ao tocar tabelas legadas. Nunca `alembic revision --autogenerate` cego contra produção — revise o script à mão. A primeira migração é baseline e é `stamp head`-ed contra qualquer schema pré-existente.
- **ARQ pool**: aberto no `lifespan` do FastAPI somente quando `REDIS_URL` está set; senão `get_arq_pool` retorna 503. `worker.py` lê o mesmo `.env`.
- Format com `ruff format` (linha 100) + `ruff check`. Os dois passam antes do commit.
- Testes: `pytest` + `pytest-asyncio` + `httpx.AsyncClient`, SQLite em memória para unit tests, `@pytest.mark.integration` para qualquer coisa que toque serviços reais (skipped por default). Cobertura obrigatória de expiração de token, assinatura inválida, papel divergente, rotação de refresh.

## Banco

Banco único: **BdDIP** (SQL Server), tabelas com prefixo `FRAP*`. Auth grava em `FRAPUsuario` e `FRAPRefreshToken`. As demais tabelas (`FRAPLancamento`, `FRAPMatch*`, etc.) já existem e foram criadas pelo pipeline da `tools/frap`.

Conexão monta a string ODBC a partir de `SQL_SERVER_*` (mesmas vars que a `tools/frap`). Para dev, é necessário estar na rede interna do TCE.
