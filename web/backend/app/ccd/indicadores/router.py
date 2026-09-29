from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ccd.indicadores import service
from app.ccd.indicadores.schemas import Painel
from app.deps import get_db_session, get_processo_session
from app.permissoes import require_modulo

router = APIRouter(
    dependencies=[Depends(require_modulo("ccd.painel"))],
    prefix="/api/v1/ccd/indicadores",
    tags=["ccd:indicadores"],
)


@router.get("", response_model=Painel)
def painel(
    bddip: Session = Depends(get_db_session),
    processo: Session = Depends(get_processo_session),
) -> Painel:
    return service.painel_cacheado(bddip, processo)
