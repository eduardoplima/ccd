"""Service do módulo desconto-folha.

Eixo "por pessoa" usa apenas BdDIP. Eixo "por órgão" depende do órgão pagador
do contracheque, que vive em BdSIAIPessoal/Bdc — a sessão (BdDIP) faz cross-DB
JOIN com `BdSIAIPessoal.dbo.*` e `Bdc.dbo.vw_Gen_Orgao`. Ambos exigem permissão
de leitura na conta SQL usada pelo backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import combinations
from typing import Any, Literal

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.desconto_folha.schemas import (
    AtrasoSistemicoItem,
    AtrasoSistemicoMes,
    AtrasoSistemicoResponse,
    CadastroManualItem,
    CadastroManualListResponse,
    CandidatoRepasseMulti,
    CpfSemSiaiItem,
    CpfSemSiaiResponse,
    AtribuirOrgaoResultado,
    DepositosOrgaoResponse,
    LancamentoDoOrgaoItem,
    LancamentosDoOrgaoResponse,
    MatchManualResultado,
    OrgaoAgregadoItem,
    OrgaoAgregadoListResponse,
    ParcelaDuplicadaItem,
    ParcelaDuplicadaResponse,
    ParcelaPessoaItem,
    ParcelasPessoaResponse,
    PessoaAgregadaItem,
    PessoaAgregadaListResponse,
    PessoaDoOrgaoItem,
    PessoasDoOrgaoResponse,
    RepasseMultiParcelaItem,
    RepasseMultiParcelaResponse,
)

_STATUS_OK = ("OK_TUDO", "MATCH_MANUAL")
_STATUS_ATRASO = ("NAO_DESCONTADA", "DESCONTADA_SEM_REPASSE", "BAIXADA_SEM_RASTRO")

# Espelha tools/frap/config.py: IdOrgaoSuperior=272 → Governo do Estado RN.
# Lançamentos depositados pelo CNPJ do Estado são expandidos para todos os
# subordinados em FRAPLancamentoOrgao.
_ID_ORGAO_SUPERIOR_ESTADO = 272


@dataclass(frozen=True, slots=True)
class _OrgaoInfo:
    cnpj_raw: str | None
    cnpj_valido: str | None
    is_estadual: bool


def _orgao_info(session: Session, id_orgao: int) -> _OrgaoInfo:
    row = session.execute(
        text(
            """
            SELECT TOP 1
                REPLACE(REPLACE(REPLACE(REPLACE(
                    LTRIM(RTRIM(ISNULL(CNPJ, ''))), '.', ''), '-', ''), '/', ''), ' ', '') AS CNPJ,
                IdOrgaoSuperior
            FROM Bdc.dbo.vw_Gen_Orgao
            WHERE IdOrgao = :id_orgao
            """
        ),
        {"id_orgao": id_orgao},
    ).first()
    cnpj_raw = (row[0] if row else None) or None
    cnpj_valido = cnpj_raw if cnpj_raw and len(cnpj_raw) == 14 else None
    id_superior = int(row[1]) if row and row[1] is not None else None
    return _OrgaoInfo(
        cnpj_raw=cnpj_raw,
        cnpj_valido=cnpj_valido,
        is_estadual=id_superior == _ID_ORGAO_SUPERIOR_ESTADO,
    )


PessoasSortKey = Literal[
    "nome",
    "cpf",
    "orgao",
    "valor_atualizado",
    "qtd_notificacoes",
    "qtd_debitos_notificados",
    "valor_debitos_notificados",
    "esperado",
]

# Whitelist de coluna → expressão SQL final. Nunca interpolar sort_by cru no SQL;
# só essas chaves chegam ao ORDER BY.
_PESSOAS_SORT_EXPR: dict[str, str] = {
    "nome": "ag.NomePessoa",
    "cpf": "ag.CpfCnpj",
    "orgao": "ag.NomeOrgaoNotificado",
    "valor_atualizado": "ISNULL(mp.ValorAtualizadoTotal, 0)",
    "qtd_notificacoes": "ISNULL(mp.QtdProcessosNotificados, 0)",
    "qtd_debitos_notificados": "ISNULL(mp.QtdDebitosNotificados, 0)",
    "valor_debitos_notificados": "ISNULL(mp.ValorDebitosNotificadosTotal, 0)",
    "esperado": "ag.TotalEsperado",
}


# ---------------------------------------------------------------------------
# CTE comum: 1 linha por parcela com o match efetivo (manual > automático).
# ---------------------------------------------------------------------------

_PARCELA_EFETIVA_CTE = """
parcela_efetiva AS (
    SELECT
        p.IdFRAPDescontoFolhaParcela,
        p.IdFRAPDescontoFolha,
        p.NumeroParcela, p.MesReferencia, p.AnoReferencia,
        p.ValorEsperado, p.DataVencimento, p.DataPagamentoParcela,
        p.SituacaoParcela, p.TipoDeBaixa,
        df.IdDescontoFolha, df.Origem, df.CpfCnpj, df.NomePessoa,
        df.IdOrgaoNotificado, df.NomeOrgaoNotificado,
        m.IdMatchDescontoFolha, m.IsManual, m.ValorContracheque,
        m.IdLancamentoFRAP, m.Observacao,
        st.Codigo AS StatusCodigo, st.Descricao AS StatusDescricao
    FROM dbo.FRAPDescontoFolhaParcela p
    JOIN dbo.FRAPDescontoFolha df ON df.IdFRAPDescontoFolha = p.IdFRAPDescontoFolha
    OUTER APPLY (
        SELECT TOP 1 m2.*
        FROM dbo.FRAPMatchDescontoFolha m2
        WHERE m2.IdFRAPDescontoFolhaParcela = p.IdFRAPDescontoFolhaParcela
        ORDER BY m2.IsManual DESC, m2.IdMatchDescontoFolha DESC
    ) m
    LEFT JOIN dbo.FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
    WHERE df.Ativo = 1
)
"""


def _periodo_where(ano: int | None, mes: int | None) -> tuple[list[str], dict[str, Any]]:
    where: list[str] = []
    params: dict[str, Any] = {}
    if ano is not None:
        where.append("pe.AnoReferencia = :ano")
        params["ano"] = ano
    if mes is not None:
        where.append("pe.MesReferencia = :mes")
        params["mes"] = mes
    return where, params


_COLLATE_CI_AI = "COLLATE SQL_Latin1_General_CP1_CI_AI"


def _like_ci_ai(col: str) -> str:
    return f"UPPER({col}) {_COLLATE_CI_AI} LIKE UPPER(:q_like) {_COLLATE_CI_AI}"


def _q_clause_pessoa_orgao(col_pessoa: str, col_orgao: str, col_cpf: str) -> str:
    return (
        f"({_like_ci_ai(col_pessoa)}"
        f" OR {_like_ci_ai(col_orgao)}"
        f" OR {col_cpf} LIKE :q_like)"
    )


def _q_norm(q: str | None) -> str | None:
    if q is None:
        return None
    s = q.strip()
    return s or None


# ---------------------------------------------------------------------------
# Por pessoa
# ---------------------------------------------------------------------------


def list_pessoas(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    status: str | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
    sort_by: PessoasSortKey | None = None,
    sort_dir: Literal["asc", "desc"] = "desc",
) -> PessoaAgregadaListResponse:
    where, params = _periodo_where(ano, mes)
    if status:
        where.append("pe.StatusCodigo = :status")
        params["status"] = status
    q_norm = _q_norm(q)
    if q_norm is not None:
        where.append(
            _q_clause_pessoa_orgao("pe.NomePessoa", "pe.NomeOrgaoNotificado", "pe.CpfCnpj")
        )
        params["q_like"] = f"%{q_norm}%"
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    if sort_by is None:
        order_by_sql = "ORDER BY ag.TotalEsperado DESC, ag.NomePessoa ASC"
    else:
        expr = _PESSOAS_SORT_EXPR[sort_by]
        direction = "ASC" if sort_dir == "asc" else "DESC"
        order_by_sql = f"ORDER BY {expr} {direction}, ag.NomePessoa ASC"

    # Pessoas sem parcelas (tipicamente Origem='C') só aparecem quando não há
    # filtro de período — período sem parcelas é vazio por construção.
    incluir_sem_parcelas = ano is None and mes is None and not status
    sem_parcelas_q_filter = ""
    if q_norm is not None:
        sem_parcelas_q_filter = " AND " + _q_clause_pessoa_orgao(
            "df.NomePessoa", "df.NomeOrgaoNotificado", "df.CpfCnpj"
        )
    sem_parcelas_union = ""
    if incluir_sem_parcelas:
        sem_parcelas_union = f"""
            UNION
            SELECT df.CpfCnpj
            FROM dbo.FRAPDescontoFolha df
            WHERE df.Ativo = 1
              AND df.CpfCnpj IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM dbo.FRAPDescontoFolhaParcela p
                  WHERE p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha
              ){sem_parcelas_q_filter}
        """

    sql_count = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE}
        SELECT COUNT(*) FROM (
            SELECT pe.CpfCnpj
            FROM parcela_efetiva pe
            {where_sql}
            GROUP BY pe.CpfCnpj
            {sem_parcelas_union}
        ) X
        """
    )
    total = int(session.execute(sql_count, params).scalar_one())

    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    sql_status_ok = ", ".join(f"'{s}'" for s in _STATUS_OK)
    sem_parcelas_agregado = ""
    if incluir_sem_parcelas:
        sem_parcelas_agregado = f"""
            UNION ALL
            SELECT
                df.CpfCnpj,
                MAX(df.NomePessoa) AS NomePessoa,
                MAX(df.IdOrgaoNotificado) AS IdOrgaoNotificado,
                MAX(df.NomeOrgaoNotificado) AS NomeOrgaoNotificado,
                0 AS QtdParcelas,
                0 AS QtdConciliadas,
                CAST(0 AS NUMERIC(18,2)) AS TotalEsperado,
                CAST(0 AS NUMERIC(18,2)) AS TotalQuitado
            FROM dbo.FRAPDescontoFolha df
            WHERE df.Ativo = 1
              AND df.CpfCnpj IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM dbo.FRAPDescontoFolhaParcela p
                  WHERE p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha
              )
              AND NOT EXISTS (
                  SELECT 1 FROM dbo.FRAPDescontoFolha df2
                  JOIN dbo.FRAPDescontoFolhaParcela p2
                       ON p2.IdFRAPDescontoFolha = df2.IdFRAPDescontoFolha
                  WHERE df2.CpfCnpj = df.CpfCnpj
              ){sem_parcelas_q_filter}
            GROUP BY df.CpfCnpj
        """

    sql = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE},
        agregado AS (
            SELECT
                pe.CpfCnpj,
                MAX(pe.NomePessoa) AS NomePessoa,
                MAX(pe.IdOrgaoNotificado) AS IdOrgaoNotificado,
                MAX(pe.NomeOrgaoNotificado) AS NomeOrgaoNotificado,
                COUNT(*) AS QtdParcelas,
                SUM(CASE WHEN pe.StatusCodigo IN ({sql_status_ok}) THEN 1 ELSE 0 END) AS QtdConciliadas,
                SUM(pe.ValorEsperado) AS TotalEsperado,
                SUM(CASE WHEN pe.StatusCodigo IN ({sql_status_ok})
                         THEN COALESCE(pe.ValorContracheque, pe.ValorEsperado) ELSE 0 END) AS TotalQuitado
            FROM parcela_efetiva pe
            {where_sql}
            GROUP BY pe.CpfCnpj
            {sem_parcelas_agregado}
        ),
        origens AS (
            SELECT df.CpfCnpj, df.Origem
            FROM dbo.FRAPDescontoFolha df
            WHERE df.Ativo = 1 AND df.CpfCnpj IS NOT NULL
            GROUP BY df.CpfCnpj, df.Origem
        )
        SELECT
            ag.CpfCnpj, ag.NomePessoa, ag.IdOrgaoNotificado, ag.NomeOrgaoNotificado,
            ag.QtdParcelas, ag.QtdConciliadas,
            ag.TotalEsperado, ag.TotalQuitado,
            ISNULL(mp.ValorAtualizadoTotal, 0) AS ValorAtualizadoTotal,
            ISNULL(mp.QtdProcessosNotificados, 0) AS QtdProcessosNotificados,
            ISNULL(mp.QtdDebitosNotificados, 0) AS QtdDebitosNotificados,
            ISNULL(mp.ValorDebitosNotificadosTotal, 0) AS ValorDebitosNotificadosTotal,
            STUFF((
                SELECT ',' + o.Origem
                FROM origens o
                WHERE o.CpfCnpj = ag.CpfCnpj
                ORDER BY o.Origem
                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(50)'), 1, 1, '') AS Origens
        FROM agregado ag
        LEFT JOIN dbo.FRAPMetricaPessoa mp ON mp.CpfCnpj = ag.CpfCnpj
        {order_by_sql}
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, page_params).mappings().all()

    items = [
        PessoaAgregadaItem(
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            id_orgao_notificado=r["IdOrgaoNotificado"],
            nome_orgao_notificado=r["NomeOrgaoNotificado"],
            qtd_parcelas=int(r["QtdParcelas"]),
            qtd_conciliadas=int(r["QtdConciliadas"] or 0),
            origens=sorted({c for c in (r["Origens"] or "").split(",") if c}),
            valor_atualizado_total=Decimal(str(r["ValorAtualizadoTotal"] or 0)),
            qtd_processos_notificados=int(r["QtdProcessosNotificados"] or 0),
            qtd_debitos_notificados=int(r["QtdDebitosNotificados"] or 0),
            valor_debitos_notificados_total=Decimal(str(r["ValorDebitosNotificadosTotal"] or 0)),
            total_esperado=Decimal(str(r["TotalEsperado"] or 0)),
            total_quitado=Decimal(str(r["TotalQuitado"] or 0)),
            saldo_aberto=Decimal(str((r["TotalEsperado"] or 0) - (r["TotalQuitado"] or 0))),
        )
        for r in rows
    ]
    return PessoaAgregadaListResponse(items=items, total=total, page=page, size=size)


def parcelas_da_pessoa(
    session: Session,
    *,
    cpfcnpj: str,
    ano: int | None = None,
) -> ParcelasPessoaResponse:
    where = ["pe.CpfCnpj = :cpf"]
    params: dict[str, Any] = {"cpf": cpfcnpj}
    if ano is not None:
        where.append("pe.AnoReferencia = :ano")
        params["ano"] = ano
    where_sql = "WHERE " + " AND ".join(where)

    sql = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE}
        SELECT
            pe.IdFRAPDescontoFolhaParcela, pe.IdFRAPDescontoFolha, pe.Origem,
            pe.NumeroParcela, pe.MesReferencia, pe.AnoReferencia,
            pe.ValorEsperado, pe.DataVencimento, pe.DataPagamentoParcela,
            pe.SituacaoParcela, pe.TipoDeBaixa,
            pe.NomePessoa, pe.IdOrgaoNotificado, pe.NomeOrgaoNotificado,
            pe.StatusCodigo, pe.StatusDescricao, pe.IsManual,
            pe.ValorContracheque, pe.IdLancamentoFRAP,
            pe.IdMatchDescontoFolha, pe.Observacao
        FROM parcela_efetiva pe
        {where_sql}
        ORDER BY pe.AnoReferencia, pe.MesReferencia, pe.NumeroParcela
        """
    )
    rows = session.execute(sql, params).mappings().all()
    if not rows:
        # Sem parcelas: ainda pode existir cadastro (Origem='C' sem parcelas, etc).
        # Busca direto em FRAPDescontoFolha pra trazer nome e órgão.
        row_df = session.execute(
            text(
                """
                SELECT TOP 1
                    MAX(NomePessoa) AS NomePessoa,
                    MAX(IdOrgaoNotificado) AS IdOrgaoNotificado,
                    MAX(NomeOrgaoNotificado) AS NomeOrgaoNotificado
                FROM dbo.FRAPDescontoFolha
                WHERE CpfCnpj = :cpf AND Ativo = 1
                """
            ),
            {"cpf": cpfcnpj},
        ).first()
        return ParcelasPessoaResponse(
            cpfcnpj=cpfcnpj,
            nome_pessoa=row_df[0] if row_df else None,
            id_orgao_notificado=int(row_df[1]) if row_df and row_df[1] is not None else None,
            nome_orgao_notificado=row_df[2] if row_df else None,
            parcelas=[],
        )

    parcelas = [
        ParcelaPessoaItem(
            id_parcela=(
                int(r["IdFRAPDescontoFolhaParcela"])
                if r["IdFRAPDescontoFolhaParcela"] is not None
                else None
            ),
            id_desconto_folha=int(r["IdFRAPDescontoFolha"]),
            origem=str(r["Origem"]),
            numero_parcela=(int(r["NumeroParcela"]) if r["NumeroParcela"] is not None else None),
            mes_referencia=(int(r["MesReferencia"]) if r["MesReferencia"] is not None else None),
            ano_referencia=(int(r["AnoReferencia"]) if r["AnoReferencia"] is not None else None),
            valor_esperado=Decimal(str(r["ValorEsperado"])),
            data_vencimento=r["DataVencimento"],
            data_pagamento=r["DataPagamentoParcela"],
            situacao_parcela=r["SituacaoParcela"],
            tipo_baixa=r["TipoDeBaixa"],
            status_codigo=r["StatusCodigo"],
            status_descricao=r["StatusDescricao"],
            is_manual=bool(r["IsManual"]) if r["IsManual"] is not None else False,
            valor_contracheque=(
                Decimal(str(r["ValorContracheque"])) if r["ValorContracheque"] is not None else None
            ),
            id_lancamento_frap=r["IdLancamentoFRAP"],
            id_match=r["IdMatchDescontoFolha"],
            observacao=r["Observacao"],
        )
        for r in rows
    ]
    # Órgão da pessoa: pega da primeira linha (todas as parcelas do mesmo CPF
    # tipicamente apontam pro mesmo DF/órgão; pega o não-nulo se houver divergência).
    id_orgao = None
    nome_orgao = None
    for r in rows:
        if r.get("IdOrgaoNotificado") is not None:
            id_orgao = int(r["IdOrgaoNotificado"])
            nome_orgao = r.get("NomeOrgaoNotificado")
            break
    return ParcelasPessoaResponse(
        cpfcnpj=rows[0]["CpfCnpj"] if "CpfCnpj" in rows[0] else cpfcnpj,
        nome_pessoa=rows[0]["NomePessoa"],
        id_orgao_notificado=id_orgao,
        nome_orgao_notificado=nome_orgao,
        parcelas=parcelas,
    )


# ---------------------------------------------------------------------------
# Por órgão notificado (df.IdOrgaoNotificado).
# 1 desconto = 1 órgão notificado. Sem cross-DB no caminho principal.
# ---------------------------------------------------------------------------


def list_orgaos(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
) -> OrgaoAgregadoListResponse:
    where, params = _periodo_where(ano, mes)
    q_norm = _q_norm(q)
    if q_norm is not None:
        where.append(_like_ci_ai("pe.NomeOrgaoNotificado"))
        params["q_like"] = f"%{q_norm}%"
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sql_count = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE}
        SELECT COUNT(*) FROM (
            SELECT pe.IdOrgaoNotificado FROM parcela_efetiva pe {where_sql}
            GROUP BY pe.IdOrgaoNotificado
        ) X
        """
    )
    total = int(session.execute(sql_count, params).scalar_one())

    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    sql_status_ok = ", ".join(f"'{s}'" for s in _STATUS_OK)
    sql = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE}
        SELECT
            pe.IdOrgaoNotificado AS IdOrgao,
            MAX(pe.NomeOrgaoNotificado) AS NomeOrgao,
            COUNT(DISTINCT pe.CpfCnpj) AS QtdPessoas,
            COUNT(*) AS QtdParcelas,
            SUM(CASE WHEN pe.StatusCodigo IN ({sql_status_ok}) THEN 1 ELSE 0 END) AS QtdConciliadas,
            SUM(pe.ValorEsperado) AS TotalEsperado,
            SUM(CASE WHEN pe.StatusCodigo IN ({sql_status_ok})
                     THEN COALESCE(pe.ValorContracheque, pe.ValorEsperado) ELSE 0 END) AS TotalQuitado
        FROM parcela_efetiva pe
        {where_sql}
        GROUP BY pe.IdOrgaoNotificado
        ORDER BY SUM(pe.ValorEsperado) DESC, MAX(pe.NomeOrgaoNotificado) ASC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, page_params).mappings().all()

    items = [
        OrgaoAgregadoItem(
            id_orgao=r["IdOrgao"],
            nome_orgao=r["NomeOrgao"],
            qtd_pessoas=int(r["QtdPessoas"]),
            qtd_parcelas=int(r["QtdParcelas"]),
            qtd_conciliadas=int(r["QtdConciliadas"]),
            total_esperado=Decimal(str(r["TotalEsperado"] or 0)),
            total_quitado=Decimal(str(r["TotalQuitado"] or 0)),
        )
        for r in rows
    ]
    return OrgaoAgregadoListResponse(items=items, total=total, page=page, size=size)


