"""Configuração: carrega .env, expõe constantes e fábrica de engines SQLAlchemy."""

from __future__ import annotations

import os
import urllib.parse
from functools import lru_cache

from dotenv import load_dotenv as _dotenv_load
from sqlalchemy import Engine, create_engine

# Constantes do domínio
FRAP_CNPJ = "22562510000195"
TCE_CNPJ = "12978037000178"
CONTAS_FRAP = ("700000-6", "600000-2")
ANOS_SIGEF = (2023, 2024, 2025)
BANCO_PROCESSO = "processo"
BANCO_DIP = "BdDIP"  # destino da persistência (tabelas FRAP*)
BANCO_SIAIPESSOAL = "BdSIAIPessoal"  # folha de pagamento (contracheques 2021+)
BANCO_BDC = "Bdc"  # tabelas Gen_Orgao (lookup de IdOrgaoSuperior)

# Hierarquia de órgãos: 272 = Governo do Estado RN. Quando IdOrgaoSuperior do
# órgão notificado é 272, o pagamento pode vir centralizado pelo Estado.
ID_ORGAO_SUPERIOR_ESTADO = 272


def banco_sigef(ano: int) -> str:
    return f"BdCargaSigef{ano}"


def cnpjs_estado_rn() -> tuple[str, ...]:
    """Lê do `.env` a lista CSV de CNPJs do Estado-RN (depositante centralizado).

    Vazia por padrão — neste caso a regra "Estado→órgão" do matcher fica desligada.
    Cada item normalizado para 14 dígitos.
    """
    load_dotenv()
    raw = os.environ.get("CNPJS_ESTADO_RN", "")
    out: list[str] = []
    for item in raw.split(","):
        digits = "".join(c for c in item if c.isdigit())
        if len(digits) == 14:
            out.append(digits)
    return tuple(out)


@lru_cache(maxsize=1)
def load_dotenv() -> None:
    """Carrega `.env` da raiz do repo. Idempotente (cache=1)."""
    _dotenv_load(override=False)


def _odbc_connect_string(database: str) -> str:
    """Monta a string ODBC para SQL Server.

    Usa Driver 18 quando disponível (mais novo), com fallback para Driver 17
    via env var `SQL_SERVER_DRIVER` se a máquina não tiver o 18.
    `TrustServerCertificate=yes` cobre certificados auto-assinados internos
    do TCE; `Encrypt=no` aceita conexões legadas.
    """
    user = os.environ["SQL_SERVER_USER"]
    pwd = os.environ["SQL_SERVER_PASS"]
    host = os.environ["SQL_SERVER_HOST"]
    port = os.environ["SQL_SERVER_PORT"]
    driver = os.environ.get("SQL_SERVER_DRIVER", "ODBC Driver 18 for SQL Server")

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={host},{port};"
        f"DATABASE={database};"
        f"UID={user};PWD={pwd};"
        f"TrustServerCertificate=yes;Encrypt=no;"
    )


def build_engine(database: str) -> Engine:
    """Constrói uma SQLAlchemy Engine apontando para o banco solicitado.

    `database` é tipicamente `processo` ou o resultado de `banco_sigef(ano)`.
    Requer `SQL_SERVER_USER/PASS/HOST/PORT` no ambiente (carrega via `load_dotenv`).
    """
    load_dotenv()
    odbc = _odbc_connect_string(database)
    url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc)
    return create_engine(url, future=True)


_oracle_thick_initialized = False


def _ensure_oracle_thick_mode() -> None:
    """Habilita thick mode no `oracledb` quando `ORACLE_INSTANTCLIENT_DIR` aponta
    para um Instant Client. O SIGEF roda Oracle 11g, que o `oracledb` em thin
    mode não suporta (DPY-3010). Idempotente.
    """
    global _oracle_thick_initialized
    if _oracle_thick_initialized:
        return
    lib_dir = os.environ.get("ORACLE_INSTANTCLIENT_DIR")
    if lib_dir:
        import oracledb
        oracledb.init_oracle_client(lib_dir=lib_dir)
    _oracle_thick_initialized = True


def build_oracle_engine(service_name: str | None = None) -> Engine:
    """SQLAlchemy Engine apontando para o Oracle do SIGEF (carga 2026+).

    Requer `ORACLE_USER/PASS/HOST/PORT/SID` no ambiente. Como o SIGEF roda 11g,
    define também `ORACLE_INSTANTCLIENT_DIR` para o caminho do Instant Client.
    """
    load_dotenv()
    _ensure_oracle_thick_mode()
    user = urllib.parse.quote_plus(os.environ["ORACLE_USER"])
    pwd = urllib.parse.quote_plus(os.environ["ORACLE_PASS"])
    host = os.environ["ORACLE_HOST"]
    port = os.environ["ORACLE_PORT"]
    svc = service_name or os.environ["ORACLE_SID"]
    url = f"oracle+oracledb://{user}:{pwd}@{host}:{port}/?service_name={svc}"
    return create_engine(url, future=True)
