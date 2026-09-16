"""Cadastro do desconto em folha (BdDIP) e leitura do que vem do banco `processo`.

SQL cru via `text()`, sem ORM — as três tabelas CCDDescontoFolha* têm
poucas colunas e as consultas precisam rodar também no SQLite dos testes.
"""

from __future__ import annotations

import logging
import unicodedata
from datetime import date, datetime
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.desconto_folha import match, notificacao, processo_lookup, schemas
from app.ccd.siai_pessoal.service import retencoes_detalhadas, valores_tce_por_competencia

logger = logging.getLogger(__name__)

# Rota do e-Contas que abre os autos já posicionados no evento (idEvento =
# Pro_ProcessoEvento.IdProcessoEvento). Os PDFs em si só existem como URL
# temporária (VisualizacaoTempAR / consultaprocessotemp), não dá para linkar.
ECONTAS_AUTOS_EVENTO = (
    "https://processos.tce.rn.gov.br/#/dashboard/processos/{id_processo}/autos/evento/{id_evento}"
)


def _agora() -> datetime:
    return datetime.utcnow().replace(microsecond=0)


def _paginacao(session: Session) -> str:
    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    return (
        "LIMIT :size OFFSET :offset"
        if dialect == "sqlite"
        else "OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY"
    )


def _processo(numero: Any, ano: Any) -> Optional[str]:
    if not numero or not ano:
        return None
    return f"{str(numero).strip()}/{str(ano).strip()}"


def _url_evento(id_processo: Any, id_evento: Any) -> Optional[str]:
    if not id_processo or not id_evento:
        return None
    return ECONTAS_AUTOS_EVENTO.format(id_processo=int(id_processo), id_evento=int(id_evento))


def _item(r: dict[str, Any]) -> schemas.CadastroListItem:
    return schemas.CadastroListItem(
        id=int(r["IdCCDDescontoFolha"]),
        id_processo=int(r["IdProcesso"]),
        processo=_processo(r["NumeroProcesso"], r["AnoProcesso"]) or str(r["IdProcesso"]),
        id_debito=r["IdDebito"],
        id_pessoa=r["IdPessoa"],
        cpf_cnpj=r["CpfCnpj"],
        responsavel=r["NomePessoa"],
        id_orgao=r["IdOrgao"],
        orgao=r["NomeOrgao"],
        notificacao=schemas.NotificacaoOut(
            numero=r["NumeroNotificacao"],
            data=r["DataNotificacao"],
            tipo=r.get("TipoNotificacao"),
            evento=r.get("EventoNotificacao"),
            url=_url_evento(r["IdProcesso"], r.get("IdEventoNotificacao")),
        ),
        ar=schemas.ArOut(
            numero_postagem=r["NumeroPostagemAr"],
            data=r["DataAr"],
            tipo=r.get("TipoRecebimento"),
            evento=r.get("EventoRecebimento"),
            url=_url_evento(r["IdProcesso"], r.get("IdEventoRecebimento")),
        ),
        resposta=schemas.RespostaOut(
            processo=_processo(r["NumeroProcessoResposta"], r["AnoProcessoResposta"]),
            evento=r["EventoResposta"],
            data=r["DataResposta"],
        ),
        status_extracao=r["StatusExtracao"],
        valor_total=float(r["ValorTotal"]) if r["ValorTotal"] is not None else None,
        parcelado=bool(r["Parcelado"]),
        qtd_valores=int(r.get("QtdValores") or 0),
        qtd_matches=int(r.get("QtdMatches") or 0),
    )


_SQL_BASE = """
SELECT c.*,
       (SELECT COUNT(*) FROM CCDDescontoFolhaValor v
         WHERE v.IdCCDDescontoFolha = c.IdCCDDescontoFolha) AS QtdValores,
       (SELECT COUNT(*) FROM CCDDescontoFolhaValor v
         JOIN CCDDescontoFolhaMatch m ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
         WHERE v.IdCCDDescontoFolha = c.IdCCDDescontoFolha) AS QtdMatches
FROM CCDDescontoFolha c
"""


_FILTROS_PRESENCA = {
    "com_notificacao": "(c.NumeroNotificacao IS NOT NULL OR c.DataNotificacao IS NOT NULL)",
    "com_recebimento": "(c.DataAr IS NOT NULL OR c.TipoRecebimento IS NOT NULL)",
    "com_resposta": "(c.NumeroProcessoResposta IS NOT NULL OR c.DataResposta IS NOT NULL)",
    "com_valores": (
        "EXISTS (SELECT 1 FROM CCDDescontoFolhaValor v"
        " WHERE v.IdCCDDescontoFolha = c.IdCCDDescontoFolha)"
    ),
    "com_conciliacao": (
        "EXISTS (SELECT 1 FROM CCDDescontoFolhaValor v"
        " JOIN CCDDescontoFolhaMatch m ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor"
        " WHERE v.IdCCDDescontoFolha = c.IdCCDDescontoFolha)"
    ),
}


