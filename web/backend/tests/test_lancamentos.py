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
from app.lancamentos.router import router as lanc_router

DDL = [
    """CREATE TABLE FRAPConta (
        IdConta INTEGER PRIMARY KEY AUTOINCREMENT,
        Banco INTEGER, Agencia TEXT, Conta TEXT, Descricao TEXT
    )""",
    """CREATE TABLE FRAPCategoria (
        IdCategoria INTEGER PRIMARY KEY,
        Codigo TEXT, Descricao TEXT
    )""",
    """CREATE TABLE FRAPStatusMatch (
        IdStatusMatch INTEGER PRIMARY KEY,
        Codigo TEXT, Matcher TEXT, Descricao TEXT
    )""",
    """CREATE TABLE FRAPExtratoArquivo (
        IdArquivo INTEGER PRIMARY KEY AUTOINCREMENT,
        IdConta INTEGER, Periodo TEXT, NomeArquivo TEXT,
        HashSha256 TEXT, QtdLancamentos INTEGER
    )""",
    """CREATE TABLE FRAPLancamento (
        IdLancamento INTEGER PRIMARY KEY AUTOINCREMENT,
        IdArquivo INTEGER, IdConta INTEGER, Periodo TEXT,
        OrdemNoArquivo INTEGER, DtMovimento DATE, DtBalancete DATE,
        AgOrigem TEXT, Lote TEXT, Historico TEXT, Documento TEXT, DocData DATE,
        Valor NUMERIC, ValorDC TEXT, Descricao TEXT,
        IdCategoria INTEGER, CpfCnpjDepositante TEXT, CpfCnpjAmbiguo INTEGER DEFAULT 0
    )""",
    """CREATE TABLE FRAPMatchOB (
        IdMatchOB INTEGER PRIMARY KEY AUTOINCREMENT,
        IdLancamento INTEGER, IdConta INTEGER, Periodo TEXT, AnoSigef INTEGER,
        CdUnidadeGestora INTEGER, CdGestao INTEGER, NuOrdemBancaria TEXT,
        DataPagamento DATE, ValorOB NUMERIC, CdCredor TEXT, NmCredor TEXT,
        NuPreparacaoPagamento TEXT, NuNotaEmpenho TEXT, IdStatusMatch INTEGER
    )""",
    """CREATE TABLE FRAPMatchPessoa (
        IdMatchPessoa INTEGER PRIMARY KEY AUTOINCREMENT,
        IdLancamento INTEGER, IdConta INTEGER, Periodo TEXT,
        IdDebito INTEGER, IdProcessoExecucao INTEGER, CpfCnpj TEXT, NomePessoa TEXT,
        ValorPago NUMERIC, ValorAPagar NUMERIC, ValorOriginalDebito NUMERIC,
        ValorCasadoEm TEXT, IdStatusMatch INTEGER
    )""",
    """CREATE TABLE FRAPMatchGuia (
        IdMatchGuia INTEGER PRIMARY KEY AUTOINCREMENT,
        IdLancamento INTEGER, IdConta INTEGER, Periodo TEXT,
        IdBoleto INTEGER, IdDebito INTEGER, IdProcessoExecucao INTEGER,
        CodigoBarras TEXT, DataPagamento DATE, ValorPago NUMERIC,
        NomePessoa TEXT, CpfCnpj TEXT, IdStatusMatch INTEGER
    )""",
    """CREATE TABLE FRAPDescontoFolha (
        IdFRAPDescontoFolha INTEGER PRIMARY KEY AUTOINCREMENT,
        CpfCnpj TEXT, NomePessoa TEXT
    )""",
    """CREATE TABLE FRAPDescontoFolhaParcela (
        IdFRAPDescontoFolhaParcela INTEGER PRIMARY KEY AUTOINCREMENT,
        IdFRAPDescontoFolha INTEGER, NumeroParcela INTEGER,
        MesReferencia INTEGER, AnoReferencia INTEGER, ValorEsperado NUMERIC
    )""",
    """CREATE TABLE FRAPMatchDescontoFolha (
        IdMatchDescontoFolha INTEGER PRIMARY KEY AUTOINCREMENT,
        IdFRAPDescontoFolhaParcela INTEGER, IdContraChequeItem INTEGER,
        IdRubrica INTEGER, ValorContracheque NUMERIC,
        IdLancamentoFRAP INTEGER, IdStatusMatch INTEGER
    )""",
]

