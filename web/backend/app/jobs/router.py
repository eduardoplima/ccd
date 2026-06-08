from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.deps import get_arq_pool, get_current_user, get_db_session, require_role
from app.jobs import service
from app.jobs.schemas import (
    ConciliarRequest,
    ConciliarTodosResponse,
    DeletarFinalizadosResponse,
    JobListResponse,
    JobOut,
    UploadExtratoResponse,
)

router = APIRouter(prefix="/api/v1/frap/jobs", tags=["frap:jobs"])
extratos_router = APIRouter(prefix="/api/v1/frap/extratos", tags=["frap:extratos"])

_ROOT = Path(__file__).resolve().parents[3]
_PASTA_EXTRATOS = _ROOT / "docs" / "extratos_frap"
_PERIODO_RE = re.compile(r"^\d{6}$")
_CONTA_RE = re.compile(r"^\d{6}-\d$")


@router.post("/parse-extratos", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def disparar_parse(
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> JobOut:
    job = await service.enqueue_job(
        pool, session, user=user, tipo="parse-extratos", funcao="task_parse_e_publicar"
    )
    return JobOut.model_validate(job)


@router.post("/conciliar", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def disparar_conciliar(
    payload: ConciliarRequest,
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> JobOut:
    job = await service.enqueue_job(
        pool,
        session,
        user=user,
        tipo="conciliar",
        funcao="task_conciliar_mes",
        argumentos={"ano": payload.ano, "mes": payload.mes},
    )
    return JobOut.model_validate(job)


@router.post(
    "/conciliar-todos",
    response_model=ConciliarTodosResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def disparar_conciliar_todos(
    ano: int = Query(..., ge=2000, le=2100),
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> ConciliarTodosResponse:
    jobs: list[JobOut] = []
    for mes in range(1, 13):
        job = await service.enqueue_job(
            pool,
            session,
            user=user,
            tipo="conciliar",
            funcao="task_conciliar_mes",
            argumentos={"ano": ano, "mes": mes},
        )
        jobs.append(JobOut.model_validate(job))
    return ConciliarTodosResponse(ano=ano, jobs=jobs)


@router.get("", response_model=JobListResponse)
def listar(
    status_: str | None = Query(default=None, alias="status"),
    tipo: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> JobListResponse:
    rows, total = service.listar_jobs(session, status=status_, tipo=tipo, page=page, size=size)
    return JobListResponse(
        items=[JobOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{id_job}", response_model=JobOut)
def detalhe(
    id_job: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> JobOut:
    job = service.obter_job(session, id_job)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job não encontrado")
    return JobOut.model_validate(job)


@router.post("/{id_job}/cancelar", response_model=JobOut)
async def cancelar(
    id_job: int,
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> JobOut:
    try:
        job = await service.cancelar_job(pool, session, id_job)
    except service.JobNaoEmAndamento as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"job not in progress (status={exc.args[0] if exc.args else '?'})",
        ) from exc
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    return JobOut.model_validate(job)


@router.delete("/finalizados", response_model=DeletarFinalizadosResponse)
def deletar_finalizados(
    tipo: str | None = Query(default=None),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> DeletarFinalizadosResponse:
    n = service.deletar_finalizados(session, tipo=tipo)
    return DeletarFinalizadosResponse(deletados=n)


@router.delete("/{id_job}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(
    id_job: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    try:
        row = service.deletar_job(session, id_job)
    except service.JobEmAndamento as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"job in progress (status={exc.args[0] if exc.args else '?'}); cancel first",
        ) from exc
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    return None


@extratos_router.post(
    "/upload", response_model=UploadExtratoResponse, status_code=status.HTTP_201_CREATED
)
async def upload_extrato(
    conta: str = Query(..., pattern=_CONTA_RE.pattern),
    periodo: str = Query(..., pattern=_PERIODO_RE.pattern),
    arquivo: UploadFile = File(...),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> UploadExtratoResponse:
    if not arquivo.filename or not arquivo.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="arquivo deve ter extensão .txt",
        )
    destino_dir = _PASTA_EXTRATOS / conta
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / f"{periodo}.txt"
    payload = await arquivo.read()
    destino.write_bytes(payload)
    return UploadExtratoResponse(
        conta=conta,
        periodo=periodo,
        bytes=len(payload),
        caminho=str(destino.relative_to(_ROOT)).replace("\\", "/"),
    )