def _totais(session: Session, where: str, params: dict[str, Any]) -> schemas.TotaisOut:
    """Totais do mesmo recorte da lista.

    Esperado por cadastro: as parcelas da resposta do órgão (CCDDescontoFolhaValor) quando
    existem; senão o saldo do débito enviado (valorOriginalDebito − ValorPago, do banco
    processo). Recebido = soma dos lançamentos do FRAP vinculados, cada um UMA vez (a mesma OB
    pode estar vinculada a parcelas de dois processos: IPERN/Nereu, L2105 em 03/2025); a receber
    = esperado − recebido. No SQLite dos testes não há banco processo: só a via das parcelas.
    """
    c = (
        session.execute(
            text(
                "SELECT COUNT(*) AS cadastros, COUNT(DISTINCT c.IdProcesso) AS processos,"
                f" COUNT(DISTINCT c.CpfCnpj) AS pessoas FROM CCDDescontoFolha c {where}"
            ),
            params,
        )
        .mappings()
        .one()
    )
    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    join_debito, saldo_debito = "", "NULL"
    if dialect != "sqlite":
        join_debito = "LEFT JOIN processo.dbo.Exe_Debito d ON d.IdDebito = c.IdDebito"
        saldo_debito = (
            "CASE WHEN d.valorOriginalDebito - COALESCE(d.ValorPago, 0) > 0"
            " THEN d.valorOriginalDebito - COALESCE(d.ValorPago, 0) ELSE 0 END"
        )
    esperado = float(
        session.execute(
            text(
                f"""
                SELECT COALESCE(SUM(COALESCE(p.esperado, {saldo_debito}, 0)), 0)
                FROM CCDDescontoFolha c
                LEFT JOIN (
                    SELECT v.IdCCDDescontoFolha, SUM(v.Valor) AS esperado
                    FROM CCDDescontoFolhaValor v GROUP BY v.IdCCDDescontoFolha
                ) p ON p.IdCCDDescontoFolha = c.IdCCDDescontoFolha
                {join_debito}
                {where}
                """
            ),
            params,
        ).scalar_one()
        or 0
    )
    recebido = float(
        session.execute(
            text(
                f"""
                SELECT COALESCE(SUM(L.Valor), 0) FROM FRAPLancamento L
                WHERE L.IdLancamento IN (
                    SELECT m.IdLancamentoFRAP
                    FROM CCDDescontoFolhaMatch m
                    JOIN CCDDescontoFolhaValor v
                      ON v.IdCCDDescontoFolhaValor = m.IdCCDDescontoFolhaValor
                    JOIN CCDDescontoFolha c ON c.IdCCDDescontoFolha = v.IdCCDDescontoFolha
                    {where}
                )
                """
            ),
            params,
        ).scalar_one()
        or 0
    )
    return schemas.TotaisOut(
        cadastros=int(c["cadastros"]),
        processos=int(c["processos"]),
        pessoas=int(c["pessoas"]),
        valor_esperado=round(esperado, 2),
        valor_recebido=round(recebido, 2),
        valor_a_receber=round(esperado - recebido, 2),
    )


def sugestoes(session: Session, q: str) -> schemas.SugestoesOut:
    """Pessoas (nome ou CPF) e órgãos com cadastro ativo cujo texto contém q (universo da tela)."""
    like, prefixo = f"%{q.strip()}%", f"{q.strip()}%"
    pessoas = (
        session.execute(
            text(
                "SELECT c.CpfCnpj AS cpf, MAX(c.NomePessoa) AS nome, COUNT(*) AS qtd"
                " FROM CCDDescontoFolha c WHERE c.Ativo = 1 AND c.CpfCnpj IS NOT NULL"
                " AND (c.NomePessoa LIKE :like OR c.CpfCnpj LIKE :prefixo)"
                " GROUP BY c.CpfCnpj ORDER BY qtd DESC, nome"
            ),
            {"like": like, "prefixo": prefixo},
        )
        .mappings()
        .all()
    )
    orgaos = (
        session.execute(
            text(
                "SELECT c.NomeOrgao AS nome, COUNT(*) AS qtd FROM CCDDescontoFolha c"
                " WHERE c.Ativo = 1 AND c.NomeOrgao LIKE :like"
                " GROUP BY c.NomeOrgao ORDER BY qtd DESC, nome"
            ),
            {"like": like},
        )
        .mappings()
        .all()
    )
    return schemas.SugestoesOut(
        pessoas=[
            schemas.SugestaoPessoa(cpf=str(p["cpf"]), nome=p["nome"], qtd=int(p["qtd"]))
            for p in pessoas[:6]
        ],
        orgaos=[schemas.SugestaoOrgao(nome=str(o["nome"]), qtd=int(o["qtd"])) for o in orgaos[:6]],
    )


