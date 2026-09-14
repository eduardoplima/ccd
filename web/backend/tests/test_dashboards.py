"""Dashboards: dedup de pessoas responsáveis, treemaps e lista de entidades.

SQLite em memória sobre ``cgad.models.Base`` (as ``*Staging`` vivem nela). O
banco ``processo`` não existe aqui, então tipo/relator degradam para
"Desconhecido" — o próprio contrato de ``_load_tipo_relator``.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.cgad.dashboards.router import router as dashboards_router
from app.deps import get_current_user, get_db_session
from cgad.etl.staging import ObrigacaoStagingORM, RecomendacaoStagingORM, ReviewStatus
from cgad.models import Base as CgadBase, RoleEnum, UserORM

AGORA = datetime(2026, 9, 10, 12, 0, 0)


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
        base = dict(
            IdComposicaoPauta=1,
            IdVotoPauta=1,
            Status=ReviewStatus.approved,
            Revisor="revisor1",
            DataRevisao=AGORA,
        )
        s.add_all(
            [
                ObrigacaoStagingORM(
                    IdProcesso=100,
                    DescricaoObrigacao="obrigação 1",
                    OrgaoResponsavel="IPERN",
                    TemMultaCominatoria=True,
                    NomeResponsavelMultaCominatoria="NEREU BATISTA LINHARES",
                    DocumentoResponsavelMultaCominatoria="123.456.789-01",
                    **base,
                ),
                ObrigacaoStagingORM(
                    IdProcesso=101,
                    DescricaoObrigacao="obrigação 2",
                    OrgaoResponsavel="IPERN",
                    TemMultaCominatoria=True,
                    NomeResponsavelMultaCominatoria="Nereu Batista Linhares",
                    DocumentoResponsavelMultaCominatoria="12345678901",
                    IdPessoaMultaCominatoria=7,
                    **base,
                ),
                RecomendacaoStagingORM(
                    IdProcesso=100,
                    DescricaoRecomendacao="recomendação 1",
                    OrgaoResponsavel="SESAP",
                    NomeResponsavel="Nereu Batista Linhares",
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
    app.include_router(dashboards_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


def test_pessoa_unica_treemaps_e_entidades(client: TestClient) -> None:
    resp = client.get("/api/v1/cgad/dashboards/summary")
    assert resp.status_code == 200
    body = resp.json()

    # Nereu chega com documento formatado, com id e só com nome: um único bucket.
    assert len(body["top_pessoas"]) == 1
    pessoa = body["top_pessoas"][0]
    assert (pessoa["obrigacoes"], pessoa["recomendacoes"], pessoa["total"]) == (2, 1, 3)

    obr = body["treemap_obrigacao"]
    assert obr["por_orgao"] == [{"nome": "IPERN", "total": 2}]
    assert obr["por_tipo"] == [{"nome": "Desconhecido", "total": 2}]
    assert obr["por_relator"] == [{"nome": "Desconhecido", "total": 2}]
    rec = body["treemap_recomendacao"]
    assert rec["por_orgao"] == [{"nome": "SESAP", "total": 1}]

    entidades = body["entidades"]
    assert len(entidades) == 3
    assert {e["pessoa"] for e in entidades} == {pessoa["nome"]}
    assert {e["status"] for e in entidades} == {"approved"}
    assert all(e["data_envio"] is None for e in entidades)
    assert sorted(e["orgao"] for e in entidades) == ["IPERN", "IPERN", "SESAP"]
