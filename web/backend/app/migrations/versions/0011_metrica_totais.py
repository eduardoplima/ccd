"""FRAPMetricaPessoa: renomeia QtdDebitosAtribuidos→QtdDebitosTotais e dropa ValorDebitosAtribuidosTotal.

A coluna passa a representar "todos os débitos ativos sem Custas" — mesmo
recorte de ValorAtualizadoTotal (DataCancelamento IS NULL + CodigoStatusDivida=1
+ CodigoTipoDebito<>1). O valor é mostrado a partir de ValorAtualizadoTotal,
então ValorDebitosAtribuidosTotal deixa de ter uso e é dropado.

Após o upgrade, rodar `frap recalcular-metricas-pessoa` para repopular
QtdDebitosTotais com o novo recorte (a contagem antiga usava LIKE aberto/suspens
e fica stale até o recalc).

Revision ID: 0011_metrica_totais
Revises: 0010_lancamento_orgao
Create Date: 2026-05-22
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0011_metrica_totais"
down_revision: str | Sequence[str] | None = "0010_lancamento_orgao"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'QtdDebitosAtribuidos'
        )
        AND NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'QtdDebitosTotais'
        )
            EXEC sp_rename
                N'dbo.FRAPMetricaPessoa.QtdDebitosAtribuidos',
                N'QtdDebitosTotais',
                N'COLUMN';
        """
    )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.default_constraints
             WHERE name = 'DF_FRAPMetricaPessoa_VDAT'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa DROP CONSTRAINT DF_FRAPMetricaPessoa_VDAT;
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'ValorDebitosAtribuidosTotal'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa DROP COLUMN ValorDebitosAtribuidosTotal;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'ValorDebitosAtribuidosTotal'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa
                ADD ValorDebitosAtribuidosTotal NUMERIC(18, 2) NOT NULL
                    CONSTRAINT DF_FRAPMetricaPessoa_VDAT DEFAULT 0;
        """
    )
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'QtdDebitosTotais'
        )
        AND NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'QtdDebitosAtribuidos'
        )
            EXEC sp_rename
                N'dbo.FRAPMetricaPessoa.QtdDebitosTotais',
                N'QtdDebitosAtribuidos',
                N'COLUMN';
        """
    )
