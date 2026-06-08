"""desconto-folha: tabela de notificações CCD + status REPASSE_VIA_ORGAO.

Adiciona:
  - dbo.FRAPNotificacaoDescontoFolha: persiste notificações CCD detectadas via
    scan de PDFs em vw_ata_informacao. UNIQUE em (NumeroProcesso, AnoProcesso,
    IdEventoCCD) para upsert idempotente.
  - Seed status `REPASSE_VIA_ORGAO` (IdStatusMatch=47) em FRAPStatusMatch para o
    matcher Nível C (match por órgão depositante).

Revision ID: 0005_notificacao_desconto_folha
Revises: 0004_orgao_notificado
Create Date: 2026-05-13
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0005_notificacao_desconto_folha"
down_revision: str | Sequence[str] | None = "0004_orgao_notificado"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPNotificacaoDescontoFolha', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.FRAPNotificacaoDescontoFolha (
                IdFRAPNotifDF      BIGINT IDENTITY(1,1) PRIMARY KEY,
                NumeroProcesso     CHAR(6)          NOT NULL,
                AnoProcesso        CHAR(4)          NOT NULL,
                IdProcesso         INT              NULL,
                IdEventoCCD        INT              NOT NULL,
                IdDebito           INT              NULL,
                DataPublicacaoCCD  DATETIME2(0)     NULL,
                ResumoCCD          NVARCHAR(MAX)    NULL,
                NomeArquivoPDF     NVARCHAR(200)    NULL,
                Origem             CHAR(1)          NOT NULL
                    CONSTRAINT DF_FRAPNotifDF_Origem DEFAULT 'C',
                DataIngestao       DATETIME2(0)     NOT NULL
                    CONSTRAINT DF_FRAPNotifDF_DataIngestao DEFAULT SYSUTCDATETIME(),
                CONSTRAINT UX_FRAPNotifDF UNIQUE (NumeroProcesso, AnoProcesso, IdEventoCCD)
            );
            CREATE INDEX IX_FRAPNotifDF_Processo
                ON dbo.FRAPNotificacaoDescontoFolha(IdProcesso);
            CREATE INDEX IX_FRAPNotifDF_Debito
                ON dbo.FRAPNotificacaoDescontoFolha(IdDebito);
        END
        """
    )

    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM dbo.FRAPStatusMatch
             WHERE Matcher = 'DESCONTO_FOLHA' AND Codigo = 'REPASSE_VIA_ORGAO'
        )
            INSERT INTO dbo.FRAPStatusMatch (IdStatusMatch, Codigo, Matcher, Descricao)
            VALUES (47, 'REPASSE_VIA_ORGAO', 'DESCONTO_FOLHA',
                    N'Repasse identificado via órgão depositante no extrato');
        """
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM dbo.FRAPStatusMatch "
        "WHERE Matcher = 'DESCONTO_FOLHA' AND Codigo = 'REPASSE_VIA_ORGAO';"
    )
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPNotificacaoDescontoFolha', 'U') IS NOT NULL
            DROP TABLE dbo.FRAPNotificacaoDescontoFolha;
        """
    )
