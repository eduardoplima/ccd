from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.auth.security import hash_password
from app.deps import get_current_user, get_db_session
from app.matches.router import router as matches_router
from tests.test_lancamentos import DDL, SEED_LOOKUPS


@pytest.fixture
def client_with_data(in_memory_engine: Engine) -> Iterator[TestClient]:
    with in_memory_engine.begin() as conn:
        for ddl in DDL:
            conn.execute(text(ddl))
        for seed in SEED_LOOKUPS:
            conn.execute(text(seed))
        conn.execute(
            text(
                "INSERT INTO FRAPLancamento (IdArquivo, IdConta, Periodo, OrdemNoArquivo, DtMovimento, Historico, Documento, Valor, ValorDC, IdCategoria) "
                "VALUES (1, 1, '012026', 1, '2026-01-15', 'Crédito', 'X', 100, 'C', 1), "
                "(1, 1, '042026', 2, '2026-04-10', 'Crédito', 'Y', 200, 'C', 1), "
                "(1, 1, '042026', 3, '2026-04-15', 'Débito', 'Z', 50, 'D', 1)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO FRAPMatchOB (IdLancamento, IdConta, Periodo, AnoSigef, NuOrdemBancaria, ValorOB, IdStatusMatch) "
                "VALUES (2, 1, '042026', 2026, '2026OB001', 200, 10)"
            )
        )

    factory = sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)
    with factory() as s:
        s.add(
            FRAPUsuario(
                Login="u1",
                Email="u@tce.rn",
                NomeCompleto="U",
                SenhaHash=hash_password("x"),
                Papel="user",
                Ativo=True,
            )
        )
        s.commit()
        admin = s.query(FRAPUsuario).one()

    def override_db() -> Iterator[Session]:
        x = factory()
        try:
            yield x
        finally:
            x.close()

    def override_user() -> FRAPUsuario:
        return admin

    app = FastAPI()
    app.include_router(matches_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user
    with TestClient(app) as c:
        yield c


def test_listar_matches_ob(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/matches/ob?ano=2026")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["matcher"] == "OB"
    assert item["nuOrdemBancaria"] == "2026OB001"
    assert float(item["valorLancamento"]) == 200.0


def test_filtro_por_mes_isola_periodo(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/matches/ob?ano=2026&mes=1")
    assert r.json()["total"] == 0
    r = client_with_data.get("/api/v1/matches/ob?ano=2026&mes=4")
    assert r.json()["total"] == 1
