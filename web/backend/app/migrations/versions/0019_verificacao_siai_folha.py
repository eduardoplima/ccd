"""FRAPVerificacaoSiaiFolha: rubricas TCE/FRAP encontradas no SIAI Pessoal.

Materializa, por competência, os descontos com rubrica TCE/FRAP no contracheque
(vwSiaiPessoalFolhaCompletaTodas) dos CPFs ativos do monitoramento de desconto
em folha. Escrita apenas pela task mensal (delete+insert por competência) —
sem índice único: a idempotência vem da própria varredura. Uma linha por
(CPF, ano, mês, órgão, rubrica), com o valor somado de todas as folhas do mês
(normal, complementar, 13º).

Revision ID: 0019_verificacao_siai_folha
Revises: 0018_monitoramento_desconto_folha
Create Date: 2026-08-28
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0019_verificacao_siai_folha"
down_revision: str | Sequence[str] | None = "0018_monitoramento_desconto_folha"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPVerificacaoSiaiFolha', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.FRAPVerificacaoSiaiFolha (
                IdFRAPVerificacaoSiaiFolha INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_FRAPVerificacaoSiaiFolha PRIMARY KEY CLUSTERED,
                CpfCnpj         VARCHAR(14)    NOT NULL,
                Ano             SMALLINT       NOT NULL,
                Mes             TINYINT        NOT NULL,
                IdOrgao         INT            NULL,
                NomeOrgao       NVARCHAR(200)  NULL,
                CodigoRubrica   VARCHAR(30)    NULL,
                NomeRubrica     NVARCHAR(200)  NULL,
                Valor           DECIMAL(18,2)  NOT NULL,
                DataVerificacao DATETIME2(0)   NOT NULL
                    CONSTRAINT DF_FRAPVerifSiaiFolha_Dt DEFAULT SYSUTCDATETIME()
            );
        END
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_FRAPVerifSiaiFolha_Cpf'
               AND object_id = OBJECT_ID('dbo.FRAPVerificacaoSiaiFolha')
        )
            CREATE NONCLUSTERED INDEX ix_FRAPVerifSiaiFolha_Cpf
                ON dbo.FRAPVerificacaoSiaiFolha(CpfCnpj, Ano, Mes);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPVerificacaoSiaiFolha', 'U') IS NOT NULL
            DROP TABLE dbo.FRAPVerificacaoSiaiFolha;
        """
    )
