-- Tabelas de controle do desconto em folha (BdDIP).
-- origem: web/backend/app/migrations/versions/0024, 0025 e 0031

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

GO

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

GO

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

GO

ALTER TABLE dbo.CCDDescontoFolha ADD TipoNotificacao CHAR(1) NULL;  -- E eletrônica / F física (postal)
ALTER TABLE dbo.CCDDescontoFolha ADD EventoNotificacao INT NULL;  -- 
ALTER TABLE dbo.CCDDescontoFolha ADD IdEventoNotificacao INT NULL;  -- 
ALTER TABLE dbo.CCDDescontoFolha ADD TipoRecebimento VARCHAR(2) NULL;  -- E certidão eletrônica / T tácito / AR / DE
ALTER TABLE dbo.CCDDescontoFolha ADD EventoRecebimento INT NULL;  -- 
ALTER TABLE dbo.CCDDescontoFolha ADD IdEventoRecebimento INT NULL;  -- 

GO

-- um crédito do FRAP só pode quitar uma parcela (migração 0031)
CREATE UNIQUE INDEX UX_CCDDescontoFolhaMatch_Lancamento
    ON dbo.CCDDescontoFolhaMatch (IdLancamentoFRAP);
