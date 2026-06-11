# Imagem do backend FastAPI + worker ARQ (mesma imagem; comando difere no compose).
# Contexto de build = raiz do repo (workspace uv: backend + tools).
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    VIRTUAL_ENV=/app/.venv \
    PATH=/app/.venv/bin:$PATH

# Driver ODBC 18 da Microsoft (SQL Server) + toolchain mínima
# + LibreOffice headless (conversão docx->pdf do módulo CCD em Linux, via soffice)
# + locale pt_BR.UTF-8 (locale.currency/num2words no Desconto em Folha).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg ca-certificates unixodbc gcc g++ \
        locales libreoffice-writer libreoffice-core --no-install-recommends \
    && sed -i 's/^# *\(pt_BR.UTF-8\)/\1/' /etc/locale.gen \
    && locale-gen pt_BR.UTF-8 \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=pt_BR.UTF-8 \
    LC_ALL=pt_BR.UTF-8

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
