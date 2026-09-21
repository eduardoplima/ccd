"""Permissões por módulo: matriz usuário × módulo (ver / editar).

`admin` vê e edita tudo; `user` vê tudo e edita os módulos com PodeEditar=1;
`restrito` (novo valor de Usuarios.Papel) só vê os módulos com linha aqui e
edita os com PodeEditar=1. As chaves de módulo vivem em `app.permissoes.MODULOS`.

Revision ID: 0026_usuario_permissoes
Revises: 0025_ccd_desconto_folha_notificacao
Create Date: 2026-09-21
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0026_usuario_permissoes"
down_revision: str | Sequence[str] | None = "0025_ccd_desconto_folha_notificacao"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.UsuarioPermissoes', 'U') IS NULL
        CREATE TABLE dbo.UsuarioPermissoes (
            IdUsuario INT NOT NULL
                CONSTRAINT FK_UsuarioPermissoes_Usuarios
                REFERENCES dbo.Usuarios (IdUsuario) ON DELETE CASCADE,
            Modulo VARCHAR(40) NOT NULL,
            PodeEditar BIT NOT NULL CONSTRAINT DF_UsuarioPermissoes_PodeEditar DEFAULT 0,
            CONSTRAINT PK_UsuarioPermissoes PRIMARY KEY (IdUsuario, Modulo)
        );
        """
    )


def downgrade() -> None:
    op.execute(
        "IF OBJECT_ID('dbo.UsuarioPermissoes', 'U') IS NOT NULL DROP TABLE dbo.UsuarioPermissoes;"
    )
