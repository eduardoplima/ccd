from __future__ import annotations

from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.matches.schemas import (
    MatchDescontoFolhaListItem,
    MatchDescontoFolhaListResponse,
    MatchGuiaListItem,
    MatchGuiaListResponse,
    MatchOBListItem,
    MatchOBListResponse,
    MatchPessoaListItem,
    MatchPessoaListResponse,
)

# Apenas matches bem-sucedidos são listados — códigos por matcher conforme tools/frap/matching/.
_SUCESSO_OB = ("EXATO", "EXATO_POR_ORDEM")
_SUCESSO_PESSOA = ("EXATO_PESSOA_VALOR",)
_SUCESSO_GUIA = ("EXATO_LOTE",)
_SUCESSO_DF = ("OK_TUDO", "MATCH_MANUAL", "REPASSE_VIA_ORGAO")


def _ano_filter(dialect: str, alias: str = "m") -> str:
    if dialect == "sqlite":
        return f"SUBSTR({alias}.Periodo, 3, 4) = :ano"
    return f"RIGHT({alias}.Periodo, 4) = :ano"


def _pagination(dialect: str) -> str:
    return (
        "LIMIT :size OFFSET :offset"
        if dialect == "sqlite"
        else "OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY"
    )


def _in_clause(prefix: str, valores: tuple[str, ...]) -> tuple[str, dict[str, str]]:
    nomes = [f"{prefix}{i}" for i in range(len(valores))]
    placeholders = ", ".join(f":{n}" for n in nomes)
    return placeholders, {n: v for n, v in zip(nomes, valores, strict=True)}


def _periodo_e_conta_where(
    *,
    ano: int | None,
    mes: int | None,
    conta: str | None,
    dialect: str,
    alias: str = "m",
    join_conta: bool = True,
) -> tuple[list[str], dict[str, Any]]:
    where: list[str] = []
    params: dict[str, Any] = {}
    if ano is not None and mes is not None:
        where.append(f"{alias}.Periodo = :periodo")
        params["periodo"] = f"{mes:02d}{ano}"
    elif ano is not None:
        where.append(_ano_filter(dialect, alias))
        params["ano"] = str(ano)
    if conta and join_conta:
        where.append("c.Conta = :conta")
        params["conta"] = conta
    return where, params


def _q_normalizado(q: str | None) -> str | None:
    if q is None:
        return None
    s = q.strip()
    return s or None


def _like_nome_clause(coluna: str, dialect: str) -> str:
    if dialect == "mssql":
        return (
            f"UPPER({coluna}) COLLATE SQL_Latin1_General_CP1_CI_AI "
            "LIKE UPPER(:q_like) COLLATE SQL_Latin1_General_CP1_CI_AI"
        )
    return f"UPPER({coluna}) LIKE UPPER(:q_like)"


def _filtro_pessoa_q(
    *,
    q: str | None,
    coluna_nome: str,
    coluna_doc: str,
    dialect: str,
) -> tuple[str | None, dict[str, Any]]:
    q_norm = _q_normalizado(q)
    if q_norm is None:
        return None, {}
    if q_norm.isdigit() and len(q_norm) >= 3:
        return f"{coluna_doc} LIKE :q_like", {"q_like": f"%{q_norm}%"}
    return _like_nome_clause(coluna_nome, dialect), {"q_like": f"%{q_norm}%"}


