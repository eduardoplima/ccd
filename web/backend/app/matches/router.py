from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.deps import get_current_user, get_db_session
from app.matches import service
from app.matches.schemas import (
    MatchDescontoFolhaListResponse,
    MatchGuiaListResponse,
    MatchOBListResponse,
    MatchPessoaListResponse,
)

router = APIRouter(prefix="/api/v1/frap/matches", tags=["frap:matches"])

_CONTA_REGEX = r"^\d{6}-\d$"


@router.get("/ob", response_model=MatchOBListResponse)
def listar_ob(
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None, ge=1, le=12),
    conta: str | None = Query(default=None, pattern=_CONTA_REGEX),
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> MatchOBListResponse:
    return service.list_matches_ob(
        session, ano=ano, mes=mes, conta=conta, q=q, page=page, size=size
    )


@router.get("/pessoa", response_model=MatchPessoaListResponse)
def listar_pessoa(
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None, ge=1, le=12),
    conta: str | None = Query(default=None, pattern=_CONTA_REGEX),
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> MatchPessoaListResponse:
    return service.list_matches_pessoa(
        session, ano=ano, mes=mes, conta=conta, q=q, page=page, size=size
    )


@router.get("/guia", response_model=MatchGuiaListResponse)
def listar_guia(
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None, ge=1, le=12),
    conta: str | None = Query(default=None, pattern=_CONTA_REGEX),
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> MatchGuiaListResponse:
    return service.list_matches_guia(
        session, ano=ano, mes=mes, conta=conta, q=q, page=page, size=size
    )


@router.get("/desconto-folha", response_model=MatchDescontoFolhaListResponse)
def listar_desconto_folha(
    ano: int | None = Query(default=None),
    mes: int | None = Query(default=None, ge=1, le=12),
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> MatchDescontoFolhaListResponse:
    return service.list_matches_desconto_folha(session, ano=ano, mes=mes, q=q, page=page, size=size)
