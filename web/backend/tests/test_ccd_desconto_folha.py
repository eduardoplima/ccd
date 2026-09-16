"""Desconto em folha: match automático/manual e listagem.

SQLite em memória com as três tabelas CCDDescontoFolha* e um FRAPLancamento
mínimo. O banco `processo` não entra: os testes cobrem só o lado BdDIP.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.auth.security import hash_password
from app.ccd.desconto_folha import match, notificacao, processo_lookup, service
from app.ccd.desconto_folha.extracao import (
    ParcelaExtraida,
    RespostaDescontoFolha,
    competencias_em_sequencia,
    trecho_confere,
)
from app.ccd.desconto_folha.router import router
from app.ccd.siai_pessoal import service as siai_service
from app.ccd.siai_pessoal.router import router as siai_router
from app.deps import get_arq_pool, get_current_user, get_db_session, get_processo_session

DDL = [
    """CREATE TABLE FRAPLancamento (
        IdLancamento INTEGER PRIMARY KEY AUTOINCREMENT,
        DtMovimento DATE, Historico TEXT, Documento TEXT, Descricao TEXT,
        Valor NUMERIC, ValorDC TEXT, IdCategoria INTEGER
    )""",
    """CREATE TABLE CCDDescontoFolha (
        IdCCDDescontoFolha INTEGER PRIMARY KEY AUTOINCREMENT,
        IdProcesso INTEGER NOT NULL, NumeroProcesso TEXT, AnoProcesso TEXT,
        IdDebito INTEGER, IdPessoa INTEGER, CpfCnpj TEXT, NomePessoa TEXT,
        IdOrgao INTEGER, NomeOrgao TEXT, NumeroNotificacao TEXT, DataNotificacao DATETIME,
        NumeroPostagemAr TEXT, DataAr DATETIME, IdProcessoResposta INTEGER,
        TipoNotificacao TEXT, EventoNotificacao INTEGER, IdEventoNotificacao INTEGER,
        TipoRecebimento TEXT, EventoRecebimento INTEGER, IdEventoRecebimento INTEGER,
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
    app.include_router(siai_router)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_processo_session] = lambda: None  # banco processo fora dos testes

    class _Pool:
        chamadas: list[tuple] = []

        async def enqueue_job(self, funcao: str, *args, **kwargs):
            self.chamadas.append((funcao, args))
            return type("J", (), {"job_id": "arq-1"})()

    pool = _Pool()
    app.dependency_overrides[get_arq_pool] = lambda: pool
    return {"client": TestClient(app), "factory": factory, "pool": pool}


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
        "url": None,  # sem banco processo nos testes
    }
    assert item["ar"]["tipo"] is None and item["notificacao"]["url"] is None
    assert item["valorTotal"] == 2477.35 and item["qtdValores"] == 1
    assert body["totais"] == {
        "cadastros": 1,
        "processos": 1,
        "pessoas": 0,  # seed sem CpfCnpj
        "valorEsperado": 2477.35,
        "valorRecebido": 0.0,
        "valorAReceber": 2477.35,
    }
    env["client"].post("/api/v1/ccd/desconto-folha/1/match-automatico")
    totais = env["client"].get("/api/v1/ccd/desconto-folha").json()["totais"]
    assert totais["valorRecebido"] == 2477.35 and totais["valorAReceber"] == 0.0


def test_sugestoes_e_filtro_por_selecao(env) -> None:
    with env["factory"]() as s:
        s.execute(
            text(
                "INSERT INTO CCDDescontoFolha (IdProcesso, NumeroProcesso, AnoProcesso, NomePessoa,"
                " CpfCnpj, NomeOrgao, DataInclusao)"
                " VALUES (1, '000200', '2024', 'FULANO DE TAL', '11122233344', 'IPERN', '2026-09-15')"
            )
        )
        s.commit()
    base = "/api/v1/ccd/desconto-folha"
    client = env["client"]
    sug = client.get(f"{base}/sugestoes", params={"q": "fula"}).json()
    assert sug == {
        "pessoas": [{"cpf": "11122233344", "nome": "FULANO DE TAL", "qtd": 1}],
        "orgaos": [],
    }
    sug = client.get(f"{base}/sugestoes", params={"q": "111"}).json()  # prefixo de CPF
    assert [p["cpf"] for p in sug["pessoas"]] == ["11122233344"]
    sug = client.get(f"{base}/sugestoes", params={"q": "ipe"}).json()
    assert sug["orgaos"] == [{"nome": "IPERN", "qtd": 1}]
    assert client.get(f"{base}/sugestoes", params={"q": "x"}).status_code == 422
    assert client.get(base, params={"cpf": "11122233344"}).json()["totais"]["pessoas"] == 1
    assert client.get(base, params={"orgao": "SEAD"}).json()["total"] == 1
    assert client.get(base, params={"orgao": "IPERN", "com_valores": "true"}).json()["total"] == 0


