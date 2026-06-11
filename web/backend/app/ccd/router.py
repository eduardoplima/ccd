"""Módulo CCD — placeholder.

Vai expor interfaces para alguns scripts deste repositório (a definir).
Por enquanto só responde um health check para confirmar o roteamento do módulo.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.models import Usuario
from app.ccd import service
from app.ccd.gen.jobs import TIPO_PREFIXO
from app.ccd.gen.paths import final_artifact
from app.ccd.schemas import FiltrosCCDResponse, ProcessoCCDListResponse
from app.deps import get_current_user, get_db_session, get_processo_session
from app.jobs import service as jobs_service
from app.jobs.schemas import JobOut

router = APIRouter(prefix="/api/v1/ccd", tags=["ccd"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "modulo": "ccd"}


@router.get("/info")
def info(_: Usuario = Depends(get_current_user)) -> dict[str, str]:
    return {
        "modulo": "ccd",
        "descricao": "Interfaces para scripts da Coordenadoria de Controle de Decisões (em definição).",
    }


@router.get("/processos", response_model=ProcessoCCDListResponse)
def listar_processos(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=200),
    marcador: str | None = Query(None),
    sem_marcador: bool = Query(False),
    relator: str | None = Query(None),
    assunto: str | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("asc"),
    session: Session = Depends(get_processo_session),
    _: Usuario = Depends(get_current_user),
) -> ProcessoCCDListResponse:
    return service.listar_processos(
        session,
        marcador=marcador,
        sem_marcador=sem_marcador,
        relator=relator,
        assunto=assunto,
        sort=sort,
        order=order,
        page=page,
        size=size,
    )


@router.get("/processos/filtros", response_model=FiltrosCCDResponse)
def listar_filtros(
    session: Session = Depends(get_processo_session),
    _: Usuario = Depends(get_current_user),
) -> FiltrosCCDResponse:
    return service.listar_filtros(session)


# ---------------------------------------------------------------------------
# Jobs de geração de documentos (compartilhado entre as páginas do CCD).
# As páginas enfileiram via seus próprios endpoints (POST .../gerar) e depois
# acompanham o andamento por aqui, baixando o artefato quando `status == done`.
# ---------------------------------------------------------------------------


def _get_ccd_job(session: Session, id_job: int):
    job = jobs_service.obter_job(session, id_job)
    if job is None or not job.Tipo.startswith(TIPO_PREFIXO):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")
    return job


@router.get("/jobs/{id_job}", response_model=JobOut)
def obter_job_ccd(
    id_job: int,
    session: Session = Depends(get_db_session),
    _: Usuario = Depends(get_current_user),
) -> JobOut:
    return JobOut.model_validate(_get_ccd_job(session, id_job))


@router.get("/jobs/{id_job}/download")
def baixar_artefato_ccd(
    id_job: int,
    session: Session = Depends(get_db_session),
    _: Usuario = Depends(get_current_user),
) -> FileResponse:
    job = _get_ccd_job(session, id_job)
    if job.Status != "done":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"job not finished (status={job.Status})",
        )
    artefato = final_artifact(id_job)
    if artefato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="artifact not found")
    media_type = "application/zip" if artefato.suffix == ".zip" else "application/pdf"
    download_name = f"{job.Tipo}_{id_job}{artefato.suffix}"
    return FileResponse(path=artefato, media_type=media_type, filename=download_name)
