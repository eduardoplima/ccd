"""CCDTAG + CCDTAGObrigacao: Cadastro Geral de Termos de Ajustamento de Gestão (CGTAG).

O art. 431, IV, "d" do Regimento Interno exige um cadastro próprio para os
TAGs, separado do CGR (obrigações de fazer, tabela `Obrigacao`). O TAG é
celebrado pelo MPC com o jurisdicionado (compromitente) e homologado pelo
Tribunal; o RI (art. 351 §3º) manda identificar a obrigação, a autoridade
responsável, o prazo e a sanção — são as colunas daqui.

Uma linha por TAG (processo + evento do documento); as obrigações da cláusula
de compromisso ficam na filha. O rascunho nasce da extração por OCR + LLM no
worker (`Revisado = 0`, `PayloadLLM` guarda o que o modelo propôs antes da
edição humana, como `ObrigacaoStaging.PayloadOriginal`); a tela edita e marca
`Revisado = 1`. Soft-delete por `Ativo`.

Revision ID: 0032_ccd_tag
Revises: 0031_ccd_df_match_lancamento_unico
Create Date: 2026-11-06
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0032_ccd_tag"
down_revision: str | Sequence[str] | None = "0031_ccd_df_match_lancamento_unico"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDTAG', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.CCDTAG (
                IdCCDTAG                 INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_CCDTAG PRIMARY KEY CLUSTERED,

                -- processo e peça de onde o termo foi lido (banco processo; sem FK física)
                IdProcesso               INT            NOT NULL,
                NumeroProcesso           CHAR(6)        NOT NULL,
                AnoProcesso              INT            NOT NULL,
                Evento                   INT            NOT NULL,
                IdEvento                 INT            NULL,
                IdInformacao             INT            NULL,

                -- identificação do termo (RI art. 351 §3º)
                Numero                   VARCHAR(40)    NOT NULL,
                Orgao                    VARCHAR(255)   NOT NULL,
                IdOrgao                  INT            NULL,
                Responsavel              VARCHAR(255)   NOT NULL,
                CargoResponsavel         VARCHAR(255)   NULL,
                CpfResponsavel           VARCHAR(11)    NULL,
                Compromissario           VARCHAR(255)   NULL,
                DataCelebracao           DATE           NULL,
                Prazo                    DATE           NULL,
                Homologacao              VARCHAR(120)   NULL,
                ValorMultaDescumprimento DECIMAL(18,2)  NULL,
                Situacao                 VARCHAR(12)    NOT NULL
                    CONSTRAINT DF_CCDTAG_Situacao DEFAULT 'VIGENTE'
                    CONSTRAINT CK_CCDTAG_Situacao
                    CHECK (Situacao IN ('VIGENTE', 'CUMPRIDO', 'RESCINDIDO', 'PRORROGADO')),

                -- rastro da extração
                Revisado                 BIT            NOT NULL
                    CONSTRAINT DF_CCDTAG_Revisado DEFAULT 0,
                TextoOCR                 NVARCHAR(MAX)  NULL,
                PayloadLLM               NVARCHAR(MAX)  NULL,
                Observacoes              NVARCHAR(MAX)  NULL,

                Ativo                    BIT            NOT NULL
                    CONSTRAINT DF_CCDTAG_Ativo DEFAULT 1,
                DataInclusao             DATETIME2(0)   NOT NULL
                    CONSTRAINT DF_CCDTAG_DtInc DEFAULT SYSUTCDATETIME(),
                IdUsuarioInclusao        INT            NULL
                    CONSTRAINT FK_CCDTAG_UsuarioInclusao
                    REFERENCES dbo.Usuarios(IdUsuario),
                DataAtualizacao          DATETIME2(0)   NULL,
                IdUsuarioAtualizacao     INT            NULL
                    CONSTRAINT FK_CCDTAG_UsuarioAtualizacao
                    REFERENCES dbo.Usuarios(IdUsuario)
            );
        END
        """
    )
    # Um TAG ativo por peça: a extração repetida do mesmo evento é barrada no endpoint.
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'UX_CCDTAG_Processo_Evento'
               AND object_id = OBJECT_ID('dbo.CCDTAG')
        )
            CREATE UNIQUE NONCLUSTERED INDEX UX_CCDTAG_Processo_Evento
                ON dbo.CCDTAG(IdProcesso, Evento)
                WHERE Ativo = 1;
        """
    )
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDTAGObrigacao', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.CCDTAGObrigacao (
                IdCCDTAGObrigacao        INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_CCDTAGObrigacao PRIMARY KEY CLUSTERED,
                IdCCDTAG                 INT            NOT NULL
                    CONSTRAINT FK_CCDTAGObrigacao_TAG
                    REFERENCES dbo.CCDTAG(IdCCDTAG) ON DELETE CASCADE,
                Ordem                    INT            NOT NULL,
                Clausula                 VARCHAR(80)    NOT NULL,
                Descricao                NVARCHAR(MAX)  NOT NULL,
                PrazoTexto               VARCHAR(255)   NULL,
                DataLimite               DATE           NULL,
                Situacao                 VARCHAR(12)    NOT NULL
                    CONSTRAINT DF_CCDTAGObrigacao_Situacao DEFAULT 'PENDENTE'
                    CONSTRAINT CK_CCDTAGObrigacao_Situacao
                    CHECK (Situacao IN ('PENDENTE', 'CUMPRIDA', 'DESCUMPRIDA', 'PRORROGADA')),
                DataCumprimento          DATE           NULL,
                EventoComprovacao        INT            NULL,
                Observacoes              NVARCHAR(MAX)  NULL
            );
        END
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_CCDTAGObrigacao_TAG'
               AND object_id = OBJECT_ID('dbo.CCDTAGObrigacao')
        )
            CREATE NONCLUSTERED INDEX ix_CCDTAGObrigacao_TAG
                ON dbo.CCDTAGObrigacao(IdCCDTAG, Ordem);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDTAGObrigacao', 'U') IS NOT NULL
            DROP TABLE dbo.CCDTAGObrigacao;
        IF OBJECT_ID('dbo.CCDTAG', 'U') IS NOT NULL
            DROP TABLE dbo.CCDTAG;
        """
    )
