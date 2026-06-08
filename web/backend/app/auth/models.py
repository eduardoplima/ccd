"""ORM de autenticação.

A webapp consolidada usa **apenas** a tabela `Usuarios` (e `TokensRenovacao`)
em BdDIP — as tabelas `FRAPUsuario`/`FRAPRefreshToken` foram abandonadas.

Para minimizar a mudança no resto do backend (escrito sobre a auth do
frap-controle) expomos:
- `Login`  como *synonym* de `NomeUsuario` (a coluna real de login em `Usuarios`);
- `TokenHash` como *synonym* de `HashToken` (a coluna real em `TokensRenovacao`);
- `NomeCompleto` como propriedade somente-leitura (= `NomeUsuario`), já que
  `Usuarios` não tem nome completo separado;
- os aliases `FRAPUsuario` / `FRAPRefreshToken` apontando para os novos modelos,
  para que `from app.auth.models import FRAPUsuario` continue funcionando.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Usuario(Base):
    __tablename__ = "Usuarios"

    IdUsuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    NomeUsuario: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    Email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    SenhaHash: Mapped[str] = mapped_column(String(255), nullable=False)
    Papel: Mapped[str] = mapped_column(String(8), nullable=False, default="user")
    Ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    DataCriacao: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    DataAtualizacao: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # `Login` é a chave de autenticação no resto do código → é a coluna NomeUsuario.
    Login = synonym("NomeUsuario")

    refresh_tokens: Mapped[list[TokenRenovacao]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )

    @property
    def NomeCompleto(self) -> str:  # noqa: N802  (nome usado pelos DTOs)
        """`Usuarios` não guarda nome completo; expõe o login por
        compatibilidade com `UserOut.nome_completo`."""
        return self.NomeUsuario


class TokenRenovacao(Base):
    __tablename__ = "TokensRenovacao"

    IdTokenRenovacao: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    IdUsuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("Usuarios.IdUsuario", ondelete="CASCADE"), nullable=False, index=True
    )
    HashToken: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    DataExpiracao: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    DataRevogacao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    DataCriacao: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)

    # O código de auth do frap usa `.TokenHash`; a coluna real é `HashToken`.
    TokenHash = synonym("HashToken")

    usuario: Mapped[Usuario] = relationship(back_populates="refresh_tokens")


# --- aliases de compatibilidade (imports legados do frap-controle) ---
FRAPUsuario = Usuario
FRAPRefreshToken = TokenRenovacao
