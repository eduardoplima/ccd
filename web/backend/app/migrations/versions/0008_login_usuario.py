"""FRAPUsuario: coluna Login (chave de autenticação).

O login passa a ser a chave para entrar (no lugar do e-mail). Existe
exatamente um usuário em produção; ele recebe Login='eduardo' no backfill.

Revision ID: 0008_login_usuario
Revises: 0007_valor_debitos_notificados
Create Date: 2026-05-13
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0008_login_usuario"
down_revision: str | Sequence[str] | None = "0007_valor_debitos_notificados"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPUsuario')
               AND name = 'Login'
        )
            ALTER TABLE dbo.FRAPUsuario ADD Login NVARCHAR(64) NULL;
        """
    )
    op.execute("UPDATE dbo.FRAPUsuario SET Login = 'eduardo' WHERE Login IS NULL;")
    op.execute("ALTER TABLE dbo.FRAPUsuario ALTER COLUMN Login NVARCHAR(64) NOT NULL;")
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ux_FRAPUsuario_Login'
               AND object_id = OBJECT_ID('dbo.FRAPUsuario')
        )
            CREATE UNIQUE INDEX ux_FRAPUsuario_Login
                ON dbo.FRAPUsuario(Login);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ux_FRAPUsuario_Login'
               AND object_id = OBJECT_ID('dbo.FRAPUsuario')
        )
            DROP INDEX ux_FRAPUsuario_Login ON dbo.FRAPUsuario;
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPUsuario')
               AND name = 'Login'
        )
            ALTER TABLE dbo.FRAPUsuario DROP COLUMN Login;
        """
    )