def listar(
    session: Session,
    *,
    q: str | None,
    page: int,
    size: int,
    com_notificacao: bool = False,
    com_recebimento: bool = False,
    com_resposta: bool = False,
    com_valores: bool = False,
    com_conciliacao: bool = False,
    cpf: str | None = None,
    orgao: str | None = None,
) -> schemas.CadastroListResponse:
    where = "WHERE c.Ativo = 1"
    params: dict[str, Any] = {}
    ligados = {
        "com_notificacao": com_notificacao,
        "com_recebimento": com_recebimento,
        "com_resposta": com_resposta,
        "com_valores": com_valores,
        "com_conciliacao": com_conciliacao,
    }
    for nome, sql in _FILTROS_PRESENCA.items():
        if ligados[nome]:
            where += f" AND {sql}"
    if cpf:
        where += " AND c.CpfCnpj = :cpf"
        params["cpf"] = cpf.strip()
    if orgao:
        where += " AND c.NomeOrgao = :orgao"
        params["orgao"] = orgao.strip()
    if q and q.strip():
        par = processo_lookup.parse_processo(q)
        if par:
            where += " AND c.NumeroProcesso = :num AND c.AnoProcesso = :ano"
            params["num"], params["ano"] = f"{par[0]:06d}", str(par[1])
        else:
            where += (
                " AND (c.NumeroProcesso LIKE :q OR c.NomePessoa LIKE :q OR c.NomeOrgao LIKE :q"
                " OR c.NumeroProcessoResposta LIKE :q)"
            )
            params["q"] = f"%{q.strip()}%"
    totais = _totais(session, where, params)
    rows = (
        session.execute(
            text(
                f"{_SQL_BASE} {where} ORDER BY c.DataInclusao DESC, c.IdCCDDescontoFolha DESC "
                f"{_paginacao(session)}"
            ).bindparams(bindparam("offset"), bindparam("size")),
            {**params, "offset": (page - 1) * size, "size": size},
        )
        .mappings()
        .all()
    )
    return schemas.CadastroListResponse(
        items=[_item(dict(r)) for r in rows],
        total=totais.cadastros,
        page=page,
        size=size,
        totais=totais,
    )


def _carregar(session: Session, id_cadastro: int) -> dict[str, Any]:
    row = (
        session.execute(
            text(f"{_SQL_BASE} WHERE c.IdCCDDescontoFolha = :c AND c.Ativo = 1"), {"c": id_cadastro}
        )
        .mappings()
        .first()
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="cadastro not found")
    return dict(row)


def _lancamento(r: dict[str, Any]) -> schemas.LancamentoOut:
    return schemas.LancamentoOut(
        id_lancamento=int(r["id_lancamento"]),
        dt_movimento=r["dt_movimento"],
        documento=r["documento"],
        historico=r["historico"],
        valor=float(r["valor"]),
    )


def _nome_info(i: dict[str, Any]) -> Optional[str]:
    nome = i.get("nome_informacao")
    return (str(nome).strip().removesuffix(".doc") or None) if nome else None


def _evento_out(
    i: dict[str, Any], *, id_processo: int, processo: str | None
) -> schemas.EventoRespostaOut:
    return schemas.EventoRespostaOut(
        processo=processo,
        id_evento=int(i["id_evento"]),
        evento=int(i["evento"]),
        nome=_nome_info(i),
        data=i.get("data_resumo"),
        url=ECONTAS_AUTOS_EVENTO.format(id_processo=id_processo, id_evento=int(i["id_evento"])),
    )


def eventos_resposta(
    sessao_processo: Session, r: dict[str, Any]
) -> list[schemas.EventoRespostaOut]:
    """Eventos que são resposta do órgão, independentemente da extração.

    Apensados (todos os eventos de cada um) e, no próprio principal, os eventos cujo
    resumo é alusivo a resposta (`processo_lookup.respostas_no_principal`).
    """
    id_principal = int(r["IdProcesso"])
    numero, ano = str(r["NumeroProcesso"]).strip(), str(r["AnoProcesso"]).strip()
    out: list[schemas.EventoRespostaOut] = []
    for ap in processo_lookup.apensados(sessao_processo, id_principal):
        infos = processo_lookup.informacoes(sessao_processo, ap["numero"], ap["ano"])
        out += [
            _evento_out(
                i, id_processo=int(ap["id_processo"]), processo=f"{ap['numero']}/{ap['ano']}"
            )
            for i in infos
        ]
    fontes = processo_lookup.respostas_no_principal(
        processo_lookup.informacoes(sessao_processo, numero, ano),
        id_processo=id_principal,
        numero=numero,
        ano=ano,
        numero_notificacao=r.get("NumeroNotificacao"),
        data_notificacao=r.get("DataNotificacao"),
    )
    for f in fontes:
        out += [_evento_out(i, id_processo=id_principal, processo=None) for i in f["infos"]]
    out.sort(key=lambda e: (e.processo or "", e.evento))
    return out


def _url_primeiro_evento(
    sessao_processo: Session, id_processo: Any, processo: str
) -> Optional[str]:
    """Link dos autos do processo de resposta aberto no 1º evento."""
    if not id_processo:
        p = processo_lookup.resolver_processo(sessao_processo, processo)
        id_processo = p["IdProcesso"] if p else None
    if not id_processo:
        return None
    return _url_evento(
        id_processo, processo_lookup.primeiro_evento(sessao_processo, int(id_processo))
    )


def retencoes(session: Session, cpf: str) -> schemas.RetencoesOut:
    """Total das rubricas TCE/FRAP já retidas no SIAI Pessoal para o CPF e a última competência."""
    por_mes = valores_tce_por_competencia(session, cpf, 2000)
    ultimo = max(por_mes) if por_mes else None
    return schemas.RetencoesOut(
        cpf=cpf,
        total=round(sum(por_mes.values()), 2),
        competencias=len(por_mes),
        ultimo_ano=ultimo[0] if ultimo else None,
        ultimo_mes=ultimo[1] if ultimo else None,
    )


