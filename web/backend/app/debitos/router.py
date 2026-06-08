from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.debitos import service
from app.debitos.schemas import DebitoLookupResponse
from app.deps import get_current_user, get_db_session

router = APIRouter(prefix="/api/v1/frap/debitos", tags=["frap:debitos"])


@router.get("", response_model=DebitoLookupResponse)
def buscar(
    cpfcnpj: str | None = Query(default=None, min_length=11, max_length=14),
    id_debito: int | None = Query(default=None, ge=1),
    id_processo: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> DebitoLookupResponse:
    return service.buscar_debitos(
        session,
        cpfcnpj=cpfcnpj,
        id_debito=id_debito,
        id_processo=id_processo,
        page=page,
        size=size,
    )