def pessoas_do_orgao(
    session: Session,
    *,
    id_orgao: int | None,
    ano: int | None = None,
    mes: int | None = None,
) -> PessoasDoOrgaoResponse | None:
    if id_orgao is None:
        where = ["pe.IdOrgaoNotificado IS NULL"]
        params: dict[str, Any] = {}
    else:
        where = ["pe.IdOrgaoNotificado = :id_orgao"]
        params = {"id_orgao": id_orgao}
    if ano is not None:
        where.append("pe.AnoReferencia = :ano")
        params["ano"] = ano
    if mes is not None:
        where.append("pe.MesReferencia = :mes")
        params["mes"] = mes
    where_sql = "WHERE " + " AND ".join(where)
    sql_status_ok = ", ".join(f"'{s}'" for s in _STATUS_OK)

    sql = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE}
        SELECT
            pe.CpfCnpj,
            MAX(pe.NomePessoa) AS NomePessoa,
            MAX(pe.NomeOrgaoNotificado) AS NomeOrgao,
            COUNT(*) AS QtdParcelas,
            SUM(CASE WHEN pe.StatusCodigo IN ({sql_status_ok}) THEN 1 ELSE 0 END) AS QtdConciliadas,
            SUM(pe.ValorEsperado) AS TotalEsperado
        FROM parcela_efetiva pe
        {where_sql}
        GROUP BY pe.CpfCnpj
        ORDER BY MAX(pe.NomePessoa) ASC
        """
    )
    rows = session.execute(sql, params).mappings().all()
    if not rows:
        return None

    pessoas = [
        PessoaDoOrgaoItem(
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            qtd_parcelas=int(r["QtdParcelas"]),
            qtd_conciliadas=int(r["QtdConciliadas"]),
            total_esperado=Decimal(str(r["TotalEsperado"] or 0)),
        )
        for r in rows
    ]
    return PessoasDoOrgaoResponse(
        id_orgao=id_orgao if id_orgao is not None else 0,
        nome_orgao=rows[0]["NomeOrgao"],
        pessoas=pessoas,
    )


# ---------------------------------------------------------------------------
# Total de depósitos feitos pelo órgão em contas FRAP.
# Cruza FRAPLancamento.CpfCnpjDepositante com Bdc.dbo.vw_Gen_Orgao.CNPJ.
# Não tenta inferir via texto/sigla — só match exato de CNPJ.
# ---------------------------------------------------------------------------


def depositos_do_orgao(session: Session, *, id_orgao: int) -> DepositosOrgaoResponse:
    info = _orgao_info(session, id_orgao)

    # Une (a) CNPJ depositante canônico + (b) inferência materializada em
    # FRAPLancamentoOrgao (populada por `frap inferir-orgaos-lancamentos`).
    # CTE com DISTINCT evita inflar SUM quando o mesmo lançamento bate em
    # ambos os critérios.
    row = session.execute(
        text(
            """
            WITH lanc_alvo AS (
                SELECT DISTINCT L.IdLancamento, L.Valor
                FROM dbo.FRAPLancamento L
                WHERE L.ValorDC = 'C'
                  AND (
                      (:cnpj IS NOT NULL AND L.CpfCnpjDepositante = :cnpj)
                      OR EXISTS (
                          SELECT 1 FROM dbo.FRAPLancamentoOrgao LO
                          WHERE LO.IdLancamento = L.IdLancamento
                            AND LO.IdOrgao = :id_orgao
                      )
                  )
            )
            SELECT COUNT(*) AS qtd, COALESCE(SUM(Valor), 0) AS total FROM lanc_alvo
            """
        ),
        {"cnpj": info.cnpj_valido, "id_orgao": id_orgao},
    ).first()
    return DepositosOrgaoResponse(
        id_orgao=id_orgao,
        cnpj=info.cnpj_raw,
        qtd=int(row[0] or 0) if row else 0,
        total=Decimal(str(row[1] or 0)) if row else Decimal(0),
        is_estadual=info.is_estadual,
    )


def lancamentos_do_orgao(session: Session, *, id_orgao: int) -> LancamentosDoOrgaoResponse:
    info = _orgao_info(session, id_orgao)

    rows = (
        session.execute(
            text(
                """
            SELECT
                L.IdLancamento,
                L.DtMovimento,
                C.Conta,
                L.Valor,
                L.Historico,
                L.Documento,
                L.Descricao,
                L.CpfCnpjDepositante,
                CASE WHEN :cnpj IS NOT NULL AND L.CpfCnpjDepositante = :cnpj
                     THEN 1 ELSE 0 END AS ViaCnpj,
                CASE WHEN EXISTS (
                        SELECT 1 FROM dbo.FRAPLancamentoOrgao LO
                        WHERE LO.IdLancamento = L.IdLancamento
                          AND LO.IdOrgao = :id_orgao
                     ) THEN 1 ELSE 0 END AS ViaInferencia
            FROM dbo.FRAPLancamento L
            JOIN dbo.FRAPConta C ON C.IdConta = L.IdConta
            WHERE L.ValorDC = 'C'
              AND (
                  (:cnpj IS NOT NULL AND L.CpfCnpjDepositante = :cnpj)
                  OR EXISTS (
                      SELECT 1 FROM dbo.FRAPLancamentoOrgao LO
                      WHERE LO.IdLancamento = L.IdLancamento
                        AND LO.IdOrgao = :id_orgao
                  )
              )
            ORDER BY L.DtMovimento DESC, L.IdLancamento DESC
            """
            ),
            {"cnpj": info.cnpj_valido, "id_orgao": id_orgao},
        )
        .mappings()
        .all()
    )

    items = [
        LancamentoDoOrgaoItem(
            id_lancamento=int(r["IdLancamento"]),
            dt_movimento=r["DtMovimento"],
            conta=str(r["Conta"]),
            valor=Decimal(str(r["Valor"] or 0)),
            historico=str(r["Historico"] or ""),
            documento=r["Documento"],
            descricao=r["Descricao"],
            cpfcnpj_depositante=r["CpfCnpjDepositante"],
            via_cnpj=bool(r["ViaCnpj"]),
            via_inferencia=bool(r["ViaInferencia"]),
        )
        for r in rows
    ]
    return LancamentosDoOrgaoResponse(id_orgao=id_orgao, items=items)


# ---------------------------------------------------------------------------
# Listar órgãos disponíveis (alimenta o dropdown do cadastro manual).
# Cross-DB: lê de Bdc.dbo.vw_Gen_Orgao filtrando por órgãos que aparecem em
# folhas de pagamento do BdSIAIPessoal — assim só aparecem órgãos relevantes.
# ---------------------------------------------------------------------------


def atribuir_orgao_pessoa(
    session: Session, *, cpfcnpj: str, id_orgao: int
) -> AtribuirOrgaoResultado | None:
    """Atribui IdOrgaoNotificado a todos os FRAPDescontoFolha do CPF sem órgão.

    Retorna None se o IdOrgao não existe em vw_Gen_Orgao ou se o CPF não tem
    nenhum cadastro ativo. Caso contrário, retorna o resultado com qtd atualizada
    e o nome do órgão.
    """
    row = session.execute(
        text(
            """
            SELECT TOP 1
                IdOrgao, LTRIM(RTRIM(NomeOrgao)) AS NomeOrgao
            FROM Bdc.dbo.vw_Gen_Orgao
            WHERE IdOrgao = :id_orgao
            """
        ),
        {"id_orgao": id_orgao},
    ).first()
    if row is None:
        return None
    nome_orgao = str(row[1])

    qtd_pessoa = session.execute(
        text("SELECT COUNT(*) FROM dbo.FRAPDescontoFolha WHERE CpfCnpj = :cpf AND Ativo = 1"),
        {"cpf": cpfcnpj},
    ).scalar_one()
    if int(qtd_pessoa) == 0:
        return None

    res = session.execute(
        text(
            """
            UPDATE dbo.FRAPDescontoFolha
            SET IdOrgaoNotificado = :id_orgao,
                NomeOrgaoNotificado = :nome_orgao
            WHERE CpfCnpj = :cpf
              AND Ativo = 1
              AND IdOrgaoNotificado IS NULL
            """
        ),
        {"id_orgao": id_orgao, "nome_orgao": nome_orgao, "cpf": cpfcnpj},
    )
    session.commit()
    return AtribuirOrgaoResultado(
        qtd_atualizados=int(res.rowcount or 0),
        id_orgao=id_orgao,
        nome_orgao=nome_orgao,
    )


def list_orgaos_disponiveis(session: Session, *, busca: str | None = None) -> list[dict[str, Any]]:
    where = []
    params: dict[str, Any] = {}
    if busca:
        where.append("UPPER(org.NomeOrgao) LIKE UPPER(:q)")
        params["q"] = f"%{busca}%"
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = text(
        f"""
        SELECT DISTINCT org.IdOrgao, LTRIM(RTRIM(org.NomeOrgao)) AS NomeOrgao
        FROM Bdc.dbo.vw_Gen_Orgao org
        {where_sql}
        ORDER BY 2
        """
    )
    rows = session.execute(sql, params).mappings().all()
    return [{"idOrgao": int(r["IdOrgao"]), "nomeOrgao": r["NomeOrgao"]} for r in rows]


# ---------------------------------------------------------------------------
# Cadastro manual
# ---------------------------------------------------------------------------


_SQL_INSERT_DESCONTO_MANUAL = """
INSERT INTO dbo.FRAPDescontoFolha
    (IdDescontoFolha, Origem, CpfCnpj, NomePessoa,
     IdOrgaoNotificado, NomeOrgaoNotificado,
     QtdParcelasPlanejadas, ValorTotalEsperado, Ativo, DataInclusao)
