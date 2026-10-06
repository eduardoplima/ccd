from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.auth.models import Usuario
from app.ccd.alertas import service
from app.ccd.alertas.schemas import AlertasResponse, TipoAlerta
from app.deps import get_current_user, get_processo_session
from app.permissoes import require_modulo

router = APIRouter(
    dependencies=[Depends(require_modulo("ccd.alertas"))],
    prefix="/api/v1/ccd/alertas",
    tags=["ccd:alertas"],
)


@router.get("", response_model=AlertasResponse)
async def listar_alertas(
    request: Request,
    tipo: TipoAlerta | None = Query(None),
    session: Session = Depends(get_processo_session),
    _: Usuario = Depends(get_current_user),
) -> AlertasResponse:
    # snapshot do job diário; sem ele (job ainda não rodou, Redis fora), calcula na hora
    pool = getattr(request.app.state, "arq_pool", None)
    bruto = await pool.get(service.SNAPSHOT_KEY) if pool is not None else None
    if bruto:
        return service.filtrar(AlertasResponse.model_validate_json(bruto), tipo)
    return await asyncio.to_thread(service.listar_alertas, session, tipo=tipo)
