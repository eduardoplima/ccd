from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from arq import ArqRedis
from arq.jobs import Job as ArqJob
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.jobs.models import FRAPJob

_FINALIZADOS = ("done", "failed", "cancelled")
_EM_ANDAMENTO = ("pending", "running")


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


async def enqueue_job(
    pool: ArqRedis,
    session: Session,
    *,
    user: FRAPUsuario,
    tipo: str,
    funcao: str,
    argumentos: dict[str, Any] | None = None,
) -> FRAPJob:
    """Cria a linha em FRAPJob e enfileira o ARQ job correspondente.

    `funcao` é o nome registrado em WorkerSettings.functions.
    Args extras (além de id_frap_job) vêm de `argumentos`.
    """
    job_row = FRAPJob(
        ArqJobId="pending",
        Tipo=tipo,
        Argumentos=json.dumps(argumentos) if argumentos else None,
        Status="pending",
        IdUsuario=user.IdUsuario,
    )
    session.add(job_row)
    session.commit()
    session.refresh(job_row)

    extra_args = list((argumentos or {}).values())
    arq_job = await pool.enqueue_job(funcao, job_row.IdFRAPJob, *extra_args)
    if arq_job is None:
        # ARQ pode retornar None se já existe job com mesmo job_id; aqui não
        # passamos job_id, então só ocorre se a fila estiver indisponível.
        job_row.Status = "failed"
        job_row.ErroMensagem = "não foi possível enfileirar o job no Redis"
        session.commit()
        return job_row

    job_row.ArqJobId = arq_job.job_id
    session.commit()
    session.refresh(job_row)
    return job_row


def listar_jobs(
    session: Session,
    *,
    status: str | None = None,
    tipo: str | None = None,
    page: int = 1,
    size: int = 50,
) -> tuple[list[FRAPJob], int]:
    stmt = select(FRAPJob)
    if status:
        stmt = stmt.where(FRAPJob.Status == status)
    if tipo:
        stmt = stmt.where(FRAPJob.Tipo == tipo)

    total = (
        session.query(FRAPJob).count()
        if not (status or tipo)
        else len(session.execute(stmt).scalars().all())
    )
    rows = (
        session.execute(
            stmt.order_by(FRAPJob.DataCriacao.desc()).offset((page - 1) * size).limit(size)
        )
        .scalars()
        .all()
    )
    return list(rows), total


def obter_job(session: Session, id_job: int) -> FRAPJob | None:
    return session.get(FRAPJob, id_job)


class JobNaoEmAndamento(Exception):
    pass


class JobEmAndamento(Exception):
    pass


async def cancelar_job(pool: ArqRedis, session: Session, id_job: int) -> FRAPJob | None:
    """Aborta o ARQ job (se ainda existir) e marca a row como `cancelled`.

    Usar somente em jobs `pending` ou `running`. Para jobs já finalizados,
    levanta `JobNaoEmAndamento`.
    """
    row = session.get(FRAPJob, id_job)
    if row is None:
        return None
    if row.Status not in _EM_ANDAMENTO:
        raise JobNaoEmAndamento(row.Status)

    if row.ArqJobId and row.ArqJobId != "pending":
        try:
            await ArqJob(row.ArqJobId, pool).abort(timeout=3.0)
        except Exception:
            # job pode já ter sumido do Redis (TTL, worker offline). seguimos.
            pass

    row.Status = "cancelled"
    row.DataFim = _utcnow()
    msg = "cancelado pelo usuário"
    row.ErroMensagem = msg if not row.ErroMensagem else f"{row.ErroMensagem}\n{msg}"[-1900:]
    session.commit()
    session.refresh(row)
    return row


def deletar_job(session: Session, id_job: int) -> FRAPJob | None:
    """Apaga a row. Recusa (`JobEmAndamento`) se status ∈ pending/running."""
    row = session.get(FRAPJob, id_job)
    if row is None:
        return None
    if row.Status in _EM_ANDAMENTO:
        raise JobEmAndamento(row.Status)
    session.delete(row)
    session.commit()
    return row


def deletar_finalizados(session: Session, *, tipo: str | None = None) -> int:
    q = session.query(FRAPJob).filter(FRAPJob.Status.in_(_FINALIZADOS))
    if tipo:
        q = q.filter(FRAPJob.Tipo == tipo)
    n = q.delete(synchronize_session=False)
    session.commit()
    return int(n)
