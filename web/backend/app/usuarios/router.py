from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.deps import get_db_session, require_role
from app.usuarios import service
from app.usuarios.schemas import (
    ResetSenhaResponse,
    UsuarioCreateRequest,
    UsuarioCreateResponse,
    UsuarioListResponse,
    UsuarioOut,
    UsuarioUpdateRequest,
)

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioCreateResponse, status_code=status.HTTP_201_CREATED)
def criar(
    payload: UsuarioCreateRequest,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> UsuarioCreateResponse:
    try:
        usuario, senha = service.criar_usuario(
            session,
            login=payload.login,
            email=payload.email,
            nome_completo=payload.nome_completo,
            papel=payload.papel,
        )
    except (service.EmailDuplicadoError, service.LoginDuplicadoError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UsuarioCreateResponse(usuario=UsuarioOut.model_validate(usuario), senha_temporaria=senha)


@router.get("", response_model=UsuarioListResponse)
def listar(
    papel: str | None = Query(default=None, pattern=r"^(user|admin)$"),
    ativo: bool | None = Query(default=None),
    q: str | None = Query(default=None, min_length=2, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> UsuarioListResponse:
    items, total = service.listar_usuarios(
        session, papel=papel, ativo=ativo, q=q, page=page, size=size
    )
    return UsuarioListResponse(
        items=[UsuarioOut.model_validate(u) for u in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{id_usuario}", response_model=UsuarioOut)
def detalhe(
    id_usuario: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> UsuarioOut:
    try:
        return UsuarioOut.model_validate(service.obter_usuario(session, id_usuario))
    except service.UsuarioNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{id_usuario}", response_model=UsuarioOut)
def atualizar(
    id_usuario: int,
    payload: UsuarioUpdateRequest,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> UsuarioOut:
    try:
        user = service.atualizar_usuario(
            session,
            id_usuario,
            nome_completo=payload.nome_completo,
            papel=payload.papel,
            ativo=payload.ativo,
        )
    except service.UsuarioNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UsuarioOut.model_validate(user)


@router.post("/{id_usuario}/reset-senha", response_model=ResetSenhaResponse)
def reset_senha(
    id_usuario: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> ResetSenhaResponse:
    try:
        senha = service.resetar_senha(session, id_usuario)
    except service.UsuarioNaoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ResetSenhaResponse(senha_temporaria=senha)
