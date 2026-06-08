"""ETL trigger and status endpoints. Admin-only.

``POST /etl/run`` enqueues the orchestrator task that runs NER → obrigação →
recomendação for the given date window. The endpoint creates an ``Extracao``
row up-front (status=``queued``) and returns ``extracao_id`` so the frontend
can poll ``GET /etl/extracoes/{id}`` for live progress.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING, Literal

from arq.jobs import Job, JobStatus
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_arq_pool, get_db_session, require_role
from app.cgad.etl import schemas
from cgad.etl.staging import (
    ObrigacaoStagingORM,
    RecomendacaoStagingORM,
    ReviewStatus,
)
from cgad.models import (
    ExtracaoEventoORM,
    ExtracaoORM,
    NERDecisaoORM,
    NERObrigacaoORM,
    NERRecomendacaoORM,
    ObrigacaoORM,
    ProcessedObrigacaoORM,
    ProcessedRecomendacaoORM,
    RecomendacaoORM,
)


if TYPE_CHECKING:
    from arq.connections import ArqRedis


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cgad/etl", tags=["etl"])

_QUEUE_NAME = "arq:queue"  # fila padrão do ARQ (mesma do worker unificado)
_TASK_NAME = "run_full_extraction"


_STATUS_MAP = {
    JobStatus.deferred: "deferred",
    JobStatus.queued: "queued",
    JobStatus.in_progress: "in_progress",
    JobStatus.complete: "complete",
    JobStatus.not_found: "not_found",
}


def _to_extracao_out(row: ExtracaoORM) -> schemas.ExtracaoOut:
    return schemas.ExtracaoOut(
        id=row.IdExtracao,
        data_inicio=row.DataInicio,
        data_fim=row.DataFim,
        data_execucao=row.DataExecucao,
        status=row.Status,
        etapa_atual=row.EtapaAtual,
        decisoes_processadas=row.DecisoesProcessadas,
        obrigacoes_geradas=row.ObrigacoesGeradas,
        recomendacoes_geradas=row.RecomendacoesGeradas,
        erros=row.Erros,
        mensagem_erro=row.MensagemErro,
        job_id=row.JobId,
    )


@router.post(
    "/run",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.ExtractionJobAccepted,
    dependencies=[Depends(require_role("admin"))],
)
async def trigger_extraction(
    body: schemas.ExtractionTriggerRequest,
    pool: "ArqRedis" = Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
) -> schemas.ExtractionJobAccepted:
    enqueued_at = datetime.utcnow()

    extracao = ExtracaoORM(
        DataInicio=body.filters.start_date,
        DataFim=body.filters.end_date,
        DataExecucao=enqueued_at,
        Status="queued",
        EtapaAtual="queued",
    )
    session.add(extracao)
    session.commit()
    session.refresh(extracao)

    job = await pool.enqueue_job(
        _TASK_NAME,
        body.filters.model_dump(mode="json"),
        extracao.IdExtracao,
        _queue_name=_QUEUE_NAME,
    )
    if job is None:
        # Couldn't enqueue: roll back the row so the history isn't polluted
        # with phantom queued runs.
        session.delete(extracao)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="failed to enqueue job",
        )

    extracao.JobId = job.job_id
    session.commit()

    return schemas.ExtractionJobAccepted(
        extracao_id=extracao.IdExtracao,
        job_id=job.job_id,
        status_url=f"/api/v1/cgad/etl/extracoes/{extracao.IdExtracao}",
        enqueued_at=enqueued_at,
    )


@router.get(
    "/extracoes",
    response_model=schemas.ExtracaoListPage,
    dependencies=[Depends(require_role("admin"))],
)
def list_extracoes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Literal["queued", "running", "done", "error"] | None = Query(
        None, alias="status"
    ),
    executed_from: datetime | None = Query(None),
    executed_to: datetime | None = Query(None),
    start_date_from: date | None = Query(None),
    start_date_to: date | None = Query(None),
    session: Session = Depends(get_db_session),
) -> schemas.ExtracaoListPage:
    """List past runs, most recent first.

    Optional filters compose with AND — empty params mean "no constraint".
    The frontend uses these to power the search panel on ``/etl``.
    """
    base = select(ExtracaoORM).order_by(ExtracaoORM.DataExecucao.desc())
    if status_filter is not None:
        base = base.where(ExtracaoORM.Status == status_filter)
    if executed_from is not None:
        base = base.where(ExtracaoORM.DataExecucao >= executed_from)
    if executed_to is not None:
        base = base.where(ExtracaoORM.DataExecucao <= executed_to)
    if start_date_from is not None:
        base = base.where(ExtracaoORM.DataInicio >= start_date_from)
    if start_date_to is not None:
        base = base.where(ExtracaoORM.DataInicio <= start_date_to)

    total = session.execute(
        select(func.count()).select_from(base.order_by(None).subquery())
    ).scalar_one()
    rows = (
        session.execute(base.offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return schemas.ExtracaoListPage(
        items=[_to_extracao_out(r) for r in rows],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/extracoes/{extracao_id}",
    response_model=schemas.ExtracaoOut,
    dependencies=[Depends(require_role("admin"))],
)
def get_extracao(
    extracao_id: int,
    session: Session = Depends(get_db_session),
) -> schemas.ExtracaoOut:
    row = session.get(ExtracaoORM, extracao_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="extracao not found"
        )
    return _to_extracao_out(row)


@router.post(
    "/extracoes/{extracao_id}/abort",
    response_model=schemas.ExtracaoOut,
    dependencies=[Depends(require_role("admin"))],
)
async def abort_extracao(
    extracao_id: int,
    pool: "ArqRedis" = Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
) -> schemas.ExtracaoOut:
    """Cancel a queued/running extraction. Signals ARQ to stop the job
    (worker must have ``allow_abort_jobs=True``) and marks the row as
    ``error`` so the orphan watchdog isn't needed.

    Idempotent: aborting an already-finished run returns the row unchanged.
    """
    row = session.get(ExtracaoORM, extracao_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="extracao not found"
        )
    if row.Status not in {"queued", "running"}:
        return _to_extracao_out(row)

    if row.JobId:
        try:
            job = Job(job_id=row.JobId, redis=pool, _queue_name=_QUEUE_NAME)
            # ``Job.abort`` waits for the worker to ack via the result. Without
            # a timeout it blocks forever when the worker is dead — bound it
            # so the endpoint always returns and the row gets marked as error.
            await job.abort(timeout=3.0)
        except Exception:
            logger.exception("abort signal failed for job %s", row.JobId)

    row.Status = "error"
    row.MensagemErro = "aborted by user"
    session.commit()
    session.refresh(row)
    return _to_extracao_out(row)


@router.delete(
    "/extracoes/{extracao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_extracao(
    extracao_id: int,
    session: Session = Depends(get_db_session),
) -> None:
    """Remove an extraction row from the history. Refuses if the run is
    still active — call ``/abort`` first. Cascades to ``ExtracaoEvento``;
    NER/Obrigação/Recomendação rows produced by the run are preserved.
    """
    row = session.get(ExtracaoORM, extracao_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="extracao not found"
        )
    if row.Status in {"queued", "running"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="cannot delete an active run — abort it first",
        )
    session.delete(row)
    session.commit()


@router.get(
    "/extracoes/{extracao_id}/eventos",
    response_model=schemas.ExtracaoEventoListPage,
    dependencies=[Depends(require_role("admin"))],
)
def list_eventos(
    extracao_id: int,
    since: datetime | None = Query(
        None,
        description="ISO-8601 timestamp; only events strictly after this are returned.",
    ),
    limit: int = Query(500, ge=1, le=2000),
    session: Session = Depends(get_db_session),
) -> schemas.ExtracaoEventoListPage:
    """Live activity feed for one extraction. Polled by the frontend every
    ~1.5s with the timestamp of the last event seen, so each request returns
    only what's new.
    """
    if session.get(ExtracaoORM, extracao_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="extracao not found"
        )

    stmt = (
        select(ExtracaoEventoORM)
        .where(ExtracaoEventoORM.IdExtracao == extracao_id)
        .order_by(ExtracaoEventoORM.IdExtracaoEvento.asc())
    )
    if since is not None:
        stmt = stmt.where(ExtracaoEventoORM.Timestamp > since)

    # Fetch one extra to know whether more pages remain.
    rows = session.execute(stmt.limit(limit + 1)).scalars().all()
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]

    return schemas.ExtracaoEventoListPage(
        items=[
            schemas.ExtracaoEventoOut(
                id=r.IdExtracaoEvento,
                extracao_id=r.IdExtracao,
                timestamp=r.Timestamp,
                tipo=r.Tipo,
                payload=r.Payload or {},
            )
            for r in rows
        ],
        has_more=has_more,
    )


@router.get(
    "/extracoes/{extracao_id}/decisoes",
    response_model=schemas.DecisaoExtraidaListPage,
    dependencies=[Depends(require_role("admin"))],
)
def list_decisoes(
    extracao_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db_session),
) -> schemas.DecisaoExtraidaListPage:
    """Drill-down: NERDecisões emitted by this extraction with their
    obrigações/recomendações attached (joined via the ``Processed*`` bridge).

    Only NERDecisões with ``RunId == str(extracao_id)`` are returned —
    extractions enqueued before stage-1 started carrying that linkage
    show empty results, which is expected.
    """
    if session.get(ExtracaoORM, extracao_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="extracao not found"
        )

    run_id = str(extracao_id)
    base = (
        select(NERDecisaoORM)
        .where(NERDecisaoORM.RunId == run_id)
        .order_by(NERDecisaoORM.IdNerDecisao.asc())
    )
    total = session.execute(
        select(func.count()).select_from(base.order_by(None).subquery())
    ).scalar_one()
    decisoes = (
        session.execute(base.offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )

    items = [_decisao_to_item(session, decisao) for decisao in decisoes]
    return schemas.DecisaoExtraidaListPage(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


def _decisao_to_item(
    session: Session, decisao: NERDecisaoORM
) -> schemas.DecisaoExtraidaItem:
    """Walk the bridge tables for one NERDecisão and gather (final_id,
    descricao, status) tuples for both kinds.

    Status comes from the staging audit row when present (approved/rejected)
    and falls back to ``pending`` when the final row exists but no audit row
    has been written yet (still in the review queue).
    """

    def _items_for_obrigacao() -> list[schemas.DecisaoItemRow]:
        stmt = (
            select(
                ObrigacaoORM.IdObrigacao,
                ObrigacaoORM.DescricaoObrigacao,
                ObrigacaoStagingORM.Status,
            )
            .join(NERObrigacaoORM, NERObrigacaoORM.IdNerDecisao == decisao.IdNerDecisao)
            .join(
                ProcessedObrigacaoORM,
                ProcessedObrigacaoORM.IdNerObrigacao == NERObrigacaoORM.IdNerObrigacao,
            )
            .join(
                ObrigacaoORM,
                ObrigacaoORM.IdObrigacao == ProcessedObrigacaoORM.IdObrigacao,
            )
            .outerjoin(
                ObrigacaoStagingORM,
                ObrigacaoStagingORM.IdObrigacao == ObrigacaoORM.IdObrigacao,
            )
            .order_by(ObrigacaoORM.IdObrigacao.asc())
        )
        rows = session.execute(stmt).all()
        return [
            schemas.DecisaoItemRow(
                id=row[0],
                descricao=row[1] or "",
                status=_status_from_staging(row[2]),
            )
            for row in rows
        ]

    def _items_for_recomendacao() -> list[schemas.DecisaoItemRow]:
        stmt = (
            select(
                RecomendacaoORM.IdRecomendacao,
                RecomendacaoORM.DescricaoRecomendacao,
                RecomendacaoStagingORM.Status,
            )
            .join(
                NERRecomendacaoORM,
                NERRecomendacaoORM.IdNerDecisao == decisao.IdNerDecisao,
            )
            .join(
                ProcessedRecomendacaoORM,
                ProcessedRecomendacaoORM.IdNerRecomendacao
                == NERRecomendacaoORM.IdNerRecomendacao,
            )
            .join(
                RecomendacaoORM,
                RecomendacaoORM.IdRecomendacao
                == ProcessedRecomendacaoORM.IdRecomendacao,
            )
            .outerjoin(
                RecomendacaoStagingORM,
                RecomendacaoStagingORM.IdRecomendacao == RecomendacaoORM.IdRecomendacao,
            )
            .order_by(RecomendacaoORM.IdRecomendacao.asc())
        )
        rows = session.execute(stmt).all()
        return [
            schemas.DecisaoItemRow(
                id=row[0],
                descricao=row[1] or "",
                status=_status_from_staging(row[2]),
            )
            for row in rows
        ]

    return schemas.DecisaoExtraidaItem(
        id_ner_decisao=decisao.IdNerDecisao,
        id_processo=decisao.IdProcesso,
        id_composicao_pauta=decisao.IdComposicaoPauta,
        id_voto_pauta=decisao.IdVotoPauta,
        data_extracao=decisao.DataExtracao,
        obrigacoes=_items_for_obrigacao(),
        recomendacoes=_items_for_recomendacao(),
    )


def _status_from_staging(raw) -> Literal["pending", "approved", "rejected"]:
    if raw is None:
        return "pending"
    return raw.value if isinstance(raw, ReviewStatus) else str(raw)


@router.get(
    "/jobs/{job_id}",
    response_model=schemas.ExtractionJobStatus,
    dependencies=[Depends(require_role("admin"))],
)
async def get_job_status(
    job_id: str,
    pool: "ArqRedis" = Depends(get_arq_pool),
) -> schemas.ExtractionJobStatus:
    job = Job(job_id=job_id, redis=pool, _queue_name=_QUEUE_NAME)
    job_status = await job.status()
    status_str = _STATUS_MAP.get(job_status, "not_found")

    if job_status == JobStatus.not_found:
        return schemas.ExtractionJobStatus(job_id=job_id, status="not_found")

    info = await job.result_info()
    if info is None:
        return schemas.ExtractionJobStatus(job_id=job_id, status=status_str)

    return schemas.ExtractionJobStatus(
        job_id=job_id,
        status=status_str,
        success=info.success,
        result=info.result if isinstance(info.result, dict) else None,
        enqueued_at=info.enqueue_time,
        started_at=info.start_time,
        finished_at=info.finish_time,
    )