def test_listagem_filtra_por_presenca(env) -> None:
    with env["factory"]() as s:
        # cadastro 2: só cadastrado, sem notificação/recebimento/resposta/valores
        s.execute(
            text(
                "INSERT INTO CCDDescontoFolha (IdProcesso, NumeroProcesso, AnoProcesso, "
                "NomePessoa, DataInclusao) VALUES (1, '000200', '2024', 'FULANO', '2026-09-15')"
            )
        )
        s.commit()
    base = "/api/v1/ccd/desconto-folha"
    client = env["client"]
    assert client.get(base).json()["total"] == 2
    for filtro in ("com_notificacao", "com_resposta", "com_valores"):
        body = client.get(base, params={filtro: "true"}).json()
        assert body["total"] == 1 and body["items"][0]["processo"] == "000100/2023", filtro
    assert client.get(base, params={"com_recebimento": "true"}).json()["total"] == 0
    assert client.get(base, params={"com_conciliacao": "true"}).json()["total"] == 0
    client.post(f"{base}/1/match-automatico")
    assert client.get(base, params={"com_conciliacao": "true"}).json()["total"] == 1
    assert client.get(base, params={"com_notificacao": "false"}).json()["total"] == 2


def test_rubrica_tce_so_desconto_tce_frap() -> None:
    assert siai_service.rubrica_tce("2", "FRAP TC")
    assert siai_service.rubrica_tce(2, "Desc. Tribunal de Contas")
    assert not siai_service.rubrica_tce("1", "FRAP TC")  # vantagem
    assert not siai_service.rubrica_tce("2", "VANT TCE")  # devolução de vantagem
    assert not siai_service.rubrica_tce("2", "INSS")
    assert siai_service.rubrica_tce("2", "DESC. PROCESSO Nº 000627/2026-TC")  # sigla TC isolada
    assert not siai_service.rubrica_tce("2", "ATCON")  # TC dentro de palavra
    assert siai_service.rubrica_tce("2", "DESC. PROC. 627/2026", processo="000627/2026")
    assert not siai_service.rubrica_tce("2", "DESC. PROC. 627/2026", processo="000100/2023")


def test_contracheque_endpoint_valida_params_e_responde_vazio_no_sqlite(env) -> None:
    base = "/api/v1/ccd/siai-pessoal/contracheque"
    r = env["client"].get(base, params={"cpf": "31209777487", "ano": 2021, "mes": 1})
    assert r.status_code == 200
    assert r.json() == {"cpf": "31209777487", "nome": None, "ano": 2021, "mes": 1, "folhas": []}
    assert (
        env["client"].get(base, params={"cpf": "31209777487", "ano": 2021, "mes": 13}).status_code
        == 422
    )
    assert env["client"].get(base, params={"cpf": "abc", "ano": 2021, "mes": 1}).status_code == 422


def test_retencoes_vazio_no_sqlite(env) -> None:
    r = env["client"].get("/api/v1/ccd/desconto-folha/retencoes", params={"cpf": "13006444434"})
    assert r.status_code == 200
    assert r.json() == {
        "cpf": "13006444434",
        "total": 0.0,
        "competencias": 0,
        "ultimoAno": None,
        "ultimoMes": None,
    }


def test_recebido_conta_a_mesma_ob_uma_vez(env) -> None:
    """Uma OB vinculada a parcelas de dois cadastros entra uma vez no recebido."""
    base = "/api/v1/ccd/desconto-folha"
    with env["factory"]() as s:
        s.execute(
            text(
                "INSERT INTO CCDDescontoFolha (IdProcesso, NumeroProcesso, AnoProcesso, NomePessoa,"
                " CpfCnpj, DataInclusao) VALUES (2, '000106', '2023', 'NEREU', '13006444434', '2026-09-14')"
            )
        )
        s.execute(
            text(
                "INSERT INTO CCDDescontoFolhaValor (IdCCDDescontoFolha, NumeroParcela, Valor, Origem)"
                " VALUES (2, 1, 2477.35, 'L')"
            )
        )
        s.commit()
    client = env["client"]
    for cadastro in (1, 2):
        client.post(f"{base}/{cadastro}/match-automatico")
    totais = client.get(base).json()["totais"]
    assert totais["valorEsperado"] == 4954.7
    assert totais["valorRecebido"] == 2477.35  # e não 4954.70
    assert totais["valorAReceber"] == 2477.35


