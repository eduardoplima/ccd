"""SIAI Pessoal: `/api/v1/ccd/siai-pessoal` (somente leitura)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.ccd.siai_pessoal import schemas, service
from app.deps import get_current_user, get_db_session

router = APIRouter(prefix="/api/v1/ccd/siai-pessoal", tags=["ccd:siai-pessoal"])


@router.get("/contracheque", response_model=schemas.ContrachequeMes)
def contracheque(
    cpf: str = Query(..., min_length=11, max_length=14, pattern=r"^\d+$"),
    ano: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    processo: str | None = Query(default=None, max_length=20),  # marca a rubrica do processo
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.ContrachequeMes:
    return service.contracheque(session, cpf, ano, mes, processo)
