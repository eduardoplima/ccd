"""desconto-folha: órgão notificado

Adiciona FRAPDescontoFolha.IdOrgaoNotificado + NomeOrgaoNotificado.
1 desconto = 1 órgão notificado (coluna ÓRGÃO da planilha "Desconto em Folha
Valores"). Eixo "por órgão" passa a agrupar por essa coluna direto, sem
cross-DB. Registros antigos ficam NULL até serem preenchidos.

Revision ID: 0004_orgao_notificado
Revises: 0003_desconto_folha_extensoes
Create Date: 2026-05-07
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0004_orgao_notificado"
down_revision: str | Sequence[str] | None = "0003_desconto_folha_extensoes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPDescontoFolha') AND name = 'IdOrgaoNotificado'
        )
            ALTER TABLE dbo.FRAPDescontoFolha ADD IdOrgaoNotificado INT NULL;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPDescontoFolha') AND name = 'NomeOrgaoNotificado'
        )
            ALTER TABLE dbo.FRAPDescontoFolha ADD NomeOrgaoNotificado NVARCHAR(200) NULL;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'IX_FRAPDescontoFolha_IdOrgaoNotificado'
               AND object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
        )
            CREATE INDEX IX_FRAPDescontoFolha_IdOrgaoNotificado
                ON dbo.FRAPDescontoFolha(IdOrgaoNotificado)
                WHERE IdOrgaoNotificado IS NOT NULL;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'IX_FRAPDescontoFolha_IdOrgaoNotificado'
               AND object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
        )
            DROP INDEX IX_FRAPDescontoFolha_IdOrgaoNotificado ON dbo.FRAPDescontoFolha;
        """
    )
    for col in ("NomeOrgaoNotificado", "IdOrgaoNotificado"):
        op.execute(
            f"""
            IF EXISTS (
                SELECT 1 FROM sys.columns
                 WHERE object_id = OBJECT_ID('dbo.FRAPDescontoFolha') AND name = '{col}'
            )
                ALTER TABLE dbo.FRAPDescontoFolha DROP COLUMN {col};
            """
        )
