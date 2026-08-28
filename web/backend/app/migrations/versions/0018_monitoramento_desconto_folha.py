"""FRAPMonitoramentoDescontoFolha: aposenta a planilha manual de monitoramento.

Uma linha por processo monitorado, cobrindo as abas "Monitoramento Geral",
"Processos Antigos" e "Monitoramento NEREU" da planilha
docs/Monitoramento Desconto em Folha.xlsx (coluna Grupo distingue a origem).
A matriz mensal de valores da planilha NÃO mora aqui — vive em
FRAPDescontoFolha (Origem='M') + FRAPDescontoFolhaParcela; o vínculo opcional
é a FK IdFRAPDescontoFolha.

Células da planilha são polimórficas (datas misturadas com "SIM"/"NÃO RECEBEU");
colunas claramente data/valor são DATE/DECIMAL, o resto é NVARCHAR para não
perder informação no import.

Revision ID: 0018_monitoramento_desconto_folha
Revises: 0017_dataset_anotacao
Create Date: 2026-08-26
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0018_monitoramento_desconto_folha"
down_revision: str | Sequence[str] | None = "0017_dataset_anotacao"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPMonitoramentoDescontoFolha', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.FRAPMonitoramentoDescontoFolha (
                IdFRAPMonitoramentoDescontoFolha INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_FRAPMonitoramentoDescontoFolha PRIMARY KEY CLUSTERED,
                Grupo                    VARCHAR(10)    NOT NULL
                    CONSTRAINT CK_FRAPMonitDF_Grupo
                    CHECK (Grupo IN ('GERAL', 'ANTIGO', 'NEREU')),
                NumeroProcesso           VARCHAR(30)    NOT NULL,
                ProcessoSei              NVARCHAR(80)   NULL,
                CpfCnpj                  VARCHAR(14)    NULL,
                NomePessoa               NVARCHAR(200)  NULL,
                IdOrgaoNotificado        INT            NULL,
                NomeOrgao                NVARCHAR(200)  NULL,
                EsferaOrgao              VARCHAR(10)    NULL,
                CadastradoDescontoFolha  BIT            NULL,
                DataDespacho             DATE           NULL,
                DataNotificacao          DATE           NULL,
                DataRecebimentoAr        DATE           NULL,
                DataResposta             DATE           NULL,
                DataSegundaNotificacao   DATE           NULL,
                DataRecebimentoAr2       DATE           NULL,
                DescFolhaTexto           NVARCHAR(100)  NULL,
                ValorPeriodo             DECIMAL(18,2)  NULL,
                PeriodoReferencia        VARCHAR(40)    NULL,
                TransfFrap               NVARCHAR(100)  NULL,
                PagoSiteTce              NVARCHAR(100)  NULL,
                TipoPagamento            NVARCHAR(60)   NULL,
                Remanescente             NVARCHAR(200)  NULL,
                Apr                      NVARCHAR(100)  NULL,
                ValorOriginal            DECIMAL(18,2)  NULL,
                Observacoes              NVARCHAR(MAX)  NULL,
                Relator                  NVARCHAR(120)  NULL,
                ValorImplementado        DECIMAL(18,2)  NULL,
                DataImplementacao        DATE           NULL,
                VerificadoSiaidp         NVARCHAR(200)  NULL,
                VerificadoFrap           NVARCHAR(400)  NULL,
                IdFRAPDescontoFolha      BIGINT         NULL
                    CONSTRAINT FK_FRAPMonitDF_DescontoFolha
                    REFERENCES dbo.FRAPDescontoFolha(IdFRAPDescontoFolha),
                Ativo                    BIT            NOT NULL
                    CONSTRAINT DF_FRAPMonitDF_Ativo DEFAULT 1,
                DataInclusao             DATETIME2(0)   NOT NULL
                    CONSTRAINT DF_FRAPMonitDF_DtInc DEFAULT SYSUTCDATETIME(),
                DataAtualizacao          DATETIME2(0)   NULL,
                IdUsuarioAtualizacao     INT            NULL
                    CONSTRAINT FK_FRAPMonitDF_Usuarios
                    REFERENCES dbo.Usuarios(IdUsuario)
            );
        END
        """
    )
    # Índice único filtrado: 1 linha ATIVA por (Grupo, NumeroProcesso, CpfCnpj) —
    # um processo pode ter vários responsáveis monitorados. O filtro Ativo=1
    # permite recriar após soft-delete e dá idempotência ao import.
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'UX_FRAPMonitDF_Grupo_Processo'
               AND object_id = OBJECT_ID('dbo.FRAPMonitoramentoDescontoFolha')
        )
            CREATE UNIQUE NONCLUSTERED INDEX UX_FRAPMonitDF_Grupo_Processo
                ON dbo.FRAPMonitoramentoDescontoFolha(Grupo, NumeroProcesso, CpfCnpj)
                WHERE Ativo = 1;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_FRAPMonitDF_CpfCnpj'
               AND object_id = OBJECT_ID('dbo.FRAPMonitoramentoDescontoFolha')
        )
            CREATE NONCLUSTERED INDEX ix_FRAPMonitDF_CpfCnpj
                ON dbo.FRAPMonitoramentoDescontoFolha(CpfCnpj)
                WHERE CpfCnpj IS NOT NULL;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_FRAPMonitDF_IdFRAPDescontoFolha'
               AND object_id = OBJECT_ID('dbo.FRAPMonitoramentoDescontoFolha')
        )
            CREATE NONCLUSTERED INDEX ix_FRAPMonitDF_IdFRAPDescontoFolha
                ON dbo.FRAPMonitoramentoDescontoFolha(IdFRAPDescontoFolha);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.FRAPMonitoramentoDescontoFolha', 'U') IS NOT NULL
            DROP TABLE dbo.FRAPMonitoramentoDescontoFolha;
        """
    )
