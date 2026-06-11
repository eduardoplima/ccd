# Imagem do backend FastAPI + worker ARQ (mesma imagem; comando difere no compose).
# Contexto de build = raiz do repo (workspace uv: backend + tools).
# Dependências apt pesadas (LibreOffice, ODBC) ficam em Dockerfile.base (ccd-backend-base:latest).
FROM ccd-backend-base:latest

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH

# uv (gerenciador de dependências/venv).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Workspace uv: precisa do pyproject/lock da raiz + dos membros (backend, tools).
COPY pyproject.toml uv.lock ./
COPY tools/ ./tools/
COPY backend/ ./backend/

# Instala backend + tools no /app/.venv (sem dev deps).
# --package: sync da raiz do workspace não instala deps de membros; precisa apontar o backend.
# --no-cache: não embute o cache do uv na camada (host tem /var pequeno — 4 GB).
RUN uv sync --frozen --no-dev --no-cache --package ccd-web-backend

# Dirs usadas pelo pipeline (montadas como volumes em runtime).
RUN mkdir -p /app/docs/extratos_frap /app/data/interim /app/data/processed /app/backend/.artifacts

EXPOSE 8000

# Comando default (sobrescrito pelo compose para backend vs worker).
# sh -c (não -lc): shell de login sourceia /etc/profile e descarta /app/.venv/bin do PATH.
CMD ["sh", "-c", "cd /app/backend && alembic upgrade head && cd /app && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
