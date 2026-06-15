from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.auth.router import router as auth_router
from app.auth.security import hash_password
from app.deps import get_db_session


@pytest.fixture
def client(in_memory_engine: Engine) -> Iterator[TestClient]:
    factory = sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)

    def override_get_db_session() -> Iterator[Session]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_db_session] = override_get_db_session

    with factory() as seed:
        seed.add(
            FRAPUsuario(
                Login="admin",
                Email="admin@tce.rn",
                SenhaHash=hash_password("senha-123"),
                Papel="admin",
                Ativo=True,
            )
        )
        seed.commit()

    with TestClient(app) as c:
        yield c


def test_login_then_me_round_trip(client: TestClient) -> None:
    login = client.post("/api/v1/auth/login", json={"login": "admin", "senha": "senha-123"})
    assert login.status_code == 200
    access = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200, me.json()
    body = me.json()
    assert body == {
        "idUsuario": body["idUsuario"],
        "login": "admin",
        "email": "admin@tce.rn",
        "nomeCompleto": "admin",
        "papel": "admin",
        "ativo": True,
        "deveTrocarSenha": False,
        "dataCriacao": body["dataCriacao"],
    }


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"login": "admin", "senha": "errada"})
    assert response.status_code == 401


def test_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
