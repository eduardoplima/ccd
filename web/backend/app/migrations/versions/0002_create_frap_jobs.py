"""baseline: tabela FRAPJob

Revision ID: 0002_create_frap_jobs
Revises: 0001_baseline_auth
Create Date: 2026-05-06

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_create_frap_jobs"
down_revision: str | Sequence[str] | None = "0001_baseline_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "FRAPJob",
        sa.Column("IdFRAPJob", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ArqJobId", sa.String(64), nullable=False, unique=True),
        sa.Column("Tipo", sa.String(40), nullable=False),
        sa.Column("Argumentos", sa.String(2000), nullable=True),
        sa.Column("Status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column(
            "IdUsuario",
            sa.Integer,
            sa.ForeignKey("FRAPUsuario.IdUsuario"),
            nullable=False,
        ),
        sa.Column(
            "DataCriacao",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("SYSUTCDATETIME()"),
        ),
        sa.Column("DataInicio", sa.DateTime, nullable=True),
        sa.Column("DataFim", sa.DateTime, nullable=True),
        sa.Column("ErroMensagem", sa.String(2000), nullable=True),
        sa.Column("Resultado", sa.String(4000), nullable=True),
    )
    op.create_index("ix_FRAPJob_ArqJobId", "FRAPJob", ["ArqJobId"], unique=True)
    op.create_index("ix_FRAPJob_IdUsuario", "FRAPJob", ["IdUsuario"])
    op.create_index("ix_FRAPJob_Status", "FRAPJob", ["Status"])
    op.create_index("ix_FRAPJob_DataCriacao", "FRAPJob", ["DataCriacao"])


def downgrade() -> None:
    op.drop_index("ix_FRAPJob_DataCriacao", table_name="FRAPJob")
    op.drop_index("ix_FRAPJob_Status", table_name="FRAPJob")
    op.drop_index("ix_FRAPJob_IdUsuario", table_name="FRAPJob")
    op.drop_index("ix_FRAPJob_ArqJobId", table_name="FRAPJob")
    op.drop_table("FRAPJob")
