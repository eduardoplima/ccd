from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.lancamentos.schemas import (
    LancamentoDetail,
    LancamentoListItem,
    LancamentoListResponse,
    Match,
    MatchDescontoFolha,
    MatchGuia,
    MatchOB,
    MatchPessoa,
    MatchResumo,
)


def listar_lancamentos(
    session: Session,
    *,
    conta: str | None = None,
    periodo: str | None = None,
    categoria: str | None = None,
    valor_dc: str | None = None,
    dt_inicio: date | None = None,
    dt_fim: date | None = None,
    valor_min: Decimal | None = None,
    valor_max: Decimal | None = None,
    cpfcnpj: str | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
) -> LancamentoListResponse:
    where: list[str] = []
    params: dict[str, Any] = {}

    if conta:
        where.append("c.Conta = :conta")
        params["conta"] = conta
    if periodo:
        where.append("L.Periodo = :periodo")
        params["periodo"] = periodo
    if categoria:
        where.append("cat.Codigo = :categoria")
        params["categoria"] = categoria
    if valor_dc in ("C", "D"):
        where.append("L.ValorDC = :valor_dc")
        params["valor_dc"] = valor_dc
    if dt_inicio:
        where.append("L.DtMovimento >= :dt_inicio")
        params["dt_inicio"] = dt_inicio
    if dt_fim:
        where.append("L.DtMovimento <= :dt_fim")
        params["dt_fim"] = dt_fim
    if valor_min is not None:
        where.append("L.Valor >= :valor_min")
        params["valor_min"] = str(valor_min)
    if valor_max is not None:
        where.append("L.Valor <= :valor_max")
        params["valor_max"] = str(valor_max)
    if cpfcnpj:
        # CPF: depositante pode vir com leading zeros (14 dígitos no campo).
        # CNPJ: 14 dígitos exatos.
        cpf_norm = "".join(c for c in cpfcnpj if c.isdigit())
        if len(cpf_norm) == 11:
            where.append("RIGHT(L.CpfCnpjDepositante, 11) = :cpfcnpj")
        else:
            where.append("L.CpfCnpjDepositante = :cpfcnpj")
        params["cpfcnpj"] = cpf_norm
    if q:
        where.append("(L.Historico LIKE :q OR L.Descricao LIKE :q OR L.Documento LIKE :q)")
        params["q"] = f"%{q}%"

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    total_sql = text(
        f"""
        SELECT COUNT(*)
        FROM FRAPLancamento L
        JOIN FRAPConta c       ON c.IdConta = L.IdConta
        JOIN FRAPCategoria cat ON cat.IdCategoria = L.IdCategoria
        {where_sql}
        """
    )
    total = int(session.execute(total_sql, params).scalar_one())

    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}

    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    pagination_sql = (
        "LIMIT :size OFFSET :offset"
        if dialect == "sqlite"
        else "OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY"
    )
    page_sql = text(
        f"""
        SELECT
            L.IdLancamento, c.Conta AS Conta, L.Periodo,
            L.DtMovimento, L.DtBalancete, L.AgOrigem, L.Lote,
            L.Historico, L.Documento, L.DocData,
            L.Valor, L.ValorDC, L.Descricao,
            cat.Codigo AS Categoria, L.CpfCnpjDepositante
        FROM FRAPLancamento L
        JOIN FRAPConta c       ON c.IdConta = L.IdConta
        JOIN FRAPCategoria cat ON cat.IdCategoria = L.IdCategoria
        {where_sql}
        ORDER BY L.DtMovimento DESC, L.IdLancamento DESC
        {pagination_sql}
        """
    ).bindparams(bindparam("offset"), bindparam("size"))

    rows = session.execute(page_sql, page_params).mappings().all()
    ids = [int(r["IdLancamento"]) for r in rows]
    matches_por_id = _carregar_matches_resumo(session, ids) if ids else {}

    items = [
        LancamentoListItem(
            id_lancamento=int(r["IdLancamento"]),
            conta=str(r["Conta"]),
            periodo=str(r["Periodo"]),
            dt_movimento=r["DtMovimento"],
            dt_balancete=r["DtBalancete"],
            ag_origem=r["AgOrigem"],
            lote=r["Lote"],
            historico=r["Historico"],
            documento=r["Documento"],
            doc_data=r["DocData"],
            valor=r["Valor"],
            valor_dc=r["ValorDC"],
            descricao=r["Descricao"],
            categoria=str(r["Categoria"]),
            cpfcnpj_depositante=r["CpfCnpjDepositante"],
            matches_resumo=matches_por_id.get(int(r["IdLancamento"]), []),
        )
        for r in rows
    ]
    return LancamentoListResponse(items=items, total=total, page=page, size=size)


