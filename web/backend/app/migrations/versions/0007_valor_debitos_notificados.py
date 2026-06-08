"""FRAPMetricaPessoa: coluna ValorDebitosNotificadosTotal.

Soma da UDF `fn_Exe_RetornaValorAtualizado` para os débitos da pessoa cuja
`IdProcessoExecucao` aparece em `FRAPNotificacaoDescontoFolha`. Materializada
para evitar avaliar a UDF durante ORDER BY.

Revision ID: 0007_valor_debitos_notificados
Revises: 0006_metrica_pessoa
Create Date: 2026-05-13
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0007_valor_debitos_notificados"
down_revision: str | Sequence[str] | None = "0006_metrica_pessoa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'ValorDebitosNotificadosTotal'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa
                ADD ValorDebitosNotificadosTotal NUMERIC(18, 2) NOT NULL
                    CONSTRAINT DF_FRAPMetricaPessoa_VDNT DEFAULT 0;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.default_constraints
             WHERE name = 'DF_FRAPMetricaPessoa_VDNT'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa DROP CONSTRAINT DF_FRAPMetricaPessoa_VDNT;
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'ValorDebitosNotificadosTotal'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa DROP COLUMN ValorDebitosNotificadosTotal;
        """
    )
