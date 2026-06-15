from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth import security
from app.auth.models import FRAPUsuario
from app.db import processo_session_scope, session_scope

bearer_scheme = HTTPBearer(auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    yield from session_scope()


def get_processo_session() -> Generator[Session, None, None]:
    """Sessão (somente leitura) para o banco `processo` (módulo CCD)."""
    yield from processo_session_scope()


# Rotas liberadas mesmo quando o usuário precisa trocar a senha (senão ele não
# conseguiria nem ver os próprios dados nem efetuar a troca).
_TROCA_SENHA_ALLOWLIST = frozenset(
    {"/api/v1/auth/me", "/api/v1/auth/trocar-senha"}
)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_db_session),
) -> FRAPUsuario:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token"
        )
    try:
        payload = security.decode_access_token(credentials.credentials)
    except security.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid subject")
    user = session.get(FRAPUsuario, int(sub))
    if user is None or not user.Ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")
    # Defesa em profundidade: usuário com senha provisória só acessa /me e a
    # troca de senha; o frontend redireciona para /conta antes disso.
    if user.DeveTrocarSenha and request.url.path not in _TROCA_SENHA_ALLOWLIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="must change password"
        )
    return user


def require_role(*roles: str):
    def _enforce(user: FRAPUsuario = Depends(get_current_user)) -> FRAPUsuario:
        if user.Papel not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="role not authorized"
            )
        return user

    return _enforce


def get_arq_pool(request: Request):
    pool = getattr(request.app.state, "arq_pool", None)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="task queue not configured (REDIS_URL missing)",
        )
    return pool
