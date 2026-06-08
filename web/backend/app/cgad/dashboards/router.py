"""Dashboards router. ``GET /api/v1/dashboards/summary``, JWT-authenticated.

When ``start_date`` / ``end_date`` are omitted the backend defaults to the
last 90 days ending today (UTC). The frontend may also send explicit dates
for the date-range picker.
"""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.cgad.dashboards import schemas, service
from app.deps import get_current_user, get_db_session
from cgad.models import UserORM


router = APIRouter(prefix="/api/v1/cgad/dashboards", tags=["dashboards"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def get_summary(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    top_n: int = Query(10, ge=1, le=50),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DashboardSummary:
    today = date.today()
    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = end_date - timedelta(days=90)
    return service.compute_summary(
        session,
        start_date=start_date,
        end_date=end_date,
        top_n=top_n,
    )