OUTPUT inserted.IdFRAPDescontoFolha
VALUES (NULL, 'M', :cpf, :nome,
        :id_orgao, :nome_orgao,
        :qtd, :valor_total, 1, SYSUTCDATETIME());
"""

_SQL_INSERT_PARCELA_MANUAL = """
INSERT INTO dbo.FRAPDescontoFolhaParcela
    (IdFRAPDescontoFolha, IdParcela, NumeroParcela, MesReferencia, AnoReferencia,
     ValorEsperado, DataVencimento)
VALUES
    (:id_pai, NULL, :numero_parcela, :mes, :ano, :valor, :dt_venc);
"""


def criar_cadastro_manual(
    session: Session,
    *,
    cpfcnpj: str,
    nome_pessoa: str,
    id_orgao_notificado: int,
    nome_orgao_notificado: str,
    parcelas: list[dict[str, Any]],
) -> int:
    valor_total = sum(Decimal(str(p["valor_esperado"])) for p in parcelas)
    id_pai = int(
        session.execute(
            text(_SQL_INSERT_DESCONTO_MANUAL),
            {
                "cpf": cpfcnpj,
                "nome": nome_pessoa,
                "id_orgao": id_orgao_notificado,
                "nome_orgao": nome_orgao_notificado,
                "qtd": len(parcelas),
                "valor_total": valor_total,
            },
        ).scalar_one()
    )
    session.execute(
        text(_SQL_INSERT_PARCELA_MANUAL),
        [
            {
                "id_pai": id_pai,
                "numero_parcela": int(p["numero_parcela"]),
                "mes": int(p["mes_referencia"]),
                "ano": int(p["ano_referencia"]),
                "valor": Decimal(str(p["valor_esperado"])),
                "dt_venc": p.get("data_vencimento"),
            }
            for p in parcelas
        ],
    )
    session.commit()
    return id_pai


def listar_cadastro_manual(
    session: Session,
    *,
    busca: str | None = None,
    page: int = 1,
    size: int = 50,
) -> CadastroManualListResponse:
    where = ["df.Origem = 'M'", "df.Ativo = 1"]
    params: dict[str, Any] = {}
    if busca:
        where.append("(df.CpfCnpj LIKE :q OR df.NomePessoa LIKE :q)")
        params["q"] = f"%{busca}%"
    where_sql = "WHERE " + " AND ".join(where)

    total = int(
        session.execute(
            text(f"SELECT COUNT(*) FROM dbo.FRAPDescontoFolha df {where_sql}"),
            params,
        ).scalar_one()
    )
    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}
    sql = text(
        f"""
        SELECT
            df.IdFRAPDescontoFolha, df.CpfCnpj, df.NomePessoa,
            df.IdOrgaoNotificado, df.NomeOrgaoNotificado,
            df.QtdParcelasPlanejadas, df.ValorTotalEsperado, df.DataInclusao
        FROM dbo.FRAPDescontoFolha df
        {where_sql}
        ORDER BY df.DataInclusao DESC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, page_params).mappings().all()
    items = [
        CadastroManualItem(
            id_desconto_folha=int(r["IdFRAPDescontoFolha"]),
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            id_orgao_notificado=r["IdOrgaoNotificado"],
            nome_orgao_notificado=r["NomeOrgaoNotificado"],
            qtd_parcelas=int(r["QtdParcelasPlanejadas"] or 0),
            valor_total=Decimal(str(r["ValorTotalEsperado"] or 0)),
            data_inclusao=r["DataInclusao"],
        )
        for r in rows
    ]
    return CadastroManualListResponse(items=items, total=total, page=page, size=size)


