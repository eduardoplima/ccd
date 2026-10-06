from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.deps import get_arq_pool, require_role
from app.jobs.agenda import JOBS, expressao_cron, horario_brasilia

router = APIRouter(
    dependencies=[Depends(require_role("admin"))],
    prefix="/api/v1/admin",
    tags=["admin"],
)


class JobAgendaOut(BaseModel):
    nome: str
    descricao: str
    cron: str | None  # UTC
    horario_brasilia: str | None


class JobEnfileiradoOut(BaseModel):
    job_id: str


@router.get("/jobs", response_model=list[JobAgendaOut])
def listar_jobs() -> list[JobAgendaOut]:
    return [
        JobAgendaOut(
            nome=j["nome"],
            descricao=j["descricao"],
            cron=expressao_cron(j["cron"]) if j["cron"] else None,
            horario_brasilia=horario_brasilia(j["cron"]) if j["cron"] else None,
        )
        for j in JOBS
    ]


@router.post("/jobs/{nome}/executar", response_model=JobEnfileiradoOut)
async def executar_job(nome: str, pool=Depends(get_arq_pool)) -> JobEnfileiradoOut:
    # só os agendados: os sob demanda exigem argumentos (id do FRAPJob etc.)
    if not any(j["nome"] == nome and j["cron"] for j in JOBS):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="scheduled job not found")
    job = await pool.enqueue_job(nome)
    if job is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="job already queued")
    return JobEnfileiradoOut(job_id=job.job_id)
