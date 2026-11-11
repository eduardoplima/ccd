"""Remoção de obrigações/recomendações curadas por acórdão (CGAD)."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.cgad.remocoes import service
from app.cgad.remocoes.router import router
from app.deps import get_current_user, get_db_session
from cgad.etl.staging import ObrigacaoStagingORM, RecomendacaoStagingORM, ReviewStatus
from cgad.models import Base as CgadBase, RoleEnum, UserORM

PROC, ACORDAO_ORIGEM, ACORDAO_REMOCAO = 553221, 112674, 127763


@pytest.fixture
def ctx(monkeypatch):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    CgadBase.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(
        service,
        "_acordaos_do_processo",
        lambda _id: [
            {"id_composicao_pauta": ACORDAO_ORIGEM},
            {"id_composicao_pauta": ACORDAO_REMOCAO},
        ],
    )
    with factory() as s:
        user = UserORM(
            NomeUsuario="revisor", Email="r@tce.rn", SenhaHash="x", Papel=RoleEnum.admin, Ativo=True
        )
        s.add(user)
        s.add(
            ObrigacaoStagingORM(
                IdProcesso=PROC,
                IdComposicaoPauta=ACORDAO_ORIGEM,
                IdVotoPauta=0,
                DescricaoObrigacao="entregar o SIAI de 2020",
                Status=ReviewStatus.approved,
            )
        )
        s.add(
            RecomendacaoStagingORM(
                IdProcesso=PROC,
                IdComposicaoPauta=ACORDAO_ORIGEM,
                IdVotoPauta=0,
                DescricaoRecomendacao="rec",
                Status=ReviewStatus.dispatched,
            )
        )
        s.commit()

    def _db():
        with factory() as s:
            yield s

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db_session] = _db
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app), factory, user


def _payload(**kw):
    base = dict(
        id_processo=PROC,
        id_composicao_pauta_remocao=ACORDAO_REMOCAO,
        justificativa="Desconstituído pelo Acórdão 297/2026",
        itens=[{"tipo": "obrigacao", "id": 1}, {"tipo": "recomendacao", "id": 1}],
    )
    return base | kw


def test_remove_marca_auditoria(ctx):
    client, factory, _ = ctx
    r = client.post("/api/v1/cgad/remocoes", json=_payload())
    assert r.status_code == 200, r.text
    assert r.json() == {"removidos": 2}
    with factory() as s:
        for orm in (ObrigacaoStagingORM, RecomendacaoStagingORM):
            x = s.get(orm, 1)
            assert x.Status == ReviewStatus.removed
            assert x.IdComposicaoPautaRemocao == ACORDAO_REMOCAO
            assert x.JustificativaRemocao.startswith("Desconstituído")
            assert x.RemovidoPor == "revisor" and x.DataRemocao is not None
    # segunda remoção do mesmo item: 409, nada muda
    assert client.post("/api/v1/cgad/remocoes", json=_payload()).status_code == 409


def test_rejeita_justificativa_vazia_e_acordao_alheio(ctx):
    client, factory, _ = ctx
    assert (
        client.post("/api/v1/cgad/remocoes", json=_payload(justificativa="  ")).status_code == 409
    )
    assert client.post("/api/v1/cgad/remocoes", json=_payload(justificativa="")).status_code == 422
    r = client.post("/api/v1/cgad/remocoes", json=_payload(id_composicao_pauta_remocao=999))
    assert r.status_code == 409
    # item de outro processo derruba o lote inteiro
    r = client.post("/api/v1/cgad/remocoes", json=_payload(id_processo=1))
    assert r.status_code == 409
    with factory() as s:
        assert s.get(ObrigacaoStagingORM, 1).Status == ReviewStatus.approved


def test_revisor_sem_edicao_nao_remove(ctx):
    client, _, user = ctx
    user.Papel = RoleEnum.reviewer  # sem linha em UsuarioPermissoes: vê, não edita
    assert client.post("/api/v1/cgad/remocoes", json=_payload()).status_code == 403
