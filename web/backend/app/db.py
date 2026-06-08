from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, future=True, pool_pre_ping=True)


@lru_cache(maxsize=1)
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def session_scope() -> Iterator[Session]:
    factory = _session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


@lru_cache(maxsize=1)
def get_processo_engine() -> Engine:
    """Engine (somente leitura) para o banco `processo` — usado pelo módulo CCD."""
    settings = get_settings()
    url = settings.odbc_url(settings.sql_server_db_processos)
    return create_engine(url, future=True, pool_pre_ping=True)


@lru_cache(maxsize=1)
def _processo_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_processo_engine(), autoflush=False, expire_on_commit=False)


def processo_session_scope() -> Iterator[Session]:
    factory = _processo_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
