"""FRAPLancamentoOrgao: materializa inferência de órgão pagador por lançamento.

Resolve depósitos zerados em /orgaos/{id}/depositos quando o CpfCnpjDepositante
do FRAPLancamento não bate com o CNPJ canônico de Bdc.dbo.vw_Gen_Orgao
(extratos usam abreviações como "P M PASSA E FICA FEB", siglas "ALRN").

Mapeamento N:N — um lançamento pode mapear a múltiplos órgãos (ex: Estado-RN
expande para subordinados). Populado offline via:
    frap inferir-orgaos-lancamentos

Revision ID: 0010_lancamento_orgao
Revises: 0009_metrica_atribuidos
Create Date: 2026-05-13
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0010_lancamento_orgao"
down_revision: str | Sequence[str] | None = "0009_metrica_atribuidos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPLancamentoOrgao', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.FRAPLancamentoOrgao (
                IdLancamento     INT          NOT NULL,
                IdOrgao          INT          NOT NULL,
                FonteInferencia  VARCHAR(20)  NOT NULL
                    CONSTRAINT DF_FRAPLancamentoOrgao_Fonte DEFAULT 'regex',
                DataInferencia   DATETIME2(0) NOT NULL
                    CONSTRAINT DF_FRAPLancamentoOrgao_DT DEFAULT SYSUTCDATETIME(),
                CONSTRAINT PK_FRAPLancamentoOrgao
                    PRIMARY KEY CLUSTERED (IdLancamento, IdOrgao)
            );
        END
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_FRAPLancamentoOrgao_IdOrgao'
               AND object_id = OBJECT_ID('dbo.FRAPLancamentoOrgao')
        )
            CREATE NONCLUSTERED INDEX ix_FRAPLancamentoOrgao_IdOrgao
                ON dbo.FRAPLancamentoOrgao(IdOrgao)
                INCLUDE (IdLancamento);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_FRAPLancamentoOrgao_IdOrgao'
               AND object_id = OBJECT_ID('dbo.FRAPLancamentoOrgao')
        )
            DROP INDEX ix_FRAPLancamentoOrgao_IdOrgao ON dbo.FRAPLancamentoOrgao;
        IF OBJECT_ID('dbo.FRAPLancamentoOrgao', 'U') IS NOT NULL
            DROP TABLE dbo.FRAPLancamentoOrgao;
        """
    )
