"""Decision-level review router. All endpoints under
``/api/v1/cgad/reviews``, JWT-authenticated.

Thin wrappers over ``app.cgad.review.service``. RFC 7807-compatible errors
come from ``HTTPException`` — FastAPI serializes them as ``{"detail": "..."}``.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db_session
from app.cgad.review import schemas, service
from app.permissoes import require_modulo
from cgad.models import UserORM


router = APIRouter(
    dependencies=[Depends(require_modulo("cgad.reviews"))],
    prefix="/api/v1/cgad/reviews",
    tags=["reviews"],
)


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


@router.get("/orgaos", response_model=list[schemas.OrgaoOut])
def list_orgaos(
    current_user: UserORM = Depends(get_current_user),
) -> list[schemas.OrgaoOut]:
    return service.list_orgaos()


@router.get("/reservas", response_model=list[schemas.ReservaUsuarioOut])
def list_reservas(
    session: Session = Depends(get_db_session),
    _: UserORM = Depends(require_modulo("cgad.reviews", editar=True)),
) -> list[schemas.ReservaUsuarioOut]:
    return service.list_reservas(session)


@router.get("/revisores", response_model=list[schemas.ReservaUsuarioOut])
def list_revisores(
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> list[schemas.ReservaUsuarioOut]:
    return service.list_revisores(session)


@router.get("/decisoes", response_model=schemas.DecisaoListPage)
def list_decisoes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    processo: str | None = Query(None),
    lista_completa: bool = Query(False),
    reserva: Literal["pendentes", "minhas", "usuario", "realizadas"] = Query("pendentes"),
    usuario: str | None = Query(None),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DecisaoListPage:
    if reserva == "usuario" and current_user.Papel != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="role not authorized")
    return service.list_decisoes(
        session,
        page=page,
        page_size=page_size,
        current_user=current_user,
        processo=processo,
        lista_completa=lista_completa,
        reserva=reserva,
        usuario=usuario,
    )


@router.post("/decisoes/claim-lote", response_model=schemas.ClaimLoteResponse)
def claim_lote(
    payload: schemas.ClaimLoteRequest,
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.ClaimLoteResponse:
    return service.claim_lote(session, quantidade=payload.quantidade, current_user=current_user)


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
