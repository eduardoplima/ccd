"""FRAPMetricaPessoa: colunas de atribuídos (todas multas em aberto).

`resumo_fases` consultava `processo.Exe_Debito` por CPF a cada hit — cada query
fazia full scan de `processo.GenPessoa` por causa do `REPLACE(...) = :cpf`.
Materializamos QtdDebitosAtribuidos e ValorDebitosAtribuidosTotal, populados
pela mesma pipeline da `tools/frap.persistencia.metrica_pessoa`.

Revision ID: 0009_metrica_atribuidos
Revises: 0008_login_usuario
Create Date: 2026-05-13
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0009_metrica_atribuidos"
down_revision: str | Sequence[str] | None = "0008_login_usuario"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'QtdDebitosAtribuidos'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa
                ADD QtdDebitosAtribuidos INT NOT NULL
                    CONSTRAINT DF_FRAPMetricaPessoa_QDA DEFAULT 0;
        """
    )
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


def downgrade() -> None:
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
        IF EXISTS (
            SELECT 1 FROM sys.default_constraints
             WHERE name = 'DF_FRAPMetricaPessoa_QDA'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa DROP CONSTRAINT DF_FRAPMetricaPessoa_QDA;
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPMetricaPessoa')
               AND name = 'QtdDebitosAtribuidos'
        )
            ALTER TABLE dbo.FRAPMetricaPessoa DROP COLUMN QtdDebitosAtribuidos;
        """
    )