def deletar_cadastro_manual(session: Session, id_desconto_folha: int) -> str:
    """Retorna 'ok', 'not_found', 'has_match', 'not_manual'."""
    row = session.execute(
        text("SELECT Origem FROM dbo.FRAPDescontoFolha WHERE IdFRAPDescontoFolha = :id"),
        {"id": id_desconto_folha},
    ).first()
    if row is None:
        return "not_found"
    if row[0] != "M":
        return "not_manual"
    n_match = int(
        session.execute(
            text(
                """
                SELECT COUNT(*) FROM dbo.FRAPMatchDescontoFolha m
                JOIN dbo.FRAPDescontoFolhaParcela p
                  ON p.IdFRAPDescontoFolhaParcela = m.IdFRAPDescontoFolhaParcela
                WHERE p.IdFRAPDescontoFolha = :id
                """
            ),
            {"id": id_desconto_folha},
        ).scalar_one()
    )
    if n_match > 0:
        return "has_match"
    session.execute(
        text("DELETE FROM dbo.FRAPDescontoFolhaParcela WHERE IdFRAPDescontoFolha = :id"),
        {"id": id_desconto_folha},
    )
    session.execute(
        text("DELETE FROM dbo.FRAPDescontoFolha WHERE IdFRAPDescontoFolha = :id"),
        {"id": id_desconto_folha},
    )
    session.commit()
    return "ok"


