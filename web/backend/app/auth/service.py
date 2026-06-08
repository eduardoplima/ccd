from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import security
from app.auth.models import FRAPRefreshToken, FRAPUsuario
from app.auth.schemas import TokenPair
from app.config import get_settings


class AuthError(Exception):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InactiveUserError(AuthError):
    pass


class InvalidRefreshTokenError(AuthError):
    pass


def authenticate_user(session: Session, login: str, senha: str) -> FRAPUsuario:
    user = session.scalar(select(FRAPUsuario).where(FRAPUsuario.Login == login.strip().lower()))
    if user is None or not security.verify_password(senha, user.SenhaHash):
        raise InvalidCredentialsError("credenciais inválidas")
    if not user.Ativo:
        raise InactiveUserError("usuário inativo")
    return user


def issue_token_pair(session: Session, user: FRAPUsuario) -> TokenPair:
    settings = get_settings()
    access_token, expires_in = security.encode_access_token(
        subject=str(user.IdUsuario), papel=user.Papel, settings=settings
    )
    refresh_token = security.generate_refresh_token()
    refresh_record = FRAPRefreshToken(
        IdUsuario=user.IdUsuario,
        TokenHash=security.hash_refresh_token(refresh_token),
        DataExpiracao=datetime.now(UTC).replace(tzinfo=None)
        + timedelta(days=settings.jwt_refresh_token_expire_days),
    )
    session.add(refresh_record)
    session.commit()
    return TokenPair(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)


def rotate_refresh_token(session: Session, refresh_token: str) -> TokenPair:
    record = _find_active_refresh(session, refresh_token)
    record.DataRevogacao = datetime.now(UTC).replace(tzinfo=None)
    session.flush()
    user = session.get(FRAPUsuario, record.IdUsuario)
    if user is None or not user.Ativo:
        session.commit()
        raise InvalidRefreshTokenError("usuário associado inválido")
    return issue_token_pair(session, user)


def logout(session: Session, refresh_token: str) -> None:
    try:
        record = _find_active_refresh(session, refresh_token)
    except InvalidRefreshTokenError:
        return
    record.DataRevogacao = datetime.now(UTC).replace(tzinfo=None)
    session.commit()


def _find_active_refresh(session: Session, refresh_token: str) -> FRAPRefreshToken:
    token_hash = security.hash_refresh_token(refresh_token)
    record = session.scalar(
        select(FRAPRefreshToken).where(FRAPRefreshToken.TokenHash == token_hash)
    )
    if record is None:
        raise InvalidRefreshTokenError("refresh token desconhecido")
    if record.DataRevogacao is not None:
        raise InvalidRefreshTokenError("refresh token revogado")
    if record.DataExpiracao < datetime.now(UTC).replace(tzinfo=None):
        raise InvalidRefreshTokenError("refresh token expirado")
    return record
