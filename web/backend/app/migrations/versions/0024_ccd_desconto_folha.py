"""Desconto em folha (CCD): cadastro → resposta do órgão → match no FRAP.

Substitui o monitoramento/matching antigo (FRAPMonitoramentoDescontoFolha,
FRAPDescontoFolha*, FRAPMatchDescontoFolha — que ficam no banco, sem uso pela
UI) por três tabelas com prefixo CCD:

- CCDDescontoFolha: um cadastro por (processo de execução, débito). Guarda o
  responsável, o órgão notificado, a notificação/AR e o apensado com a resposta
  do órgão (texto extraído do PDF do share pela LLM).
- CCDDescontoFolhaValor: os valores da resposta (único ou parcelas), com origem
  L (LLM) ou M (manual).
- CCDDescontoFolhaMatch: o crédito de FRAPLancamento vinculado a cada valor.

Seed: copia os cadastros ativos de FRAPMonitoramentoDescontoFolha, resolvendo
IdProcesso por número/ano e IdDebito/IdPessoa quando o par (processo, CPF)
tem um único débito vigente (folha da cadeia IdDebitoAnterior, sem
DataCancelamento). Os demais entram sem débito, para completar na tela.

Revision ID: 0024_ccd_desconto_folha
Revises: 0023_staging_status_dispatched
Create Date: 2026-09-14
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0024_ccd_desconto_folha"
down_revision: str | Sequence[str] | None = "0023_staging_status_dispatched"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDDescontoFolha', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.CCDDescontoFolha (
                IdCCDDescontoFolha      INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_CCDDescontoFolha PRIMARY KEY CLUSTERED,
                IdProcesso              INT            NOT NULL,
                NumeroProcesso          CHAR(6)        NOT NULL,
                AnoProcesso             CHAR(4)        NOT NULL,
                IdDebito                INT            NULL,
                IdPessoa                INT            NULL,
                CpfCnpj                 VARCHAR(14)    NULL,
                NomePessoa              NVARCHAR(200)  NULL,
                IdOrgao                 INT            NULL,
                NomeOrgao               NVARCHAR(200)  NULL,
                NumeroNotificacao       VARCHAR(12)    NULL,
                DataNotificacao         DATETIME       NULL,
                NumeroPostagemAr        VARCHAR(20)    NULL,
                DataAr                  DATETIME       NULL,
                IdProcessoResposta      INT            NULL,
                NumeroProcessoResposta  CHAR(6)        NULL,
                AnoProcessoResposta     CHAR(4)        NULL,
                EventoResposta          INT            NULL,
                DataResposta            DATETIME       NULL,
                ArquivoResposta         NVARCHAR(400)  NULL,
                TrechoResposta          NVARCHAR(MAX)  NULL,
                ValorTotal              NUMERIC(18,2)  NULL,
                Parcelado               BIT            NOT NULL CONSTRAINT DF_CCDDF_Parcelado DEFAULT (0),
                DataExtracao            DATETIME       NULL,
                StatusExtracao          VARCHAR(12)    NOT NULL
                    CONSTRAINT DF_CCDDF_StatusExtracao DEFAULT ('PENDENTE')
                    CONSTRAINT CK_CCDDF_StatusExtracao
                    CHECK (StatusExtracao IN ('PENDENTE', 'OK', 'SEM_RESPOSTA', 'ERRO')),
                Observacoes             NVARCHAR(MAX)  NULL,
                Ativo                   BIT            NOT NULL CONSTRAINT DF_CCDDF_Ativo DEFAULT (1),
                DataInclusao            DATETIME       NOT NULL CONSTRAINT DF_CCDDF_DataInclusao DEFAULT (SYSUTCDATETIME()),
                DataAtualizacao         DATETIME       NULL,
                IdUsuario               INT            NULL
            );
            CREATE UNIQUE INDEX UX_CCDDescontoFolha_Processo_Debito
                ON dbo.CCDDescontoFolha (IdProcesso, IdDebito)
                WHERE Ativo = 1 AND IdDebito IS NOT NULL;
            CREATE INDEX IX_CCDDescontoFolha_Processo ON dbo.CCDDescontoFolha (NumeroProcesso, AnoProcesso);
        END
        """
    )
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDDescontoFolhaValor', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.CCDDescontoFolhaValor (
                IdCCDDescontoFolhaValor INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_CCDDescontoFolhaValor PRIMARY KEY CLUSTERED,
                IdCCDDescontoFolha      INT            NOT NULL
                    CONSTRAINT FK_CCDDFValor_Cadastro REFERENCES dbo.CCDDescontoFolha (IdCCDDescontoFolha),
                NumeroParcela           INT            NOT NULL CONSTRAINT DF_CCDDFValor_Parcela DEFAULT (1),
                MesReferencia           TINYINT        NULL,
                AnoReferencia           SMALLINT       NULL,
                Valor                   NUMERIC(18,2)  NOT NULL,
                Origem                  CHAR(1)        NOT NULL
                    CONSTRAINT CK_CCDDFValor_Origem CHECK (Origem IN ('L', 'M'))
            );
            CREATE INDEX IX_CCDDescontoFolhaValor_Cadastro ON dbo.CCDDescontoFolhaValor (IdCCDDescontoFolha);
        END
        """
    )
    op.execute(
        """
        IF OBJECT_ID('dbo.CCDDescontoFolhaMatch', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.CCDDescontoFolhaMatch (
                IdCCDDescontoFolhaMatch INT IDENTITY(1,1) NOT NULL
                    CONSTRAINT PK_CCDDescontoFolhaMatch PRIMARY KEY CLUSTERED,
                IdCCDDescontoFolhaValor INT            NOT NULL
                    CONSTRAINT FK_CCDDFMatch_Valor REFERENCES dbo.CCDDescontoFolhaValor (IdCCDDescontoFolhaValor),
                IdLancamentoFRAP        BIGINT         NOT NULL,
                Automatico              BIT            NOT NULL CONSTRAINT DF_CCDDFMatch_Auto DEFAULT (0),
                IdUsuario               INT            NULL,
                DataMatch               DATETIME       NOT NULL CONSTRAINT DF_CCDDFMatch_Data DEFAULT (SYSUTCDATETIME()),
                Observacao              NVARCHAR(400)  NULL
            );
            CREATE UNIQUE INDEX UX_CCDDescontoFolhaMatch_Valor ON dbo.CCDDescontoFolhaMatch (IdCCDDescontoFolhaValor);
            CREATE INDEX IX_CCDDescontoFolhaMatch_Lancamento ON dbo.CCDDescontoFolhaMatch (IdLancamentoFRAP);
        END
        """
    )
    # Seed a partir do monitoramento (idempotente: não duplica processo+débito).
    op.execute(
        """
        INSERT INTO dbo.CCDDescontoFolha
            (IdProcesso, NumeroProcesso, AnoProcesso, IdDebito, IdPessoa, CpfCnpj, NomePessoa,
             IdOrgao, NomeOrgao, Observacoes, StatusExtracao)
        SELECT p.IdProcesso, RTRIM(p.numero_processo), RTRIM(p.ano_processo),
               d.IdDebito, d.IdPessoa, m.CpfCnpj, m.NomePessoa,
               m.IdOrgaoNotificado, m.NomeOrgao,
               CASE WHEN d.IdDebito IS NULL THEN 'migrado do monitoramento sem débito único'
                    ELSE 'migrado do monitoramento' END,
               'PENDENTE'
        FROM dbo.FRAPMonitoramentoDescontoFolha m
        JOIN processo.dbo.Processos p
          ON RTRIM(p.numero_processo) COLLATE DATABASE_DEFAULT = LEFT(LTRIM(m.NumeroProcesso), 6)
         AND RTRIM(p.ano_processo) COLLATE DATABASE_DEFAULT = RIGHT(RTRIM(m.NumeroProcesso), 4)
        OUTER APPLY (
            SELECT MAX(x.IdDebito) AS IdDebito, MAX(x.IdPessoa) AS IdPessoa
            FROM (
                SELECT e.IdDebito, dp.IDPessoa AS IdPessoa
                FROM processo.dbo.Exe_Debito e
                JOIN processo.dbo.Exe_DebitoPessoa dp ON dp.IDDebito = e.IdDebito
                JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
                WHERE (e.IdProcessoExecucao = p.IdProcesso OR e.IdProcessoOrigem = p.IdProcesso)
                  AND e.DataCancelamento IS NULL
                  AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito f
                                  WHERE f.IdDebitoAnterior = e.IdDebito
                                    AND f.DataCancelamento IS NULL)
                  AND REPLACE(REPLACE(REPLACE(gp.Documento, '.', ''), '-', ''), '/', '') COLLATE DATABASE_DEFAULT
                      = REPLACE(REPLACE(REPLACE(m.CpfCnpj, '.', ''), '-', ''), '/', '')
            ) x
            HAVING COUNT(*) = 1
        ) d
        WHERE m.Ativo = 1
          AND NOT EXISTS (
              SELECT 1 FROM dbo.CCDDescontoFolha c
              WHERE c.IdProcesso = p.IdProcesso
                AND ISNULL(c.IdDebito, -1) = ISNULL(d.IdDebito, -1)
          );
        """
    )


def downgrade() -> None:
    op.execute(
        "IF OBJECT_ID('dbo.CCDDescontoFolhaMatch', 'U') IS NOT NULL DROP TABLE dbo.CCDDescontoFolhaMatch;"
    )
    op.execute(
        "IF OBJECT_ID('dbo.CCDDescontoFolhaValor', 'U') IS NOT NULL DROP TABLE dbo.CCDDescontoFolhaValor;"
    )
    op.execute(
        "IF OBJECT_ID('dbo.CCDDescontoFolha', 'U') IS NOT NULL DROP TABLE dbo.CCDDescontoFolha;"
    )
