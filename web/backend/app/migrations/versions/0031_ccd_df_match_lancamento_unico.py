"""Desconto em folha: um crédito FRAP serve a uma única parcela.

Até aqui o match automático reusava a mesma OB para várias parcelas sem
competência (ex.: 003636/2017, parcelas 2–4 na OB de 05/08/2026; 36 parcelas do
cadastro 170 numa só OB). Mantém um vínculo por lançamento (manual antes do
automático, depois o mais antigo, depois a menor parcela) e troca o índice comum
de IdLancamentoFRAP por UNIQUE.

Downgrade só volta o índice comum: os vínculos apagados não são restaurados.

Revision ID: 0031_ccd_df_match_lancamento_unico
Revises: 0030_beneficio_data_acordao
Create Date: 2026-10-07
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0031_ccd_df_match_lancamento_unico"
down_revision: str | Sequence[str] | None = "0030_beneficio_data_acordao"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        WITH d AS (
            SELECT m.IdCCDDescontoFolhaMatch,
                   ROW_NUMBER() OVER (
                       PARTITION BY m.IdLancamentoFRAP
                       ORDER BY m.Automatico, m.DataMatch, v.NumeroParcela,
                                v.IdCCDDescontoFolhaValor) AS rn
              FROM dbo.CCDDescontoFolhaMatch m
              JOIN dbo.CCDDescontoFolhaValor v
                ON v.IdCCDDescontoFolhaValor = m.IdCCDDescontoFolhaValor
        )
        DELETE FROM dbo.CCDDescontoFolhaMatch
         WHERE IdCCDDescontoFolhaMatch IN (SELECT IdCCDDescontoFolhaMatch FROM d WHERE rn > 1);
        """
    )
    op.execute(
        """
        IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_CCDDescontoFolhaMatch_Lancamento'
                     AND object_id = OBJECT_ID('dbo.CCDDescontoFolhaMatch'))
            DROP INDEX IX_CCDDescontoFolhaMatch_Lancamento ON dbo.CCDDescontoFolhaMatch;
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_CCDDescontoFolhaMatch_Lancamento'
                         AND object_id = OBJECT_ID('dbo.CCDDescontoFolhaMatch'))
            CREATE UNIQUE INDEX UX_CCDDescontoFolhaMatch_Lancamento
                ON dbo.CCDDescontoFolhaMatch (IdLancamentoFRAP);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_CCDDescontoFolhaMatch_Lancamento'
                     AND object_id = OBJECT_ID('dbo.CCDDescontoFolhaMatch'))
            DROP INDEX UX_CCDDescontoFolhaMatch_Lancamento ON dbo.CCDDescontoFolhaMatch;
        IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_CCDDescontoFolhaMatch_Lancamento'
                         AND object_id = OBJECT_ID('dbo.CCDDescontoFolhaMatch'))
            CREATE INDEX IX_CCDDescontoFolhaMatch_Lancamento
                ON dbo.CCDDescontoFolhaMatch (IdLancamentoFRAP);
        """
    )
