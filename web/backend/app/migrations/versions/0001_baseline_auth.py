"""baseline: tabelas FRAPUsuario e FRAPRefreshToken

Revision ID: 0001_baseline_auth
Revises:
Create Date: 2026-05-06

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_baseline_auth"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "FRAPUsuario",
        sa.Column("IdUsuario", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("Email", sa.String(255), nullable=False, unique=True),
        sa.Column("NomeCompleto", sa.String(255), nullable=False),
        sa.Column("SenhaHash", sa.String(255), nullable=False),
        sa.Column("Papel", sa.String(20), nullable=False, server_default="user"),
        sa.Column("Ativo", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column(
            "DataCriacao",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.Column(
            "DataAtualizacao",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
    )

    op.create_table(
        "FRAPRefreshToken",
        sa.Column("IdRefreshToken", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "IdUsuario",
            sa.Integer,
            sa.ForeignKey("FRAPUsuario.IdUsuario", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("TokenHash", sa.String(64), nullable=False, unique=True),
        sa.Column("DataExpiracao", sa.DateTime, nullable=False),
        sa.Column("DataRevogacao", sa.DateTime, nullable=True),
        sa.Column(
            "DataCriacao",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
    )
    op.create_index("ix_FRAPRefreshToken_IdUsuario", "FRAPRefreshToken", ["IdUsuario"])


def downgrade() -> None:
    op.drop_index("ix_FRAPRefreshToken_IdUsuario", table_name="FRAPRefreshToken")
    op.drop_table("FRAPRefreshToken")
    op.drop_table("FRAPUsuario")