def mapa_retencoes(session: Session, cpf: str) -> schemas.MapaRetencoesOut:
    """Meses com retenção TCE/FRAP no SIAI (por rubrica) e as parcelas conciliadas do CPF.

    Parcela sem competência (a LLM extraiu só o valor) mas com crédito vinculado entra no
    mês ANTERIOR ao do crédito: o órgão retém em M e repassa em M+1 (Nereu: retenção 02/2025
    R$ 2.460,35 = OB de 05/03/2025). Fica marcada como competência inferida.

    ponytail: meses com parcela conciliada mas sem retenção no SIAI ficam fora do mapa.
    """
    cpf = cpf.strip()
    cadastros = (
        session.execute(
            text(
                "SELECT IdCCDDescontoFolha, NumeroProcesso, AnoProcesso, NomePessoa"
                " FROM CCDDescontoFolha WHERE Ativo = 1 AND CpfCnpj = :cpf"
            ),
            {"cpf": cpf},
        )
        .mappings()
        .all()
    )
    processos = [_processo(c["NumeroProcesso"], c["AnoProcesso"]) or "" for c in cadastros]
    nome = next((str(c["NomePessoa"]).strip() for c in cadastros if c["NomePessoa"]), None)
    parcelas = (
        session.execute(
            text(
                """
                SELECT c.IdCCDDescontoFolha AS id_cadastro, c.NumeroProcesso, c.AnoProcesso,
                       v.NumeroParcela, v.AnoReferencia, v.MesReferencia, v.Valor,
                       L.IdLancamento AS id_lancamento, L.DtMovimento AS dt_movimento,
                       L.Documento AS documento, L.Historico AS historico, L.Valor AS valor_lanc
                FROM CCDDescontoFolhaValor v
                JOIN CCDDescontoFolha c ON c.IdCCDDescontoFolha = v.IdCCDDescontoFolha
                LEFT JOIN CCDDescontoFolhaMatch m
                  ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
                LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamentoFRAP
                WHERE c.Ativo = 1 AND c.CpfCnpj = :cpf
                ORDER BY c.NumeroProcesso, v.NumeroParcela
                """
            ),
            {"cpf": cpf},
        )
        .mappings()
        .all()
    )
    usos: dict[int, int] = {}  # IdLancamento -> nº de parcelas que o usam
    for p in parcelas:
        if p["id_lancamento"]:
            usos[int(p["id_lancamento"])] = usos.get(int(p["id_lancamento"]), 0) + 1
    por_mes: dict[tuple[int, int], schemas.MesRetencaoOut] = {}
    lancamentos_no_mes: dict[tuple[int, int], set[int]] = {}
    for r in retencoes_detalhadas(session, cpf, [p for p in processos if p]):
        chave = (r["ano"], r["mes"])
        mes = por_mes.setdefault(chave, schemas.MesRetencaoOut(ano=r["ano"], mes=r["mes"]))
        mes.retencoes.append(
            schemas.RetencaoMesOut(
                orgao=r["orgao"], codigo=r["codigo"], rubrica=r["rubrica"], valor=r["valor"]
            )
        )
        mes.total_retido = round(mes.total_retido + r["valor"], 2)
    for p in parcelas:
        lanc = _lancamento({**p, "valor": p["valor_lanc"]}) if p["id_lancamento"] else None
        inferida = False
        if p["AnoReferencia"] is not None and p["MesReferencia"] is not None:
            chave = (int(p["AnoReferencia"]), int(p["MesReferencia"]))
        elif lanc is not None and lanc.dt_movimento is not None:
            d = lanc.dt_movimento
            chave = (d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12)
            inferida = True
        else:
            continue
        mes = por_mes.get(chave)
        if mes is None:
            continue
        mes.parcelas.append(
            schemas.ParcelaMesOut(
                id_cadastro=int(p["id_cadastro"]),
                processo=_processo(p["NumeroProcesso"], p["AnoProcesso"]) or "",
                numero_parcela=int(p["NumeroParcela"]),
                valor=float(p["Valor"]),
                conciliado=lanc is not None,
                competencia_inferida=inferida,
                credito_compartilhado=lanc is not None and usos.get(lanc.id_lancamento, 0) > 1,
                lancamento=lanc,
            )
        )
        if lanc is not None:
            vistos = lancamentos_no_mes.setdefault(chave, set())
            if lanc.id_lancamento not in vistos:  # a mesma OB só entra uma vez no mês
                vistos.add(lanc.id_lancamento)
                mes.total_conciliado = round(mes.total_conciliado + lanc.valor, 2)
            mes.conciliado = True
    meses = sorted(por_mes.values(), key=lambda m: (m.ano, m.mes), reverse=True)
    return schemas.MapaRetencoesOut(
        cpf=cpf,
        nome=nome,
        total_retido=round(sum(m.total_retido for m in meses), 2),
        total_conciliado=round(sum(m.total_conciliado for m in meses), 2),
        meses=meses,
    )