def test_mapa_retencoes_vazio_no_sqlite(env) -> None:
    base = "/api/v1/ccd/desconto-folha/retencoes/mapa"
    with env["factory"]() as s:
        s.execute(
            text("UPDATE CCDDescontoFolha SET CpfCnpj = '13006444434' WHERE IdCCDDescontoFolha = 1")
        )
        s.commit()
    r = env["client"].get(base, params={"cpf": "13006444434"})
    assert r.status_code == 200
    body = r.json()
    assert body["nome"] == "NEREU BATISTA LINHARES" and body["meses"] == []
    assert body["totalRetido"] == 0.0 and body["totalConciliado"] == 0.0
    assert env["client"].get(base, params={"cpf": "abc"}).status_code == 422


def test_detalhe_sem_banco_processo_vem_sem_eventos(env) -> None:
    body = env["client"].get("/api/v1/ccd/desconto-folha/1").json()
    assert body["processo"] == "000100/2023" and body["eventosResposta"] == []


def test_eventos_resposta_monta_link_do_econtas(monkeypatch) -> None:
    apensado = [
        {
            "id_evento": 7405613,
            "evento": 3,
            "nome_informacao": "Requerimento.doc",
            "data_resumo": None,
        },
        {"id_evento": 7405612, "evento": 2, "nome_informacao": "Capa.doc", "data_resumo": None},
    ]
    principal = [
        {
            "id_evento": 9001,
            "evento": 149,
            "nome_informacao": "Certidão",
            "resumo": "Certidão",
            "data_resumo": datetime(2026, 3, 10),
        },
        {
            "id_evento": 9000,
            "evento": 147,
            "nome_informacao": "Volume_Digitalizado_TCE.doc",
            "resumo": "Resposta à Comunicação - Notificação nº 000248/2026",
            "data_resumo": datetime(2026, 3, 9),
        },
    ]
    monkeypatch.setattr(
        processo_lookup,
        "apensados",
        lambda _s, _id: [
            {"id_processo": 629445, "numero": "301796", "ano": "2026", "data_registro": None}
        ],
    )
    monkeypatch.setattr(
        processo_lookup,
        "informacoes",
        lambda _s, numero, ano: apensado if numero == "301796" else principal,
    )
    # sem extração (colunas de resposta vazias) os eventos aparecem mesmo assim
    r = {
        "IdProcesso": 619064,
        "NumeroProcesso": "003045",
        "AnoProcesso": "2025",
        "NumeroNotificacao": "000248/2026",
        "DataNotificacao": datetime(2026, 2, 2),
        "IdProcessoResposta": None,
        "NumeroProcessoResposta": None,
        "AnoProcessoResposta": None,
    }
    eventos = service.eventos_resposta(object(), r)  # type: ignore[arg-type]
    assert [(e.processo, e.evento) for e in eventos] == [
        (None, 147),
        ("301796/2026", 2),
        ("301796/2026", 3),
    ]
    assert eventos[1].nome == "Capa"
    assert (
        eventos[1].url
        == "https://processos.tce.rn.gov.br/#/dashboard/processos/629445/autos/evento/7405612"
    )
    assert eventos[0].url.endswith("/processos/619064/autos/evento/9000")
    assert eventos[0].nome == "Volume_Digitalizado_TCE"


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
    # Ligadura "ti" perdida na extração do PDF e citação curta de tabela.
    assert trecho_confere(
        "foi somada à multa instituída no Protocolo SEI n° 00110012.003279/2024-28",
        "foi somada à multa ins tuída no Protocolo SEI n°00110012.003279/2024-28",
    )
    assert trecho_confere(
        "Valor Principal 2.527,70", "Débito\nValor Principal 2.527,70\nJuros 0,00"
    )


# ----- notificação / recebimento ---------------------------------------------


