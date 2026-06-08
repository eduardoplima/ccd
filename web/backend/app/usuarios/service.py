from __future__ import annotations

import secrets
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.models import FRAPRefreshToken, FRAPUsuario
from app.auth.security import (
    BCRYPT_MAX_BYTES,
    PasswordTooLongError,
    hash_password,
    verify_password,
)


class UsuarioError(Exception):
    pass


class EmailDuplicadoError(UsuarioError):
    pass


class LoginDuplicadoError(UsuarioError):
    pass


class UsuarioNaoEncontradoError(UsuarioError):
    pass


class SenhaAtualInvalidaError(UsuarioError):
    pass


def gerar_senha_temporaria() -> str:
    return secrets.token_urlsafe(9)


def criar_usuario(
    session: Session, *, login: str, email: str, nome_completo: str, papel: str
) -> tuple[FRAPUsuario, str]:
    senha = gerar_senha_temporaria()
    login_norm = login.strip().lower()
    email_norm = email.strip().lower()
    if session.scalar(select(FRAPUsuario).where(FRAPUsuario.Login == login_norm)):
        raise LoginDuplicadoError(f"login já cadastrado: {login_norm}")
    # `Usuarios` não tem coluna de nome completo separada; o login é o NomeUsuario.
    _ = nome_completo
    user = FRAPUsuario(
        Login=login_norm,
        Email=email_norm,
        SenhaHash=hash_password(senha),
        Papel=papel,
        Ativo=True,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        if session.scalar(select(FRAPUsuario).where(FRAPUsuario.Login == login_norm)):
            raise LoginDuplicadoError(f"login já cadastrado: {login_norm}") from exc
        raise EmailDuplicadoError(f"e-mail já cadastrado: {email_norm}") from exc
    session.refresh(user)
    return user, senha


def listar_usuarios(
    session: Session,
    *,
    papel: str | None = None,
    ativo: bool | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
) -> tuple[list[FRAPUsuario], int]:
    stmt = select(FRAPUsuario)
    count_stmt = select(func.count()).select_from(FRAPUsuario)
    if papel:
        stmt = stmt.where(FRAPUsuario.Papel == papel)
        count_stmt = count_stmt.where(FRAPUsuario.Papel == papel)
    if ativo is not None:
        stmt = stmt.where(FRAPUsuario.Ativo == ativo)
        count_stmt = count_stmt.where(FRAPUsuario.Ativo == ativo)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                FRAPUsuario.Login.like(like),
                FRAPUsuario.Email.like(like),
            )
        )
        count_stmt = count_stmt.where(
            or_(
                FRAPUsuario.Login.like(like),
                FRAPUsuario.Email.like(like),
            )
        )

    total = int(session.execute(count_stmt).scalar_one())
    rows = (
        session.execute(
            stmt.order_by(FRAPUsuario.IdUsuario.desc()).offset((page - 1) * size).limit(size)
        )
        .scalars()
        .all()
    )
    return list(rows), total


def obter_usuario(session: Session, id_usuario: int) -> FRAPUsuario:
    user = session.get(FRAPUsuario, id_usuario)
    if user is None:
        raise UsuarioNaoEncontradoError(f"usuário {id_usuario} não encontrado")
    return user


def atualizar_usuario(
    session: Session,
    id_usuario: int,
    *,
    nome_completo: str | None = None,
    papel: str | None = None,
    ativo: bool | None = None,
) -> FRAPUsuario:
    user = obter_usuario(session, id_usuario)
    # `nome_completo` não é persistido (Usuarios não tem essa coluna); ignorado.
    _ = nome_completo
    if papel is not None:
        user.Papel = papel
    if ativo is not None:
        user.Ativo = ativo
        if not ativo:
            _revogar_refresh_tokens(session, user.IdUsuario)
    user.DataAtualizacao = datetime.now(UTC).replace(tzinfo=None)
    session.commit()
    session.refresh(user)
    return user


def resetar_senha(session: Session, id_usuario: int) -> str:
    user = obter_usuario(session, id_usuario)
    senha = gerar_senha_temporaria()
    user.SenhaHash = hash_password(senha)
    user.DataAtualizacao = datetime.now(UTC).replace(tzinfo=None)
    _revogar_refresh_tokens(session, user.IdUsuario)
    session.commit()
    return senha


def trocar_senha(session: Session, *, user: FRAPUsuario, senha_atual: str, senha_nova: str) -> None:
    if not verify_password(senha_atual, user.SenhaHash):
        raise SenhaAtualInvalidaError("senha atual incorreta")
    if len(senha_nova.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise PasswordTooLongError(f"senha excede {BCRYPT_MAX_BYTES} bytes (limite do bcrypt)")
    user.SenhaHash = hash_password(senha_nova)
    user.DataAtualizacao = datetime.now(UTC).replace(tzinfo=None)
    _revogar_refresh_tokens(session, user.IdUsuario)
    session.commit()


def _revogar_refresh_tokens(session: Session, id_usuario: int) -> None:
    now = datetime.now(UTC).replace(tzinfo=None)
    tokens = (
        session.execute(
            select(FRAPRefreshToken)
            .where(FRAPRefreshToken.IdUsuario == id_usuario)
            .where(FRAPRefreshToken.DataRevogacao.is_(None))
        )
        .scalars()
        .all()
    )
    for t in tokens:
        t.DataRevogacao = now
