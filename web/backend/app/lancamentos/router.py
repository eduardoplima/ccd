from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.deps import get_current_user, get_db_session
from app.lancamentos import service
from app.lancamentos.schemas import LancamentoDetail, LancamentoListResponse

router = APIRouter(prefix="/api/v1/frap/lancamentos", tags=["frap:lancamentos"])


@router.get("", response_model=LancamentoListResponse)
def listar(
    conta: str | None = Query(default=None, pattern=r"^\d{6}-\d$"),
    periodo: str | None = Query(default=None, pattern=r"^\d{6}$"),
    categoria: str | None = Query(default=None),
    valor_dc: str | None = Query(default=None, pattern=r"^[CD]$"),
    dt_inicio: date | None = Query(default=None),
    dt_fim: date | None = Query(default=None),
    valor_min: Decimal | None = Query(default=None, ge=0),
    valor_max: Decimal | None = Query(default=None, ge=0),
    cpfcnpj: str | None = Query(default=None, alias="cpfCnpj", min_length=11, max_length=14),
    q: str | None = Query(default=None, min_length=2, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> LancamentoListResponse:
    if valor_min is not None and valor_max is not None and valor_min > valor_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="valor_min must be <= valor_max",
        )
    return service.listar_lancamentos(
        session,
        conta=conta,
        periodo=periodo,
        categoria=categoria,
        valor_dc=valor_dc,
        dt_inicio=dt_inicio,
        dt_fim=dt_fim,
        valor_min=valor_min,
        valor_max=valor_max,
        cpfcnpj=cpfcnpj,
        q=q,
        page=page,
        size=size,
    )


@router.get("/{id_lancamento}", response_model=LancamentoDetail)
def detalhe(
    id_lancamento: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> LancamentoDetail:
    detail = service.get_lancamento_detail(session, id_lancamento)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lancamento not found")
    return detail
