"""Multas não cominadas: só obrigações com multa prevista cujo processo não tem
débito tipo 5. O banco ``processo`` não existe no SQLite, então o lookup em
``Exe_Debito`` é substituído por monkeypatch."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.cgad.multas_nao_cominadas import service
from app.cgad.multas_nao_cominadas.router import router
from app.deps import get_current_user, get_db_session
from cgad.etl.staging import ObrigacaoStagingORM, ReviewStatus
from cgad.models import Base as CgadBase, RoleEnum, UserORM

AGORA = datetime(2026, 9, 25, 12, 0, 0)


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    CgadBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    with factory() as s:
        base = dict(IdComposicaoPauta=1, IdVotoPauta=1, Revisor="revisor1", DataRevisao=AGORA)
        s.add_all(
            [
                ObrigacaoStagingORM(  # entra: multa prevista, processo sem débito 5
                    IdProcesso=100,
                    DescricaoObrigacao="obrigação 1",
                    Status=ReviewStatus.approved,
                    TemMultaCominatoria=True,
                    NomeResponsavelMultaCominatoria="NEREU BATISTA LINHARES",
                    ValorMultaCominatoria=50.0,
                    DataCumprimento=date(2026, 1, 15),
                    **base,
                ),
                ObrigacaoStagingORM(  # sai: processo 101 tem débito 5
                    IdProcesso=101,
                    DescricaoObrigacao="obrigação 2",
                    Status=ReviewStatus.dispatched,
                    TemMultaCominatoria=True,
                    **base,
                ),
                ObrigacaoStagingORM(  # sai: sem multa prevista
                    IdProcesso=100,
                    DescricaoObrigacao="obrigação 3",
                    Status=ReviewStatus.approved,
                    TemMultaCominatoria=False,
                    **base,
                ),
                ObrigacaoStagingORM(  # sai: pendente
                    IdProcesso=102,
                    DescricaoObrigacao="obrigação 4",
                    Status=ReviewStatus.pending,
                    TemMultaCominatoria=True,
                    **base,
                ),
            ]
        )
        s.add(
            UserORM(
                NomeUsuario="revisor1",
                Email="r@tce.rn",
                SenhaHash="x",
                Papel=RoleEnum.reviewer,
                Ativo=True,
            )
        )
        s.commit()
        user = s.query(UserORM).one()
        s.expunge(user)

    def override_db() -> Iterator[Session]:
        s = factory()
        try:
            yield s
        finally:
            s.close()

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def test_lista_so_quem_nao_tem_debito_tipo_5(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(service, "_processos_com_multa_cadastrada", lambda ids: {101})
    resp = client.get("/api/v1/cgad/multas-nao-cominadas")
    assert resp.status_code == 200
    body = resp.json()
    assert (body["total_obrigacoes"], body["total_processos"]) == (1, 1)
    (item,) = body["items"]
    assert item["id_processo"] == 100
    assert item["descricao"] == "obrigação 1"
    assert item["valor_dia"] == 50.0
    assert item["data_cumprimento"] == "2026-01-15"
    assert item["status"] == "approved"
    assert item["data_revisao"] is not None


def test_falha_no_banco_processo_vira_503(client: TestClient, monkeypatch) -> None:
    def boom(ids):
        raise RuntimeError("sem MSSQL")

    monkeypatch.setattr(service, "_processos_com_multa_cadastrada", boom)
    assert client.get("/api/v1/cgad/multas-nao-cominadas").status_code == 503
