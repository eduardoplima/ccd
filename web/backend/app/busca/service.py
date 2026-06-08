"""Busca por pessoa (nome/CPF) e por processo (NUP).

Toda query passa por `dbo.GenPessoa`, `dbo.Exe_Debito`, `dbo.Exe_DebitoPessoa` e
`dbo.Processos`. O caminho é o mesmo do legado de execução — ver
`tools/frap/processo/repos.py:23` para o pattern de normalização de documento.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.busca.schemas import (
    DebitoPessoaItem,
    DebitoPessoaListResponse,
    PessoaItem,
    PessoaListResponse,
    ProcessoHeader,
    ProcessoResultado,
)

# Normalização do Documento — mesma usada em tools/frap/processo/repos.py.
_DOC_NORM = "REPLACE(REPLACE(REPLACE(REPLACE(GP.Documento, '.', ''), '-', ''), '/', ''), ' ', '')"


def buscar_pessoas(session: Session, *, q: str, page: int, size: int) -> PessoaListResponse:
    q_norm = q.strip()
    so_digitos = q_norm.replace(".", "").replace("-", "").replace("/", "").replace(" ", "")
    is_doc = so_digitos.isdigit() and len(so_digitos) >= 11

    if is_doc:
        where = f"{_DOC_NORM} = :q"
        params: dict[str, Any] = {"q": so_digitos}
    else:
        # Nome: LIKE com COLLATE accent-insensitive (cai no padrão SQL Server).
        where = (
            "UPPER(GP.Nome) COLLATE SQL_Latin1_General_CP1_CI_AI "
            "LIKE UPPER(:q) COLLATE SQL_Latin1_General_CP1_CI_AI"
        )
        params = {"q": f"%{q_norm}%"}

    total = int(
        session.execute(
            text(
                f"""
                SELECT COUNT(*) FROM dbo.GenPessoa GP
                WHERE {where}
                """
            ),
            params,
        ).scalar_one()
    )

    offset = (page - 1) * size
    sql = text(
        f"""
        SELECT
            GP.IdPessoa,
            {_DOC_NORM} AS CpfCnpj,
            GP.Nome,
            (SELECT COUNT(*) FROM dbo.Exe_DebitoPessoa EDP
             WHERE EDP.IDPessoa = GP.IdPessoa) AS QtdDebitos
        FROM dbo.GenPessoa GP
        WHERE {where}
        ORDER BY GP.Nome ASC
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = session.execute(sql, {**params, "offset": offset, "size": size}).mappings().all()

    items = [
        PessoaItem(
            id_pessoa=int(r["IdPessoa"]),
            cpfcnpj=r["CpfCnpj"],
            nome=r["Nome"],
            qtd_debitos=int(r["QtdDebitos"] or 0),
        )
        for r in rows
    ]
    return PessoaListResponse(items=items, total=total)


def buscar_processo(
    session: Session,
    *,
    numero: str,
    ano: str,
    tipo: Literal["origem", "execucao"],
) -> ProcessoResultado | None:
    # NUP padrão tem 6 dígitos pra `numero_processo`.
    numero_padded = numero.zfill(6)
    proc = (
        session.execute(
            text(
                """
            SELECT TOP 1 IdProcesso, numero_processo, ano_processo,
                   assunto, interessado, valor
            FROM dbo.Processos
            WHERE numero_processo = :num AND ano_processo = :ano
            """
            ),
            {"num": numero_padded, "ano": ano},
        )
        .mappings()
        .first()
    )
    if proc is None:
        return None

    id_processo = int(proc["IdProcesso"])
    coluna_fk = "IdProcessoOrigem" if tipo == "origem" else "IdProcessoExecucao"

    rows = (
        session.execute(
            text(
                f"""
            SELECT
                GP.IdPessoa,
                {_DOC_NORM} AS CpfCnpj,
                GP.Nome,
                COUNT(DISTINCT ED.IdDebito) AS QtdDebitos
            FROM dbo.Exe_Debito ED
            JOIN dbo.Exe_DebitoPessoa EDP ON EDP.IDDebito = ED.IdDebito
            JOIN dbo.GenPessoa GP         ON GP.IdPessoa  = EDP.IDPessoa
            WHERE ED.{coluna_fk} = :id_processo
            GROUP BY GP.IdPessoa, GP.Documento, GP.Nome
            ORDER BY GP.Nome ASC
            """
            ),
            {"id_processo": id_processo},
        )
        .mappings()
        .all()
    )

    pessoas = [
        PessoaItem(
            id_pessoa=int(r["IdPessoa"]),
            cpfcnpj=r["CpfCnpj"],
            nome=r["Nome"],
            qtd_debitos=int(r["QtdDebitos"] or 0),
        )
        for r in rows
    ]

    header = ProcessoHeader(
        id_processo=id_processo,
        numero_processo=str(proc["numero_processo"]).strip(),
        ano_processo=str(proc["ano_processo"]).strip(),
        assunto=proc["assunto"].strip() if proc["assunto"] else None,
        interessado=proc["interessado"].strip() if proc["interessado"] else None,
        valor=Decimal(str(proc["valor"])) if proc["valor"] is not None else None,
    )
    return ProcessoResultado(processo=header, tipo=tipo, pessoas=pessoas)


def buscar_debitos_pessoa(
    session: Session,
    *,
    cpfcnpj: str,
    id_processo: int | None,
) -> DebitoPessoaListResponse:
    where = [f"{_DOC_NORM} = :cpf"]
    params: dict[str, Any] = {"cpf": cpfcnpj}
    if id_processo is not None:
        where.append("(ED.IdProcessoOrigem = :idp OR ED.IdProcessoExecucao = :idp)")
        params["idp"] = id_processo
    where_sql = " AND ".join(where)

    rows = (
        session.execute(
            text(
                f"""
            SELECT
                ED.IdDebito, ED.IdProcessoOrigem, ED.IdProcessoExecucao,
                ED.valorOriginalDebito, ED.ValorPago, ED.dataAto, ED.dataBaixa,
                (SELECT COUNT(*) FROM dbo.FRAPMatchPessoa MP
                  WHERE MP.IdDebito = ED.IdDebito) AS MatchesPessoa,
                (SELECT COUNT(*) FROM dbo.FRAPMatchGuia MG
                  WHERE MG.IdDebito = ED.IdDebito) AS MatchesGuia
            FROM dbo.Exe_Debito ED
            JOIN dbo.Exe_DebitoPessoa EDP ON EDP.IDDebito = ED.IdDebito
            JOIN dbo.GenPessoa GP         ON GP.IdPessoa  = EDP.IDPessoa
            WHERE {where_sql} AND ED.DataCancelamento IS NULL
            ORDER BY ED.dataAto DESC, ED.IdDebito DESC
            """
            ),
            params,
        )
        .mappings()
        .all()
    )

    items = [
        DebitoPessoaItem(
            id_debito=int(r["IdDebito"]),
            id_processo_origem=r["IdProcessoOrigem"],
            id_processo_execucao=r["IdProcessoExecucao"],
            valor_original_debito=(
                Decimal(str(r["valorOriginalDebito"]))
                if r["valorOriginalDebito"] is not None
                else None
            ),
            valor_pago=Decimal(str(r["ValorPago"])) if r["ValorPago"] is not None else None,
            data_ato=r["dataAto"],
            data_baixa=r["dataBaixa"],
            matches_pessoa=int(r["MatchesPessoa"] or 0),
            matches_guia=int(r["MatchesGuia"] or 0),
        )
        for r in rows
    ]
    return DebitoPessoaListResponse(items=items, total=len(items))
