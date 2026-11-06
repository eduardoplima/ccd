"""CGTAG: endpoints e montagem do registro a partir da saída do LLM.

SQLite em memória com CCDTAG/CCDTAGObrigacao. O banco `processo`, o share e
o LLM ficam de fora: o endpoint de extração só enfileira.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.auth.security import hash_password
from app.ccd.tags import service
from app.ccd.tags.router import router
from app.ccd.tags.tasks import ObrigacaoExtraida, TagExtraido, montar_registro, parse_data
from app.deps import get_arq_pool, get_current_user, get_db_session, get_processo_session

DDL = [
    """CREATE TABLE CCDTAG (
        IdCCDTAG INTEGER PRIMARY KEY AUTOINCREMENT,
        IdProcesso INTEGER NOT NULL, NumeroProcesso TEXT NOT NULL, AnoProcesso INTEGER NOT NULL,
        Evento INTEGER NOT NULL, IdEvento INTEGER, IdInformacao INTEGER,
        Numero TEXT NOT NULL, Orgao TEXT NOT NULL, IdOrgao INTEGER, Responsavel TEXT NOT NULL,
        CargoResponsavel TEXT, CpfResponsavel TEXT, Compromissario TEXT, DataCelebracao DATE,
        Prazo DATE, Homologacao TEXT, ValorMultaDescumprimento NUMERIC,
        Situacao TEXT NOT NULL DEFAULT 'VIGENTE', Revisado INTEGER NOT NULL DEFAULT 0,
        TextoOCR TEXT, PayloadLLM TEXT, Observacoes TEXT, Ativo INTEGER NOT NULL DEFAULT 1,
        DataInclusao DATETIME NOT NULL, IdUsuarioInclusao INTEGER, DataAtualizacao DATETIME,
        IdUsuarioAtualizacao INTEGER
    )""",
    """CREATE TABLE CCDTAGObrigacao (
        IdCCDTAGObrigacao INTEGER PRIMARY KEY AUTOINCREMENT,
        IdCCDTAG INTEGER NOT NULL, Ordem INTEGER NOT NULL, Clausula TEXT NOT NULL,
        Descricao TEXT NOT NULL, PrazoTexto TEXT, DataLimite DATE,
        Situacao TEXT NOT NULL DEFAULT 'PENDENTE', DataCumprimento DATE,
        EventoComprovacao INTEGER, Observacoes TEXT
    )""",
]

PECA = {
    "IdProcesso": 396087,
    "numero": "014254",
    "ano": 2015,
    "id_evento": 6680548,
    "id_informacao": 3038071,
}


def _extraido() -> TagExtraido:
    return TagExtraido(
        numero="001/2025-PROC-GRC",
        orgao="Câmara Municipal de Natal",
        responsavel="Ériko Samuel Xavier de Oliveira",
        cargo_responsavel="Presidente",
        compromissario="Ricart César Coelho dos Santos",
        valor_multa_descumprimento=15000.0,
        obrigacoes=[
            ObrigacaoExtraida(
                clausula="Cláusula Segunda, caput",
                descricao="Aprovar lei da CEAPM",
                prazo_texto="120 dias a partir de 1º de agosto de 2025",
                data_limite="28/11/2025",
            ),
            ObrigacaoExtraida(
                clausula="Cláusula Segunda, §1º", descricao="Portal", data_limite="29/10/2025"
            ),
            ObrigacaoExtraida(
                clausula="Cláusula Terceira",
                descricao="Comprovar permanência",
                data_limite="15/12/2026",
            ),
        ],
    )


@pytest.fixture
def env(in_memory_engine: Engine):
    with in_memory_engine.begin() as conn:
        for ddl in DDL:
            conn.execute(text(ddl))
    factory = sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)
    with factory() as s:
        s.add(
            FRAPUsuario(
                NomeUsuario="admin",
                Email="a@tce.rn",
                SenhaHash=hash_password("x"),
                Papel="admin",
                Ativo=True,
            )
        )
        s.commit()
        user = s.query(FRAPUsuario).one()
        cab, obs = montar_registro(PECA, 298, "texto do termo", _extraido())
        service.criar(s, cabecalho=cab, obrigacoes=obs, id_usuario=user.IdUsuario)

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
    app.dependency_overrides[get_processo_session] = lambda: None

    class _Pool:
        chamadas: list[tuple] = []

        async def enqueue_job(self, funcao: str, *args, **kwargs):
            self.chamadas.append((funcao, args))
            return type("J", (), {"job_id": "arq-1"})()

    pool = _Pool()
    app.dependency_overrides[get_arq_pool] = lambda: pool
    return {"client": TestClient(app), "factory": factory, "pool": pool}


def test_parse_data() -> None:
    assert parse_data("até 28/11/2025") == date(2025, 11, 28)
    assert parse_data("31/02/2025") is None
    assert parse_data(None) is None


def test_montar_registro_prazo_e_maior_data_limite() -> None:
    cab, obs = montar_registro(PECA, 298, "t", _extraido())
    assert cab["Prazo"] == date(2026, 12, 15)
    assert cab["NumeroProcesso"] == "014254" and cab["Evento"] == 298
    assert [o["DataLimite"] for o in obs] == [
        date(2025, 11, 28),
        date(2025, 10, 29),
        date(2026, 12, 15),
    ]


def test_lista_e_detalhe(env) -> None:
    lista = env["client"].get("/api/v1/ccd/tags").json()
    assert lista["total"] == 1
    item = lista["items"][0]
    assert item["processo"] == "014254/2015" and item["qtdObrigacoes"] == 3
    assert item["proximaDataLimite"] == "2025-10-29" and item["revisado"] is False
    det = env["client"].get(f"/api/v1/ccd/tags/{item['id']}").json()
    assert det["valorMultaDescumprimento"] == 15000.0
    assert [o["clausula"] for o in det["obrigacoes"]][0] == "Cláusula Segunda, caput"


def test_extrair_enfileira_job(env) -> None:
    resp = env["client"].post(
        "/api/v1/ccd/tags/extrair", json={"processo": "14254/2015", "evento": 298}
    )
    assert resp.status_code == 202, resp.text
    assert resp.json()["tipo"] == "ccd-tags-extrair"
    funcao, args = env["pool"].chamadas[-1]
    assert funcao == "task_extrair_tag" and args[1:3] == ("014254/2015", 298)


def test_patch_e_put_obrigacoes(env) -> None:
    c = env["client"]
    r = c.patch("/api/v1/ccd/tags/1", json={"revisado": True, "homologacao": "Acórdão 142/2025-TC"})
    assert r.status_code == 200 and r.json()["revisado"] is True
    r = c.put(
        "/api/v1/ccd/tags/1/obrigacoes",
        json={
            "obrigacoes": [
                {
                    "clausula": "Cláusula Segunda, caput",
                    "descricao": "Lei",
                    "dataLimite": "2025-11-28",
                    "situacao": "CUMPRIDA",
                    "dataCumprimento": "2025-11-26",
                    "eventoComprovacao": 338,
                },
            ]
        },
    )
    assert r.status_code == 200, r.text
    assert [o["situacao"] for o in r.json()["obrigacoes"]] == ["CUMPRIDA"]
    assert r.json()["proximaDataLimite"] is None  # nenhuma pendente
    assert c.delete("/api/v1/ccd/tags/1").status_code == 204
    assert c.get("/api/v1/ccd/tags").json()["total"] == 0