def detalhe(
    session: Session, id_cadastro: int, sessao_processo: Session | None = None
) -> schemas.CadastroDetalhe:
    r = _carregar(session, id_cadastro)
    eventos: list[schemas.EventoRespostaOut] = []
    if sessao_processo is not None:
        try:
            eventos = eventos_resposta(sessao_processo, r)
        except Exception:  # enriquecimento somente leitura: não derruba o detalhe
            logger.warning(
                "eventos do apensado indisponíveis (cadastro %s)", id_cadastro, exc_info=True
            )
    valores_rows = (
        session.execute(
            text(
                """
                SELECT v.IdCCDDescontoFolhaValor AS id_valor, v.NumeroParcela, v.MesReferencia,
                       v.AnoReferencia, v.Valor, v.Origem,
                       m.IdCCDDescontoFolhaMatch AS id_match, m.Automatico, m.DataMatch, m.Observacao,
                       L.IdLancamento AS id_lancamento, L.DtMovimento AS dt_movimento,
                       L.Documento AS documento, L.Historico AS historico, L.Valor AS valor_lanc
                FROM CCDDescontoFolhaValor v
                LEFT JOIN CCDDescontoFolhaMatch m ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
                LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamentoFRAP
                WHERE v.IdCCDDescontoFolha = :c
                ORDER BY v.AnoReferencia, v.MesReferencia, v.NumeroParcela, v.IdCCDDescontoFolhaValor
                """
            ),
            {"c": id_cadastro},
        )
        .mappings()
        .all()
    )
    anos = [int(v["AnoReferencia"]) for v in valores_rows if v["AnoReferencia"] is not None]
    siai: dict[tuple[int, int], float] = {}
    if anos and r["CpfCnpj"]:
        try:
            siai = valores_tce_por_competencia(
                session, r["CpfCnpj"], min(anos), _processo(r["NumeroProcesso"], r["AnoProcesso"])
            )
        except Exception:  # enriquecimento somente leitura: não derruba o detalhe
            logger.warning("SIAI Pessoal indisponível (cadastro %s)", id_cadastro, exc_info=True)
    valores: list[schemas.ValorOut] = []
    for v in valores_rows:
        m: schemas.MatchOut | None = None
        cands: list[schemas.LancamentoOut] = []
        if v["id_match"] is not None:
            m = schemas.MatchOut(
                id_match=int(v["id_match"]),
                lancamento=schemas.LancamentoOut(
                    id_lancamento=int(v["id_lancamento"]),
                    dt_movimento=v["dt_movimento"],
                    documento=v["documento"],
                    historico=v["historico"],
                    valor=float(v["valor_lanc"] or 0),
                ),
                automatico=bool(v["Automatico"]),
                data_match=v["DataMatch"],
                observacao=v["Observacao"],
            )
        else:
            cands = [
                _lancamento(c)
                for c in match.candidatos(
                    session,
                    float(v["Valor"]),
                    match.data_minima(
                        mes=v["MesReferencia"],
                        ano=v["AnoReferencia"],
                        data_resposta=r["DataResposta"],
                    ),
                )
            ]
        valores.append(
            schemas.ValorOut(
                id_valor=int(v["id_valor"]),
                numero_parcela=int(v["NumeroParcela"]),
                mes=v["MesReferencia"],
                ano=v["AnoReferencia"],
                valor=float(v["Valor"]),
                origem=v["Origem"],
                valor_siai=(
                    siai.get((int(v["AnoReferencia"]), int(v["MesReferencia"])))
                    if v["AnoReferencia"] is not None and v["MesReferencia"] is not None
                    else None
                ),
                match=m,
                candidatos=cands,
            )
        )
    base = _item(r)
    if not r["NumeroProcessoResposta"] and eventos:
        # Antes da extração, o cabeçalho aponta para o último evento de resposta achado.
        ult = max(eventos, key=lambda e: (e.data or datetime.min, e.evento))
        base.resposta = schemas.RespostaOut(
            processo=ult.processo or base.processo, evento=ult.evento, data=ult.data
        )
    if sessao_processo is not None and base.resposta.processo:
        try:
            base.resposta.url = _url_primeiro_evento(
                sessao_processo, r.get("IdProcessoResposta"), base.resposta.processo
            )
        except Exception:  # enriquecimento somente leitura
            logger.warning("1º evento da resposta indisponível (cadastro %s)", id_cadastro)
    return schemas.CadastroDetalhe(
        **base.model_dump(),
        trecho_resposta=r["TrechoResposta"],
        arquivo_resposta=r["ArquivoResposta"],
        data_extracao=r["DataExtracao"],
        observacoes=r["Observacoes"],
        valores=valores,
        eventos_resposta=eventos,
    )


# ----- lookup / criação (banco processo) -------------------------------------


def lookup(sessao_processo: Session, processo: str) -> schemas.ProcessoLookup:
    p = processo_lookup.resolver_processo(sessao_processo, processo)
    if p is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="processo not found")
    debitos = [
        schemas.DebitoLookup(
            id_debito=int(d["id_debito"]),
            valor_original=float(d["valor_original"]) if d["valor_original"] is not None else None,
            tipo=d["tipo"],
            status=d["status"],
            cancelado=d["data_cancelamento"] is not None,
            desdobrado=bool(d.get("desdobrado")),
            id_pessoa=d["id_pessoa"],
            nome_pessoa=d["nome_pessoa"],
            documento=d["documento"],
        )
        for d in processo_lookup.debitos_do_processo(sessao_processo, int(p["IdProcesso"]))
    ]
    return schemas.ProcessoLookup(
        id_processo=int(p["IdProcesso"]),
        processo=f"{p['numero']}/{p['ano']}",
        orgao=processo_lookup.orgao_notificado(sessao_processo, int(p["IdProcesso"])),
        debitos=debitos,
    )


