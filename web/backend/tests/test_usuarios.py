from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPRefreshToken, FRAPUsuario
from app.auth.router import router as auth_router
from app.auth.security import hash_password
from app.deps import get_current_user, get_db_session
from app.usuarios.router import router as usuarios_router


def _build_app(factory: sessionmaker[Session], current_user_factory) -> FastAPI:
    def override_db() -> Iterator[Session]:
        s = factory()
        try:
            yield s
        finally:
            s.close()

    app = FastAPI()
    app.include_router(usuarios_router)
    app.include_router(auth_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = current_user_factory
    return app


@pytest.fixture
def factory(in_memory_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)


def _seed_admin(factory: sessionmaker[Session]) -> FRAPUsuario:
    with factory() as s:
        admin = FRAPUsuario(
            Login="admin",
            Email="admin@tce.rn",
            NomeCompleto="Admin",
            SenhaHash=hash_password("senha-admin"),
            Papel="admin",
            Ativo=True,
        )
        s.add(admin)
        s.commit()
        s.refresh(admin)
        s.expunge(admin)
        return admin


def _seed_user(factory: sessionmaker[Session]) -> FRAPUsuario:
    with factory() as s:
        u = FRAPUsuario(
            Login="user1",
            Email="user@tce.rn",
            NomeCompleto="User",
            SenhaHash=hash_password("senha-user"),
            Papel="user",
            Ativo=True,
        )
        s.add(u)
        s.commit()
        s.refresh(u)
        s.expunge(u)
        return u


def test_user_nao_pode_listar(factory: sessionmaker[Session]) -> None:
    user = _seed_user(factory)
    app = _build_app(factory, lambda: user)
    with TestClient(app) as c:
        r = c.get("/api/v1/usuarios")
        assert r.status_code == 403


def test_admin_cria_usuario_e_recebe_senha_temporaria(
    factory: sessionmaker[Session],
) -> None:
    admin = _seed_admin(factory)
    app = _build_app(factory, lambda: admin)
    with TestClient(app) as c:
        r = c.post(
            "/api/v1/usuarios",
            json={
                "login": "novo",
                "email": "novo@tce.rn",
                "nomeCompleto": "Novo",
                "papel": "user",
            },
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["usuario"]["login"] == "novo"
        assert body["usuario"]["email"] == "novo@tce.rn"
        assert len(body["senhaTemporaria"]) >= 8


def test_admin_cria_login_duplicado_retorna_409(factory: sessionmaker[Session]) -> None:
    admin = _seed_admin(factory)
    app = _build_app(factory, lambda: admin)
    with TestClient(app) as c:
        c.post(
            "/api/v1/usuarios",
            json={"login": "xyz", "email": "x@tce.rn", "nomeCompleto": "X", "papel": "user"},
        )
        r = c.post(
            "/api/v1/usuarios",
            json={"login": "xyz", "email": "y@tce.rn", "nomeCompleto": "X", "papel": "user"},
        )
        assert r.status_code == 409


def test_admin_lista_e_filtra(factory: sessionmaker[Session]) -> None:
    admin = _seed_admin(factory)
    _seed_user(factory)
    app = _build_app(factory, lambda: admin)
    with TestClient(app) as c:
        all_users = c.get("/api/v1/usuarios").json()
        assert all_users["total"] == 2
        only_admin = c.get("/api/v1/usuarios?papel=admin").json()
        assert only_admin["total"] == 1
        assert only_admin["items"][0]["login"] == "admin"


def test_admin_atualiza_e_inativa_revoga_refresh(
    factory: sessionmaker[Session],
) -> None:
    admin = _seed_admin(factory)
    user = _seed_user(factory)
    # gera refresh token para o user
    with factory() as s:
        from datetime import UTC, datetime, timedelta

        s.add(
            FRAPRefreshToken(
                IdUsuario=user.IdUsuario,
                TokenHash="a" * 64,
                DataExpiracao=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7),
            )
        )
        s.commit()
    app = _build_app(factory, lambda: admin)
    with TestClient(app) as c:
        r = c.patch(
            f"/api/v1/usuarios/{user.IdUsuario}",
            json={"ativo": False, "papel": "admin"},
        )
        assert r.status_code == 200
        assert r.json()["ativo"] is False
        assert r.json()["papel"] == "admin"
    # confere revogação
    with factory() as s:
        token = s.query(FRAPRefreshToken).one()
        assert token.DataRevogacao is not None


def test_admin_reset_senha_devolve_string(factory: sessionmaker[Session]) -> None:
    admin = _seed_admin(factory)
    user = _seed_user(factory)
    app = _build_app(factory, lambda: admin)
    with TestClient(app) as c:
        r = c.post(f"/api/v1/usuarios/{user.IdUsuario}/reset-senha")
        assert r.status_code == 200
        assert len(r.json()["senhaTemporaria"]) >= 8


def test_user_troca_propria_senha(factory: sessionmaker[Session]) -> None:
    user = _seed_user(factory)
    app = _build_app(factory, lambda: user)
    with TestClient(app) as c:
        r = c.post(
            "/api/v1/auth/trocar-senha",
            json={"senhaAtual": "senha-user", "senhaNova": "outra-senha-12"},
        )
        assert r.status_code == 204


def test_user_trocar_senha_atual_errada_retorna_401(
    factory: sessionmaker[Session],
) -> None:
    user = _seed_user(factory)
    app = _build_app(factory, lambda: user)
    with TestClient(app) as c:
        r = c.post(
            "/api/v1/auth/trocar-senha",
            json={"senhaAtual": "errada", "senhaNova": "outra-senha-12"},
        )
        assert r.status_code == 401
