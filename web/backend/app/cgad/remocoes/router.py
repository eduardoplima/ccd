"""``/api/v1/cgad/remocoes``: tira obrigações/recomendações curadas do acervo
indicando o acórdão que determinou a remoção."""

from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.cgad.remocoes import schemas, service
from app.deps import get_db_session
from app.permissoes import require_modulo

logger = logging.getLogger(__name__)

router = APIRouter(
    dependencies=[Depends(require_modulo("cgad.reviews"))],
    prefix="/api/v1/cgad/remocoes",
    tags=["cgad-remocoes"],
)

_PROCESSO = re.compile(r"^\s*(\d{1,6})\s*/\s*(\d{4})\s*$")


@router.get("", response_model=schemas.Consulta)
def consultar(
    processo: str = Query(..., description="NNNNNN/AAAA"),
    session: Session = Depends(get_db_session),
) -> schemas.Consulta:
    m = _PROCESSO.match(processo)
    if not m:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail="processo must be NNNNNN/AAAA"
        )
    try:
        out = service.consultar(session, int(m.group(1)), int(m.group(2)))
    except Exception as exc:
        logger.exception("failed to load remocoes for %s", processo)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="processo database unavailable"
        ) from exc
    if out is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="processo not found")
    return out


@router.post("", response_model=schemas.RemocaoResultado)
def remover(
    payload: schemas.RemocaoPayload,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_modulo("cgad.reviews", editar=True)),
) -> schemas.RemocaoResultado:
    try:
        return service.remover(session, payload, user.NomeUsuario)
    except service.RemocaoInvalida as exc:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