def _carregar_matches_resumo(session: Session, ids: list[int]) -> dict[int, list[MatchResumo]]:
    sql = text(
        """
        SELECT IdLancamento, 'OB' AS Matcher, st.Codigo AS Status, COUNT(*) AS Qtd
        FROM FRAPMatchOB m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamento IN :ids
        GROUP BY m.IdLancamento, st.Codigo
        UNION ALL
        SELECT IdLancamento, 'PESSOA', st.Codigo, COUNT(*)
        FROM FRAPMatchPessoa m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamento IN :ids
        GROUP BY m.IdLancamento, st.Codigo
        UNION ALL
        SELECT IdLancamento, 'GUIA', st.Codigo, COUNT(*)
        FROM FRAPMatchGuia m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamento IN :ids
        GROUP BY m.IdLancamento, st.Codigo
        UNION ALL
        SELECT IdLancamentoFRAP, 'DESCONTO_FOLHA', st.Codigo, COUNT(*)
        FROM FRAPMatchDescontoFolha m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamentoFRAP IN :ids
        GROUP BY m.IdLancamentoFRAP, st.Codigo
        """
    ).bindparams(bindparam("ids", expanding=True))

    rows = session.execute(sql, {"ids": ids}).mappings().all()
    out: dict[int, list[MatchResumo]] = defaultdict(list)
    for r in rows:
        out[int(r["IdLancamento"])].append(
            MatchResumo(matcher=r["Matcher"], status=r["Status"], quantidade=int(r["Qtd"]))
        )
    return dict(out)


def get_lancamento_detail(session: Session, id_lancamento: int) -> LancamentoDetail | None:
    base_sql = text(
        """
        SELECT
            L.IdLancamento, c.Conta AS Conta, L.Periodo,
            L.DtMovimento, L.DtBalancete, L.AgOrigem, L.Lote,
            L.Historico, L.Documento, L.DocData,
            L.Valor, L.ValorDC, L.Descricao,
            cat.Codigo AS Categoria, L.CpfCnpjDepositante, L.CpfCnpjAmbiguo,
            arq.NomeArquivo
        FROM FRAPLancamento L
        JOIN FRAPConta c             ON c.IdConta = L.IdConta
        JOIN FRAPCategoria cat       ON cat.IdCategoria = L.IdCategoria
        JOIN FRAPExtratoArquivo arq  ON arq.IdArquivo = L.IdArquivo
        WHERE L.IdLancamento = :id
        """
    )
    row = session.execute(base_sql, {"id": id_lancamento}).mappings().first()
    if row is None:
        return None

    matches: list[Match] = [
        *_carregar_matches_ob(session, id_lancamento),
        *_carregar_matches_pessoa(session, id_lancamento),
        *_carregar_matches_guia(session, id_lancamento),
        *_carregar_matches_desconto_folha(session, id_lancamento),
    ]

    return LancamentoDetail(
        id_lancamento=int(row["IdLancamento"]),
        conta=str(row["Conta"]),
        periodo=str(row["Periodo"]),
        dt_movimento=row["DtMovimento"],
        dt_balancete=row["DtBalancete"],
        ag_origem=row["AgOrigem"],
        lote=row["Lote"],
        historico=row["Historico"],
        documento=row["Documento"],
        doc_data=row["DocData"],
        valor=row["Valor"],
        valor_dc=row["ValorDC"],
        descricao=row["Descricao"],
        categoria=str(row["Categoria"]),
        cpfcnpj_depositante=row["CpfCnpjDepositante"],
        cpfcnpj_ambiguo=bool(row["CpfCnpjAmbiguo"]),
        nome_arquivo=row["NomeArquivo"],
        matches=matches,
    )