SEED_LOOKUPS = [
    "INSERT INTO FRAPConta (IdConta, Banco, Agencia, Conta, Descricao) VALUES (1, 1, '3795-8', '700000-6', 'TCE RN FRAP')",
    "INSERT INTO FRAPCategoria (IdCategoria, Codigo) VALUES (1, 'OB_RECEBIDA')",
    "INSERT INTO FRAPCategoria (IdCategoria, Codigo) VALUES (2, 'GUIA_RECEBIMENTO')",
    "INSERT INTO FRAPStatusMatch (IdStatusMatch, Codigo, Matcher, Descricao) VALUES (10, 'EXATO', 'OB', 'OB casa')",
    "INSERT INTO FRAPStatusMatch (IdStatusMatch, Codigo, Matcher, Descricao) VALUES (20, 'EXATO_PESSOA_VALOR', 'PESSOA', 'pessoa casa')",
    "INSERT INTO FRAPStatusMatch (IdStatusMatch, Codigo, Matcher, Descricao) VALUES (35, 'EXATO_LOTE', 'GUIA', 'lote casa')",
    "INSERT INTO FRAPStatusMatch (IdStatusMatch, Codigo, Matcher, Descricao) VALUES (40, 'OK_TUDO', 'DESCONTO_FOLHA', 'tudo bate')",
    "INSERT INTO FRAPExtratoArquivo (IdArquivo, IdConta, Periodo, NomeArquivo, QtdLancamentos) VALUES (1, 1, '042026', '042026.txt', 2)",
]


@pytest.fixture
def client_with_data(in_memory_engine: Engine) -> Iterator[TestClient]:
    with in_memory_engine.begin() as conn:
        for ddl in DDL:
            conn.execute(text(ddl))
        for seed in SEED_LOOKUPS:
            conn.execute(text(seed))

    factory = sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)

    with factory() as seed:
        seed.add(
            FRAPUsuario(
                Login="u1",
                Email="u@tce.rn",
                NomeCompleto="User",
                SenhaHash=hash_password("x"),
                Papel="user",
                Ativo=True,
            )
        )
        seed.commit()
        admin = seed.query(FRAPUsuario).one()

    def override_db() -> Iterator[Session]:
        s = factory()
        try:
            yield s
        finally:
            s.close()

    def override_user() -> FRAPUsuario:
        return admin

    app = FastAPI()
    app.include_router(lanc_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as c:
        yield c


def _insert_lancamento(engine: Engine, **kw) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """INSERT INTO FRAPLancamento
                   (IdArquivo, IdConta, Periodo, OrdemNoArquivo, DtMovimento, Historico,
                    Documento, Valor, ValorDC, IdCategoria, CpfCnpjDepositante)
                   VALUES (1, 1, '042026', :ordem, :dt, :hist, :doc, :valor, :dc, :cat, :cpf)
                """
            ),
            kw,
        )
        return result.lastrowid  # type: ignore[return-value]


def test_listar_sem_lancamentos_retorna_vazio(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/lancamentos")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_listar_inclui_matches_resumo(
    client_with_data: TestClient, in_memory_engine: Engine
) -> None:
    id_lanc = _insert_lancamento(
        in_memory_engine,
        ordem=1,
        dt="2026-04-15",
        hist="Ordem Bancária",
        doc="2026OB001",
        valor=1000,
        dc="C",
        cat=1,
        cpf=None,
    )
    with in_memory_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO FRAPMatchOB (IdLancamento, IdConta, Periodo, AnoSigef, NuOrdemBancaria, ValorOB, IdStatusMatch) VALUES (:l, 1, '042026', 2026, '2026OB001', 1000, 10)"
            ),
            {"l": id_lanc},
        )

    r = client_with_data.get("/api/v1/lancamentos")
    assert r.status_code == 200
    item = r.json()["items"][0]
    assert item["matchesResumo"] == [{"matcher": "OB", "status": "EXATO", "quantidade": 1}]