def _dados_processo(sessao_processo: Session, p: dict[str, Any]) -> dict[str, Any]:
    """Notificação, AR e apensado mais recente do processo de execução."""
    idp = int(p["IdProcesso"])
    infos = processo_lookup.informacoes(sessao_processo, p["numero"], p["ano"])
    apensos = processo_lookup.apensados(sessao_processo, idp)
    ap = apensos[0] if apensos else None
    return {
        **notificacao.localizar(
            sessao_processo,
            id_processo=idp,
            numero=p["numero"],
            ano=p["ano"],
            id_origem=p["id_origem"],
        ),
        "IdProcessoResposta": ap["id_processo"] if ap else None,
        "NumeroProcessoResposta": ap["numero"] if ap else None,
        "AnoProcessoResposta": ap["ano"] if ap else None,
        "EventoResposta": processo_lookup.evento_apensamento(infos, ap["data_registro"])
        if ap
        else None,
        "DataResposta": ap["data_registro"] if ap else None,
    }


def criar(
    session: Session,
    sessao_processo: Session,
    payload: schemas.CadastroInput,
    *,
    id_usuario: int,
) -> schemas.CadastroDetalhe:
    p = processo_lookup.processo_por_id(sessao_processo, payload.id_processo)
    if p is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="processo not found")
    if payload.id_debito is not None:
        existe = session.execute(
            text(
                "SELECT 1 FROM CCDDescontoFolha WHERE IdProcesso = :p AND IdDebito = :d AND Ativo = 1"
            ),
            {"p": payload.id_processo, "d": payload.id_debito},
        ).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="cadastro already exists"
            )

    id_pessoa = payload.id_pessoa
    if id_pessoa is None and payload.id_debito is not None:
        for d in processo_lookup.debitos_do_processo(sessao_processo, payload.id_processo):
            if int(d["id_debito"]) == payload.id_debito and d["id_pessoa"] is not None:
                id_pessoa = int(d["id_pessoa"])
                break
    pessoa = processo_lookup.pessoa(sessao_processo, id_pessoa) if id_pessoa else None
    nome_orgao = (payload.nome_orgao or "").strip() or processo_lookup.orgao_notificado(
        sessao_processo, payload.id_processo
    )
    extra = _dados_processo(sessao_processo, p)
    agora = _agora()
    session.execute(
        text(
            """
            INSERT INTO CCDDescontoFolha
                (IdProcesso, NumeroProcesso, AnoProcesso, IdDebito, IdPessoa, CpfCnpj, NomePessoa,
                 NomeOrgao, NumeroNotificacao, DataNotificacao, TipoNotificacao, EventoNotificacao,
                 IdEventoNotificacao, NumeroPostagemAr, DataAr, TipoRecebimento, EventoRecebimento,
                 IdEventoRecebimento, IdProcessoResposta, NumeroProcessoResposta, AnoProcessoResposta,
                 EventoResposta, DataResposta, StatusExtracao, Parcelado, Observacoes, Ativo,
                 DataInclusao, IdUsuario)
            VALUES (:IdProcesso, :NumeroProcesso, :AnoProcesso, :IdDebito, :IdPessoa, :CpfCnpj,
                    :NomePessoa, :NomeOrgao, :NumeroNotificacao, :DataNotificacao, :TipoNotificacao,
                    :EventoNotificacao, :IdEventoNotificacao, :NumeroPostagemAr, :DataAr,
                    :TipoRecebimento, :EventoRecebimento, :IdEventoRecebimento, :IdProcessoResposta,
                    :NumeroProcessoResposta, :AnoProcessoResposta, :EventoResposta, :DataResposta,
                    'PENDENTE', 0, :Observacoes, 1, :agora, :usuario)
            """
        ),
        {
            "IdProcesso": payload.id_processo,
            "NumeroProcesso": p["numero"],
            "AnoProcesso": p["ano"],
            "IdDebito": payload.id_debito,
            "IdPessoa": id_pessoa,
            "CpfCnpj": "".join(ch for ch in str(pessoa["documento"] or "") if ch.isdigit()) or None
            if pessoa
            else None,
            "NomePessoa": pessoa["nome"] if pessoa else None,
            "NomeOrgao": nome_orgao,
            "Observacoes": payload.observacoes,
            "agora": agora,
            "usuario": id_usuario,
            **extra,
        },
    )
    session.commit()
    novo = session.execute(
        text(
            "SELECT MAX(IdCCDDescontoFolha) FROM CCDDescontoFolha "
            "WHERE IdProcesso = :p AND IdUsuario = :u AND DataInclusao = :agora"
        ),
        {"p": payload.id_processo, "u": id_usuario, "agora": agora},
    ).scalar_one()
    return detalhe(session, int(novo))


