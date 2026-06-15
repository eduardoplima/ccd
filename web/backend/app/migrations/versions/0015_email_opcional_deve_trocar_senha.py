"""Email opcional + DeveTrocarSenha (troca obrigatória no 1º acesso).

- `Usuarios.Email` passa a ser NULLable e a unicidade vira **índice filtrado**
  (`WHERE Email IS NOT NULL`), pois no SQL Server um índice único comum só
  admite UM NULL — com vários usuários sem e-mail isso violaria a unicidade.
- Nova coluna `DeveTrocarSenha bit NOT NULL DEFAULT 0`. Linhas existentes
  (admin, eduardo) ficam 0 (não forçadas); contas criadas com senha provisória
  gravam 1 e são barradas até trocar a senha.

Revision ID: 0015_email_opcional_deve_trocar_senha
Revises: 0014_repoint_user_fks
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0015_email_opcional_deve_trocar_senha"
down_revision: str | Sequence[str] | None = "0014_repoint_user_fks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) troca o índice único cheio por um filtrado (permite múltiplos NULLs)
    op.execute("DROP INDEX ix_usuarios_email ON dbo.Usuarios;")
    # 2) Email passa a aceitar NULL
    op.execute("ALTER TABLE dbo.Usuarios ALTER COLUMN Email varchar(255) NULL;")
    op.execute(
        "CREATE UNIQUE INDEX ix_usuarios_email ON dbo.Usuarios(Email) "
        "WHERE Email IS NOT NULL;"
    )
    # 3) nova coluna; existentes recebem 0 (não forçados a trocar)
    op.execute(
        "ALTER TABLE dbo.Usuarios "
        "ADD DeveTrocarSenha bit NOT NULL "
        "CONSTRAINT DF_Usuarios_DeveTrocarSenha DEFAULT 0;"
    )


def downgrade() -> None:
    # remove a coluna (dropa o default nomeado antes)
    op.execute("ALTER TABLE dbo.Usuarios DROP CONSTRAINT DF_Usuarios_DeveTrocarSenha;")
    op.execute("ALTER TABLE dbo.Usuarios DROP COLUMN DeveTrocarSenha;")
    # volta o índice único cheio (falha se houver Email NULL — limpar antes)
    op.execute("DROP INDEX ix_usuarios_email ON dbo.Usuarios;")
    op.execute("ALTER TABLE dbo.Usuarios ALTER COLUMN Email varchar(255) NOT NULL;")
    op.execute("CREATE UNIQUE INDEX ix_usuarios_email ON dbo.Usuarios(Email);")
