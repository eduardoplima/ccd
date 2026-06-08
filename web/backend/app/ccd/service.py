from __future__ import annotations

from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.schemas import (
    FiltrosCCDResponse,
    MarcadorOption,
    ProcessoCCDListResponse,
    ProcessoCCDOut,
    RelatorOption,
)

# Setor CCD no banco `processo` (Setor.idSetor / Pro_Marcador.IdSetor).
ID_SETOR_CCD = 762

# Whitelist de ordenação: chave de coluna -> expressão SQL (nunca interpolar input).
_SORT_COLUMNS: dict[str, str] = {
    "processo": "p.ano_processo, p.numero_processo",
    "marcador": "mc.marcador",
    "data_marcador": "mc.DataInclusao",
    "origem": "o.nome",
    "relator": "r.nome",
    "tipo": "t.descricao",
    "assunto": "p.assunto",
}
_DEFAULT_ORDER = "mc.DataInclusao DESC, p.ano_processo DESC, p.numero_processo DESC"


def listar_processos(
    session: Session,
    *,
    marcador: str | None = None,
    sem_marcador: bool = False,
    relator: str | None = None,
    assunto: str | None = None,
    sort: str | None = None,
    order: str = "asc",
    page: int = 1,
    size: int = 100,
) -> ProcessoCCDListResponse:
    where: list[str] = ["p.setor_atual = 'CCD'", "p.IdProcessoApensador IS NULL"]
    params: dict[str, Any] = {"id_setor": ID_SETOR_CCD}

    if sem_marcador:
        where.append("mc.marcador IS NULL")
    elif marcador:
        where.append("mc.marcador = :marcador")
        params["marcador"] = marcador
    if relator:
        where.append("p.codigo_relator = :relator_codigo")
        params["relator_codigo"] = relator
    if assunto:
        where.append("p.assunto LIKE :assunto")
        params["assunto"] = f"%{assunto}%"

    where_sql = " AND ".join(where)
    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}

    if sort in _SORT_COLUMNS:
        direction = "DESC" if str(order).lower() == "desc" else "ASC"
        if sort == "processo":
            order_sql = f"p.ano_processo {direction}, p.numero_processo {direction}"
        else:
            # desempate estável por processo (colunas distintas da de ordenação)
            order_sql = (
                f"{_SORT_COLUMNS[sort]} {direction}, "
                "p.ano_processo DESC, p.numero_processo DESC"
            )
    else:
        order_sql = _DEFAULT_ORDER

    sql = text(
        f"""
        WITH marc AS (
            SELECT mp.IdProcesso, m.Descricao AS marcador, mp.DataInclusao,
                   ROW_NUMBER() OVER (
                       PARTITION BY mp.IdProcesso ORDER BY mp.DataInclusao DESC
                   ) AS rn
            FROM dbo.Pro_MarcadorProcesso mp
            JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
            WHERE m.IdSetor = :id_setor AND mp.DataExclusao IS NULL
        )
        SELECT
            RTRIM(p.numero_processo) AS numero_processo,
            RTRIM(p.ano_processo)    AS ano_processo,
            RTRIM(mc.marcador)       AS marcador,
            mc.DataInclusao          AS data_marcador,
            RTRIM(o.nome)            AS origem,
            RTRIM(r.nome)            AS relator,
            RTRIM(t.descricao)       AS tipo,
            RTRIM(p.assunto)         AS assunto,
            COUNT(*) OVER()          AS total
        FROM dbo.Processos p
        LEFT JOIN marc mc      ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
        LEFT JOIN dbo.Relator r ON r.codigo = p.codigo_relator
        LEFT JOIN dbo.Tipo t    ON t.codigo = p.codigo_tipo_processo
        LEFT JOIN dbo.Orgaos o  ON o.codigo = p.sigla_origem
        WHERE {where_sql}
        ORDER BY {order_sql}
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))

    rows = session.execute(sql, page_params).mappings().all()
    total = int(rows[0]["total"]) if rows else 0

    items = [
        ProcessoCCDOut(
            processo=f"{r['numero_processo']}/{r['ano_processo']}",
            numero_processo=r["numero_processo"],
            ano_processo=r["ano_processo"],
            marcador=r["marcador"],
            data_marcador=r["data_marcador"],
            origem=r["origem"],
            relator=r["relator"],
            tipo=r["tipo"],
            assunto=r["assunto"],
        )
        for r in rows
    ]
    return ProcessoCCDListResponse(items=items, total=total, page=page, size=size)


def listar_filtros(session: Session) -> FiltrosCCDResponse:
    # Contagem de processos do conjunto por marcador-CCD MAIS RECENTE. O grupo
    # NULL (marcador IS NULL) é a contagem de "sem marcador".
    rows = session.execute(
        text(
            """
            WITH marc AS (
                SELECT mp.IdProcesso, m.Descricao AS marcador,
                       ROW_NUMBER() OVER (
                           PARTITION BY mp.IdProcesso ORDER BY mp.DataInclusao DESC
                       ) AS rn
                FROM dbo.Pro_MarcadorProcesso mp
                JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
                WHERE m.IdSetor = :id_setor AND mp.DataExclusao IS NULL
            )
            SELECT RTRIM(mc.marcador) AS descricao, COUNT(*) AS quantidade
            FROM dbo.Processos p
            LEFT JOIN marc mc ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
            WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
            GROUP BY RTRIM(mc.marcador)
            ORDER BY descricao
            """
        ),
        {"id_setor": ID_SETOR_CCD},
    ).mappings().all()

    marcadores = [
        MarcadorOption(descricao=str(r["descricao"]).strip(), quantidade=int(r["quantidade"]))
        for r in rows
        if r["descricao"]
    ]
    sem_marcador = next((int(r["quantidade"]) for r in rows if not r["descricao"]), 0)

    relatores = [
        RelatorOption(codigo=str(r["codigo"]).strip(), nome=str(r["nome"]).strip())
        for r in session.execute(
            text(
                """
                SELECT DISTINCT RTRIM(r.codigo) AS codigo, RTRIM(r.nome) AS nome
                FROM dbo.Processos p
                JOIN dbo.Relator r ON r.codigo = p.codigo_relator
                WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
                ORDER BY nome
                """
            )
        ).mappings().all()
    ]

    return FiltrosCCDResponse(
        marcadores=marcadores, sem_marcador=sem_marcador, relatores=relatores
    )
