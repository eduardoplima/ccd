"""Cadastro do desconto em folha (BdDIP) e leitura do que vem do banco `processo`.

SQL cru via `text()`, sem ORM — as três tabelas CCDDescontoFolha* têm
poucas colunas e as consultas precisam rodar também no SQLite dos testes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.desconto_folha import match, processo_lookup, schemas


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
            numero=r["NumeroNotificacao"], data=r["DataNotificacao"]
        ),
        ar=schemas.ArOut(numero_postagem=r["NumeroPostagemAr"], data=r["DataAr"]),
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


def listar(
    session: Session, *, q: str | None, page: int, size: int
) -> schemas.CadastroListResponse:
    where = "WHERE c.Ativo = 1"
    params: dict[str, Any] = {}
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
    total = int(
        session.execute(
            text(f"SELECT COUNT(*) FROM CCDDescontoFolha c {where}"), params
        ).scalar_one()
    )
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
        items=[_item(dict(r)) for r in rows], total=total, page=page, size=size
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


def detalhe(session: Session, id_cadastro: int) -> schemas.CadastroDetalhe:
    r = _carregar(session, id_cadastro)
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
                match=m,
                candidatos=cands,
            )
        )
    base = _item(r)
    return schemas.CadastroDetalhe(
        **base.model_dump(),
        trecho_resposta=r["TrechoResposta"],
        arquivo_resposta=r["ArquivoResposta"],
        data_extracao=r["DataExtracao"],
        observacoes=r["Observacoes"],
        valores=valores,
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
    notif = processo_lookup.notificacao(
        sessao_processo, numero=p["numero"], ano=p["ano"], id_processo=idp, id_origem=p["id_origem"]
    )
    ar = processo_lookup.ar(
        sessao_processo,
        id_informacao=notif["id_informacao"],
        id_citacao=notif["id_citacao"],
        numero_postagem=notif["numero_postagem"],
    )
    apensos = processo_lookup.apensados(sessao_processo, idp)
    ap = apensos[0] if apensos else None
    return {
        "NumeroNotificacao": notif["numero"],
        "DataNotificacao": notif["data"],
        "NumeroPostagemAr": ar["numero_postagem"],
        "DataAr": ar["data"],
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
                 NomeOrgao, NumeroNotificacao, DataNotificacao, NumeroPostagemAr, DataAr,
                 IdProcessoResposta, NumeroProcessoResposta, AnoProcessoResposta, EventoResposta,
                 DataResposta, StatusExtracao, Parcelado, Observacoes, Ativo, DataInclusao, IdUsuario)
            VALUES (:IdProcesso, :NumeroProcesso, :AnoProcesso, :IdDebito, :IdPessoa, :CpfCnpj,
                    :NomePessoa, :NomeOrgao, :NumeroNotificacao, :DataNotificacao, :NumeroPostagemAr,
                    :DataAr, :IdProcessoResposta, :NumeroProcessoResposta, :AnoProcessoResposta,
                    :EventoResposta, :DataResposta, 'PENDENTE', 0, :Observacoes, 1, :agora, :usuario)
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
                NumeroPostagemAr = :NumeroPostagemAr, DataAr = :DataAr,
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
