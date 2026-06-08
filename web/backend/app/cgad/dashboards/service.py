"""Dashboards business logic.

One entry point: ``compute_summary`` runs a handful of aggregate queries and
returns a single ``DashboardSummary`` ready to render. All "atividade"
counters filter by ``DataRevisao`` on the staging audit row; the
``pendentes_*`` snapshot ignores the date range (current inbox state).

Aggregations small enough to fit in one page are finalised in Python after the
query — simpler than UNION/CTE in SQLAlchemy core and the row count is bounded
by reviewer activity in the period.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.cgad.dashboards import schemas
from cgad.etl.staging import (
    ObrigacaoStagingORM,
    RecomendacaoStagingORM,
    ReviewStatus,
)
from cgad.models import ObrigacaoORM, RecomendacaoORM


def _to_period_bounds(start_date: date, end_date: date) -> tuple[datetime, datetime]:
    """Half-open day range expressed as inclusive datetime bounds: from
    ``start 00:00:00`` to ``end 23:59:59.999999``. Matches the way ``DataRevisao``
    is stored (UTC-naive datetime) so a date-only filter doesn't accidentally
    drop reviews made on ``end_date``.
    """
    return (
        datetime.combine(start_date, time.min),
        datetime.combine(end_date, time.max),
    )


def _count_pending(
    session: Session, final_orm, staging_orm, fk_col, pk_col, staging_pk
) -> int:
    stmt = (
        select(func.count())
        .select_from(final_orm)
        .outerjoin(staging_orm, fk_col == pk_col)
        .where(staging_pk.is_(None))
    )
    return int(session.execute(stmt).scalar_one())


def _count_pendentes_obrigacao(session: Session) -> int:
    return _count_pending(
        session,
        ObrigacaoORM,
        ObrigacaoStagingORM,
        ObrigacaoStagingORM.IdObrigacao,
        ObrigacaoORM.IdObrigacao,
        ObrigacaoStagingORM.IdObrigacaoStaging,
    )


def _count_pendentes_recomendacao(session: Session) -> int:
    return _count_pending(
        session,
        RecomendacaoORM,
        RecomendacaoStagingORM,
        RecomendacaoStagingORM.IdRecomendacao,
        RecomendacaoORM.IdRecomendacao,
        RecomendacaoStagingORM.IdRecomendacaoStaging,
    )


def _aggregate_orgaos(
    session: Session, start: datetime, end: datetime
) -> list[schemas.OrgaoBucket]:
    obrig_rows = session.execute(
        select(
            ObrigacaoStagingORM.OrgaoResponsavel.label("nome"),
            func.count().label("count"),
        )
        .where(
            ObrigacaoStagingORM.Status == ReviewStatus.approved,
            ObrigacaoStagingORM.DataRevisao.between(start, end),
            ObrigacaoStagingORM.OrgaoResponsavel.is_not(None),
        )
        .group_by(ObrigacaoStagingORM.OrgaoResponsavel)
    ).all()

    recom_rows = session.execute(
        select(
            RecomendacaoStagingORM.OrgaoResponsavel.label("nome"),
            func.count().label("count"),
        )
        .where(
            RecomendacaoStagingORM.Status == ReviewStatus.approved,
            RecomendacaoStagingORM.DataRevisao.between(start, end),
            RecomendacaoStagingORM.OrgaoResponsavel.is_not(None),
        )
        .group_by(RecomendacaoStagingORM.OrgaoResponsavel)
    ).all()

    by_nome: dict[str, dict[str, int]] = defaultdict(
        lambda: {"obrigacoes": 0, "recomendacoes": 0}
    )
    for row in obrig_rows:
        by_nome[row.nome]["obrigacoes"] = int(row.count)
    for row in recom_rows:
        by_nome[row.nome]["recomendacoes"] = int(row.count)

    return [
        schemas.OrgaoBucket(
            nome=nome,
            obrigacoes=counts["obrigacoes"],
            recomendacoes=counts["recomendacoes"],
            total=counts["obrigacoes"] + counts["recomendacoes"],
        )
        for nome, counts in by_nome.items()
    ]


def _aggregate_pessoas(
    session: Session, start: datetime, end: datetime
) -> list[schemas.PessoaBucket]:
    """Combine NomeResponsavelMultaCominatoria (Obrigação) with NomeResponsavel
    (Recomendação). Solidários (SolidariosMultaCominatoria JSON) are out of
    scope for v1 — see plan.
    """
    obrig_rows = session.execute(
        select(
            ObrigacaoStagingORM.NomeResponsavelMultaCominatoria.label("nome"),
            ObrigacaoStagingORM.DocumentoResponsavelMultaCominatoria.label("documento"),
            func.count().label("count"),
        )
        .where(
            ObrigacaoStagingORM.Status == ReviewStatus.approved,
            ObrigacaoStagingORM.DataRevisao.between(start, end),
            ObrigacaoStagingORM.TemMultaCominatoria == True,  # noqa: E712 — MSSQL rejects `IS 1`
            ObrigacaoStagingORM.NomeResponsavelMultaCominatoria.is_not(None),
        )
        .group_by(
            ObrigacaoStagingORM.NomeResponsavelMultaCominatoria,
            ObrigacaoStagingORM.DocumentoResponsavelMultaCominatoria,
        )
    ).all()

    recom_rows = session.execute(
        select(
            RecomendacaoStagingORM.NomeResponsavel.label("nome"),
            func.count().label("count"),
        )
        .where(
            RecomendacaoStagingORM.Status == ReviewStatus.approved,
            RecomendacaoStagingORM.DataRevisao.between(start, end),
            RecomendacaoStagingORM.NomeResponsavel.is_not(None),
        )
        .group_by(RecomendacaoStagingORM.NomeResponsavel)
    ).all()

    by_key: dict[tuple[str, Optional[str]], dict[str, int]] = defaultdict(
        lambda: {"obrigacoes": 0, "recomendacoes": 0}
    )
    for row in obrig_rows:
        by_key[(row.nome, row.documento)]["obrigacoes"] = int(row.count)
    for row in recom_rows:
        # Recomendação só tem nome — agregação pode colidir com chaves de
        # obrigação que tenham documento. Mantém ``documento=None`` separado.
        by_key[(row.nome, None)]["recomendacoes"] += int(row.count)

    return [
        schemas.PessoaBucket(
            nome=nome,
            documento=documento,
            obrigacoes=counts["obrigacoes"],
            recomendacoes=counts["recomendacoes"],
            total=counts["obrigacoes"] + counts["recomendacoes"],
        )
        for (nome, documento), counts in by_key.items()
    ]


def _kpis(session: Session, start: datetime, end: datetime) -> schemas.KpiBlock:
    pendentes_o = _count_pendentes_obrigacao(session)
    pendentes_r = _count_pendentes_recomendacao(session)

    revisadas_o = int(
        session.execute(
            select(func.count()).where(
                ObrigacaoStagingORM.DataRevisao.between(start, end)
            )
        ).scalar_one()
    )
    revisadas_r = int(
        session.execute(
            select(func.count()).where(
                RecomendacaoStagingORM.DataRevisao.between(start, end)
            )
        ).scalar_one()
    )
    revisadas_total = revisadas_o + revisadas_r

    aprovadas_o = int(
        session.execute(
            select(func.count()).where(
                ObrigacaoStagingORM.Status == ReviewStatus.approved,
                ObrigacaoStagingORM.DataRevisao.between(start, end),
            )
        ).scalar_one()
    )
    aprovadas_r = int(
        session.execute(
            select(func.count()).where(
                RecomendacaoStagingORM.Status == ReviewStatus.approved,
                RecomendacaoStagingORM.DataRevisao.between(start, end),
            )
        ).scalar_one()
    )
    aprovadas_total = aprovadas_o + aprovadas_r

    obrigacoes_com_multa = int(
        session.execute(
            select(func.count()).where(
                ObrigacaoStagingORM.Status == ReviewStatus.approved,
                ObrigacaoStagingORM.DataRevisao.between(start, end),
                ObrigacaoStagingORM.TemMultaCominatoria == True,  # noqa: E712
            )
        ).scalar_one()
    )

    ticket_medio = session.execute(
        select(func.avg(ObrigacaoStagingORM.ValorMultaCominatoria)).where(
            ObrigacaoStagingORM.Status == ReviewStatus.approved,
            ObrigacaoStagingORM.DataRevisao.between(start, end),
            ObrigacaoStagingORM.TemMultaCominatoria == True,  # noqa: E712
            ObrigacaoStagingORM.ValorMultaCominatoria.is_not(None),
        )
    ).scalar_one_or_none()

    return schemas.KpiBlock(
        pendentes_obrigacao=pendentes_o,
        pendentes_recomendacao=pendentes_r,
        revisadas_periodo=revisadas_total,
        aprovadas_periodo=aprovadas_total,
        percent_aprovacao=(
            aprovadas_total / revisadas_total if revisadas_total else 0.0
        ),
        obrigacoes_com_multa=obrigacoes_com_multa,
        ticket_medio_multa=float(ticket_medio) if ticket_medio is not None else None,
    )


def compute_summary(
    session: Session,
    *,
    start_date: date,
    end_date: date,
    top_n: int = 10,
) -> schemas.DashboardSummary:
    start, end = _to_period_bounds(start_date, end_date)

    orgaos = _aggregate_orgaos(session, start, end)
    orgaos.sort(key=lambda b: b.total, reverse=True)

    pessoas = _aggregate_pessoas(session, start, end)
    pessoas.sort(key=lambda b: b.total, reverse=True)

    return schemas.DashboardSummary(
        kpis=_kpis(session, start, end),
        top_orgaos=orgaos[:top_n],
        top_pessoas=pessoas[:top_n],
    )
