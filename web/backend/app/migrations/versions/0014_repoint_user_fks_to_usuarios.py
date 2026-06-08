"""Repoint user FKs de FRAPUsuario para Usuarios.

A webapp consolidada usa apenas `Usuarios` para autenticação. As tabelas
operacionais do FRAP que referenciavam `FRAPUsuario` precisam apontar para
`Usuarios`:

- `FRAPJob.IdUsuario`              -> Usuarios.IdUsuario
- `FRAPMatchDescontoFolha.IdUsuarioConcilia` -> Usuarios.IdUsuario

Os dados históricos guardavam IdUsuario=1 (eduardo em FRAPUsuario). Em
`Usuarios`, id 1 = admin e id 2 = eduardo, então remapeamos 1 -> 2 para
preservar a atribuição ao eduardo antes de recriar as FKs.

Revision ID: 0014_repoint_user_fks
Revises: 0013_lancamento_seq_bb
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0014_repoint_user_fks"
down_revision: str | Sequence[str] | None = "0013_lancamento_seq_bb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _drop_fks_referencing(table: str, referenced: str) -> None:
    """Dropa dinamicamente toda FK em `table` que referencia `referenced`
    (os nomes auto-gerados pelo SQL Server variam)."""
    op.execute(
        f"""
        DECLARE @sql NVARCHAR(MAX) = N'';
        SELECT @sql = @sql + N'ALTER TABLE dbo.{table} DROP CONSTRAINT '
                            + QUOTENAME(fk.name) + N';'
        FROM sys.foreign_keys fk
        WHERE fk.parent_object_id = OBJECT_ID('dbo.{table}')
          AND fk.referenced_object_id = OBJECT_ID('dbo.{referenced}');
        EXEC sp_executesql @sql;
        """
    )


def upgrade() -> None:
    # 1) remove FKs antigas -> FRAPUsuario (senão o remap abaixo viola a FK,
    #    pois FRAPUsuario só tem id 1)
    _drop_fks_referencing("FRAPJob", "FRAPUsuario")
    _drop_fks_referencing("FRAPMatchDescontoFolha", "FRAPUsuario")

    # 2) preserva atribuição ao eduardo (FRAPUsuario.1 -> Usuarios.2)
    op.execute("UPDATE dbo.FRAPJob SET IdUsuario = 2 WHERE IdUsuario = 1;")
    op.execute(
        "UPDATE dbo.FRAPMatchDescontoFolha SET IdUsuarioConcilia = 2 "
        "WHERE IdUsuarioConcilia = 1;"
    )

    # 3) recria FKs apontando para Usuarios
    op.execute(
        "ALTER TABLE dbo.FRAPJob "
        "ADD CONSTRAINT FK_FRAPJob_Usuarios "
        "FOREIGN KEY (IdUsuario) REFERENCES dbo.Usuarios(IdUsuario);"
    )
    op.execute(
        "ALTER TABLE dbo.FRAPMatchDescontoFolha "
        "ADD CONSTRAINT FK_FRAPMatchDescontoFolha_Usuarios "
        "FOREIGN KEY (IdUsuarioConcilia) REFERENCES dbo.Usuarios(IdUsuario);"
    )


def downgrade() -> None:
    _drop_fks_referencing("FRAPJob", "Usuarios")
    _drop_fks_referencing("FRAPMatchDescontoFolha", "Usuarios")
    op.execute(
        "ALTER TABLE dbo.FRAPJob "
        "ADD CONSTRAINT FK_FRAPJob_FRAPUsuario "
        "FOREIGN KEY (IdUsuario) REFERENCES dbo.FRAPUsuario(IdUsuario);"
    )
    op.execute(
        "ALTER TABLE dbo.FRAPMatchDescontoFolha "
        "ADD CONSTRAINT FK_FRAPMatchDescontoFolha_Usuario "
        "FOREIGN KEY (IdUsuarioConcilia) REFERENCES dbo.FRAPUsuario(IdUsuario);"
    )