def _carregar_matches_ob(session: Session, id_lancamento: int) -> list[MatchOB]:
    sql = text(
        """
        SELECT
            m.IdMatchOB, m.AnoSigef, m.CdUnidadeGestora, m.CdGestao,
            m.NuOrdemBancaria, m.DataPagamento, m.ValorOB,
            m.CdCredor, m.NmCredor, m.NuPreparacaoPagamento, m.NuNotaEmpenho,
            st.Codigo AS Status, st.Descricao AS StatusDescricao
        FROM FRAPMatchOB m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamento = :id
        ORDER BY m.IdMatchOB
        """
    )
    return [
        MatchOB(
            id_match=int(r["IdMatchOB"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            ano_sigef=r["AnoSigef"],
            cd_unidade_gestora=r["CdUnidadeGestora"],
            cd_gestao=r["CdGestao"],
            nu_ordem_bancaria=r["NuOrdemBancaria"],
            data_pagamento=r["DataPagamento"],
            valor_ob=r["ValorOB"],
            cd_credor=r["CdCredor"],
            nm_credor=r["NmCredor"],
            nu_preparacao_pagamento=r["NuPreparacaoPagamento"],
            nu_nota_empenho=r["NuNotaEmpenho"],
        )
        for r in session.execute(sql, {"id": id_lancamento}).mappings().all()
    ]


def _carregar_matches_pessoa(session: Session, id_lancamento: int) -> list[MatchPessoa]:
    sql = text(
        """
        SELECT
            m.IdMatchPessoa, m.IdDebito, m.IdProcessoExecucao,
            m.CpfCnpj, m.NomePessoa,
            m.ValorPago, m.ValorAPagar, m.ValorOriginalDebito, m.ValorCasadoEm,
            st.Codigo AS Status, st.Descricao AS StatusDescricao
        FROM FRAPMatchPessoa m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamento = :id
        ORDER BY m.IdMatchPessoa
        """
    )
    return [
        MatchPessoa(
            id_match=int(r["IdMatchPessoa"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            id_debito=r["IdDebito"],
            id_processo_execucao=r["IdProcessoExecucao"],
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            valor_pago=r["ValorPago"],
            valor_a_pagar=r["ValorAPagar"],
            valor_original_debito=r["ValorOriginalDebito"],
            valor_casado_em=r["ValorCasadoEm"],
        )
        for r in session.execute(sql, {"id": id_lancamento}).mappings().all()
    ]


def _carregar_matches_guia(session: Session, id_lancamento: int) -> list[MatchGuia]:
    sql = text(
        """
        SELECT
            m.IdMatchGuia, m.IdBoleto, m.IdDebito, m.IdProcessoExecucao,
            m.CodigoBarras, m.DataPagamento, m.ValorPago, m.NomePessoa, m.CpfCnpj,
            st.Codigo AS Status, st.Descricao AS StatusDescricao
        FROM FRAPMatchGuia m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamento = :id
        ORDER BY m.IdMatchGuia
        """
    )
    return [
        MatchGuia(
            id_match=int(r["IdMatchGuia"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            id_boleto=r["IdBoleto"],
            id_debito=r["IdDebito"],
            id_processo_execucao=r["IdProcessoExecucao"],
            codigo_barras=r["CodigoBarras"],
            data_pagamento=r["DataPagamento"],
            valor_pago=r["ValorPago"],
            nome_pessoa=r["NomePessoa"],
            cpfcnpj=r["CpfCnpj"],
        )
        for r in session.execute(sql, {"id": id_lancamento}).mappings().all()
    ]


def _carregar_matches_desconto_folha(
    session: Session, id_lancamento: int
) -> list[MatchDescontoFolha]:
    sql = text(
        """
        SELECT
            m.IdMatchDescontoFolha, m.IdFRAPDescontoFolhaParcela,
            p.NumeroParcela, p.MesReferencia, p.AnoReferencia, p.ValorEsperado,
            df.CpfCnpj, df.NomePessoa,
            m.IdContraChequeItem, m.ValorContracheque,
            st.Codigo AS Status, st.Descricao AS StatusDescricao
        FROM FRAPMatchDescontoFolha m
        JOIN FRAPDescontoFolhaParcela p ON p.IdFRAPDescontoFolhaParcela = m.IdFRAPDescontoFolhaParcela
        JOIN FRAPDescontoFolha df ON df.IdFRAPDescontoFolha = p.IdFRAPDescontoFolha
        JOIN FRAPStatusMatch st         ON st.IdStatusMatch = m.IdStatusMatch
        WHERE m.IdLancamentoFRAP = :id
        ORDER BY m.IdMatchDescontoFolha
        """
    )
    return [
        MatchDescontoFolha(
            id_match=int(r["IdMatchDescontoFolha"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            id_parcela=r["IdFRAPDescontoFolhaParcela"],
            numero_parcela=r["NumeroParcela"],
            mes_referencia=r["MesReferencia"],
            ano_referencia=r["AnoReferencia"],
            valor_esperado=r["ValorEsperado"],
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            id_contracheque_item=r["IdContraChequeItem"],
            valor_contracheque=r["ValorContracheque"],
        )
        for r in session.execute(sql, {"id": id_lancamento}).mappings().all()
    ]
