"""Dashboards router. ``GET /api/v1/cgad/dashboards/summary``, JWT-authenticated.

Sem recorte de período: a página consolida tudo que já foi aprovado/enviado.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.cgad.dashboards import schemas, service
from app.deps import get_current_user, get_db_session
from cgad.models import UserORM


router = APIRouter(prefix="/api/v1/cgad/dashboards", tags=["dashboards"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(
    top_n: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DashboardSummary:
    return service.compute_summary(session, top_n=top_n)
