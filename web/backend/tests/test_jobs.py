from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.auth.security import hash_password
from app.deps import get_arq_pool, get_current_user, get_db_session
from app.jobs.models import FRAPJob
from app.jobs.router import extratos_router, router as jobs_router


class FakeArqJob:
    def __init__(self, job_id: str) -> None:
        self.job_id = job_id


class FakeArqPool:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    async def enqueue_job(self, function: str, *args, **kwargs):
        self.calls.append((function, args, kwargs))
        return FakeArqJob(f"arq-{len(self.calls)}")


def _build_app(
    factory: sessionmaker[Session], current_user_factory, pool: FakeArqPool | None
) -> FastAPI:
    def override_db() -> Iterator[Session]:
        s = factory()
        try:
            yield s
        finally:
            s.close()

    app = FastAPI()
    app.include_router(jobs_router)
    app.include_router(extratos_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = current_user_factory
    if pool is not None:
        app.dependency_overrides[get_arq_pool] = lambda: pool
    return app


@pytest.fixture
def factory(in_memory_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)


def _seed_admin(factory: sessionmaker[Session]) -> FRAPUsuario:
    with factory() as s:
        u = FRAPUsuario(
            Login="admin",
            Email="admin@tce.rn",
            NomeCompleto="Admin",
            SenhaHash=hash_password("x"),
            Papel="admin",
            Ativo=True,
        )
        s.add(u)
        s.commit()
        s.refresh(u)
        s.expunge(u)
        return u


def _seed_user(factory: sessionmaker[Session]) -> FRAPUsuario:
    with factory() as s:
        u = FRAPUsuario(
            Login="u1",
            Email="u@tce.rn",
            NomeCompleto="U",
            SenhaHash=hash_password("x"),
            Papel="user",
            Ativo=True,
        )
        s.add(u)
        s.commit()
        s.refresh(u)
        s.expunge(u)
        return u


def test_user_nao_pode_disparar_parse(factory: sessionmaker[Session]) -> None:
    user = _seed_user(factory)
    pool = FakeArqPool()
    app = _build_app(factory, lambda: user, pool)
    with TestClient(app) as c:
        r = c.post("/api/v1/jobs/parse-extratos")
        assert r.status_code == 403


def test_admin_dispara_parse_cria_FRAPJob_e_enfileira(
    factory: sessionmaker[Session],
) -> None:
    admin = _seed_admin(factory)
    pool = FakeArqPool()
    app = _build_app(factory, lambda: admin, pool)
    with TestClient(app) as c:
        r = c.post("/api/v1/jobs/parse-extratos")
        assert r.status_code == 202, r.text
        body = r.json()
        assert body["status"] == "pending"
        assert body["arqJobId"] == "arq-1"
    with factory() as s:
        rows = s.query(FRAPJob).all()
        assert len(rows) == 1
        assert rows[0].Tipo == "parse-extratos"
    assert pool.calls[0][0] == "task_parse_e_publicar"


def test_admin_dispara_conciliar_passa_ano_mes(
    factory: sessionmaker[Session],
) -> None:
    admin = _seed_admin(factory)
    pool = FakeArqPool()
    app = _build_app(factory, lambda: admin, pool)
    with TestClient(app) as c:
        r = c.post("/api/v1/jobs/conciliar", json={"ano": 2026, "mes": 4})
        assert r.status_code == 202
    func, args, _ = pool.calls[0]
    assert func == "task_conciliar_mes"
    assert args[1:] == (2026, 4)


def test_admin_dispara_conciliar_todos_enfileira_12_jobs(
    factory: sessionmaker[Session],
) -> None:
    admin = _seed_admin(factory)
    pool = FakeArqPool()
    app = _build_app(factory, lambda: admin, pool)
    with TestClient(app) as c:
        r = c.post("/api/v1/jobs/conciliar-todos", params={"ano": 2026})
        assert r.status_code == 202, r.text
        body = r.json()
        assert body["ano"] == 2026
        assert len(body["jobs"]) == 12
    meses = [args[2] for (_, args, _) in pool.calls]
    assert meses == list(range(1, 13))


def test_listar_jobs_ordenado_por_data(factory: sessionmaker[Session]) -> None:
    admin = _seed_admin(factory)
    pool = FakeArqPool()
    app = _build_app(factory, lambda: admin, pool)
    with TestClient(app) as c:
        c.post("/api/v1/jobs/parse-extratos")
        c.post("/api/v1/jobs/conciliar", json={"ano": 2026, "mes": 4})
        r = c.get("/api/v1/jobs")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 2
        assert body["items"][0]["tipo"] == "conciliar"


def test_jobs_503_sem_pool_configurado(factory: sessionmaker[Session]) -> None:
    admin = _seed_admin(factory)
    app = _build_app(factory, lambda: admin, pool=None)
    with TestClient(app) as c:
        r = c.post("/api/v1/jobs/parse-extratos")
        assert r.status_code == 503


def test_upload_extrato_grava_em_docs(
    factory: sessionmaker[Session], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.jobs.router as router_module

    pasta_fake = tmp_path / "extratos_frap"
    monkeypatch.setattr(router_module, "_PASTA_EXTRATOS", pasta_fake)
    monkeypatch.setattr(router_module, "_ROOT", tmp_path)

    admin = _seed_admin(factory)
    app = _build_app(factory, lambda: admin, pool=None)
    with TestClient(app) as c:
        r = c.post(
            "/api/v1/extratos/upload",
            params={"conta": "700000-6", "periodo": "042026"},
            files={"arquivo": ("042026.txt", b"conteudo do extrato", "text/plain")},
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["bytes"] == len(b"conteudo do extrato")
    saved = pasta_fake / "700000-6" / "042026.txt"
    assert saved.read_bytes() == b"conteudo do extrato"


def test_upload_rejeita_extensao_nao_txt(factory: sessionmaker[Session]) -> None:
    admin = _seed_admin(factory)
    app = _build_app(factory, lambda: admin, pool=None)
    with TestClient(app) as c:
        r = c.post(
            "/api/v1/extratos/upload",
            params={"conta": "700000-6", "periodo": "042026"},
            files={"arquivo": ("042026.csv", b"x", "text/csv")},
        )
        assert r.status_code == 400
