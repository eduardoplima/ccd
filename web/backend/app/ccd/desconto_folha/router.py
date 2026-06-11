"""Endpoints HTTP da página "Desconto em Folha" do CCD.

`GET /candidatos` lista os processos candidatos; `POST /gerar` valida a seleção,
normaliza os números (6 dígitos, zero-padded) e enfileira o job ARQ de geração.
O acompanhamento (status/download) usa os endpoints compartilhados em
`app.ccd.router` (`/api/v1/ccd/jobs/{id}` e `.../download`).
"""

from __future__ import annotations

import re

from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import Usuario
from app.ccd.desconto_folha import service
from app.ccd.desconto_folha.schemas import CandidatosResponse, GerarRequest
from app.ccd.gen.jobs import enqueue_ccd_job
from app.deps import get_arq_pool, get_current_user, get_db_session, get_processo_session
from app.jobs.schemas import JobOut

router = APIRouter(prefix="/api/v1/ccd/desconto-folha", tags=["ccd:desconto-folha"])

_PROCESSO_RE = re.compile(r"^\d{1,6}/\d{4}$")


@router.get("/candidatos", response_model=CandidatosResponse)
def listar_candidatos(
    todos: bool = Query(False),
    session: Session = Depends(get_processo_session),
    _: Usuario = Depends(get_current_user),
) -> CandidatosResponse:
    return service.listar_candidatos(session, todos=todos)


def _normalizar(processos: list[str]) -> list[str]:
    """Valida e normaliza `numero/ano` → `numero` com 6 dígitos zero-padded.

    Espelha o `RTRIM(numero_processo)` do banco (que guarda `001425`).
    Remove duplicatas preservando a ordem.
    """
    if not processos:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="processos list must not be empty",
        )
    vistos: set[str] = set()
    normalizados: list[str] = []
    for item in processos:
        bruto = (item or "").strip()
        if not _PROCESSO_RE.match(bruto):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"invalid processo format: {item!r} (expected numero/ano)",
            )
        numero, ano = bruto.split("/")
        normalizado = f"{int(numero):06d}/{ano}"
        if normalizado not in vistos:
            vistos.add(normalizado)
            normalizados.append(normalizado)
    return normalizados


@router.post("/gerar", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def gerar(
    payload: GerarRequest,
    pool: ArqRedis = Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: Usuario = Depends(get_current_user),
) -> JobOut:
    processos = _normalizar(payload.processos)
    job = await enqueue_ccd_job(
        pool,
        session,
        user=user,
        tipo="ccd-desconto-folha",
        funcao="task_gerar_desconto_folha",
        processos=processos,
        modo="selecao",
    )
    return JobOut.model_validate(job)
