"""Decision-level review router. All endpoints under
``/api/v1/cgad/reviews``, JWT-authenticated.

Thin wrappers over ``app.cgad.review.service``. RFC 7807-compatible errors
come from ``HTTPException`` — FastAPI serializes them as ``{"detail": "..."}``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db_session
from app.cgad.review import schemas, service
from cgad.models import UserORM


router = APIRouter(prefix="/api/v1/cgad/reviews", tags=["reviews"])


@router.get("/awaiting-dispatch", response_model=schemas.AwaitingDispatchPage)
def list_awaiting_dispatch(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.AwaitingDispatchPage:
    return service.list_awaiting_dispatch(
        session,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )


@router.get("/decisoes", response_model=schemas.DecisaoListPage)
def list_decisoes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    processo: str | None = Query(None),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DecisaoListPage:
    return service.list_decisoes(
        session,
        page=page,
        page_size=page_size,
        current_user=current_user,
        processo=processo,
    )


@router.get("/decisoes/{id}", response_model=schemas.DecisaoDetail)
def get_decisao(
    id: int,
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DecisaoDetail:
    return service.get_decisao(session, id=id, current_user=current_user)


@router.get("/decisoes/{id}/texto-acordao", response_model=schemas.DecisaoTexto)
def get_decisao_texto(
    id: int,
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DecisaoTexto:
    return service.get_decisao_texto(session, id=id, current_user=current_user)


@router.post("/decisoes/{id}/claim", response_model=schemas.ClaimResponse)
def claim_decisao(
    id: int,
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.ClaimResponse:
    return service.claim(session, id=id, current_user=current_user)


@router.post("/decisoes/{id}/release", status_code=status.HTTP_204_NO_CONTENT)
def release_decisao(
    id: int,
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> None:
    service.release(session, id=id, current_user=current_user)


@router.post("/decisoes/{id}/approve", response_model=schemas.DecisaoDetail)
def approve_decisao(
    id: int,
    payload: schemas.DecisaoReviewPayload,
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DecisaoDetail:
    return service.approve_decisao(session, id=id, payload=payload, current_user=current_user)
