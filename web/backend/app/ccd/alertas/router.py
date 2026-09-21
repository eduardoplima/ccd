from __future__ import annotations

from fastapi import APIRouter, Depends, Query
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
def listar_alertas(
    tipo: TipoAlerta | None = Query(None),
    session: Session = Depends(get_processo_session),
    _: Usuario = Depends(get_current_user),
) -> AlertasResponse:
    return service.listar_alertas(session, tipo=tipo)
