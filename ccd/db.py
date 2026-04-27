"""Single source of truth for MSSQL connections.

Replaces three divergent helpers (utils_ccd.get_connection, antecedentes.py
get_connection, decisoes-etl/etl.py ETL.get_connection). All consumers should
use `get_connection()` here, which returns a SQLAlchemy Engine.

Env vars: SQL_SERVER_HOST, SQL_SERVER_USER, SQL_SERVER_PASS, SQL_SERVER_PORT.
The legacy `SQLSERVER_*` names from decisoes-etl are also accepted as fallback.
"""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ccd.config import load_env


def _env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def get_connection(db: str = "processo") -> Engine:
    """Return a SQLAlchemy Engine for the given MSSQL database."""
    load_env()

    server = _env("SQL_SERVER_HOST", "SQLSERVER_HOST")
    user = _env("SQL_SERVER_USER", "SQLSERVER_USER")
    password = _env("SQL_SERVER_PASS", "SQLSERVER_PASS")
    port = _env("SQL_SERVER_PORT", "SQLSERVER_PORT", default="1433")

    missing = [
        name for name, value in (
            ("SQL_SERVER_HOST", server),
            ("SQL_SERVER_USER", user),
            ("SQL_SERVER_PASS", password),
        ) if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing env vars: {', '.join(missing)}. "
            f"Check the .env at the repo root or scripts/.env."
        )

    # Server may contain a backslash for named instances (e.g. HOST\Instance);
    # quote_plus keeps the URL parser happy.
    user_q = quote_plus(user)
    password_q = quote_plus(password)
    server_q = quote_plus(server)

    url = f"mssql+pymssql://{user_q}:{password_q}@{server_q}:{port}/{db}"
    return create_engine(url)


def run_query(sql: str, conn: Engine | Any | None = None, **params) -> Any:
    """Execute a SQL statement with named params, return a SQLAlchemy Result.

    Use named placeholders (`:name`) in `sql` and pass values as kwargs.
    """
    if conn is None:
        conn = get_connection()
    if isinstance(conn, Engine):
        with conn.connect() as c:
            return c.execute(text(sql), params)
    return conn.execute(text(sql), params)


def run_query_df(sql: str, conn: Engine | Any | None = None, **params) -> pd.DataFrame:
    """Execute a SQL statement with named params, return the result as a DataFrame."""
    if conn is None:
        conn = get_connection()
    return pd.read_sql(text(sql), conn, params=params)
