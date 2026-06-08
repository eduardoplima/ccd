"""desconto-folha: cadastro manual + match manual

Adiciona:
  - FRAPDescontoFolha.Origem ('P' processo / 'M' manual); afrouxa IdDescontoFolha NULL.
  - Filtered unique index em FRAPDescontoFolha.IdDescontoFolha (substitui UNIQUE constraint).
  - Filtered unique index em FRAPDescontoFolhaParcela(IdFRAPDescontoFolha, IdParcela).
  - FRAPMatchDescontoFolha.IsManual / IdUsuarioConcilia / DataConcilia / Observacao.
  - Seed status `MATCH_MANUAL` (IdStatusMatch=46) em FRAPStatusMatch.

Revision ID: 0003_desconto_folha_extensoes
Revises: 0002_create_frap_jobs
Create Date: 2026-05-07
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0003_desconto_folha_extensoes"
down_revision: str | Sequence[str] | None = "0002_create_frap_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # FRAPDescontoFolha: adicionar Origem; afrouxar IdDescontoFolha; trocar UNIQUE por filtered index.
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPDescontoFolha') AND name = 'Origem'
        )
            ALTER TABLE dbo.FRAPDescontoFolha
                ADD Origem CHAR(1) NOT NULL CONSTRAINT DF_FRAPDescontoFolha_Origem DEFAULT 'P';
        """
    )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.key_constraints
             WHERE name = 'UQ_FRAPDescontoFolha_IdDF'
               AND parent_object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
        )
            ALTER TABLE dbo.FRAPDescontoFolha DROP CONSTRAINT UQ_FRAPDescontoFolha_IdDF;
        """
    )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
               AND name = 'IdDescontoFolha'
               AND is_nullable = 0
        )
            ALTER TABLE dbo.FRAPDescontoFolha ALTER COLUMN IdDescontoFolha INT NULL;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'UX_FRAPDescontoFolha_IdDF'
               AND object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
        )
            CREATE UNIQUE INDEX UX_FRAPDescontoFolha_IdDF
                ON dbo.FRAPDescontoFolha(IdDescontoFolha)
                WHERE IdDescontoFolha IS NOT NULL;
        """
    )

    # FRAPDescontoFolhaParcela: trocar UNIQUE constraint por filtered index (parcela manual = IdParcela NULL).
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.key_constraints
             WHERE name = 'UQ_FRAPDescontoFolhaParcela_PaiIdParcela'
               AND parent_object_id = OBJECT_ID('dbo.FRAPDescontoFolhaParcela')
        )
            ALTER TABLE dbo.FRAPDescontoFolhaParcela
                DROP CONSTRAINT UQ_FRAPDescontoFolhaParcela_PaiIdParcela;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'UX_FRAPDescontoFolhaParcela_PaiIdParcela'
               AND object_id = OBJECT_ID('dbo.FRAPDescontoFolhaParcela')
        )
            CREATE UNIQUE INDEX UX_FRAPDescontoFolhaParcela_PaiIdParcela
                ON dbo.FRAPDescontoFolhaParcela(IdFRAPDescontoFolha, IdParcela)
                WHERE IdParcela IS NOT NULL;
        """
    )

    # FRAPMatchDescontoFolha: campos para conciliação manual.
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha') AND name = 'IsManual'
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha
                ADD IsManual BIT NOT NULL CONSTRAINT DF_FRAPMatchDescontoFolha_IsManual DEFAULT 0;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha') AND name = 'IdUsuarioConcilia'
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha
                ADD IdUsuarioConcilia INT NULL;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.foreign_keys
             WHERE name = 'FK_FRAPMatchDescontoFolha_Usuario'
               AND parent_object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha')
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha
                ADD CONSTRAINT FK_FRAPMatchDescontoFolha_Usuario
                FOREIGN KEY (IdUsuarioConcilia) REFERENCES dbo.FRAPUsuario(IdUsuario);
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha') AND name = 'DataConcilia'
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha
                ADD DataConcilia DATETIME2(0) NULL;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha') AND name = 'Observacao'
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha
                ADD Observacao NVARCHAR(500) NULL;
        """
    )

    # Seed: status MATCH_MANUAL para o matcher DESCONTO_FOLHA.
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM dbo.FRAPStatusMatch
             WHERE Matcher = 'DESCONTO_FOLHA' AND Codigo = 'MATCH_MANUAL'
        )
            INSERT INTO dbo.FRAPStatusMatch (IdStatusMatch, Codigo, Matcher, Descricao)
            VALUES (46, 'MATCH_MANUAL', 'DESCONTO_FOLHA',
                    N'Conciliação manual: 1 lançamento FRAP cobre 1+ parcelas');
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM dbo.FRAPStatusMatch WHERE Matcher = 'DESCONTO_FOLHA' AND Codigo = 'MATCH_MANUAL';"
    )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.foreign_keys
             WHERE name = 'FK_FRAPMatchDescontoFolha_Usuario'
               AND parent_object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha')
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha DROP CONSTRAINT FK_FRAPMatchDescontoFolha_Usuario;
        """
    )
    for col in ("Observacao", "DataConcilia", "IdUsuarioConcilia"):
        op.execute(
            f"""
            IF EXISTS (
                SELECT 1 FROM sys.columns
                 WHERE object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha') AND name = '{col}'
            )
                ALTER TABLE dbo.FRAPMatchDescontoFolha DROP COLUMN {col};
            """
        )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.default_constraints
             WHERE name = 'DF_FRAPMatchDescontoFolha_IsManual'
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha DROP CONSTRAINT DF_FRAPMatchDescontoFolha_IsManual;
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMatchDescontoFolha') AND name = 'IsManual'
        )
            ALTER TABLE dbo.FRAPMatchDescontoFolha DROP COLUMN IsManual;
        """
    )

    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'UX_FRAPDescontoFolhaParcela_PaiIdParcela'
               AND object_id = OBJECT_ID('dbo.FRAPDescontoFolhaParcela')
        )
            DROP INDEX UX_FRAPDescontoFolhaParcela_PaiIdParcela ON dbo.FRAPDescontoFolhaParcela;
        IF NOT EXISTS (
            SELECT 1 FROM sys.key_constraints
             WHERE name = 'UQ_FRAPDescontoFolhaParcela_PaiIdParcela'
               AND parent_object_id = OBJECT_ID('dbo.FRAPDescontoFolhaParcela')
        )
            ALTER TABLE dbo.FRAPDescontoFolhaParcela
                ADD CONSTRAINT UQ_FRAPDescontoFolhaParcela_PaiIdParcela
                UNIQUE (IdFRAPDescontoFolha, IdParcela);
        """
    )

    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'UX_FRAPDescontoFolha_IdDF'
               AND object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
        )
            DROP INDEX UX_FRAPDescontoFolha_IdDF ON dbo.FRAPDescontoFolha;
        """
    )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
               AND name = 'IdDescontoFolha'
               AND is_nullable = 1
        )
            ALTER TABLE dbo.FRAPDescontoFolha ALTER COLUMN IdDescontoFolha INT NOT NULL;
        IF NOT EXISTS (
            SELECT 1 FROM sys.key_constraints
             WHERE name = 'UQ_FRAPDescontoFolha_IdDF'
               AND parent_object_id = OBJECT_ID('dbo.FRAPDescontoFolha')
        )
            ALTER TABLE dbo.FRAPDescontoFolha
                ADD CONSTRAINT UQ_FRAPDescontoFolha_IdDF UNIQUE (IdDescontoFolha);
        """
    )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.default_constraints
             WHERE name = 'DF_FRAPDescontoFolha_Origem'
        )
            ALTER TABLE dbo.FRAPDescontoFolha DROP CONSTRAINT DF_FRAPDescontoFolha_Origem;
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPDescontoFolha') AND name = 'Origem'
        )
            ALTER TABLE dbo.FRAPDescontoFolha DROP COLUMN Origem;
        """
    )
