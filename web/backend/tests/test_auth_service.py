from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.models import FRAPRefreshToken, FRAPUsuario
from app.auth.security import hash_password, hash_refresh_token


def _create_user(
    session: Session,
    login: str = "user1",
    email: str = "u@tce.rn",
    papel: str = "user",
    ativo: bool = True,
) -> FRAPUsuario:
    user = FRAPUsuario(
        Login=login,
        Email=email,
        SenhaHash=hash_password("senha-123"),
        Papel=papel,
        Ativo=ativo,
    )
    session.add(user)
    session.commit()
    return user


def test_authenticate_user_ok(db_session: Session) -> None:
    _create_user(db_session)
    user = service.authenticate_user(db_session, "user1", "senha-123")
    assert user.Login == "user1"


def test_authenticate_user_wrong_password(db_session: Session) -> None:
    _create_user(db_session)
    with pytest.raises(service.InvalidCredentialsError):
        service.authenticate_user(db_session, "user1", "errada")


def test_authenticate_user_inactive(db_session: Session) -> None:
    _create_user(db_session, ativo=False)
    with pytest.raises(service.InactiveUserError):
        service.authenticate_user(db_session, "user1", "senha-123")


def test_issue_token_pair_persists_refresh(db_session: Session) -> None:
    user = _create_user(db_session)
    pair = service.issue_token_pair(db_session, user)
    refresh = db_session.query(FRAPRefreshToken).one()
    assert refresh.TokenHash == hash_refresh_token(pair.refresh_token)
    assert refresh.IdUsuario == user.IdUsuario
    assert refresh.DataRevogacao is None


def test_rotate_refresh_token_revokes_old_and_issues_new(db_session: Session) -> None:
    user = _create_user(db_session)
    old = service.issue_token_pair(db_session, user)
    new = service.rotate_refresh_token(db_session, old.refresh_token)
    assert new.refresh_token != old.refresh_token
    revogados = (
        db_session.query(FRAPRefreshToken)
        .filter(FRAPRefreshToken.DataRevogacao.isnot(None))
        .count()
    )
    assert revogados == 1


def test_rotate_refresh_token_rejects_revoked(db_session: Session) -> None:
    user = _create_user(db_session)
    pair = service.issue_token_pair(db_session, user)
    service.logout(db_session, pair.refresh_token)
    with pytest.raises(service.InvalidRefreshTokenError):
        service.rotate_refresh_token(db_session, pair.refresh_token)


def test_rotate_refresh_token_rejects_expired(db_session: Session) -> None:
    user = _create_user(db_session)
    pair = service.issue_token_pair(db_session, user)
    record = db_session.query(FRAPRefreshToken).one()
    record.DataExpiracao = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
    db_session.commit()
    with pytest.raises(service.InvalidRefreshTokenError):
        service.rotate_refresh_token(db_session, pair.refresh_token)
