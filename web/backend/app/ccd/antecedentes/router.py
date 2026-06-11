from __future__ import annotations

import re

from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.ccd.antecedentes import service
from app.ccd.antecedentes.schemas import (
    CandidatosAntecedentesResponse,
    GerarAntecedentesRequest,
)
from app.ccd.gen.jobs import enqueue_ccd_job
from app.deps import get_arq_pool, get_current_user, get_db_session, get_processo_session
from app.jobs.schemas import JobOut

router = APIRouter(prefix="/api/v1/ccd/antecedentes", tags=["ccd:antecedentes"])

_PROCESSO_RE = re.compile(r"^\d{1,6}/\d{4}$")


@router.get("/candidatos", response_model=CandidatosAntecedentesResponse)
def listar_candidatos(
    todos: bool = Query(False),
    session: Session = Depends(get_processo_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> CandidatosAntecedentesResponse:
    return service.listar_candidatos(session, todos=todos)


@router.post("/gerar", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def gerar(
    body: GerarAntecedentesRequest,
    pool: ArqRedis = Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> JobOut:
    if not body.processos:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="processos must not be empty",
        )

    normalizados: list[str] = []
    for raw in body.processos:
        valor = raw.strip()
        if not _PROCESSO_RE.match(valor):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"invalid processo format: {raw!r} (expected numero/ano)",
            )
        numero, ano = valor.split("/")
        chave = f"{numero.zfill(6)}/{ano}"
        if chave not in normalizados:
            normalizados.append(chave)

    job = await enqueue_ccd_job(
        pool,
        session,
        user=user,
        tipo="ccd-antecedentes",
        funcao="task_gerar_antecedentes",
        processos=normalizados,
        modo="selecao",
    )
    return JobOut.model_validate(job)
