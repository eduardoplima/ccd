from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.models import FRAPUsuario
from app.auth.schemas import LoginRequest, RefreshRequest, TokenPair, UserOut
from app.auth.security import PasswordTooLongError
from app.deps import get_current_user, get_db_session
from app.usuarios import service as usuarios_service
from app.usuarios.schemas import TrocarSenhaRequest

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, session: Session = Depends(get_db_session)) -> TokenPair:
    try:
        user = service.authenticate_user(session, payload.login, payload.senha)
    except service.InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except service.InactiveUserError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return service.issue_token_pair(session, user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, session: Session = Depends(get_db_session)) -> TokenPair:
    try:
        return service.rotate_refresh_token(session, payload.refresh_token)
    except service.InvalidRefreshTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, session: Session = Depends(get_db_session)) -> None:
    service.logout(session, payload.refresh_token)


@router.get("/me", response_model=UserOut)
def me(user: FRAPUsuario = Depends(get_current_user)) -> FRAPUsuario:
    return user


@router.post("/trocar-senha", status_code=status.HTTP_204_NO_CONTENT)
def trocar_senha(
    payload: TrocarSenhaRequest,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> None:
    try:
        usuarios_service.trocar_senha(
            session,
            user=user,
            senha_atual=payload.senha_atual,
            senha_nova=payload.senha_nova,
        )
    except usuarios_service.SenhaAtualInvalidaError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except PasswordTooLongError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
