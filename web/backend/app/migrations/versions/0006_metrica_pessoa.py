"""desconto-folha: tabela materializada de métricas por pessoa.

Pré-computa ValorAtualizadoTotal (UDF cara via cross-DB processo.*) e contagens
de processos/débitos notificados por CPF. A view "por pessoa" passa a usar
LEFT JOIN com essa tabela, eliminando subqueries N+1 que travavam o ORDER BY.

Revision ID: 0006_metrica_pessoa
Revises: 0005_notificacao_desconto_folha
Create Date: 2026-05-12
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0006_metrica_pessoa"
down_revision: str | Sequence[str] | None = "0005_notificacao_desconto_folha"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPMetricaPessoa', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.FRAPMetricaPessoa (
                CpfCnpj                   VARCHAR(14)    NOT NULL PRIMARY KEY,
                ValorAtualizadoTotal      NUMERIC(18,2)  NOT NULL
                    CONSTRAINT DF_FRAPMetricaPessoa_VAT DEFAULT 0,
                QtdProcessosNotificados   INT            NOT NULL
                    CONSTRAINT DF_FRAPMetricaPessoa_QPN DEFAULT 0,
                QtdDebitosNotificados     INT            NOT NULL
                    CONSTRAINT DF_FRAPMetricaPessoa_QDN DEFAULT 0,
                DataAtualizacao           DATETIME2(0)   NOT NULL
                    CONSTRAINT DF_FRAPMetricaPessoa_DT DEFAULT SYSUTCDATETIME()
            );
        END
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPMetricaPessoa', 'U') IS NOT NULL
            DROP TABLE dbo.FRAPMetricaPessoa;
        """
    )