# ---------------------------------------------------------------------------
# Match manual
# ---------------------------------------------------------------------------


def criar_match_manual(
    session: Session,
    *,
    id_lancamento_frap: int,
    ids_parcela: list[int],
    id_usuario: int,
    observacao: str | None,
) -> MatchManualResultado:
    # status MATCH_MANUAL
    id_status = int(
        session.execute(
            text(
                "SELECT IdStatusMatch FROM dbo.FRAPStatusMatch "
                "WHERE Matcher = 'DESCONTO_FOLHA' AND Codigo = 'MATCH_MANUAL'"
            )
        ).scalar_one()
    )
    sql = text(
        """
        INSERT INTO dbo.FRAPMatchDescontoFolha
            (IdFRAPDescontoFolhaParcela, IdLancamentoFRAP, IdStatusMatch,
             IsManual, IdUsuarioConcilia, DataConcilia, Observacao)
        OUTPUT inserted.IdMatchDescontoFolha
        VALUES (:id_parcela, :id_lanc, :id_status, 1, :id_usuario, SYSUTCDATETIME(), :obs);
        """
    )
    ids_match: list[int] = []
    for id_parcela in ids_parcela:
        rid = session.execute(
            sql,
            {
                "id_parcela": id_parcela,
                "id_lanc": id_lancamento_frap,
                "id_status": id_status,
                "id_usuario": id_usuario,
                "obs": observacao,
            },
        ).scalar_one()
        ids_match.append(int(rid))
    session.commit()
    return MatchManualResultado(matches_criados=len(ids_match), ids_match=ids_match)