def test_listar_filtro_valor_range(client_with_data: TestClient, in_memory_engine: Engine) -> None:
    for valor in (50, 150, 500, 1500):
        _insert_lancamento(
            in_memory_engine,
            ordem=valor,
            dt="2026-04-15",
            hist="X",
            doc="X",
            valor=valor,
            dc="C",
            cat=1,
            cpf=None,
        )

    r = client_with_data.get("/api/v1/lancamentos", params={"valor_min": 100, "valor_max": 1000})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert sorted(float(it["valor"]) for it in body["items"]) == [150.0, 500.0]

    r = client_with_data.get("/api/v1/lancamentos", params={"valor_min": 500})
    assert r.json()["total"] == 2

    r = client_with_data.get("/api/v1/lancamentos", params={"valor_max": 100})
    assert r.json()["total"] == 1

    r = client_with_data.get("/api/v1/lancamentos", params={"valor_min": 1000, "valor_max": 500})
    assert r.status_code == 400


def test_detalhe_404_quando_inexistente(client_with_data: TestClient) -> None:
    r = client_with_data.get("/api/v1/lancamentos/9999")
    assert r.status_code == 404


def test_detalhe_agrega_quatro_matchers(
    client_with_data: TestClient, in_memory_engine: Engine
) -> None:
    id_lanc = _insert_lancamento(
        in_memory_engine,
        ordem=1,
        dt="2026-04-15",
        hist="Recebimentos Diversos",
        doc="X",
        valor=500,
        dc="C",
        cat=2,
        cpf="00394544012787",
    )
    with in_memory_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO FRAPMatchOB (IdLancamento, IdConta, Periodo, AnoSigef, NuOrdemBancaria, ValorOB, IdStatusMatch) VALUES (:l, 1, '042026', 2026, '2026OB777', 500, 10)"
            ),
            {"l": id_lanc},
        )
        conn.execute(
            text(
                "INSERT INTO FRAPMatchPessoa (IdLancamento, IdConta, Periodo, CpfCnpj, NomePessoa, ValorPago, IdStatusMatch) VALUES (:l, 1, '042026', '00394544012787', 'Min Saude', 500, 20)"
            ),
            {"l": id_lanc},
        )
        conn.execute(
            text(
                "INSERT INTO FRAPMatchGuia (IdLancamento, IdConta, Periodo, CodigoBarras, ValorPago, IdStatusMatch) VALUES (:l, 1, '042026', '12345', 500, 35)"
            ),
            {"l": id_lanc},
        )
        conn.execute(
            text(
                "INSERT INTO FRAPDescontoFolha (IdFRAPDescontoFolha, CpfCnpj, NomePessoa) VALUES (1, '00394544012787', 'Servidor')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO FRAPDescontoFolhaParcela (IdFRAPDescontoFolhaParcela, IdFRAPDescontoFolha, NumeroParcela, MesReferencia, AnoReferencia, ValorEsperado) VALUES (1, 1, 3, 4, 2026, 500)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO FRAPMatchDescontoFolha (IdFRAPDescontoFolhaParcela, IdLancamentoFRAP, ValorContracheque, IdStatusMatch) VALUES (1, :l, 500, 40)"
            ),
            {"l": id_lanc},
        )

    r = client_with_data.get(f"/api/v1/lancamentos/{id_lanc}")
    assert r.status_code == 200, r.json()
    body = r.json()
    matchers = sorted(m["matcher"] for m in body["matches"])
    assert matchers == ["DESCONTO_FOLHA", "GUIA", "OB", "PESSOA"]
    by_matcher = {m["matcher"]: m for m in body["matches"]}
    assert by_matcher["OB"]["nuOrdemBancaria"] == "2026OB777"
    assert by_matcher["PESSOA"]["nomePessoa"] == "Min Saude"
    assert by_matcher["GUIA"]["codigoBarras"] == "12345"
    assert by_matcher["DESCONTO_FOLHA"]["numeroParcela"] == 3