def test_regexes_da_notificacao_e_do_recebimento() -> None:
    assert (
        notificacao.numero_da_notificacao("MANDADO DE NOTIFICAÇÃO 000933/2026 - DE\n")
        == "000933/2026"
    )
    assert (
        notificacao.numero_da_notificacao("\nNOTIFICAÇÃO Nº 001904 / 2025 - DE\n") == "001904/2025"
    )
    assert notificacao.numero_da_notificacao("nada aqui") is None
    assert notificacao.tipo_da_notificacao("(NOVO) 8_Mandado_Notificação", "") == "E"
    assert notificacao.tipo_da_notificacao("NOTIFICAÇÃO PARA DESCONTO EM FOLHA", "") == "F"
    assert (
        notificacao.tipo_da_notificacao("MANDADO_NOTIFICAÇÃO", "responder pelo Portal e-TCE") == "E"
    )
    assert notificacao.data_recebimento(
        "CERTIFICA que a NOTIFICAÇÃO nº. 000933/2026 foi efetiva, tendo sido recebida pelo "
        "destinatário em 08/04/2026 e, por conseguinte,"
    ) == datetime(2026, 4, 8)
    assert notificacao.data_recebimento(
        "CERTIFICA o recebimento tácito da CITAÇÃO nº. 003316/2026 em 15/09/2026, nos termos"
    ) == datetime(2026, 9, 15)
    assert notificacao.data_inicio_prazo(
        "Comunicação NOTIFICAÇÃO 000933/2026\nInicio do prazo 09/04/2026\n"
    ) == datetime(2026, 4, 9)
    assert (
        notificacao.classificar_recebimento("CERTIDÃO DE RECEBIMENTO DE COMUNICAÇÃO ELETRÔNICA")
        == "E"
    )
    assert (
        notificacao.classificar_recebimento("RECEBIMENTO TÁCITO DA COMUNICAÇÃO ELETRÔNICA") == "T"
    )
    assert notificacao.classificar_recebimento("AR_Digitalizado_Retorno") == "AR"
    assert notificacao.classificar_recebimento("Capa.doc") is None


def _info(evento, setor, nome, data, resumo="x", id_evento=None, ordem=None):
    return {
        "id_informacao": 3_000_000 + evento,
        "evento": evento,
        "id_evento": id_evento or 7_000_000 + evento,
        "setor": setor,
        "ordem": ordem or evento + 1,
        "nome_informacao": nome,
        "resumo": resumo,
        "data_resumo": data,
        "Inativa": None,
        "arquivo": f"{setor}_000239_2026_{evento + 1:04d}.pdf",
    }


def test_localizar_acha_mandado_da_de_e_certidao_eletronica(monkeypatch) -> None:
    # 239/2026: despacho da CCD (65), mandado eletrônico da DE (69), certidão de
    # recebimento (70), certidão de decurso da DE_EXP (72) e uma cópia da origem.
    infos = [
        _info(
            10,
            "DAE_SEI",
            "MANDADO_NOTIFICAÇÃO_VIA POSTAL",
            datetime(2020, 1, 1),
            "Evento do Processo Original",
        ),
        _info(
            65,
            "CCD",
            "DESCONTO_EM_FOLHA_Notificação.doc",
            datetime(2026, 3, 27),
            "Determinação para Desconto em Folha...",
        ),
        _info(
            69,
            "DE",
            "(NOVO) 8_Mandado_Notificação",
            datetime(2026, 4, 7),
            "Mandado de Notificação",
            id_evento=7186888,
        ),
        _info(
            70,
            "DE_MANDA",
            "CERTIDÃO DE RECEBIMENTO DE COMUNICAÇÃO ELETRÔNICA",
            datetime(2026, 4, 8),
            "Certidão",
            id_evento=7188408,
        ),
        _info(72, "DE_EXP", "Certidão", datetime(2026, 6, 18), "Certidão"),
    ]
    textos = {
        "DE_000239_2026_0070.pdf": "MANDADO DE NOTIFICAÇÃO 000933/2026 - DE ... Portal e-TCE",
        "DE_MANDA_000239_2026_0071.pdf": "CERTIFICA que a NOTIFICAÇÃO nº. 000933/2026 foi efetiva, tendo sido recebida pelo destinatário em 08/04/2026",
    }
    monkeypatch.setattr(processo_lookup, "informacoes", lambda _s, n, a: infos)
    monkeypatch.setattr(notificacao, "_texto", lambda i: textos.get(i["arquivo"], ""))
    monkeypatch.setattr(notificacao, "_certidao_not", lambda *_a: None)
    monkeypatch.setattr(
        processo_lookup,
        "notificacao",
        lambda *_a, **_k: {
            "numero": None,
            "data": None,
            "id_informacao": None,
            "id_citacao": None,
            "numero_postagem": None,
        },
    )
    monkeypatch.setattr(
        processo_lookup, "ar", lambda *_a, **_k: {"numero_postagem": None, "data": None}
    )

    r = notificacao.localizar(
        object(), id_processo=624864, numero="000239", ano="2026", id_origem=None
    )  # type: ignore[arg-type]
    assert r["NumeroNotificacao"] == "000933/2026"
    assert r["TipoNotificacao"] == "E"
    assert r["DataNotificacao"] == datetime(2026, 4, 7)
    assert (r["EventoNotificacao"], r["IdEventoNotificacao"]) == (69, 7186888)
    assert r["TipoRecebimento"] == "E"
    assert r["DataAr"] == datetime(2026, 4, 8)
    assert (r["EventoRecebimento"], r["IdEventoRecebimento"]) == (70, 7188408)


