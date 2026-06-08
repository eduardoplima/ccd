"""Módulo CCD — placeholder.

Vai expor interfaces para alguns scripts deste repositório (a definir).
Por enquanto só responde um health check para confirmar o roteamento do módulo.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.models import Usuario
from app.ccd import service
from app.ccd.schemas import FiltrosCCDResponse, ProcessoCCDListResponse
from app.deps import get_current_user, get_processo_session

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
