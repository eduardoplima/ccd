"""Conjunto de dados anotado (CGAD). Endpoints sob
``/api/v1/cgad/dataset``, autenticados por JWT.

Envelope fino sobre ``app.cgad.dataset.service``. Cada anotador só enxerga a
própria fila — o service resolve tudo por ``current_user.NomeUsuario``.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.cgad.dataset import schemas, service
from app.deps import get_current_user, get_db_session, require_role
from cgad.models import UserORM


router = APIRouter(prefix="/api/v1/cgad/dataset", tags=["dataset"])


@router.get("/documentos", response_model=schemas.DocumentoListPage)
def list_documentos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: schemas.StatusAnotacao | None = Query(None),
    origem: schemas.Origem | None = Query(None),
    ano: int | None = Query(None, ge=2000, le=2100),
    com_entidades: bool | None = Query(None),
    sem_atos_pessoal: bool | None = Query(None),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DocumentoListPage:
    return service.list_documentos(
        session,
        anotador=current_user.NomeUsuario,
        page=page,
        page_size=page_size,
        status_filtro=status,
        origem=origem,
        ano=ano,
        com_entidades=com_entidades,
        sem_atos_pessoal=sem_atos_pessoal,
    )


# `com_entidades`/`sem_atos_pessoal` aqui não filtram o documento pedido: definem
# de qual fila sai o `proximo_pendente`, para o botão Concluir não jogar o
# anotador da aba de triagem de volta na fila inteira.
@router.get("/documentos/{id}", response_model=schemas.DocumentoDetail)
def get_documento(
    id: int,
    com_entidades: bool | None = Query(None),
    sem_atos_pessoal: bool | None = Query(None),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DocumentoDetail:
    return service.get_documento(
        session,
        id=id,
        anotador=current_user.NomeUsuario,
        com_entidades=com_entidades,
        sem_atos_pessoal=sem_atos_pessoal,
    )


@router.put("/documentos/{id}/anotacao", response_model=schemas.DocumentoDetail)
def salvar_anotacao(
    id: int,
    payload: schemas.AnotacaoPayload,
    com_entidades: bool | None = Query(None),
    sem_atos_pessoal: bool | None = Query(None),
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.DocumentoDetail:
    return service.salvar_anotacao(
        session,
        id=id,
        payload=payload,
        anotador=current_user.NomeUsuario,
        com_entidades=com_entidades,
        sem_atos_pessoal=sem_atos_pessoal,
    )


@router.get("/progresso", response_model=schemas.Progresso)
def progresso(
    session: Session = Depends(get_db_session),
    current_user: UserORM = Depends(get_current_user),
) -> schemas.Progresso:
    return service.progresso(session)


# Admin-only: expõe as anotações dos três lado a lado, o que quebraria a
# anotação cega se qualquer anotador visse.
@router.get(
    "/divergencias",
    response_model=schemas.Divergencias,
    dependencies=[Depends(require_role("admin"))],
)
def divergencias(session: Session = Depends(get_db_session)) -> schemas.Divergencias:
    return service.divergencias(session)


@router.get(
    "/divergencias/{id}",
    response_model=schemas.DivergenciaDetail,
    dependencies=[Depends(require_role("admin"))],
)
def divergencia_detail(
    id: int,
    session: Session = Depends(get_db_session),
) -> schemas.DivergenciaDetail:
    return service.divergencia_detail(session, id=id)


@router.get(
    "/export",
    response_model=list[schemas.DocumentoExport],
    dependencies=[Depends(require_role("admin"))],
)
def export(
    anotador: str = Query(..., min_length=1),
    session: Session = Depends(get_db_session),
) -> list[schemas.DocumentoExport]:
    return service.export(session, anotador=anotador)