def test_localizar_cai_na_certidao_not_e_no_inicio_do_prazo(monkeypatch) -> None:
    # fluxo postal antigo sem PDF legível: número vem da Cit_Certidao NOT e o
    # recebimento da certidão da DE_EXP ("Inicio do prazo").
    infos = [
        _info(84, "DAE_MANDA", "NOTIFICAÇÃO PARA DESCONTO EM FOLHA", datetime(2024, 10, 28)),
        _info(90, "DE_EXP", "Processo_certidaodiretoriaexpediente_TCE.doc", datetime(2025, 1, 10)),
    ]
    monkeypatch.setattr(processo_lookup, "informacoes", lambda _s, n, a: infos)
    monkeypatch.setattr(
        notificacao,
        "_texto",
        lambda i: "Inicio do prazo 05/11/2024" if i["setor"] == "DE_EXP" else "",
    )
    monkeypatch.setattr(
        notificacao, "_certidao_not", lambda *_a: ("001940/2024", datetime(2024, 12, 1))
    )
    monkeypatch.setattr(
        processo_lookup,
        "notificacao",
        lambda *_a, **_k: {
            "numero": None,
            "data": None,
            "id_informacao": None,
            "id_citacao": None,
            "numero_postagem": None,
        },
    )
    monkeypatch.setattr(
        processo_lookup, "ar", lambda *_a, **_k: {"numero_postagem": None, "data": None}
    )

    r = notificacao.localizar(object(), id_processo=1, numero="000100", ano="2023", id_origem=None)  # type: ignore[arg-type]
    assert r["NumeroNotificacao"] == "001940/2024"
    assert r["DataNotificacao"] == datetime(2024, 10, 28)  # a data é a do mandado, não da certidão
    assert r["TipoNotificacao"] == "F" and r["EventoNotificacao"] == 84
    assert r["TipoRecebimento"] == "DE" and r["DataAr"] == datetime(2024, 11, 5)


def test_endpoint_localizar_notificacoes_enfileira_job(env) -> None:
    resp = env["client"].post("/api/v1/ccd/desconto-folha/localizar-notificacoes")
    assert resp.status_code == 202
    assert resp.json()["tipo"] == "ccd-desconto-folha-notificacoes"
    assert env["pool"].chamadas[-1][0] == "task_localizar_notificacoes_desconto_folha"


def test_respostas_no_principal_filtra_por_notificacao() -> None:
    dn = datetime(2026, 2, 2, 11, 9)
    infos = [
        {"evento": 40, "resumo": "Certidão", "data_resumo": datetime(2026, 3, 10)},
        {  # resposta a outra notificação, antes da atual
            "evento": 31,
            "resumo": "Resposta à Comunicação - Notificação nº 001330/2025",
            "data_resumo": datetime(2025, 9, 1),
        },
        {  # a resposta certa, em dois PDFs do mesmo evento
            "evento": 39,
            "resumo": "Resposta à Comunicação - Notificação nº 000248/2026",
            "data_resumo": datetime(2026, 3, 9, 10, 51),
        },
        {
            "evento": 39,
            "resumo": "Resposta à Comunicação - Notificação nº 000248/2026",
            "data_resumo": datetime(2026, 3, 9, 10, 52),
        },
    ]
    fontes = processo_lookup.respostas_no_principal(
        infos,
        id_processo=619064,
        numero="003045",
        ano="2025",
        numero_notificacao="000248/2026",
        data_notificacao=dn,
    )
    assert [f["evento"] for f in fontes] == [39]
    assert fontes[0]["numero"] == "003045" and len(fontes[0]["infos"]) == 2
    assert fontes[0]["data_registro"] == datetime(2026, 3, 9, 10, 51)
    # sem número na resposta, vale a data
    infos[1]["resumo"] = "Resposta à Comunicação"
    infos[1]["data_resumo"] = datetime(2026, 3, 20)
    assert sorted(f["evento"] for f in _respostas_sem_numero(infos, dn)) == [31, 39]


