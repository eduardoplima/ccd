from __future__ import annotations

from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.debitos.schemas import DebitoLookupItem, DebitoLookupResponse


def _build_where(
    *,
    cpfcnpj: str | None,
    id_debito: int | None,
    id_processo: int | None,
    pessoa: bool,
) -> tuple[list[str], dict[str, Any]]:
    where: list[str] = []
    params: dict[str, Any] = {}
    if cpfcnpj:
        where.append("m.CpfCnpj = :cpfcnpj")
        params["cpfcnpj"] = cpfcnpj
    if id_debito is not None:
        where.append("m.IdDebito = :id_debito")
        params["id_debito"] = id_debito
    if id_processo is not None:
        where.append("m.IdProcessoExecucao = :id_processo")
        params["id_processo"] = id_processo
    return where, params


def buscar_debitos(
    session: Session,
    *,
    cpfcnpj: str | None = None,
    id_debito: int | None = None,
    id_processo: int | None = None,
    page: int = 1,
    size: int = 50,
) -> DebitoLookupResponse:
    if not (cpfcnpj or id_debito is not None or id_processo is not None):
        return DebitoLookupResponse(items=[], total=0, page=page, size=size)

    dialect = session.bind.dialect.name if session.bind is not None else "mssql"

    where_p, params_p = _build_where(
        cpfcnpj=cpfcnpj, id_debito=id_debito, id_processo=id_processo, pessoa=True
    )
    where_g, params_g = _build_where(
        cpfcnpj=cpfcnpj, id_debito=id_debito, id_processo=id_processo, pessoa=False
    )
    where_p_sql = ("WHERE " + " AND ".join(where_p)) if where_p else ""
    where_g_sql = ("WHERE " + " AND ".join(where_g)) if where_g else ""

    pagination = (
        "LIMIT :size OFFSET :offset"
        if dialect == "sqlite"
        else "OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY"
    )

    base = f"""
        SELECT
            'PESSOA' AS Matcher,
            m.IdMatchPessoa AS IdMatch,
            st.Codigo AS Status, st.Descricao AS StatusDescricao,
            c.Conta, m.Periodo,
            m.CpfCnpj, m.NomePessoa,
            m.IdDebito, m.IdProcessoExecucao,
            CAST(NULL AS INTEGER) AS IdBoleto,
            CAST(NULL AS VARCHAR(60)) AS CodigoBarras,
            m.ValorPago AS ValorPago,
            L.IdLancamento, L.DtMovimento, L.Valor AS ValorLancamento
        FROM FRAPMatchPessoa m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        JOIN FRAPConta c ON c.IdConta = m.IdConta
        LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamento
        {where_p_sql}
        UNION ALL
        SELECT
            'GUIA' AS Matcher,
            m.IdMatchGuia AS IdMatch,
            st.Codigo, st.Descricao,
            c.Conta, m.Periodo,
            m.CpfCnpj, m.NomePessoa,
            m.IdDebito, m.IdProcessoExecucao,
            m.IdBoleto, m.CodigoBarras,
            m.ValorPago,
            L.IdLancamento, L.DtMovimento, L.Valor
        FROM FRAPMatchGuia m
        JOIN FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
        JOIN FRAPConta c ON c.IdConta = m.IdConta
        LEFT JOIN FRAPLancamento L ON L.IdLancamento = m.IdLancamento
        {where_g_sql}
    """

    # Parâmetros para o WHERE de cada lado vão como o mesmo dict (mesmas chaves).
    params = {**params_p, **params_g}

    total_sql = text(f"SELECT COUNT(*) FROM ({base}) sub")
    total = int(session.execute(total_sql, params).scalar_one())

    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    page_sql = text(
        f"""
        SELECT * FROM (
            {base}
        ) sub
        ORDER BY DtMovimento DESC, IdLancamento DESC
        {pagination}
        """
    ).bindparams(bindparam("offset"), bindparam("size"))

    rows = session.execute(page_sql, page_params).mappings().all()
    items = [
        DebitoLookupItem(
            matcher=r["Matcher"],
            id_match=int(r["IdMatch"]),
            status=r["Status"],
            status_descricao=r["StatusDescricao"],
            conta=str(r["Conta"]),
            periodo=str(r["Periodo"]),
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            id_debito=r["IdDebito"],
            id_processo_execucao=r["IdProcessoExecucao"],
            id_boleto=r["IdBoleto"],
            codigo_barras=r["CodigoBarras"],
            valor_pago=r["ValorPago"],
            id_lancamento=r["IdLancamento"],
            dt_movimento=r["DtMovimento"],
            valor_lancamento=r["ValorLancamento"],
        )
        for r in rows
    ]
    return DebitoLookupResponse(items=items, total=total, page=page, size=size)