def deletar_match_manual(session: Session, id_match: int) -> str:
    row = session.execute(
        text("SELECT IsManual FROM dbo.FRAPMatchDescontoFolha WHERE IdMatchDescontoFolha = :id"),
        {"id": id_match},
    ).first()
    if row is None:
        return "not_found"
    if not bool(row[0]):
        return "not_manual"
    session.execute(
        text("DELETE FROM dbo.FRAPMatchDescontoFolha WHERE IdMatchDescontoFolha = :id"),
        {"id": id_match},
    )
    session.commit()
    return "ok"


# ---------------------------------------------------------------------------
# Tipologia 1.2: Repasse multi-parcela
#
# Lançamentos OB_RECEBIDA cujo Valor ≈ soma de 2+ parcelas em atraso da mesma
# pessoa. Identifica casos onde o credor pagou várias parcelas em um único
# repasse — comum quando o servidor está em atraso há vários meses.
# ---------------------------------------------------------------------------

_TOLERANCIA_VALOR = Decimal("0.02")
_MAX_COMBINACAO_TAM = 5


def tipologia_repasse_multi_parcela(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    cpfcnpj: str | None = None,
) -> RepasseMultiParcelaResponse:
    where_l: list[str] = [
        "cat.Codigo = 'OB_RECEBIDA'",
        "L.CpfCnpjDepositante IS NOT NULL",
        "L.ValorDC = 'C'",
    ]
    params: dict[str, Any] = {}
    if ano is not None:
        where_l.append("YEAR(L.DtMovimento) = :ano")
        params["ano"] = ano
    if mes is not None:
        where_l.append("MONTH(L.DtMovimento) = :mes")
        params["mes"] = mes
    if cpfcnpj:
        cpf_norm = "".join(c for c in cpfcnpj if c.isdigit())
        if len(cpf_norm) == 11:
            where_l.append("RIGHT(L.CpfCnpjDepositante, 11) = :cpf")
        else:
            where_l.append("L.CpfCnpjDepositante = :cpf")
        params["cpf"] = cpf_norm
    where_sql = " AND ".join(where_l)

    sql_lanc = text(
        f"""
        SELECT
            L.IdLancamento, L.DtMovimento, L.Valor, L.Historico,
            L.CpfCnpjDepositante,
            RIGHT(L.CpfCnpjDepositante, 11) AS CpfNorm,
            (SELECT TOP 1 df.NomePessoa FROM dbo.FRAPDescontoFolha df
              WHERE df.CpfCnpj = RIGHT(L.CpfCnpjDepositante, 11) AND df.Ativo = 1
              ORDER BY df.IdFRAPDescontoFolha DESC) AS NomePessoa
        FROM dbo.FRAPLancamento L
        JOIN dbo.FRAPCategoria cat ON cat.IdCategoria = L.IdCategoria
        WHERE {where_sql}
          AND NOT EXISTS (
              SELECT 1 FROM dbo.FRAPMatchDescontoFolha m
              JOIN dbo.FRAPStatusMatch s ON s.IdStatusMatch = m.IdStatusMatch
              WHERE m.IdLancamentoFRAP = L.IdLancamento
                AND s.Codigo IN ('OK_TUDO', 'MATCH_MANUAL')
          )
        ORDER BY L.DtMovimento DESC, L.IdLancamento DESC
        """
    )
    lancamentos = session.execute(sql_lanc, params).mappings().all()
    if not lancamentos:
        return RepasseMultiParcelaResponse(items=[])

    cpfs = list({r["CpfNorm"] for r in lancamentos if r["CpfNorm"]})
    if not cpfs:
        return RepasseMultiParcelaResponse(items=[])
    sql_parcelas = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE}
        SELECT pe.IdFRAPDescontoFolhaParcela, pe.CpfCnpj,
               pe.NumeroParcela, pe.MesReferencia, pe.AnoReferencia,
               pe.ValorEsperado, pe.StatusCodigo
        FROM parcela_efetiva pe
        WHERE pe.CpfCnpj IN :cpfs
          AND pe.IdFRAPDescontoFolhaParcela IS NOT NULL
          AND pe.StatusCodigo IN ('NAO_DESCONTADA', 'DESCONTADA_SEM_REPASSE', 'BAIXADA_SEM_RASTRO')
        """
    ).bindparams(bindparam("cpfs", expanding=True))
    parcelas_rows = session.execute(sql_parcelas, {"cpfs": cpfs}).mappings().all()

    parcelas_por_cpf: dict[str, list[dict[str, Any]]] = {}
    for r in parcelas_rows:
        parcelas_por_cpf.setdefault(r["CpfCnpj"], []).append(
            {
                "id": int(r["IdFRAPDescontoFolhaParcela"]),
                "num": int(r["NumeroParcela"]) if r["NumeroParcela"] is not None else None,
                "mes": int(r["MesReferencia"]) if r["MesReferencia"] is not None else None,
                "ano": int(r["AnoReferencia"]) if r["AnoReferencia"] is not None else None,
                "valor": Decimal(str(r["ValorEsperado"])),
            }
        )

    items: list[RepasseMultiParcelaItem] = []
    for L in lancamentos:
        cpf = L["CpfNorm"]
        candidatas = parcelas_por_cpf.get(cpf, []) if cpf else []
        if len(candidatas) < 2:
            continue
        valor_l = Decimal(str(L["Valor"]))
        encontradas: list[CandidatoRepasseMulti] = []
        for tam in range(2, min(_MAX_COMBINACAO_TAM, len(candidatas)) + 1):
            for combo in combinations(candidatas, tam):
                soma = sum((p["valor"] for p in combo), Decimal("0"))
                if abs(soma - valor_l) <= _TOLERANCIA_VALOR:
                    desc = " + ".join(
                        f"{p['num'] or '?'}ª {str(p['mes']).zfill(2)}/{p['ano']}"
                        if p["mes"] and p["ano"]
                        else f"#{p['id']}"
                        for p in combo
                    )
                    encontradas.append(
                        CandidatoRepasseMulti(
                            ids_parcela=[p["id"] for p in combo],
                            soma_candidata=soma,
                            descricao_combinacao=desc,
                        )
                    )
            if encontradas:
                break  # pega só a menor combinação que bate
        if encontradas:
            items.append(
                RepasseMultiParcelaItem(
                    id_lancamento=int(L["IdLancamento"]),
                    dt_movimento=L["DtMovimento"],
                    valor=valor_l,
                    historico=L["Historico"],
                    cpfcnpj=cpf,
                    nome_pessoa=L["NomePessoa"],
                    candidatos=encontradas,
                )
            )
    return RepasseMultiParcelaResponse(items=items)


# ---------------------------------------------------------------------------
# Tipologia 1.3: CPF sem cadastro em SIAIPessoal
# Cross-DB com BdSIAIPessoal.dbo.Comum_Pessoa
# ---------------------------------------------------------------------------


def tipologia_cpf_sem_siaipessoal(session: Session) -> CpfSemSiaiResponse:
    sql = text(
        """
        SELECT
            df.IdFRAPDescontoFolha, df.CpfCnpj, df.NomePessoa, df.Origem,
            df.NomeOrgaoNotificado,
            (SELECT COUNT(*) FROM dbo.FRAPDescontoFolhaParcela p
              WHERE p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha) AS Qtd
        FROM dbo.FRAPDescontoFolha df
        LEFT JOIN BdSIAIPessoal.dbo.Comum_Pessoa cp ON cp.CPF = df.CpfCnpj
        WHERE df.Ativo = 1
          AND df.CpfCnpj IS NOT NULL
          AND LEN(df.CpfCnpj) = 11
          AND cp.IdPessoa IS NULL
        ORDER BY df.NomePessoa
        """
    )
    rows = session.execute(sql).mappings().all()
    items = [
        CpfSemSiaiItem(
            id_desconto_folha=int(r["IdFRAPDescontoFolha"]),
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            origem=str(r["Origem"]),
            qtd_parcelas=int(r["Qtd"] or 0),
            nome_orgao_notificado=r["NomeOrgaoNotificado"],
        )
        for r in rows
    ]
    return CpfSemSiaiResponse(items=items)


# ---------------------------------------------------------------------------
# Tipologia 1.4: Parcela duplicada
# Mesmo (IdFRAPDescontoFolha, NumeroParcela, MesReferencia, AnoReferencia, ValorEsperado)
# com 2+ linhas distintas em FRAPDescontoFolhaParcela.
# ---------------------------------------------------------------------------


def tipologia_parcela_duplicada(
    session: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
) -> ParcelaDuplicadaResponse:
    where = ["df.Ativo = 1"]
    params: dict[str, Any] = {}
    if ano is not None:
        where.append("p.AnoReferencia = :ano")
        params["ano"] = ano
    if mes is not None:
        where.append("p.MesReferencia = :mes")
        params["mes"] = mes
    where_sql = "WHERE " + " AND ".join(where)
    sql = text(
        f"""
        WITH dup AS (
            SELECT p.IdFRAPDescontoFolha, p.NumeroParcela, p.MesReferencia, p.AnoReferencia,
                   p.ValorEsperado, COUNT(*) AS Qtd
            FROM dbo.FRAPDescontoFolhaParcela p
            JOIN dbo.FRAPDescontoFolha df ON df.IdFRAPDescontoFolha = p.IdFRAPDescontoFolha
            {where_sql}
            GROUP BY p.IdFRAPDescontoFolha, p.NumeroParcela, p.MesReferencia, p.AnoReferencia,
                     p.ValorEsperado
            HAVING COUNT(*) > 1
        )
        SELECT df.IdFRAPDescontoFolha, df.CpfCnpj, df.NomePessoa,
               dup.NumeroParcela, dup.MesReferencia, dup.AnoReferencia,
               dup.ValorEsperado, dup.Qtd,
               STUFF((
                  SELECT ',' + CAST(p2.IdFRAPDescontoFolhaParcela AS VARCHAR(20))
                  FROM dbo.FRAPDescontoFolhaParcela p2
                  WHERE p2.IdFRAPDescontoFolha = dup.IdFRAPDescontoFolha
                    AND p2.NumeroParcela = dup.NumeroParcela
                    AND p2.MesReferencia = dup.MesReferencia
                    AND p2.AnoReferencia = dup.AnoReferencia
                    AND p2.ValorEsperado = dup.ValorEsperado
                  FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'),
                1, 1, '') AS IdsCSV
        FROM dup
        JOIN dbo.FRAPDescontoFolha df ON df.IdFRAPDescontoFolha = dup.IdFRAPDescontoFolha
        ORDER BY df.NomePessoa, dup.AnoReferencia, dup.MesReferencia
        """
    )
    rows = session.execute(sql, params).mappings().all()
    items = [
        ParcelaDuplicadaItem(
            id_desconto_folha=int(r["IdFRAPDescontoFolha"]),
            cpfcnpj=r["CpfCnpj"],
            nome_pessoa=r["NomePessoa"],
            numero_parcela=int(r["NumeroParcela"]),
            mes_referencia=int(r["MesReferencia"]),
            ano_referencia=int(r["AnoReferencia"]),
            valor_esperado=Decimal(str(r["ValorEsperado"])),
            qtd=int(r["Qtd"]),
            ids_parcela=[int(x) for x in str(r["IdsCSV"]).split(",") if x],
        )
        for r in rows
    ]
    return ParcelaDuplicadaResponse(items=items)


# ---------------------------------------------------------------------------
# Tipologia 1.5: Atraso sistemático por órgão
# Para cada (orgão, mês) computa pct de NAO_DESCONTADA. Reporta órgãos com
# >= N meses CONSECUTIVOS acima do threshold.
# ---------------------------------------------------------------------------


def tipologia_atraso_sistemico(
    session: Session,
    *,
    ano: int | None = None,
    meses_consecutivos: int = 3,
    pct_minimo: float = 0.2,
) -> AtrasoSistemicoResponse:
    where = [
        "pe.AnoReferencia IS NOT NULL",
        "pe.MesReferencia IS NOT NULL",
        "pe.Virtual = 0",
    ]
    params: dict[str, Any] = {}
    if ano is not None:
        where.append("pe.AnoReferencia = :ano")
        params["ano"] = ano
    where_sql = "WHERE " + " AND ".join(where)
    sql = text(
        f"""
        WITH {_PARCELA_EFETIVA_CTE}
        SELECT
            pe.IdOrgaoNotificado, MAX(pe.NomeOrgaoNotificado) AS NomeOrgao,
            pe.AnoReferencia, pe.MesReferencia,
            COUNT(*) AS QtdParcelas,
            SUM(CASE WHEN pe.StatusCodigo = 'NAO_DESCONTADA' THEN 1 ELSE 0 END) AS QtdNaoDesc
        FROM parcela_efetiva pe
        {where_sql}
        GROUP BY pe.IdOrgaoNotificado, pe.AnoReferencia, pe.MesReferencia
        ORDER BY pe.IdOrgaoNotificado, pe.AnoReferencia, pe.MesReferencia
        """
    )
    rows = session.execute(sql, params).mappings().all()

    by_orgao: dict[int | None, dict[str, Any]] = {}
    for r in rows:
        key = r["IdOrgaoNotificado"]
        bucket = by_orgao.setdefault(key, {"nome": r["NomeOrgao"], "meses": []})
        if r["NomeOrgao"]:
            bucket["nome"] = r["NomeOrgao"]
        qtd = int(r["QtdParcelas"])
        atraso = int(r["QtdNaoDesc"])
        pct = (atraso / qtd) if qtd else 0.0
        bucket["meses"].append(
            {
                "ano": int(r["AnoReferencia"]),
                "mes": int(r["MesReferencia"]),
                "qtd": qtd,
                "atraso": atraso,
                "pct": pct,
            }
        )

    items: list[AtrasoSistemicoItem] = []
    for id_orgao, data in by_orgao.items():
        meses = data["meses"]
        # encontrar maior corrida consecutiva acima do threshold (em ordem de calendário)
        run_atual = 0
        run_max = 0
        run_max_meses: list[dict[str, Any]] = []
        run_atual_meses: list[dict[str, Any]] = []
        prev: tuple[int, int] | None = None
        for m in meses:
            consec = prev is None or _eh_mes_seguinte(prev, (m["ano"], m["mes"]))
            if m["pct"] >= pct_minimo and consec:
                run_atual += 1
                run_atual_meses.append(m)
            else:
                if m["pct"] >= pct_minimo:
                    run_atual = 1
                    run_atual_meses = [m]
                else:
                    run_atual = 0
                    run_atual_meses = []
            if run_atual > run_max:
                run_max = run_atual
                run_max_meses = list(run_atual_meses)
            prev = (m["ano"], m["mes"])

        if run_max >= meses_consecutivos:
            pct_medio = sum(m["pct"] for m in run_max_meses) / len(run_max_meses)
            items.append(
                AtrasoSistemicoItem(
                    id_orgao=id_orgao,
                    nome_orgao=data["nome"],
                    qtd_meses_consecutivos=run_max,
                    pct_medio=round(pct_medio, 4),
                    detalhe_meses=[
                        AtrasoSistemicoMes(
                            ano=m["ano"],
                            mes=m["mes"],
                            pct_atraso=round(m["pct"], 4),
                            qtd_parcelas=m["qtd"],
                            qtd_em_atraso=m["atraso"],
                        )
                        for m in run_max_meses
                    ],
                )
            )

    items.sort(key=lambda x: (-x.qtd_meses_consecutivos, -x.pct_medio))
    return AtrasoSistemicoResponse(items=items)


def _eh_mes_seguinte(prev: tuple[int, int], curr: tuple[int, int]) -> bool:
    pa, pm = prev
    ca, cm = curr
    if ca == pa and cm == pm + 1:
        return True
    if ca == pa + 1 and pm == 12 and cm == 1:
        return True
    return False