def list_matches_ob(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    conta: str | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
) -> MatchOBListResponse:
    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    where, params = _periodo_e_conta_where(ano=ano, mes=mes, conta=conta, dialect=dialect)
    placeholders, params_st = _in_clause("st_ob_", _SUCESSO_OB)
    where.insert(0, f"st.Codigo IN ({placeholders})")
    params.update(params_st)
    q_norm = _q_normalizado(q)
    if q_norm is not None:
        nome_like = _like_nome_clause("m.NmCredor", dialect)
        where.append(f"({nome_like} OR m.NuOrdemBancaria LIKE :q_like)")
        params["q_like"] = f"%{q_norm}%"
    where_sql = "WHERE " + " AND ".join(where)
    total = int(
        session.execute(
            text(
                f"""
                SELECT COUNT(*) FROM FRAPMatchOB m
                JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
                JOIN FRAPConta c ON c.IdConta = m.IdConta
                {where_sql}
                """
            ),
            params,
        ).scalar_one()
    )
    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    sql = text(
        f"""
        SELECT
            m.IdMatchOB, st.Codigo AS Status, st.Descricao AS StatusDescricao,
            c.Conta, m.Periodo,
            L.IdLancamento, L.DtMovimento, L.Valor AS ValorLancamento, L.ValorDC,
            L.Historico, L.Documento AS DocumentoExtrato,
            m.AnoSigef, m.NuOrdemBancaria, m.CdUnidadeGestora,
            m.DataPagamento, m.ValorOB, m.CdCredor, m.NmCredor
        FROM FRAPMatchOB m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        JOIN FRAPConta c ON c.IdConta = m.IdConta
        LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamento
        {where_sql}
        ORDER BY m.IdMatchOB DESC
        {_pagination(dialect)}
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, page_params).mappings().all()
    items = [
        MatchOBListItem(
            id_match=int(r["IdMatchOB"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            conta=str(r["Conta"]),
            periodo=str(r["Periodo"]),
            id_lancamento=r["IdLancamento"],
            dt_movimento=r["DtMovimento"],
            valor_lancamento=r["ValorLancamento"],
            valor_dc=r["ValorDC"],
            historico=r["Historico"],
            documento_extrato=r["DocumentoExtrato"],
            ano_sigef=int(r["AnoSigef"]),
            nu_ordem_bancaria=r["NuOrdemBancaria"],
            cd_unidade_gestora=r["CdUnidadeGestora"],
            data_pagamento=r["DataPagamento"],
            valor_ob=r["ValorOB"],
            cd_credor=r["CdCredor"],
            nm_credor=r["NmCredor"],
        )
        for r in rows
    ]
    return MatchOBListResponse(items=items, total=total, page=page, size=size)


def list_matches_pessoa(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    conta: str | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
) -> MatchPessoaListResponse:
    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    where, params = _periodo_e_conta_where(ano=ano, mes=mes, conta=conta, dialect=dialect)
    placeholders, params_st = _in_clause("st_p_", _SUCESSO_PESSOA)
    where.insert(0, f"st.Codigo IN ({placeholders})")
    params.update(params_st)
    clause, q_params = _filtro_pessoa_q(
        q=q, coluna_nome="m.NomePessoa", coluna_doc="m.CpfCnpj", dialect=dialect
    )
    if clause is not None:
        where.append(clause)
        params.update(q_params)
    where_sql = "WHERE " + " AND ".join(where)
    total = int(
        session.execute(
            text(
                f"""
                SELECT COUNT(*) FROM FRAPMatchPessoa m
                JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
                JOIN FRAPConta c ON c.IdConta = m.IdConta
                {where_sql}
                """
            ),
            params,
        ).scalar_one()
    )
    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    sql = text(
        f"""
        SELECT
            m.IdMatchPessoa, st.Codigo AS Status, st.Descricao AS StatusDescricao,
            c.Conta, m.Periodo,
            L.IdLancamento, L.DtMovimento, L.Valor AS ValorLancamento, L.ValorDC,
            L.Historico, L.Documento AS DocumentoExtrato,
            m.IdDebito, m.CpfCnpj, m.NomePessoa,
            m.ValorPago, m.ValorAPagar, m.ValorCasadoEm
        FROM FRAPMatchPessoa m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        JOIN FRAPConta c ON c.IdConta = m.IdConta
        LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamento
        {where_sql}
        ORDER BY m.IdMatchPessoa DESC
        {_pagination(dialect)}
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, page_params).mappings().all()
    items = [
        MatchPessoaListItem(
            id_match=int(r["IdMatchPessoa"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            conta=str(r["Conta"]),
            periodo=str(r["Periodo"]),
            id_lancamento=r["IdLancamento"],
            dt_movimento=r["DtMovimento"],
            valor_lancamento=r["ValorLancamento"],
            valor_dc=r["ValorDC"],
            historico=r["Historico"],
            documento_extrato=r["DocumentoExtrato"],
            id_debito=r["IdDebito"],
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            valor_pago=r["ValorPago"],
            valor_a_pagar=r["ValorAPagar"],
            valor_casado_em=r["ValorCasadoEm"],
        )
        for r in rows
    ]
    return MatchPessoaListResponse(items=items, total=total, page=page, size=size)


def list_matches_guia(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    conta: str | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
) -> MatchGuiaListResponse:
    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    where, params = _periodo_e_conta_where(ano=ano, mes=mes, conta=conta, dialect=dialect)
    placeholders, params_st = _in_clause("st_g_", _SUCESSO_GUIA)
    where.insert(0, f"st.Codigo IN ({placeholders})")
    params.update(params_st)
    clause, q_params = _filtro_pessoa_q(
        q=q, coluna_nome="m.NomePessoa", coluna_doc="m.CpfCnpj", dialect=dialect
    )
    if clause is not None:
        where.append(clause)
        params.update(q_params)
    where_sql = "WHERE " + " AND ".join(where)
    total = int(
        session.execute(
            text(
                f"""
                SELECT COUNT(*) FROM FRAPMatchGuia m
                JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
                JOIN FRAPConta c ON c.IdConta = m.IdConta
                {where_sql}
                """
            ),
            params,
        ).scalar_one()
    )
    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    sql = text(
        f"""
        SELECT
            m.IdMatchGuia, st.Codigo AS Status, st.Descricao AS StatusDescricao,
            c.Conta, m.Periodo,
            L.IdLancamento, L.DtMovimento, L.Valor AS ValorLancamento, L.ValorDC,
            L.Historico, L.Documento AS DocumentoExtrato,
            m.IdBoleto, m.IdDebito, m.CodigoBarras, m.DataPagamento,
            m.ValorPago, m.NomePessoa, m.CpfCnpj
        FROM FRAPMatchGuia m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        JOIN FRAPConta c ON c.IdConta = m.IdConta
        LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamento
        {where_sql}
        ORDER BY m.IdMatchGuia DESC
        {_pagination(dialect)}
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, page_params).mappings().all()
    items = [
        MatchGuiaListItem(
            id_match=int(r["IdMatchGuia"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            conta=str(r["Conta"]),
            periodo=str(r["Periodo"]),
            id_lancamento=r["IdLancamento"],
            dt_movimento=r["DtMovimento"],
            valor_lancamento=r["ValorLancamento"],
            valor_dc=r["ValorDC"],
            historico=r["Historico"],
            documento_extrato=r["DocumentoExtrato"],
            id_boleto=r["IdBoleto"],
            id_debito=r["IdDebito"],
            codigo_barras=r["CodigoBarras"],
            data_pagamento=r["DataPagamento"],
            valor_pago=r["ValorPago"],
            nome_pessoa=r["NomePessoa"],
            cpfcnpj=r["CpfCnpj"],
        )
        for r in rows
    ]
    return MatchGuiaListResponse(items=items, total=total, page=page, size=size)


def list_matches_desconto_folha(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
) -> MatchDescontoFolhaListResponse:
    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    where: list[str] = []
    params: dict[str, Any] = {}
    placeholders, params_st = _in_clause("st_df_", _SUCESSO_DF)
    where.append(f"st.Codigo IN ({placeholders})")
    params.update(params_st)
    if ano is not None and mes is not None:
        where.append("p.AnoReferencia = :ano AND p.MesReferencia = :mes")
        params["ano"] = ano
        params["mes"] = mes
    elif ano is not None:
        where.append("p.AnoReferencia = :ano")
        params["ano"] = ano
    clause, q_params = _filtro_pessoa_q(
        q=q, coluna_nome="df.NomePessoa", coluna_doc="df.CpfCnpj", dialect=dialect
    )
    if clause is not None:
        where.append(clause)
        params.update(q_params)
    where_sql = "WHERE " + " AND ".join(where)

    total = int(
        session.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM FRAPMatchDescontoFolha m
                JOIN FRAPDescontoFolhaParcela p ON p.IdFRAPDescontoFolhaParcela = m.IdFRAPDescontoFolhaParcela
                JOIN FRAPDescontoFolha df ON df.IdFRAPDescontoFolha = p.IdFRAPDescontoFolha
                JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
                {where_sql}
                """
            ),
            params,
        ).scalar_one()
    )
    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    sql = text(
        f"""
        SELECT
            m.IdMatchDescontoFolha, st.Codigo AS Status, st.Descricao AS StatusDescricao,
            p.IdFRAPDescontoFolhaParcela AS IdParcela, p.NumeroParcela,
            p.MesReferencia, p.AnoReferencia, p.ValorEsperado,
            df.CpfCnpj, df.NomePessoa,
            m.ValorContracheque,
            L.IdLancamento, L.DtMovimento, L.Valor AS ValorLancamento
        FROM FRAPMatchDescontoFolha m
        JOIN FRAPDescontoFolhaParcela p ON p.IdFRAPDescontoFolhaParcela = m.IdFRAPDescontoFolhaParcela
        JOIN FRAPDescontoFolha df ON df.IdFRAPDescontoFolha = p.IdFRAPDescontoFolha
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamentoFRAP
        {where_sql}
        ORDER BY m.IdMatchDescontoFolha DESC
        {_pagination(dialect)}
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, page_params).mappings().all()
    items = [
        MatchDescontoFolhaListItem(
            id_match=int(r["IdMatchDescontoFolha"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            id_parcela=r["IdParcela"],
            numero_parcela=r["NumeroParcela"],
            mes_referencia=r["MesReferencia"],
            ano_referencia=r["AnoReferencia"],
            valor_esperado=r["ValorEsperado"],
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            valor_contracheque=r["ValorContracheque"],
            id_lancamento=r["IdLancamento"],
            dt_movimento=r["DtMovimento"],
            valor_lancamento=r["ValorLancamento"],
        )
        for r in rows
    ]
    return MatchDescontoFolhaListResponse(items=items, total=total, page=page, size=size)