def atualizar_dados_processo(
    session: Session, sessao_processo: Session, id_cadastro: int
) -> schemas.CadastroDetalhe:
    """Reconsulta notificação/AR/apensado no banco `processo` (cadastros migrados)."""
    r = _carregar(session, id_cadastro)
    p = processo_lookup.processo_por_id(sessao_processo, int(r["IdProcesso"]))
    if p is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="processo not found")
    extra = _dados_processo(sessao_processo, p)
    session.execute(
        text(
            """
            UPDATE CCDDescontoFolha SET
                NumeroNotificacao = :NumeroNotificacao, DataNotificacao = :DataNotificacao,
                TipoNotificacao = :TipoNotificacao, EventoNotificacao = :EventoNotificacao,
                IdEventoNotificacao = :IdEventoNotificacao,
                NumeroPostagemAr = :NumeroPostagemAr, DataAr = :DataAr,
                TipoRecebimento = :TipoRecebimento, EventoRecebimento = :EventoRecebimento,
                IdEventoRecebimento = :IdEventoRecebimento,
                IdProcessoResposta = COALESCE(:IdProcessoResposta, IdProcessoResposta),
                NumeroProcessoResposta = COALESCE(:NumeroProcessoResposta, NumeroProcessoResposta),
                AnoProcessoResposta = COALESCE(:AnoProcessoResposta, AnoProcessoResposta),
                EventoResposta = COALESCE(:EventoResposta, EventoResposta),
                DataResposta = COALESCE(:DataResposta, DataResposta),
                DataAtualizacao = :agora
            WHERE IdCCDDescontoFolha = :c
            """
        ),
        {**extra, "agora": _agora(), "c": id_cadastro},
    )
    session.commit()
    return detalhe(session, id_cadastro)


def atualizar(
    session: Session, sessao_processo: Session, id_cadastro: int, patch: schemas.CadastroPatch
) -> schemas.CadastroDetalhe:
    r = _carregar(session, id_cadastro)
    campos: dict[str, Any] = {"c": id_cadastro, "agora": _agora()}
    sets = ["DataAtualizacao = :agora"]
    if patch.id_debito is not None:
        sets.append("IdDebito = :IdDebito")
        campos["IdDebito"] = patch.id_debito
    id_pessoa = patch.id_pessoa
    if id_pessoa is None and patch.id_debito is not None:
        for d in processo_lookup.debitos_do_processo(sessao_processo, int(r["IdProcesso"])):
            if int(d["id_debito"]) == patch.id_debito and d["id_pessoa"] is not None:
                id_pessoa = int(d["id_pessoa"])
    if id_pessoa is not None:
        pessoa = processo_lookup.pessoa(sessao_processo, id_pessoa)
        sets += ["IdPessoa = :IdPessoa", "NomePessoa = :NomePessoa", "CpfCnpj = :CpfCnpj"]
        campos["IdPessoa"] = id_pessoa
        campos["NomePessoa"] = pessoa["nome"] if pessoa else None
        campos["CpfCnpj"] = (
            "".join(ch for ch in str(pessoa["documento"] or "") if ch.isdigit()) or None
            if pessoa
            else None
        )
    if patch.nome_orgao is not None:
        sets.append("NomeOrgao = :NomeOrgao")
        campos["NomeOrgao"] = patch.nome_orgao.strip() or None
    if patch.observacoes is not None:
        sets.append("Observacoes = :Observacoes")
        campos["Observacoes"] = patch.observacoes
    session.execute(
        text(f"UPDATE CCDDescontoFolha SET {', '.join(sets)} WHERE IdCCDDescontoFolha = :c"), campos
    )
    session.commit()
    return detalhe(session, id_cadastro)


def remover(session: Session, id_cadastro: int) -> None:
    _carregar(session, id_cadastro)
    session.execute(
        text(
            "UPDATE CCDDescontoFolha SET Ativo = 0, DataAtualizacao = :agora WHERE IdCCDDescontoFolha = :c"
        ),
        {"c": id_cadastro, "agora": _agora()},
    )
    session.commit()


# ----- valores ---------------------------------------------------------------


def criar_valor(
    session: Session, id_cadastro: int, payload: schemas.ValorInput
) -> schemas.CadastroDetalhe:
    _carregar(session, id_cadastro)
    session.execute(
        text(
            "INSERT INTO CCDDescontoFolhaValor "
            "(IdCCDDescontoFolha, NumeroParcela, MesReferencia, AnoReferencia, Valor, Origem) "
            "VALUES (:c, :n, :m, :a, :v, 'M')"
        ),
        {
            "c": id_cadastro,
            "n": payload.numero_parcela,
            "m": payload.mes,
            "a": payload.ano,
            "v": round(payload.valor, 2),
        },
    )
    session.commit()
    return detalhe(session, id_cadastro)


def _valor_do_cadastro(session: Session, id_cadastro: int, id_valor: int) -> None:
    ok = session.execute(
        text(
            "SELECT 1 FROM CCDDescontoFolhaValor WHERE IdCCDDescontoFolhaValor = :v AND IdCCDDescontoFolha = :c"
        ),
        {"v": id_valor, "c": id_cadastro},
    ).first()
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="valor not found")


def atualizar_valor(
    session: Session, id_cadastro: int, id_valor: int, payload: schemas.ValorInput
) -> schemas.CadastroDetalhe:
    _valor_do_cadastro(session, id_cadastro, id_valor)
    session.execute(
        text(
            "UPDATE CCDDescontoFolhaValor SET NumeroParcela = :n, MesReferencia = :m, "
            "AnoReferencia = :a, Valor = :v, Origem = 'M' WHERE IdCCDDescontoFolhaValor = :id"
        ),
        {
            "id": id_valor,
            "n": payload.numero_parcela,
            "m": payload.mes,
            "a": payload.ano,
            "v": round(payload.valor, 2),
        },
    )
    # Valor mudou: o match antigo não vale mais.
    session.execute(
        text("DELETE FROM CCDDescontoFolhaMatch WHERE IdCCDDescontoFolhaValor = :id"),
        {"id": id_valor},
    )
    session.commit()
    return detalhe(session, id_cadastro)


