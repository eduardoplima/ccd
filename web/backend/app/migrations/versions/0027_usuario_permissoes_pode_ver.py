"""Permissões por módulo: visualização removível (PodeVer).

O papel `restrito` sai: todo usuário vê tudo por default e o admin remove a
visualização módulo a módulo (linha com PodeVer=0). Sem linha = só vê;
PodeEditar=1 = edita.

Revision ID: 0027_usuario_permissoes_pode_ver
Revises: 0026_usuario_permissoes
Create Date: 2026-09-21
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0027_usuario_permissoes_pode_ver"
down_revision: str | Sequence[str] | None = "0026_usuario_permissoes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "IF COL_LENGTH('dbo.UsuarioPermissoes', 'PodeVer') IS NULL "
        "ALTER TABLE dbo.UsuarioPermissoes ADD PodeVer BIT NOT NULL "
        "CONSTRAINT DF_UsuarioPermissoes_PodeVer DEFAULT 1;"
    )
    op.execute("UPDATE dbo.Usuarios SET Papel = 'user' WHERE Papel = 'restrito';")


def downgrade() -> None:
    op.execute(
        "IF COL_LENGTH('dbo.UsuarioPermissoes', 'PodeVer') IS NOT NULL BEGIN "
        "ALTER TABLE dbo.UsuarioPermissoes DROP CONSTRAINT DF_UsuarioPermissoes_PodeVer; "
        "ALTER TABLE dbo.UsuarioPermissoes DROP COLUMN PodeVer; END"
    )
