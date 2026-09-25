"""``GET /api/v1/cgad/multas-nao-cominadas``: obrigações aprovadas com multa
cominatória prevista cujo processo não tem débito tipo 5 cadastrado."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.cgad.multas_nao_cominadas import schemas, service
from app.deps import get_db_session
from app.permissoes import require_modulo

logger = logging.getLogger(__name__)

router = APIRouter(
    dependencies=[Depends(require_modulo("cgad.multas-nao-cominadas"))],
    prefix="/api/v1/cgad/multas-nao-cominadas",
    tags=["multas-nao-cominadas"],
)


@router.get("", response_model=schemas.MultasNaoCominadas)
def listar(session: Session = Depends(get_db_session)) -> schemas.MultasNaoCominadas:
    try:
        return service.listar(session)
    except Exception as exc:
        logger.exception("failed to load multas nao cominadas")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="processo database unavailable",
        ) from exc
