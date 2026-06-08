from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.auth.security import hash_password
from app.debitos.router import router as debitos_router
from app.deps import get_current_user, get_db_session
from tests.test_lancamentos import DDL, SEED_LOOKUPS


@pytest.fixture
def client_with_data(in_memory_engine: Engine) -> Iterator[TestClient]:
    with in_memory_engine.begin() as conn:
        for ddl in DDL:
            conn.execute(text(ddl))
        for seed in SEED_LOOKUPS:
            conn.execute(text(seed))
        # Lançamento + match Pessoa + match Guia mesmo CPF
        conn.execute(
            text(
                "INSERT INTO FRAPLancamento (IdArquivo, IdConta, Periodo, OrdemNoArquivo, DtMovimento, Historico, Documento, Valor, ValorDC, IdCategoria, CpfCnpjDepositante) "
                "VALUES (1, 1, '042026', 1, '2026-04-15', 'Crédito', 'X', 500, 'C', 1, '12345678900')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO FRAPMatchPessoa (IdLancamento, IdConta, Periodo, IdDebito, IdProcessoExecucao, CpfCnpj, NomePessoa, ValorPago, IdStatusMatch) "
                "VALUES (1, 1, '042026', 777, 999, '12345678900', 'Joao', 500, 20)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO FRAPMatchGuia (IdLancamento, IdConta, Periodo, IdBoleto, IdDebito, CpfCnpj, NomePessoa, ValorPago, IdStatusMatch) "
                "VALUES (1, 1, '042026', 555, 777, '12345678900', 'Joao', 500, 35)"
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
    app.include_router(debitos_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user
    with TestClient(app) as c:
        yield c


def test_busca_sem_filtro_retorna_vazio(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/debitos")
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_busca_por_cpfcnpj_retorna_pessoa_e_guia(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/debitos?cpfcnpj=12345678900")
    assert r.status_code == 200, r.text
    body = r.json()
    matchers = sorted(item["matcher"] for item in body["items"])
    assert matchers == ["GUIA", "PESSOA"]


def test_busca_por_id_debito(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/debitos?id_debito=777")
    body = r.json()
    matchers = sorted(item["matcher"] for item in body["items"])
    assert matchers == ["GUIA", "PESSOA"]


def test_busca_por_id_processo(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/debitos?id_processo=999")
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["matcher"] == "PESSOA"