def _respostas_sem_numero(infos, dn):
    return processo_lookup.respostas_no_principal(
        infos, id_processo=1, numero="1", ano="2025", numero_notificacao=None, data_notificacao=dn
    )


def test_competencias_em_sequencia_preenche_a_partir_da_primeira() -> None:
    linhas = [
        (1, 11, 2025, 1800.0),
        (2, None, None, 1800.0),
        (3, None, None, 1800.0),
        (4, None, None, 1080.51),
    ]
    assert [(m, a) for _, m, a, _ in competencias_em_sequencia(linhas)] == [
        (11, 2025),
        (12, 2025),
        (1, 2026),
        (2, 2026),
    ]
    # sem nenhuma competência, não inventa
    assert competencias_em_sequencia([(1, None, None, 5.0), (2, None, None, 5.0)]) == [
        (1, None, None, 5.0),
        (2, None, None, 5.0),
    ]


def test_match_automatico_parcelas_iguais_em_ordem_de_data(env) -> None:
    with env["factory"]() as s:
        s.execute(text("DELETE FROM CCDDescontoFolhaValor WHERE IdCCDDescontoFolha = 1"))
        s.execute(
            text(
                "INSERT INTO CCDDescontoFolhaValor (IdCCDDescontoFolha, NumeroParcela, MesReferencia, AnoReferencia, Valor, Origem) VALUES "
                "(1, 1, 2, 2026, 1800, 'L'), (1, 2, 3, 2026, 1800, 'L'), (1, 3, 4, 2026, 1800, 'L'), (1, 4, 5, 2026, 1080.51, 'L')"
            )
        )
        s.execute(
            text(
                "INSERT INTO FRAPLancamento (DtMovimento, Historico, Documento, Descricao, Valor, ValorDC, IdCategoria) VALUES "
                "('2026-05-05', 'Ordem Bancária', 'c', 'ESTADO', 1800, 'C', 1),"
                "('2026-03-03', 'Ordem Bancária', 'a', 'ESTADO', 1800, 'C', 1),"
                "('2026-04-02', 'Ordem Bancária', 'b', 'ESTADO', 1800, 'C', 1),"
                "('2026-01-10', 'Ordem Bancária', 'antes', 'ESTADO', 1800, 'C', 1)"
            )
        )
        s.commit()
        assert match.match_automatico(s, id_cadastro=1) == 3
        docs = s.execute(
            text(
                "SELECT v.NumeroParcela, L.Documento FROM CCDDescontoFolhaValor v "
                "JOIN CCDDescontoFolhaMatch m ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor "
                "JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamentoFRAP ORDER BY v.NumeroParcela"
            )
        ).all()
        assert [tuple(r) for r in docs] == [(1, "a"), (2, "b"), (3, "c")]  # 1.080,51 fica sem match


def test_texto_padrao_orgao() -> None:
    assert service.texto_padrao_orgao("PREFEITURA MUNICIPAL DE LAJES") == "LAJES"
    assert service.texto_padrao_orgao("CÂMARA MUNICIPAL DE FRUTUOSO GOMES") == "FRUTUOSO"
    assert service.texto_padrao_orgao("ALRN") == "ASSEMBL"
    assert service.texto_padrao_orgao("IPERN") == "ESTADO"
    assert service.texto_padrao_orgao("SEEC/RN") == "ESTADO"
    assert service.texto_padrao_orgao(None) is None


