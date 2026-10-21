from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.auth.models import Usuario
from app.ccd.monitoramentos import service
from app.ccd.monitoramentos.schemas import MonitoramentosResponse
from app.deps import get_current_user, get_processo_session
from app.permissoes import require_modulo

router = APIRouter(
    dependencies=[Depends(require_modulo("ccd.monitoramentos"))],
    prefix="/api/v1/ccd/monitoramentos",
    tags=["ccd:monitoramentos"],
)


@router.get("", response_model=MonitoramentosResponse)
async def listar_monitoramentos(
    request: Request,
    session: Session = Depends(get_processo_session),
    _: Usuario = Depends(get_current_user),
) -> MonitoramentosResponse:
    # snapshot do job diário; sem ele, monta na hora só com o banco + análises guardadas
    pool = getattr(request.app.state, "arq_pool", None)
    bruto = await pool.get(service.SNAPSHOT_KEY) if pool is not None else None
    if bruto:
        return MonitoramentosResponse.model_validate_json(bruto)
    guardadas = service.analises_de_json(
        await pool.get(service.ANALISES_KEY) if pool is not None else None
    )
    analises = {**service.carregar_seed(), **guardadas}
    resp, _novas = await asyncio.to_thread(service.montar, session, analises)
    resp.calculado_em = None
    return resp
