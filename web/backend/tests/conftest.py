from __future__ import annotations

from collections.abc import Iterator

import pytest
from freezegun import freeze_time
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base


@pytest.fixture(autouse=True)
def tmp_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SQL_SERVER_HOST", "localhost")
    monkeypatch.setenv("SQL_SERVER_PORT", "1433")
    monkeypatch.setenv("SQL_SERVER_USER", "test")
    monkeypatch.setenv("SQL_SERVER_PASS", "test")
    monkeypatch.setenv("SQL_SERVER_DATABASE", "BdDIP")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-do-not-use-in-production")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    monkeypatch.delenv("REDIS_URL", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()


@pytest.fixture
def in_memory_engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(in_memory_engine: Engine) -> Iterator[Session]:
    factory = sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def frozen_time():
    with freeze_time("2026-05-06T12:00:00Z") as frozen:
        yield frozen
