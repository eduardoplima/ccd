from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class FRAPJob(Base):
    __tablename__ = "FRAPJob"

    IdFRAPJob: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ArqJobId: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    Tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    Argumentos: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    Status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    IdUsuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("Usuarios.IdUsuario"), nullable=False, index=True
    )
    DataCriacao: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    DataInicio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    DataFim: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ErroMensagem: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    Resultado: Mapped[str | None] = mapped_column(String(4000), nullable=True)
