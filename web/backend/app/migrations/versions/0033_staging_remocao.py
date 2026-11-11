"""Remoção de obrigações/recomendações curadas por acórdão posterior.

Status 'removed' + colunas de auditoria (acórdão que determinou a remoção,
justificativa, quem e quando) em ObrigacaoStaging e RecomendacaoStaging.
A linha fica no BdDIP; sai do acervo porque todos os filtros (painéis,
aguardando envio, vwCCDDeterminacao) já usam Status IN ('approved','dispatched').

Revision ID: 0033_staging_remocao
Revises: 0032_ccd_tag
Create Date: 2026-11-11
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0033_staging_remocao"
down_revision: str | Sequence[str] | None = "0032_ccd_tag"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABELAS = ("ObrigacaoStaging", "RecomendacaoStaging")
_NOVOS = "'pending', 'approved', 'rejected', 'dispatched', 'removed'"
_ANTIGOS = "'pending', 'approved', 'rejected', 'dispatched'"
_COLUNAS = (
    ("IdComposicaoPautaRemocao", "int NULL"),
    ("JustificativaRemocao", "varchar(max) NULL"),
    ("RemovidoPor", "varchar(255) NULL"),
    ("DataRemocao", "datetime NULL"),
)


def _troca_check(tabela: str, valores: str) -> None:
    op.execute(
        f"""
        DECLARE @nome sysname;
        SELECT @nome = name FROM sys.check_constraints
         WHERE parent_object_id = OBJECT_ID('dbo.{tabela}')
           AND definition LIKE '%Status%';
        IF @nome IS NOT NULL
            EXEC('ALTER TABLE dbo.{tabela} DROP CONSTRAINT [' + @nome + ']');
        """
    )
    op.execute(
        f"ALTER TABLE dbo.{tabela} ADD CONSTRAINT CK_{tabela}_Status CHECK (Status IN ({valores}));"
    )


def upgrade() -> None:
    for tabela in _TABELAS:
        for col, tipo in _COLUNAS:
            op.execute(
                f"IF COL_LENGTH('dbo.{tabela}', '{col}') IS NULL "
                f"ALTER TABLE dbo.{tabela} ADD {col} {tipo};"
            )
        _troca_check(tabela, _NOVOS)


def downgrade() -> None:
    for tabela in _TABELAS:
        op.execute(f"UPDATE dbo.{tabela} SET Status = 'approved' WHERE Status = 'removed';")
        _troca_check(tabela, _ANTIGOS)
        for col, _ in _COLUNAS:
            op.execute(
                f"IF COL_LENGTH('dbo.{tabela}', '{col}') IS NOT NULL "
                f"ALTER TABLE dbo.{tabela} DROP COLUMN {col};"
            )
