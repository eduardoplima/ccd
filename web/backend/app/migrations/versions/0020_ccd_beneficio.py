"""CCDBeneficio: staging dos benefícios da CCD para o SisBenefícios.

A CCD registra benefícios potenciais e efetivos (Res. 027/2021-TCE, art. 6º
§1º IV, redação da Res. 029/2025). O aplicativo SisBenefícios tem banco
próprio (BdBeneficio, tabela-alvo Beneficio_PropostaBeneficio) alimentado por
scripts de outro setor — esta tabela é o staging local: jobs de detecção
inserem candidatos, a tela caracteriza/valida, o export gera xlsx/json com os
nomes de campo do BdBeneficio.

Colunas Id* de classificação espelham os domínios do BdBeneficio
(Beneficio_TipoBeneficio, Beneficio_AreaTematica etc.). Sem FK física — são
bancos distintos; a validade é conferida no service contra os domínios lidos
ao vivo. Prefixo CCD (não FRAP): feature do domínio CCD.

DESCARTADO é status, não soft-delete: mantém Ativo=1, então a ChaveOrigem
continua ocupada no índice único filtrado e o job de detecção não recria o
candidato. Soft-delete (Ativo=0) fica para registro manual criado por engano.

Revision ID: 0020_ccd_beneficio
Revises: 0019_verificacao_siai_folha
Create Date: 2026-08-31
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0020_ccd_beneficio"
down_revision: str | Sequence[str] | None = "0019_verificacao_siai_folha"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDBeneficio', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.CCDBeneficio (
                IdCCDBeneficio           INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_CCDBeneficio PRIMARY KEY CLUSTERED,

                -- ciclo de vida do registro no fluxo interno da CCD
                Status                   VARCHAR(10)    NOT NULL
                    CONSTRAINT DF_CCDBeneficio_Status DEFAULT 'RASCUNHO'
                    CONSTRAINT CK_CCDBeneficio_Status
                    CHECK (Status IN ('RASCUNHO', 'VALIDADO', 'ENVIADO', 'DESCARTADO')),
                DataEnvio                DATETIME2(0)   NULL,
                LoteEnvio                VARCHAR(30)    NULL,

                -- origem da detecção e chave de idempotência
                Origem                   VARCHAR(20)    NOT NULL
                    CONSTRAINT DF_CCDBeneficio_Origem DEFAULT 'MANUAL'
                    CONSTRAINT CK_CCDBeneficio_Origem
                    CHECK (Origem IN ('MANUAL', 'DEBITO', 'BOLETO', 'PGE',
                                      'FOLHA', 'DIVIDA_ATIVA', 'FRAP')),
                ChaveOrigem              VARCHAR(120)   NULL,
                IdDebitoExecucao         INT            NULL,

                -- campos-espelho de BdBeneficio.dbo.Beneficio_PropostaBeneficio
                DescricaoPropostaBeneficio      VARCHAR(500)  NOT NULL,
                MemoriaCalculoPropostaBeneficio VARCHAR(200)  NULL,
                ValorQuantidade                 DECIMAL(14,2) NULL,
                JustificativaPropostaBeneficio  VARCHAR(500)  NULL,
                IdBeneficioSituacaoEfetivacao   SMALLINT      NULL
                    CONSTRAINT CK_CCDBeneficio_SitEfetivacao
                    CHECK (IdBeneficioSituacaoEfetivacao IN (1, 2)),  -- 1=Efetivo, 2=Potencial
                IdAreaTematica           SMALLINT       NULL,
                IdCaracterizacaoBeneficio TINYINT       NULL,
                IdUnidadeDeMedida        TINYINT        NULL,
                IdBeneficioSituacao      SMALLINT       NULL,
                IdTipoBeneficio          INT            NULL,
                IdSubTipoBeneficio       INT            NULL,
                NumeroProcessoDecisao    VARCHAR(6)     NULL,
                AnoProcessoDecisao       SMALLINT       NULL,
                IdProcessoDecisao        INT            NULL,
                DescricaoMotivo          VARCHAR(5000)  NULL,

                -- vínculo interno efetivo -> potencial (Manual MQB, item 3.6);
                -- vira IdBeneficioAnterior na importação, resolvido pelo script do outro setor
                IdCCDBeneficioPotencial  INT            NULL
                    CONSTRAINT FK_CCDBeneficio_Potencial
                    REFERENCES dbo.CCDBeneficio(IdCCDBeneficio),

                -- contexto do candidato (triagem sem voltar ao banco processo)
                CpfCnpj                  VARCHAR(14)    NULL,
                NomePessoa               NVARCHAR(200)  NULL,
                DataOcorrencia           DATE           NULL,

                Ativo                    BIT            NOT NULL
                    CONSTRAINT DF_CCDBeneficio_Ativo DEFAULT 1,
                DataInclusao             DATETIME2(0)   NOT NULL
                    CONSTRAINT DF_CCDBeneficio_DtInc DEFAULT SYSUTCDATETIME(),
                DataAtualizacao          DATETIME2(0)   NULL,
                IdUsuarioAtualizacao     INT            NULL
                    CONSTRAINT FK_CCDBeneficio_Usuarios
                    REFERENCES dbo.Usuarios(IdUsuario)
            );
        END
        """
    )
    # Idempotência dos jobs de detecção: 1 linha ativa por ChaveOrigem.
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'UX_CCDBeneficio_ChaveOrigem'
               AND object_id = OBJECT_ID('dbo.CCDBeneficio')
        )
            CREATE UNIQUE NONCLUSTERED INDEX UX_CCDBeneficio_ChaveOrigem
                ON dbo.CCDBeneficio(ChaveOrigem)
                WHERE Ativo = 1 AND ChaveOrigem IS NOT NULL;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_CCDBeneficio_Status'
               AND object_id = OBJECT_ID('dbo.CCDBeneficio')
        )
            CREATE NONCLUSTERED INDEX ix_CCDBeneficio_Status
                ON dbo.CCDBeneficio(Status, IdBeneficioSituacaoEfetivacao)
                WHERE Ativo = 1;
        """
    )
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes
             WHERE name = 'ix_CCDBeneficio_Processo'
               AND object_id = OBJECT_ID('dbo.CCDBeneficio')
        )
            CREATE NONCLUSTERED INDEX ix_CCDBeneficio_Processo
                ON dbo.CCDBeneficio(NumeroProcessoDecisao, AnoProcessoDecisao);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDBeneficio', 'U') IS NOT NULL
            DROP TABLE dbo.CCDBeneficio;
        """
    )
