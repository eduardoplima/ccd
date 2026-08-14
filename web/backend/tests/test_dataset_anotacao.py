"""Conjunto de dados anotado: validação de spans, isolamento entre anotadores
e formato do export.

SQLite em memória com a metadata de ``cgad.models`` (as tabelas CGAD vivem numa
Base declarativa própria, separada da ``app.db.Base`` do FRAP).
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.cgad.dataset.router import router as dataset_router
from app.deps import get_current_user, get_db_session
from cgad.models import (
    Base as CgadBase,
    DatasetAnotacaoORM,
    DatasetDocumentoORM,
    RoleEnum,
    UserORM,
)


TEXTO = "DECIDEM aplicar multa de R$ 1.000 ao gestor e recomendar a revisão do edital."
# offsets:                       ^22          ^35                ^54
MULTA = {"start": 22, "end": 35, "label": "MULTA"}


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
    def __init__(self, user: UserORM) -> None:
        self.user = user


def _seed_user(
    factory: sessionmaker[Session], nome: str, papel: RoleEnum = RoleEnum.reviewer
) -> UserORM:
    with factory() as s:
        u = UserORM(
            NomeUsuario=nome,
            Email=f"{nome}@tce.rn",
            SenhaHash="x",
            Papel=papel,
            Ativo=True,
        )
        s.add(u)
        s.commit()
        s.refresh(u)
        s.expunge(u)
        return u


@pytest.fixture
def env(factory: sessionmaker[Session]):
    eduardo = _seed_user(factory, "eduardo")
    isabella = _seed_user(factory, "isabella")
    admin = _seed_user(factory, "admin", RoleEnum.admin)

    with factory() as s:
        doc = DatasetDocumentoORM(Texto=TEXTO, Origem="decicontas", IdExterno=42)
        outro = DatasetDocumentoORM(Texto=TEXTO, Origem="ampliacao", Processo="1/2025")
        s.add_all([doc, outro])
        s.flush()
        ids = [doc.IdDocumento, outro.IdDocumento]
        for id_doc in ids:
            for anotador in ("eduardo", "isabella"):
                s.add(DatasetAnotacaoORM(IdDocumento=id_doc, Anotador=anotador, Status="pending"))
        s.commit()

    holder = UserHolder(isabella)

    def override_db() -> Iterator[Session]:
        s = factory()
        try:
            yield s
        finally:
            s.close()

    app = FastAPI()
    app.include_router(dataset_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = lambda: holder.user
    return {
        "client": TestClient(app),
        "holder": holder,
        "eduardo": eduardo,
        "isabella": isabella,
        "admin": admin,
        "doc": ids[0],
        "outro": ids[1],
    }


BASE = "/api/v1/cgad/dataset"


# ----- validação de spans ----------------------------------------------------


def test_span_fora_do_texto_e_rejeitado(env):
    r = env["client"].put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [{"start": 0, "end": len(TEXTO) + 5, "label": "MULTA"}]},
    )
    assert r.status_code == 422
    assert "excede o texto" in r.json()["detail"]


def test_spans_sobrepostos_sao_rejeitados(env):
    r = env["client"].put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={
            "spans": [
                {"start": 10, "end": 30, "label": "MULTA"},
                {"start": 25, "end": 40, "label": "OBRIGACAO"},
            ]
        },
    )
    assert r.status_code == 422


def test_span_invertido_e_rejeitado(env):
    r = env["client"].put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [{"start": 30, "end": 10, "label": "MULTA"}]},
    )
    assert r.status_code == 422


def test_rotulo_desconhecido_e_rejeitado(env):
    r = env["client"].put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [{"start": 0, "end": 5, "label": "APOSENTADORIA"}]},
    )
    assert r.status_code == 422


# ----- isolamento entre anotadores (a cegueira) ------------------------------


def test_anotador_nao_ve_spans_de_outro(env):
    client, holder = env["client"], env["holder"]

    holder.user = env["eduardo"]
    assert (
        client.put(f"{BASE}/documentos/{env['doc']}/anotacao", json={"spans": [MULTA]}).status_code
        == 200
    )

    holder.user = env["isabella"]
    detalhe = client.get(f"{BASE}/documentos/{env['doc']}").json()
    assert detalhe["spans"] == []
    assert detalhe["status"] == "pending"


def test_documento_nao_atribuido_da_404(env, factory):
    with factory() as s:
        alheio = DatasetDocumentoORM(Texto=TEXTO, Origem="ampliacao")
        s.add(alheio)
        s.commit()
        id_alheio = alheio.IdDocumento

    assert env["client"].get(f"{BASE}/documentos/{id_alheio}").status_code == 404


def test_abas_de_probabilidade_usam_a_uniao_das_triagens(env, factory):
    with factory() as s:
        s.add_all(
            [
                DatasetAnotacaoORM(
                    IdDocumento=env["doc"],
                    Anotador="deepseek",
                    Status="done",
                    Spans=json.dumps([MULTA]),
                ),
                DatasetAnotacaoORM(
                    IdDocumento=env["outro"],
                    Anotador="deepseek",
                    Status="done",
                    Spans="[]",
                ),
            ]
        )
        s.commit()

    def abas():
        client = env["client"]
        com = client.get(f"{BASE}/documentos", params={"com_entidades": True}).json()
        sem = client.get(f"{BASE}/documentos", params={"com_entidades": False}).json()
        return (
            [i["id"] for i in com["items"]],
            [i["id"] for i in sem["items"]],
            com["com_entidades"],
        )

    assert abas() == ([env["doc"]], [env["outro"]], 1)

    # O eduardo marcou o que o modelo deixou passar: a união põe os dois na aba.
    with factory() as s:
        anot = (
            s.query(DatasetAnotacaoORM)
            .filter_by(IdDocumento=env["outro"], Anotador="eduardo")
            .one()
        )
        anot.Spans = json.dumps([MULTA])
        anot.Status = "done"
        s.commit()

    assert abas() == ([env["doc"], env["outro"]], [], 2)

    # O cartão conta a fila inteira, não a aba aberta.
    todos = env["client"].get(f"{BASE}/documentos").json()
    assert len(todos["items"]) == 2
    assert todos["com_entidades"] == 2


def test_filtro_esconde_atos_de_pessoal_mas_mantem_sem_tipo(env, factory):
    with factory() as s:
        s.get(DatasetDocumentoORM, env["doc"]).CodigoTipoProcesso = "APO"
        s.commit()

    pagina = env["client"].get(f"{BASE}/documentos", params={"sem_atos_pessoal": True}).json()
    # o `outro` está sem tipo: não é ato de pessoal, então fica.
    assert [i["id"] for i in pagina["items"]] == [env["outro"]]
    assert pagina["pendentes"] == 1


def test_lista_conta_apenas_o_proprio_progresso(env):
    client, holder = env["client"], env["holder"]

    holder.user = env["eduardo"]
    client.put(f"{BASE}/documentos/{env['doc']}/anotacao", json={"spans": [MULTA]})

    holder.user = env["isabella"]
    pagina = client.get(f"{BASE}/documentos").json()
    assert pagina["concluidos"] == 0
    assert pagina["pendentes"] == 2


# ----- fluxo de anotação -----------------------------------------------------


def test_concluir_aponta_o_proximo_pendente(env):
    r = env["client"].put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [MULTA], "status": "done"},
    )
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["status"] == "done"
    assert corpo["spans"] == [MULTA]
    assert corpo["proximo_pendente"] == env["outro"]


def test_rascunho_nao_conclui(env):
    corpo = (
        env["client"]
        .put(
            f"{BASE}/documentos/{env['doc']}/anotacao",
            json={"spans": [MULTA], "status": "pending"},
        )
        .json()
    )
    assert corpo["status"] == "pending"
    assert corpo["data_conclusao"] is None


# ----- progresso e concordância ----------------------------------------------


def test_concordancia_total_quando_anotacoes_batem(env):
    client, holder = env["client"], env["holder"]
    for usuario in (env["eduardo"], env["isabella"]):
        holder.user = usuario
        client.put(
            f"{BASE}/documentos/{env['doc']}/anotacao",
            json={"spans": [MULTA], "status": "done"},
        )

    par = client.get(f"{BASE}/progresso").json()["concordancia"][0]
    assert par["documentos_comuns"] == 1
    assert par["f1"] == 1.0


def test_concordancia_zero_quando_rotulos_divergem(env):
    client, holder = env["client"], env["holder"]
    holder.user = env["eduardo"]
    client.put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [MULTA], "status": "done"},
    )
    holder.user = env["isabella"]
    client.put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [{**MULTA, "label": "OBRIGACAO"}], "status": "done"},
    )

    assert client.get(f"{BASE}/progresso").json()["concordancia"][0]["f1"] == 0.0


# ----- export ----------------------------------------------------------------


def test_export_no_formato_do_corpus(env):
    client, holder = env["client"], env["holder"]
    holder.user = env["eduardo"]
    client.put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [MULTA], "status": "done"},
    )

    holder.user = env["admin"]
    doc = client.get(f"{BASE}/export", params={"anotador": "eduardo"}).json()[0]
    assert doc["id"] == 42  # IdExterno do corpus, não o id interno
    assert doc["text"] == TEXTO
    assert len(doc["tokens"]) == len(doc["ner_tags"]) == len(doc["token_offsets"])
    assert doc["entities"] == [MULTA]

    # BIO: o primeiro token do span recebe B-, os seguintes I-.
    marcados = [t for t in doc["ner_tags"] if t != "O"]
    assert marcados[0] == "B-MULTA"
    assert set(marcados[1:]) <= {"I-MULTA"}

    # offsets reconstroem o token a partir do texto
    for token, (ini, fim) in zip(doc["tokens"], doc["token_offsets"]):
        assert TEXTO[ini:fim] == token


def test_export_ignora_pendentes(env):
    client, holder = env["client"], env["holder"]
    client.put(
        f"{BASE}/documentos/{env['doc']}/anotacao",
        json={"spans": [MULTA], "status": "pending"},
    )
    holder.user = env["admin"]
    assert client.get(f"{BASE}/export", params={"anotador": "isabella"}).json() == []


def test_export_e_restrito_a_admin(env):
    assert env["client"].get(f"{BASE}/export", params={"anotador": "eduardo"}).status_code == 403
