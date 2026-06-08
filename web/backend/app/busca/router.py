from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.busca import service
from app.busca.schemas import (
    DebitoPessoaListResponse,
    PessoaListResponse,
    ProcessoResultado,
)
from app.deps import get_current_user, get_db_session

router = APIRouter(prefix="/api/v1/frap/busca", tags=["frap:busca"])


@router.get("/pessoas", response_model=PessoaListResponse)
def buscar_pessoas(
    q: str = Query(..., min_length=3, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> PessoaListResponse:
    return service.buscar_pessoas(session, q=q, page=page, size=size)


@router.get("/processo", response_model=ProcessoResultado)
def buscar_processo(
    numero: str = Query(..., pattern=r"^\d{1,6}$"),
    ano: str = Query(..., pattern=r"^\d{4}$"),
    tipo: Literal["origem", "execucao"] = Query(default="origem"),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> ProcessoResultado:
    out = service.buscar_processo(session, numero=numero, ano=ano, tipo=tipo)
    if out is None:
        raise HTTPException(status_code=404, detail="processo not found")
    return out


@router.get("/debitos-pessoa", response_model=DebitoPessoaListResponse)
def buscar_debitos_pessoa(
    cpfcnpj: str = Query(..., min_length=11, max_length=14),
    id_processo: int | None = Query(default=None, ge=1),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> DebitoPessoaListResponse:
    return service.buscar_debitos_pessoa(session, cpfcnpj=cpfcnpj, id_processo=id_processo)