def remover_valor(session: Session, id_cadastro: int, id_valor: int) -> schemas.CadastroDetalhe:
    _valor_do_cadastro(session, id_cadastro, id_valor)
    session.execute(
        text("DELETE FROM CCDDescontoFolhaMatch WHERE IdCCDDescontoFolhaValor = :id"),
        {"id": id_valor},
    )
    session.execute(
        text("DELETE FROM CCDDescontoFolhaValor WHERE IdCCDDescontoFolhaValor = :id"),
        {"id": id_valor},
    )
    session.commit()
    return detalhe(session, id_cadastro)


# ----- match -----------------------------------------------------------------


def vincular(
    session: Session,
    id_cadastro: int,
    id_valor: int,
    payload: schemas.MatchInput,
    *,
    id_usuario: int,
) -> schemas.CadastroDetalhe:
    _valor_do_cadastro(session, id_cadastro, id_valor)
    existe = session.execute(
        text("SELECT 1 FROM FRAPLancamento WHERE IdLancamento = :l"), {"l": payload.id_lancamento}
    ).first()
    if not existe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lancamento not found")
    match.vincular(
        session,
        id_valor=id_valor,
        id_lancamento=payload.id_lancamento,
        id_usuario=id_usuario,
        automatico=False,
        observacao=payload.observacao,
    )
    return detalhe(session, id_cadastro)


def desvincular(session: Session, id_cadastro: int, id_valor: int) -> schemas.CadastroDetalhe:
    _valor_do_cadastro(session, id_cadastro, id_valor)
    match.desvincular(session, id_valor=id_valor)
    return detalhe(session, id_cadastro)


def match_automatico(session: Session, id_cadastro: int) -> schemas.MatchAutomaticoResultado:
    _carregar(session, id_cadastro)
    return schemas.MatchAutomaticoResultado(
        vinculados=match.match_automatico(session, id_cadastro=id_cadastro)
    )


# ----- FRAP-first: créditos do extrato sem depender da resposta ----------------

# Palavras do nome do órgão que não identificam nada na descrição do extrato.
_PALAVRAS_FRACAS = {
    "PREFEITURA",
    "MUNICIPAL",
    "MUNICIPIO",
    "CAMARA",
    "SECRETARIA",
    "ESTADUAL",
    "ESTADO",
    "GOVERNO",
    "FUNDO",
    "INSTITUTO",
    "DE",
    "DO",
    "DA",
    "DOS",
    "DAS",
    "E",
    "RN",
    "PM",
    "PMS",
}
# OB do SIGEF chega como "ESTADO DO RIO GRANDE D": órgão estadual só se acha por valor.
_TEXTO_ESTADO = "ESTADO"
_ALIASES = {
    "ALRN": "ASSEMBL",
    "ASSEMBLEIA": "ASSEMBL",
    "IPERN": _TEXTO_ESTADO,
    "SEEC": _TEXTO_ESTADO,
    "SEECRN": _TEXTO_ESTADO,
    "SEAD": _TEXTO_ESTADO,
    "SESAP": _TEXTO_ESTADO,
}


def texto_padrao_orgao(nome_orgao: Any) -> Optional[str]:
    """Primeira palavra "forte" do órgão, como aparece na descrição do extrato."""
    limpo = unicodedata.normalize("NFKD", str(nome_orgao or "")).encode("ascii", "ignore").decode()
    for p in limpo.upper().replace("/", " ").replace("-", " ").split():
        if p in _ALIASES:
            return _ALIASES[p]
        if p not in _PALAVRAS_FRACAS and len(p) >= 4:
            return p
    return None


def creditos_frap(
    session: Session,
    id_cadastro: int,
    *,
    texto: str | None = None,
    valor: float | None = None,
    desde: date | None = None,
) -> schemas.CreditosFrapResponse:
    r = _carregar(session, id_cadastro)
    if texto is None:
        texto = texto_padrao_orgao(r["NomeOrgao"])
    if desde is None:
        dn = r["DataNotificacao"]
        if isinstance(dn, str):
            dn = datetime.fromisoformat(dn[:19])
        desde = dn.date() if isinstance(dn, datetime) else dn
    aviso = None
    if (texto or "").upper() == _TEXTO_ESTADO and not valor:
        # A OB do SIGEF não traz o órgão: sem o valor da parcela viria todo o Estado.
        aviso = "Repasse de órgão estadual chega como OB do Estado, sem o nome do órgão. Informe o valor da parcela."
    rows = [] if aviso else match.creditos(session, texto=texto or None, valor=valor, desde=desde)
    return schemas.CreditosFrapResponse(
        texto=texto or None,
        desde=desde,
        valor=valor,
        aviso=aviso,
        items=[
            schemas.CreditoFrapOut(
                **_lancamento(c).model_dump(),
                descricao=c["descricao"],
                id_cadastro_vinculado=c["id_cadastro_vinculado"],
            )
            for c in rows
        ],
    )


def adotar_creditos_frap(
    session: Session, id_cadastro: int, payload: schemas.AdotarCreditosInput, *, id_usuario: int
) -> schemas.CadastroDetalhe:
    _carregar(session, id_cadastro)
    match.adotar(
        session,
        id_cadastro=id_cadastro,
        ids_lancamento=payload.ids_lancamento,
        id_usuario=id_usuario,
    )
    return detalhe(session, id_cadastro)
