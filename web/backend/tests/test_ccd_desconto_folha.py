"""Desconto em folha: match automático/manual e listagem.

SQLite em memória com as três tabelas CCDDescontoFolha* e um FRAPLancamento
mínimo. O banco `processo` não entra: os testes cobrem só o lado BdDIP.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.auth.security import hash_password
from app.ccd.desconto_folha import match
from app.ccd.desconto_folha.extracao import trecho_confere
from app.ccd.desconto_folha.router import router
from app.deps import get_current_user, get_db_session

DDL = [
    """CREATE TABLE FRAPLancamento (
        IdLancamento INTEGER PRIMARY KEY AUTOINCREMENT,
        DtMovimento DATE, Historico TEXT, Documento TEXT,
        Valor NUMERIC, ValorDC TEXT, IdCategoria INTEGER
    )""",
    """CREATE TABLE CCDDescontoFolha (
        IdCCDDescontoFolha INTEGER PRIMARY KEY AUTOINCREMENT,
        IdProcesso INTEGER NOT NULL, NumeroProcesso TEXT, AnoProcesso TEXT,
        IdDebito INTEGER, IdPessoa INTEGER, CpfCnpj TEXT, NomePessoa TEXT,
        IdOrgao INTEGER, NomeOrgao TEXT, NumeroNotificacao TEXT, DataNotificacao DATETIME,
        NumeroPostagemAr TEXT, DataAr DATETIME, IdProcessoResposta INTEGER,
        NumeroProcessoResposta TEXT, AnoProcessoResposta TEXT, EventoResposta INTEGER,
        DataResposta DATETIME, ArquivoResposta TEXT, TrechoResposta TEXT,
        ValorTotal NUMERIC, Parcelado INTEGER DEFAULT 0, DataExtracao DATETIME,
        StatusExtracao TEXT DEFAULT 'PENDENTE', Observacoes TEXT, Ativo INTEGER DEFAULT 1,
        DataInclusao DATETIME, DataAtualizacao DATETIME, IdUsuario INTEGER
    )""",
    """CREATE TABLE CCDDescontoFolhaValor (
        IdCCDDescontoFolhaValor INTEGER PRIMARY KEY AUTOINCREMENT,
        IdCCDDescontoFolha INTEGER NOT NULL, NumeroParcela INTEGER DEFAULT 1,
        MesReferencia INTEGER, AnoReferencia INTEGER, Valor NUMERIC NOT NULL, Origem TEXT
    )""",
    """CREATE TABLE CCDDescontoFolhaMatch (
        IdCCDDescontoFolhaMatch INTEGER PRIMARY KEY AUTOINCREMENT,
        IdCCDDescontoFolhaValor INTEGER NOT NULL UNIQUE, IdLancamentoFRAP INTEGER NOT NULL,
        Automatico INTEGER DEFAULT 0, IdUsuario INTEGER, DataMatch DATETIME, Observacao TEXT
    )""",
]

SEED = [
    # cadastro 1: 100/2023, resposta em 300031/2025 registrada em 07/01/2025
    """INSERT INTO CCDDescontoFolha (IdProcesso, NumeroProcesso, AnoProcesso, IdDebito, NomePessoa,
        NomeOrgao, NumeroNotificacao, NumeroProcessoResposta, AnoProcessoResposta, EventoResposta,
        DataResposta, StatusExtracao, ValorTotal, DataInclusao)
       VALUES (576955, '000100', '2023', 23056, 'NEREU BATISTA LINHARES', 'SEAD', '001940/2024',
        '300031', '2025', 87, '2025-01-07', 'OK', 2477.35, '2026-09-14')""",
    "INSERT INTO CCDDescontoFolhaValor (IdCCDDescontoFolha, NumeroParcela, Valor, Origem) VALUES (1, 1, 2477.35, 'L')",
    # crédito único de 2.477,35 depois da resposta; um débito e um crédito antigo como ruído
    "INSERT INTO FRAPLancamento (DtMovimento, Historico, Documento, Valor, ValorDC, IdCategoria) VALUES ('2025-06-05', 'Ordem Bancária', '202.506.040.011.394', 2477.35, 'C', 1)",
    "INSERT INTO FRAPLancamento (DtMovimento, Historico, Documento, Valor, ValorDC, IdCategoria) VALUES ('2025-06-06', 'Tarifa', 'x', 2477.35, 'D', 9)",
    "INSERT INTO FRAPLancamento (DtMovimento, Historico, Documento, Valor, ValorDC, IdCategoria) VALUES ('2024-03-01', 'OB antiga', 'y', 2477.35, 'C', 1)",
]


@pytest.fixture
def env(in_memory_engine: Engine):
    with in_memory_engine.begin() as conn:
        for ddl in DDL:
            conn.execute(text(ddl))
        for seed in SEED:
            conn.execute(text(seed))
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
    return {"client": TestClient(app), "factory": factory}


def test_match_automatico_vincula_candidato_unico(env) -> None:
    with env["factory"]() as s:
        assert match.match_automatico(s, id_cadastro=1) == 1
        row = s.execute(
            text("SELECT IdLancamentoFRAP, Automatico FROM CCDDescontoFolhaMatch")
        ).first()
    assert row is not None and (int(row[0]), int(row[1])) == (1, 1)


def test_match_automatico_nao_vincula_com_dois_candidatos(env) -> None:
    with env["factory"]() as s:
        s.execute(
            text(
                "INSERT INTO FRAPLancamento (DtMovimento, Historico, Documento, Valor, ValorDC, IdCategoria) "
                "VALUES ('2025-07-05', 'Outra OB', 'z', 2477.35, 'C', 3)"
            )
        )
        s.commit()
        assert match.match_automatico(s, id_cadastro=1) == 0
    detalhe = env["client"].get("/api/v1/ccd/desconto-folha/1").json()
    valor = detalhe["valores"][0]
    assert valor["match"] is None
    assert [c["idLancamento"] for c in valor["candidatos"]] == [1, 4]


def test_vincular_e_desvincular_manual(env) -> None:
    client = env["client"]
    resp = client.post(
        "/api/v1/ccd/desconto-folha/1/valores/1/match", json={"idLancamento": 1, "observacao": "ok"}
    )
    assert resp.status_code == 200
    m = resp.json()["valores"][0]["match"]
    assert m["automatico"] is False and m["lancamento"]["documento"] == "202.506.040.011.394"
    assert client.get("/api/v1/ccd/desconto-folha").json()["items"][0]["qtdMatches"] == 1

    resp = client.delete("/api/v1/ccd/desconto-folha/1/valores/1/match")
    assert resp.status_code == 200 and resp.json()["valores"][0]["match"] is None
    assert (
        client.post(
            "/api/v1/ccd/desconto-folha/1/valores/1/match", json={"idLancamento": 999}
        ).status_code
        == 404
    )


def test_listagem_monta_colunas(env) -> None:
    body = env["client"].get("/api/v1/ccd/desconto-folha", params={"q": "100/2023"}).json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["processo"] == "000100/2023"
    assert item["orgao"] == "SEAD"
    assert item["responsavel"] == "NEREU BATISTA LINHARES"
    assert item["notificacao"]["numero"] == "001940/2024"
    assert item["ar"]["numeroPostagem"] is None
    assert item["resposta"] == {
        "processo": "300031/2025",
        "evento": 87,
        "data": "2025-01-07T00:00:00",
    }
    assert item["valorTotal"] == 2477.35 and item["qtdValores"] == 1


def test_valor_manual_reseta_match(env) -> None:
    client = env["client"]
    client.post("/api/v1/ccd/desconto-folha/1/valores/1/match", json={"idLancamento": 1})
    resp = client.patch(
        "/api/v1/ccd/desconto-folha/1/valores/1", json={"numeroParcela": 1, "valor": 1000}
    )
    assert resp.status_code == 200
    v = resp.json()["valores"][0]
    assert v["origem"] == "M" and v["match"] is None and v["candidatos"] == []


def test_trecho_confere_tolera_ligaduras_e_espacos() -> None:
    texto = "…as multas foram somadas, totalizando um montante de\nR$2.477,35, desconto este que fora implantado na integralidade…"
    assert trecho_confere(
        "totalizando um montante de R$2.477,35, desconto este que fora implantado", texto
    )
    assert not trecho_confere(
        "totalizando um montante de R$9.999,99, valor inventado pela LLM", texto
    )
    assert not trecho_confere("curto", texto)
