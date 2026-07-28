"""Decision-level review flow: claim/TTL, single-POST approve, guards.

Uses SQLite in-memory with ``cgad.models.Base`` metadata (the CGAD tables live
in their own declarative Base, separate from the FRAP ``app.db.Base``). MSSQL
context lookups (numero/ano, texto_acordao) degrade gracefully to None inside
the service, so no real database is needed.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.cgad.review.router import router as reviews_router
from app.deps import get_current_user, get_db_session
from cgad.etl.staging import (
    MultaStagingORM,
    ObrigacaoStagingORM,
    RecomendacaoStagingORM,
    RessarcimentoStagingORM,
)
from cgad.models import (
    Base as CgadBase,
    NERDecisaoORM,
    NERMultaORM,
    NERObrigacaoORM,
    NERRecomendacaoORM,
    NERRessarcimentoORM,
    ObrigacaoORM,
    ProcessedObrigacaoORM,
    RoleEnum,
    UserORM,
)


@pytest.fixture
def factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    CgadBase.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class UserHolder:
    """Mutable holder so tests can switch the authenticated user mid-test."""

    def __init__(self, user: UserORM) -> None:
        self.user = user


def _seed_user(factory: sessionmaker[Session], nome: str) -> UserORM:
    with factory() as s:
        u = UserORM(
            NomeUsuario=nome,
            Email=f"{nome}@tce.rn",
            SenhaHash="x",
            Papel=RoleEnum.reviewer,
            Ativo=True,
        )
        s.add(u)
        s.commit()
        s.refresh(u)
        s.expunge(u)
        return u


def _seed_decisao(factory: sessionmaker[Session]) -> dict:
    """One decision with one NER child of each type, plus a stage-2 final row
    (and bridge) for the obrigação."""
    with factory() as s:
        decisao = NERDecisaoORM(
            IdProcesso=100,
            IdComposicaoPauta=200,
            IdVotoPauta=300,
            RawJson="{}",
        )
        s.add(decisao)
        s.flush()

        multa = NERMultaORM(
            IdNerDecisao=decisao.IdNerDecisao, Ordem=1, DescricaoMulta="multa de R$ 1.000"
        )
        obrigacao = NERObrigacaoORM(
            IdNerDecisao=decisao.IdNerDecisao,
            Ordem=1,
            DescricaoObrigacao="obrigação de fazer X",
        )
        recomendacao = NERRecomendacaoORM(
            IdNerDecisao=decisao.IdNerDecisao,
            Ordem=1,
            DescricaoRecomendacao="recomendação Y",
        )
        ressarcimento = NERRessarcimentoORM(
            IdNerDecisao=decisao.IdNerDecisao,
            Ordem=1,
            DescricaoRessarcimento="ressarcimento de R$ 500",
        )
        s.add_all([multa, obrigacao, recomendacao, ressarcimento])
        s.flush()

        final_obr = ObrigacaoORM(
            IdProcesso=100,
            IdComposicaoPauta=200,
            IdVotoPauta=300,
            DescricaoObrigacao="obrigação de fazer X (stage-2)",
            Prazo="30 dias",
        )
        s.add(final_obr)
        s.flush()
        s.add(
            ProcessedObrigacaoORM(
                IdNerObrigacao=obrigacao.IdNerObrigacao,
                IdObrigacao=final_obr.IdObrigacao,
                DataProcessamento=datetime.utcnow(),
            )
        )
        s.commit()
        ids = {
            "decisao": decisao.IdNerDecisao,
            "multa": multa.IdNerMulta,
            "obrigacao": obrigacao.IdNerObrigacao,
            "recomendacao": recomendacao.IdNerRecomendacao,
            "ressarcimento": ressarcimento.IdNerRessarcimento,
            "final_obrigacao": final_obr.IdObrigacao,
        }
    return ids


@pytest.fixture
def env(factory: sessionmaker[Session]):
    user = _seed_user(factory, "revisor1")
    other = _seed_user(factory, "revisor2")
    ids = _seed_decisao(factory)
    holder = UserHolder(user)

    def override_db() -> Iterator[Session]:
        s = factory()
        try:
            yield s
        finally:
            s.close()

    app = FastAPI()
    app.include_router(reviews_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = lambda: holder.user
    client = TestClient(app)
    return {
        "client": client,
        "factory": factory,
        "ids": ids,
        "holder": holder,
        "user": user,
        "other": other,
    }


def _payload_completo(ids: dict, *, incluir_manual: bool = True) -> dict:
    entidades = [
        {
            "tipo": "multa",
            "id_ner": ids["multa"],
            "resultado": "rejected",
            "observacoes": "não é multa, é citação do relatório",
        },
        {
            "tipo": "obrigacao",
            "id_ner": ids["obrigacao"],
            "resultado": "approved",
            "campos": {
                "tipo": "obrigacao",
                "descricao_obrigacao": "obrigação editada pelo revisor",
                "prazo": "60 dias",
            },
        },
        {
            "tipo": "recomendacao",
            "id_ner": ids["recomendacao"],
            "resultado": "approved",
            "campos": {
                "tipo": "recomendacao",
                "descricao_recomendacao": "recomendação Y",
            },
        },
        {
            "tipo": "ressarcimento",
            "id_ner": ids["ressarcimento"],
            "resultado": "approved",
            "campos": {
                "tipo": "ressarcimento",
                "descricao_ressarcimento": "ressarcimento de R$ 500",
                "valor_dano": 500.0,
            },
        },
    ]
    if incluir_manual:
        entidades.append(
            {
                "tipo": "multa",
                "id_ner": None,
                "resultado": "approved",
                "campos": {
                    "tipo": "multa",
                    "descricao_multa": "multa que o extrator não pegou",
                    "valor_fixo": 2000.0,
                },
            }
        )
    return {"entidades": entidades}


def test_list_decisoes_counts(env):
    resp = env["client"].get("/api/v1/cgad/reviews/decisoes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["id"] == env["ids"]["decisao"]
    assert (item["multas"], item["obrigacoes"], item["recomendacoes"], item["ressarcimentos"]) == (
        1,
        1,
        1,
        1,
    )


def test_detail_entidades(env):
    resp = env["client"].get(f"/api/v1/cgad/reviews/decisoes/{env['ids']['decisao']}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["entidades"]) == 4
    por_tipo = {e["tipo"]: e for e in body["entidades"]}
    # obrigação usa os campos da linha final do stage-2
    assert por_tipo["obrigacao"]["campos"]["descricao_obrigacao"] == (
        "obrigação de fazer X (stage-2)"
    )
    assert por_tipo["obrigacao"]["campos"]["prazo"] == "30 dias"
    # multa não tem stage-2: campos default com a descrição NER
    assert por_tipo["multa"]["campos"]["descricao_multa"] == "multa de R$ 1.000"
    assert all(e["status"] == "pending" for e in body["entidades"])


def test_claim_conflict_and_ttl_takeover(env, frozen_time):
    client, ids, holder = env["client"], env["ids"], env["holder"]
    url = f"/api/v1/cgad/reviews/decisoes/{ids['decisao']}/claim"

    assert client.post(url).status_code == 200

    holder.user = env["other"]
    resp = client.post(url)
    assert resp.status_code == 409
    assert "revisor1" in resp.json()["detail"]

    frozen_time.tick(16 * 60)  # TTL de 15 min expira
    assert client.post(url).status_code == 200


def test_approve_requires_claim(env):
    resp = env["client"].post(
        f"/api/v1/cgad/reviews/decisoes/{env['ids']['decisao']}/approve",
        json=_payload_completo(env["ids"]),
    )
    assert resp.status_code == 403


def test_approve_happy_path(env):
    client, ids, factory = env["client"], env["ids"], env["factory"]
    base = f"/api/v1/cgad/reviews/decisoes/{ids['decisao']}"

    assert client.post(f"{base}/claim").status_code == 200
    resp = client.post(f"{base}/approve", json=_payload_completo(ids))
    assert resp.status_code == 200, resp.json()
    body = resp.json()
    assert body["revisado_por"] == "revisor1"
    assert body["claimed_by"] is None

    with factory() as s:
        multas = s.execute(select(MultaStagingORM)).scalars().all()
        assert {m.IdNerMulta for m in multas} == {ids["multa"], None}
        rejeitada = next(m for m in multas if m.IdNerMulta == ids["multa"])
        assert rejeitada.Status.value == "rejected"
        assert rejeitada.DescricaoMulta == "multa de R$ 1.000"  # descrição original
        manual = next(m for m in multas if m.IdNerMulta is None)
        assert manual.Status.value == "approved"
        assert manual.ValorFixo == 2000.0
        assert manual.IdProcesso == 100

        obr = s.execute(select(ObrigacaoStagingORM)).scalar_one()
        assert obr.IdNerObrigacao == ids["obrigacao"]
        assert obr.IdObrigacao == ids["final_obrigacao"]  # FK final via bridge
        assert obr.DescricaoObrigacao == "obrigação editada pelo revisor"
        assert obr.Status.value == "approved"

        rec = s.execute(select(RecomendacaoStagingORM)).scalar_one()
        assert rec.IdNerRecomendacao == ids["recomendacao"]

        res = s.execute(select(RessarcimentoStagingORM)).scalar_one()
        assert res.ValorDano == 500.0

        # linha final permanece intacta (modelo de auditoria)
        final = s.get(ObrigacaoORM, ids["final_obrigacao"])
        assert final.DescricaoObrigacao == "obrigação de fazer X (stage-2)"

        decisao = s.get(NERDecisaoORM, ids["decisao"])
        assert decisao.RevisadoPor == "revisor1"
        assert decisao.ReservadoPor is None

    # decisão sai da lista de pendentes
    assert client.get("/api/v1/cgad/reviews/decisoes").json()["total"] == 0

    # awaiting-dispatch mostra os aprovados (4 = 3 extraídos + 1 manual)
    dispatch = client.get("/api/v1/cgad/reviews/awaiting-dispatch").json()
    assert dispatch["total"] == 4
    assert {i["tipo"] for i in dispatch["items"]} == {
        "multa",
        "obrigacao",
        "recomendacao",
        "ressarcimento",
    }


def test_approve_incomplete_payload(env):
    client, ids = env["client"], env["ids"]
    base = f"/api/v1/cgad/reviews/decisoes/{ids['decisao']}"
    client.post(f"{base}/claim")

    payload = _payload_completo(ids, incluir_manual=False)
    payload["entidades"] = payload["entidades"][:-1]  # falta o ressarcimento
    resp = client.post(f"{base}/approve", json=payload)
    assert resp.status_code == 422
    assert "recarregue" in resp.json()["detail"]


def test_approve_unknown_entity(env):
    client, ids = env["client"], env["ids"]
    base = f"/api/v1/cgad/reviews/decisoes/{ids['decisao']}"
    client.post(f"{base}/claim")

    payload = _payload_completo(ids)
    payload["entidades"][1]["id_ner"] = 999999
    resp = client.post(f"{base}/approve", json=payload)
    assert resp.status_code == 422


def test_reapprove_conflict(env):
    client, ids = env["client"], env["ids"]
    base = f"/api/v1/cgad/reviews/decisoes/{ids['decisao']}"
    client.post(f"{base}/claim")
    assert client.post(f"{base}/approve", json=_payload_completo(ids)).status_code == 200

    # segundo approve: decisão já revisada → claim recusa com 409
    assert client.post(f"{base}/claim").status_code == 409
    resp = client.post(f"{base}/approve", json=_payload_completo(ids))
    assert resp.status_code in (403, 409)


def test_reject_sem_motivo(env):
    client, ids = env["client"], env["ids"]
    base = f"/api/v1/cgad/reviews/decisoes/{ids['decisao']}"
    client.post(f"{base}/claim")

    payload = _payload_completo(ids)
    payload["entidades"][0]["observacoes"] = "curto"  # < 10 chars
    resp = client.post(f"{base}/approve", json=payload)
    assert resp.status_code == 422


def test_manual_entity_cannot_be_rejected(env):
    client, ids = env["client"], env["ids"]
    base = f"/api/v1/cgad/reviews/decisoes/{ids['decisao']}"
    client.post(f"{base}/claim")

    payload = _payload_completo(ids)
    payload["entidades"].append(
        {
            "tipo": "multa",
            "id_ner": None,
            "resultado": "rejected",
            "observacoes": "motivo suficientemente longo",
        }
    )
    resp = client.post(f"{base}/approve", json=payload)
    assert resp.status_code == 422