def test_creditos_frap_filtra_e_sinaliza_vinculado(env) -> None:
    client = env["client"]
    with env["factory"]() as s:
        s.execute(
            text(
                "INSERT INTO FRAPLancamento (DtMovimento, Historico, Documento, Descricao, Valor, ValorDC, IdCategoria) VALUES "
                "('2026-03-03', 'Ordem Bancária', 'a', 'ESTADO DO RIO GRANDE D', 1800, 'C', 1),"
                "('2026-04-02', 'Ordem Bancária', 'b', 'ESTADO DO RIO GRANDE D', 1800, 'C', 1),"
                "('2026-04-22', 'Transferência recebida', 'c', '22/04 PM LAJES C MOVIMENTO', 434.34, 'C', 3),"
                "('2026-04-30', 'Tarifa', 'd', 'ESTADO DO RIO GRANDE D', 1800, 'D', 9)"
            )
        )
        s.execute(
            text(
                "UPDATE CCDDescontoFolha SET NomeOrgao = 'IPERN', DataNotificacao = '2026-02-02' "
                "WHERE IdCCDDescontoFolha = 1"
            )
        )
        s.commit()
    # o crédito de 2.477,35 (id 1) já está vinculado ao valor 1 do cadastro 1
    client.post("/api/v1/ccd/desconto-folha/1/valores/1/match", json={"idLancamento": 1})

    r = client.get("/api/v1/ccd/desconto-folha/1/frap-creditos").json()
    assert r["texto"] == "ESTADO" and r["desde"] == "2026-02-02"
    assert r["items"] == [] and "valor da parcela" in r["aviso"]  # Estado sem valor = ruído

    r = client.get("/api/v1/ccd/desconto-folha/1/frap-creditos", params={"valor": 1800}).json()
    assert r["aviso"] is None
    assert [i["documento"] for i in r["items"]] == ["a", "b"]  # débito e Lajes fora

    r = client.get("/api/v1/ccd/desconto-folha/1/frap-creditos", params={"texto": "LAJES"}).json()
    assert [i["valor"] for i in r["items"]] == [434.34]

    r = client.get(
        "/api/v1/ccd/desconto-folha/1/frap-creditos",
        params={"texto": "", "desde": "2025-01-01", "valor": 2477.35},
    ).json()
    assert [(i["documento"], i["idCadastroVinculado"]) for i in r["items"]] == [
        ("202.506.040.011.394", 1)
    ]


def test_adotar_cria_valores_vinculados(env) -> None:
    client = env["client"]
    with env["factory"]() as s:
        s.execute(
            text(
                "INSERT INTO FRAPLancamento (DtMovimento, Historico, Documento, Descricao, Valor, ValorDC, IdCategoria) VALUES "
                "('2026-03-03', 'Ordem Bancária', 'a', 'ESTADO DO RIO GRANDE D', 1800, 'C', 1),"
                "('2026-04-02', 'Ordem Bancária', 'b', 'ESTADO DO RIO GRANDE D', 1800, 'C', 1)"
            )
        )
        s.commit()
    ids = [4, 5]
    resp = client.post("/api/v1/ccd/desconto-folha/1/frap-creditos", json={"idsLancamento": ids})
    assert resp.status_code == 200
    novos = [v for v in resp.json()["valores"] if v["origem"] == "M"]
    assert [(v["numeroParcela"], v["mes"], v["ano"], v["valor"]) for v in novos] == [
        (2, 3, 2026, 1800.0),
        (3, 4, 2026, 1800.0),
    ]
    assert all(v["match"] and v["match"]["automatico"] is False for v in novos)
    assert novos[0]["match"]["lancamento"]["documento"] == "a"
    # adotar de novo não duplica (já vinculados)
    resp = client.post("/api/v1/ccd/desconto-folha/1/frap-creditos", json={"idsLancamento": ids})
    assert len([v for v in resp.json()["valores"] if v["origem"] == "M"]) == 2
    assert client.get("/api/v1/ccd/desconto-folha").json()["items"][0]["qtdMatches"] == 2


def test_parcela_sem_valor_nao_derruba_a_extracao() -> None:
    # a LLM devolve parcelas com valor nulo em respostas que só listam competências
    r = RespostaDescontoFolha.model_validate(
        {
            "encontrou": True,
            "parcelado": True,
            "parcelas": [{"numero": 1, "valor": None}, {"numero": 2, "valor": 10}],
        }
    )
    assert [p.valor for p in r.parcelas] == [None, 10.0]
    assert ParcelaExtraida(numero=1).valor is None
