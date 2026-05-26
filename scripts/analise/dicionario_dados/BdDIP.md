# Dicionário de dados — BdDIP

Gerado em 2026-05-21. 79 objetos · 1024 colunas.

## dbo.alembic_version

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | version_num | varchar(32) | N | PK | — | — |

## dbo.CancelamentoObrigacao

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCancelamentoObrigacao | int | N | PK, IDENT | — | — |
| 2 | IdObrigacao | int | N | — | — | — |
| 3 | MotivoCancelamento | varchar(MAX) | N | — | — | — |
| 4 | DataCancelamento | date | N | — | — | — |

## dbo.CancelamentoRecomendacao

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCancelamentoRecomendacao | int | N | PK, IDENT | — | — |
| 2 | IdRecomendacao | int | N | — | — | — |
| 3 | MotivoCancelamento | varchar(MAX) | N | — | — | — |
| 4 | DataCancelamento | date | N | — | — | — |

## dbo.ClassificacaoDecisao

Tabela · ~375 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdClassificacaoDecisao | int | N | PK, IDENT | — | — |
| 2 | Classificacao | varchar(100) | Y | — | — | — |
| 3 | IdDecisao | int | N | — | — | Chave estrangeira para processo.dbo.ata_composicao_pauta |

## dbo.DecisaoProcessada

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDecisaoProcessada | int | N | IDENT | — | — |
| 3 | IdNERDecisao | int | Y | — | — | — |
| 5 | DataProcessamento | timestamp | Y | — | — | — |

## dbo.Dim_Debito

Tabela · ~26.834 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDebito | int | N | PK | — | — |
| 2 | IdProcessoOrigem | int | Y | — | — | — |
| 3 | ProcessoOrigem | varchar(11) | Y | — | — | — |
| 4 | IdProcessoExecucao | int | Y | — | — | — |
| 5 | ProcessoExecucao | varchar(11) | Y | — | — | — |
| 8 | ValorOriginalDebito | money | Y | — | — | — |
| 9 | ValorAtualizado | money | Y | — | — | — |
| 10 | CodigoTipoDebito | int | Y | — | — | — |
| 11 | CodigoStatusDivida | int | Y | — | — | — |
| 12 | IdOrgaoCredor | int | Y | — | — | — |
| 13 | IdDebitoAnterior | int | Y | — | — | — |
| 14 | DataAto | datetime | Y | — | — | — |
| 15 | EnviadoPGE | varchar(3) | Y | — | — | — |
| 16 | Protestado | varchar(3) | Y | — | — | — |
| 17 | IdDebitoOrigem | int | Y | — | — | — |
| 18 | StatusVigente | int | Y | — | — | — |
| 19 | ValorAmortizado | money | Y | — | — | — |
| 20 | ValorQuitacao | money | Y | — | — | — |
| 21 | ValorPago | money | Y | — | — | — |
| 22 | ValorAmortizadoVigente | money | Y | — | — | — |
| 23 | ValorQuitacaoVigente | money | Y | — | — | — |
| 24 | ValorPagoVigente | money | Y | — | — | — |

## dbo.Dim_Debito_Version

Tabela · ~16.452 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | SK_IdDebito | bigint | N | PK, IDENT | — | — |
| 2 | IdDebito | int | Y | — | — | — |
| 3 | Version | int | N | — | — | — |
| 4 | IdProcessoOrigem | int | Y | — | — | — |
| 5 | ProcessoOrigem | varchar(11) | Y | — | — | — |
| 6 | IdProcessoExecucao | int | Y | — | — | — |
| 7 | ProcessoExecucao | varchar(11) | Y | — | — | — |
| 8 | DataDecisao | datetime | Y | — | — | — |
| 9 | DataTransito | datetime | Y | — | — | — |
| 10 | DateFrom | datetime | Y | — | — | — |
| 11 | DateTo | datetime | Y | — | — | — |
| 12 | ValorOriginalDebito | money | Y | — | — | — |
| 13 | ValorAtualizado | money | Y | — | — | — |
| 15 | CodigoTipoDebito | int | Y | — | — | — |
| 16 | CodigoStatusDivida | int | Y | — | — | — |
| 17 | IdOrgaoCredor | int | Y | — | — | — |

## dbo.Dim_DebitoBoleto

Tabela · ~34.320 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDebitoBoleto | int | N | PK | — | — |
| 2 | IdBoleto | int | N | — | — | — |
| 3 | IdDebito | int | N | — | — | — |
| 4 | ValorOriginal | money | Y | — | — | — |
| 5 | Correcao | money | Y | — | — | — |
| 6 | Juros | money | Y | — | — | — |
| 7 | ValorTotalAPagar | money | Y | — | — | — |
| 8 | DataPagamento | datetime | Y | — | — | — |
| 9 | ValorPago | money | Y | — | — | — |

## dbo.Dim_DebitoPessoa

Tabela · ~27.417 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDebitoPessoa | int | N | PK | — | — |
| 2 | IdDebito | int | Y | — | — | — |
| 3 | IdPessoa | int | Y | — | — | — |

## dbo.Dim_Orgao

Tabela · ~1.177 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgao | int | N | PK | — | — |
| 2 | CodigoOrgao | char(10) | N | — | — | — |
| 3 | NomeOrgao | varchar(150) | N | — | — | — |

## dbo.Dim_Pessoa

Tabela · ~85.160 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPessoa | int | N | PK | — | — |
| 2 | CPF | varchar(11) | Y | — | — | — |
| 3 | CNPJ | varchar(14) | Y | — | — | — |
| 4 | Documento | varchar(14) | Y | — | — | — |
| 5 | Nome | varchar(100) | Y | — | — | — |

## dbo.Dim_RepasseDividaAtiva

Tabela · ~1.760 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPagamentoPGE | int | N | PK | — | — |
| 2 | IdDebito | int | N | — | — | — |
| 3 | DataPagamento | datetime | N | — | — | — |
| 4 | ValorPrincipal | money | N | — | — | — |
| 5 | Multa | money | N | — | — | — |
| 6 | Juros | money | N | — | — | — |
| 7 | ValorPago | money | N | — | — | — |

## dbo.Dim_StatusDivida

Tabela · ~18 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | CodigoStatusDivida | int | N | PK | — | — |
| 2 | DescricaoStatusDivida | varchar(500) | N | — | — | — |
| 3 | StatusCancelamento | bit | Y | — | — | — |

## dbo.Dim_Tempo

Tabela · ~780 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | N | PK | — | — |
| 2 | IdAno | int | N | — | — | — |
| 3 | Ano | int | N | — | — | — |
| 4 | IdSemestre | int | N | — | — | — |
| 5 | NSemestre | int | N | — | — | — |
| 6 | Semestre | varchar(100) | N | — | — | — |
| 7 | IdQuadrimestre | int | N | — | — | — |
| 8 | NQuadrimestre | int | N | — | — | — |
| 9 | Quadrimestre | varchar(100) | N | — | — | — |
| 10 | IdTrimestre | int | N | — | — | — |
| 11 | NTrimestre | int | N | — | — | — |
| 12 | Trimestre | varchar(100) | N | — | — | — |
| 13 | IdBimestre | int | N | — | — | — |
| 14 | NBimestre | int | N | — | — | — |
| 15 | Bimestre | varchar(100) | N | — | — | — |
| 16 | IdMes | int | N | — | — | — |
| 17 | NMes | int | N | — | — | — |
| 18 | Mes | varchar(100) | N | — | — | — |

## dbo.Dim_TipoDebito

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | CodigoTipoDebito | int | N | PK | — | — |
| 2 | Descricao | varchar(30) | Y | — | — | — |
| 3 | OrdemNarrativa | int | Y | — | — | — |
| 4 | Ativo | bit | Y | — | — | — |
| 5 | CodigoNaturezaMidasPGE | int | Y | — | — | — |

## dbo.Extracao

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdExtracao | int | N | PK, IDENT | — | — |
| 2 | DataInicio | date | N | — | — | — |
| 3 | DataFim | date | N | — | — | — |
| 4 | DataExecucao | datetime | N | — | (getdate()) | — |
| 5 | Status | varchar(20) | N | — | ('done') | — |
| 6 | EtapaAtual | varchar(30) | N | — | ('done') | — |
| 7 | DecisoesProcessadas | int | N | — | ('0') | — |
| 8 | ObrigacoesGeradas | int | N | — | ('0') | — |
| 9 | RecomendacoesGeradas | int | N | — | ('0') | — |
| 10 | Erros | int | N | — | ('0') | — |
| 11 | MensagemErro | varchar(MAX) | Y | — | — | — |
| 12 | JobId | varchar(64) | Y | — | — | — |

## dbo.ExtracaoEvento

Tabela · ~623 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdExtracaoEvento | int | N | PK, IDENT | — | — |
| 2 | IdExtracao | int | N | FK → dbo.Extracao(IdExtracao) | — | — |
| 3 | Timestamp | datetime | N | — | (getdate()) | — |
| 4 | Tipo | varchar(40) | N | — | — | — |
| 5 | Payload | nvarchar(MAX) | Y | — | — | — |

## dbo.Fato_Debito

Tabela · ~48.735 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFato | bigint | N | PK, IDENT | — | — |
| 2 | SK_IdDebito | bigint | N | — | — | — |
| 3 | IdDebito | int | N | — | — | — |
| 4 | IdTempo | int | N | — | — | — |

## dbo.FRAPAlembicVersion

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | version_num | varchar(32) | N | PK | — | — |

## dbo.FRAPCategoria

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCategoria | tinyint | N | PK | — | — |
| 2 | Codigo | varchar(40) | N | — | — | — |
| 3 | Descricao | nvarchar(200) | Y | — | — | — |

## dbo.FRAPConta

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdConta | int | N | PK, IDENT | — | — |
| 2 | Banco | smallint | N | — | — | — |
| 3 | Agencia | varchar(10) | N | — | — | — |
| 4 | Conta | varchar(20) | N | — | — | — |
| 5 | Descricao | nvarchar(200) | Y | — | — | — |
| 6 | Ativa | bit | N | — | ((1)) | — |
| 7 | DataCadastro | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPDescontoFolha

Tabela · ~278 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFRAPDescontoFolha | bigint | N | PK, IDENT | — | — |
| 2 | IdDescontoFolha | int | Y | — | — | — |
| 3 | IdProcesso | int | Y | — | — | — |
| 4 | IdDebito | int | Y | — | — | — |
| 5 | IdParcelamento | int | Y | — | — | — |
| 6 | IdPessoa | int | Y | — | — | — |
| 7 | CpfCnpj | varchar(14) | Y | — | — | — |
| 8 | NomePessoa | nvarchar(200) | Y | — | — | — |
| 9 | QtdParcelasPlanejadas | int | Y | — | — | — |
| 10 | ValorTotalEsperado | numeric(18,2) | Y | — | — | — |
| 11 | SituacaoParcelamento | char(1) | Y | — | — | — |
| 12 | Ativo | bit | N | — | ((1)) | — |
| 13 | DataInclusao | datetime2(0) | Y | — | — | — |
| 14 | DataIngestao | datetime2(0) | N | — | (sysutcdatetime()) | — |
| 15 | Origem | char(1) | N | — | ('P') | — |
| 16 | IdOrgaoNotificado | int | Y | — | — | — |
| 17 | NomeOrgaoNotificado | nvarchar(200) | Y | — | — | — |

## dbo.FRAPDescontoFolhaParcela

Tabela · ~2.829 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFRAPDescontoFolhaParcela | bigint | N | PK, IDENT | — | — |
| 2 | IdFRAPDescontoFolha | bigint | N | FK → dbo.FRAPDescontoFolha(IdFRAPDescontoFolha) | — | — |
| 3 | IdParcela | int | Y | — | — | — |
| 4 | NumeroParcela | int | N | — | — | — |
| 5 | MesReferencia | tinyint | N | — | — | — |
| 6 | AnoReferencia | smallint | N | — | — | — |
| 7 | ValorEsperado | numeric(18,2) | N | — | — | — |
| 8 | DataVencimento | date | Y | — | — | — |
| 9 | DataPagamentoParcela | date | Y | — | — | — |
| 10 | SituacaoParcela | char(1) | Y | — | — | — |
| 11 | TipoDeBaixa | int | Y | — | — | — |
| 12 | DataIngestao | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPExtratoArquivo

Tabela · ~124 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivo | bigint | N | PK, IDENT | — | — |
| 2 | IdConta | int | N | FK → dbo.FRAPConta(IdConta) | — | — |
| 3 | Periodo | char(6) | N | — | — | — |
| 4 | NomeArquivo | varchar(200) | N | — | — | — |
| 5 | HashSha256 | char(64) | Y | — | — | — |
| 6 | QtdLancamentos | int | N | — | — | — |
| 7 | DataIngestao | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPJob

Tabela · ~49 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFRAPJob | int | N | PK, IDENT | — | — |
| 2 | ArqJobId | varchar(64) | N | — | — | — |
| 3 | Tipo | varchar(40) | N | — | — | — |
| 4 | Argumentos | varchar(2000) | Y | — | — | — |
| 5 | Status | varchar(20) | N | — | ('pending') | — |
| 6 | IdUsuario | int | N | FK → dbo.FRAPUsuario(IdUsuario) | — | — |
| 7 | DataCriacao | datetime | N | — | (sysutcdatetime()) | — |
| 8 | DataInicio | datetime | Y | — | — | — |
| 9 | DataFim | datetime | Y | — | — | — |
| 10 | ErroMensagem | varchar(2000) | Y | — | — | — |
| 11 | Resultado | varchar(4000) | Y | — | — | — |

## dbo.FRAPLancamento

Tabela · ~3.026 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLancamento | bigint | N | PK, IDENT | — | — |
| 2 | IdArquivo | bigint | N | FK → dbo.FRAPExtratoArquivo(IdArquivo) | — | — |
| 3 | IdConta | int | N | FK → dbo.FRAPConta(IdConta) | — | — |
| 4 | Periodo | char(6) | N | — | — | — |
| 5 | OrdemNoArquivo | int | N | — | — | — |
| 6 | DtMovimento | date | N | — | — | — |
| 7 | DtBalancete | date | Y | — | — | — |
| 8 | AgOrigem | varchar(20) | Y | — | — | — |
| 9 | Lote | varchar(20) | Y | — | — | — |
| 10 | Historico | varchar(60) | N | — | — | — |
| 11 | Documento | varchar(40) | Y | — | — | — |
| 12 | DocData | date | Y | — | — | — |
| 13 | Valor | numeric(18,2) | N | — | — | — |
| 14 | ValorDC | char(1) | N | — | — | — |
| 15 | Descricao | nvarchar(500) | Y | — | — | — |
| 16 | IdCategoria | tinyint | N | FK → dbo.FRAPCategoria(IdCategoria) | — | — |
| 17 | CpfCnpjDepositante | varchar(14) | Y | — | — | — |
| 18 | CpfCnpjAmbiguo | bit | N | — | ((0)) | — |
| 19 | DataInsercao | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPLancamentoOrgao

Tabela · ~28.835 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLancamento | int | N | PK | — | — |
| 2 | IdOrgao | int | N | PK | — | — |
| 3 | FonteInferencia | varchar(20) | N | — | ('regex') | — |
| 4 | DataInferencia | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPMatchDescontoFolha

Tabela · ~2.457 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMatchDescontoFolha | bigint | N | PK, IDENT | — | — |
| 2 | IdFRAPDescontoFolhaParcela | bigint | N | FK → dbo.FRAPDescontoFolhaParcela(IdFRAPDescontoFolhaParcela) | — | — |
| 3 | IdContraChequeItem | int | Y | — | — | — |
| 4 | IdRubrica | int | Y | — | — | — |
| 5 | ValorContracheque | numeric(18,2) | Y | — | — | — |
| 6 | IdLancamentoFRAP | bigint | Y | FK → dbo.FRAPLancamento(IdLancamento) | — | — |
| 7 | IdStatusMatch | tinyint | N | FK → dbo.FRAPStatusMatch(IdStatusMatch) | — | — |
| 8 | DataCalculo | datetime2(0) | N | — | (sysutcdatetime()) | — |
| 9 | IsManual | bit | N | — | ((0)) | — |
| 10 | IdUsuarioConcilia | int | Y | FK → dbo.FRAPUsuario(IdUsuario) | — | — |
| 11 | DataConcilia | datetime2(0) | Y | — | — | — |
| 12 | Observacao | nvarchar(500) | Y | — | — | — |

## dbo.FRAPMatchGuia

Tabela · ~1.224 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMatchGuia | bigint | N | PK, IDENT | — | — |
| 2 | IdLancamento | bigint | Y | FK → dbo.FRAPLancamento(IdLancamento) | — | — |
| 3 | IdConta | int | N | FK → dbo.FRAPConta(IdConta) | — | — |
| 4 | Periodo | char(6) | N | — | — | — |
| 5 | IdBoleto | int | Y | — | — | — |
| 6 | IdDebito | int | Y | — | — | — |
| 7 | IdProcessoExecucao | int | Y | — | — | — |
| 8 | CodigoBarras | varchar(60) | Y | — | — | — |
| 9 | DataPagamento | date | Y | — | — | — |
| 10 | ValorPago | numeric(18,2) | Y | — | — | — |
| 11 | NomePessoa | nvarchar(200) | Y | — | — | — |
| 12 | CpfCnpj | varchar(14) | Y | — | — | — |
| 13 | IdStatusMatch | tinyint | N | FK → dbo.FRAPStatusMatch(IdStatusMatch) | — | — |
| 14 | DataCalculo | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPMatchOB

Tabela · ~613 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMatchOB | bigint | N | PK, IDENT | — | — |
| 2 | IdLancamento | bigint | Y | FK → dbo.FRAPLancamento(IdLancamento) | — | — |
| 3 | IdConta | int | N | FK → dbo.FRAPConta(IdConta) | — | — |
| 4 | Periodo | char(6) | N | — | — | — |
| 5 | AnoSigef | smallint | N | — | — | — |
| 6 | CdUnidadeGestora | int | Y | — | — | — |
| 7 | CdGestao | int | Y | — | — | — |
| 8 | NuOrdemBancaria | varchar(20) | Y | — | — | — |
| 9 | DataPagamento | date | Y | — | — | — |
| 10 | ValorOB | numeric(18,2) | Y | — | — | — |
| 11 | CdCredor | varchar(20) | Y | — | — | — |
| 12 | NmCredor | nvarchar(200) | Y | — | — | — |
| 13 | NuPreparacaoPagamento | varchar(20) | Y | — | — | — |
| 14 | NuNotaEmpenho | varchar(20) | Y | — | — | — |
| 15 | IdStatusMatch | tinyint | N | FK → dbo.FRAPStatusMatch(IdStatusMatch) | — | — |
| 16 | DataCalculo | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPMatchPessoa

Tabela · ~39 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMatchPessoa | bigint | N | PK, IDENT | — | — |
| 2 | IdLancamento | bigint | N | FK → dbo.FRAPLancamento(IdLancamento) | — | — |
| 3 | IdConta | int | N | FK → dbo.FRAPConta(IdConta) | — | — |
| 4 | Periodo | char(6) | N | — | — | — |
| 5 | IdDebito | int | Y | — | — | — |
| 6 | IdProcessoExecucao | int | Y | — | — | — |
| 7 | CpfCnpj | varchar(14) | N | — | — | — |
| 8 | NomePessoa | nvarchar(200) | Y | — | — | — |
| 9 | ValorPago | numeric(18,2) | Y | — | — | — |
| 10 | ValorAPagar | numeric(18,2) | Y | — | — | — |
| 11 | ValorOriginalDebito | numeric(18,2) | Y | — | — | — |
| 12 | ValorCasadoEm | varchar(100) | Y | — | — | — |
| 13 | IdStatusMatch | tinyint | N | FK → dbo.FRAPStatusMatch(IdStatusMatch) | — | — |
| 14 | DataCalculo | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPMetricaPessoa

Tabela · ~161 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | CpfCnpj | varchar(14) | N | PK | — | — |
| 2 | ValorAtualizadoTotal | numeric(18,2) | N | — | ((0)) | — |
| 3 | QtdProcessosNotificados | int | N | — | ((0)) | — |
| 4 | QtdDebitosNotificados | int | N | — | ((0)) | — |
| 5 | DataAtualizacao | datetime2(0) | N | — | (sysutcdatetime()) | — |
| 6 | ValorDebitosNotificadosTotal | numeric(18,2) | N | — | ((0)) | — |
| 7 | QtdDebitosAtribuidos | int | N | — | ((0)) | — |
| 8 | ValorDebitosAtribuidosTotal | numeric(18,2) | N | — | ((0)) | — |

## dbo.FRAPNotificacaoDescontoFolha

Tabela · ~294 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFRAPNotifDF | bigint | N | PK, IDENT | — | — |
| 2 | NumeroProcesso | char(6) | N | — | — | — |
| 3 | AnoProcesso | char(4) | N | — | — | — |
| 4 | IdProcesso | int | Y | — | — | — |
| 5 | IdEventoCCD | int | N | — | — | — |
| 6 | IdDebito | int | Y | — | — | — |
| 7 | DataPublicacaoCCD | datetime2(0) | Y | — | — | — |
| 8 | ResumoCCD | nvarchar(MAX) | Y | — | — | — |
| 9 | NomeArquivoPDF | nvarchar(200) | Y | — | — | — |
| 10 | Origem | char(1) | N | — | ('C') | — |
| 11 | DataIngestao | datetime2(0) | N | — | (sysutcdatetime()) | — |

## dbo.FRAPRefreshToken

Tabela · ~88 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRefreshToken | int | N | PK, IDENT | — | — |
| 2 | IdUsuario | int | N | FK → dbo.FRAPUsuario(IdUsuario) | — | — |
| 3 | TokenHash | varchar(64) | N | — | — | — |
| 4 | DataExpiracao | datetime | N | — | — | — |
| 5 | DataRevogacao | datetime | Y | — | — | — |
| 6 | DataCriacao | datetime | N | — | (sysutcdatetime()) | — |

## dbo.FRAPStatusMatch

Tabela · ~23 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdStatusMatch | tinyint | N | PK | — | — |
| 2 | Codigo | varchar(40) | N | — | — | — |
| 3 | Matcher | varchar(20) | N | — | — | — |
| 4 | Descricao | nvarchar(200) | Y | — | — | — |

## dbo.FRAPUsuario

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdUsuario | int | N | PK, IDENT | — | — |
| 2 | Email | varchar(255) | N | — | — | — |
| 3 | NomeCompleto | varchar(255) | N | — | — | — |
| 4 | SenhaHash | varchar(255) | N | — | — | — |
| 5 | Papel | varchar(20) | N | — | ('user') | — |
| 6 | Ativo | bit | N | — | ((1)) | — |
| 7 | DataCriacao | datetime | N | — | (sysutcdatetime()) | — |
| 8 | DataAtualizacao | datetime | N | — | (sysutcdatetime()) | — |
| 9 | Login | nvarchar(64) | N | — | — | — |

## dbo.Irregularidade

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdIrregularidade | int | N | PK, IDENT | — | — |
| 2 | IdMonitoramento | int | N | FK → dbo.Monitoramento(IdMonitoramento) | — | — |
| 3 | Descricao | varchar(MAX) | N | — | — | — |

## dbo.Monitoramento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMonitoramento | int | N | PK, IDENT | — | — |
| 2 | IdDecisao | int | N | — | — | — |
| 3 | DataMonitoramento | varchar(10) | N | — | — | — |
| 4 | Descricao | varchar(MAX) | N | — | — | — |

## dbo.MultaProcessada

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMultaProcessada | int | N | PK, IDENT | — | — |
| 2 | IdNerMulta | int | N | FK → dbo.NERMulta(IdNerMulta) | — | — |
| 3 | DataProcessamento | datetime2(7) | N | — | — | — |

## dbo.NERDecisao

Tabela · ~759 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNerDecisao | int | N | PK, IDENT | — | — |
| 2 | IdProcesso | int | N | — | — | — |
| 3 | IdComposicaoPauta | int | N | — | — | — |
| 4 | IdVotoPauta | int | N | — | — | — |
| 5 | Modelo | varchar(100) | Y | — | — | — |
| 6 | VersaoPrompt | varchar(50) | Y | — | — | — |
| 7 | RunId | varchar(64) | Y | — | — | — |
| 8 | RawJson | nvarchar(MAX) | N | — | — | — |
| 9 | DataExtracao | datetime2(7) | N | — | (sysutcdatetime()) | — |

## dbo.NERMulta

Tabela · ~67 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNerMulta | int | N | PK, IDENT | — | — |
| 2 | IdNerDecisao | int | N | FK → dbo.NERDecisao(IdNerDecisao) | — | — |
| 3 | Ordem | int | N | — | — | — |
| 4 | DescricaoMulta | nvarchar(MAX) | N | — | — | — |

## dbo.NERObrigacao

Tabela · ~159 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNerObrigacao | int | N | PK, IDENT | — | — |
| 2 | IdNerDecisao | int | N | FK → dbo.NERDecisao(IdNerDecisao) | — | — |
| 3 | Ordem | int | N | — | — | — |
| 4 | DescricaoObrigacao | nvarchar(MAX) | N | — | — | — |

## dbo.NERRecomendacao

Tabela · ~112 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNerRecomendacao | int | N | PK, IDENT | — | — |
| 2 | IdNerDecisao | int | N | FK → dbo.NERDecisao(IdNerDecisao) | — | — |
| 3 | Ordem | int | N | — | — | — |
| 4 | DescricaoRecomendacao | nvarchar(MAX) | N | — | — | — |

## dbo.NERRessarcimento

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNerRessarcimento | int | N | PK, IDENT | — | — |
| 2 | IdNerDecisao | int | N | FK → dbo.NERDecisao(IdNerDecisao) | — | — |
| 3 | Ordem | int | N | — | — | — |
| 4 | DescricaoRessarcimento | nvarchar(MAX) | N | — | — | — |

## dbo.Obrigacao

Tabela · ~1.335 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdObrigacao | int | N | PK, IDENT | — | — |
| 2 | IdProcesso | int | N | — | — | — |
| 3 | IdComposicaoPauta | int | N | — | — | — |
| 4 | IdVotoPauta | int | N | — | — | — |
| 5 | DescricaoObrigacao | varchar(8000) | N | — | — | — |
| 6 | DeFazer | bit | Y | — | — | — |
| 7 | Prazo | varchar(MAX) | Y | — | — | — |
| 8 | DataCumprimento | date | Y | — | — | — |
| 9 | OrgaoResponsavel | varchar(MAX) | Y | — | — | — |
| 10 | IdOrgaoResponsavel | int | Y | — | — | — |
| 11 | TemMultaCominatoria | bit | Y | — | — | — |
| 12 | NomeResponsavelMultaCominatoria | varchar(MAX) | Y | — | — | — |
| 13 | DocumentoResponsavelMultaCominatoria | varchar(MAX) | Y | — | — | — |
| 14 | IdPessoaMultaCominatoria | int | Y | — | — | — |
| 15 | ValorMultaCominatoria | float | Y | — | — | — |
| 16 | PeriodoMultaCominatoria | varchar(MAX) | Y | — | — | — |
| 17 | EMultaCominatoriaSolidaria | bit | Y | — | — | — |
| 18 | SolidariosMultaCominatoria | nvarchar(MAX) | Y | — | — | — |
| 19 | Cancelado | bit | Y | — | — | — |
| 20 | ReservadoPor | varchar(255) | Y | — | — | — |
| 21 | DataReserva | datetime | Y | — | — | — |

## dbo.ObrigacaoPreprocessada

Tabela · ~190 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | ERecomendacao | bit | Y | — | ((0)) | — |
| 2 | Valor | varchar(1000) | Y | — | — | — |
| 3 | IdObrigacao | int | N | IDENT | — | — |
| 4 | IdDecisao | int | N | — | — | — |
| 5 | Prazo | varchar(MAX) | N | — | — | — |
| 6 | Descricao | varchar(MAX) | N | — | — | — |
| 7 | OrgaoResponsavel | varchar(MAX) | N | — | — | — |
| 8 | Validado | bit | Y | — | — | — |

## dbo.ObrigacaoProcessada

Tabela · ~155 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdObrigacaoProcessada | int | N | PK, IDENT | — | — |
| 2 | IdNerObrigacao | int | N | FK → dbo.NERObrigacao(IdNerObrigacao) | — | — |
| 3 | IdObrigacao | int | Y | FK → dbo.Obrigacao(IdObrigacao) | — | — |
| 4 | DataProcessamento | datetime2(7) | N | — | — | — |

## dbo.ObrigacaoStaging

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdObrigacaoStaging | int | N | PK, IDENT | — | — |
| 2 | IdProcesso | int | N | — | — | — |
| 3 | IdComposicaoPauta | int | N | — | — | — |
| 4 | IdVotoPauta | int | N | — | — | — |
| 5 | DescricaoObrigacao | varchar(MAX) | N | — | — | — |
| 6 | DeFazer | bit | Y | — | ((1)) | — |
| 7 | Prazo | varchar(MAX) | Y | — | — | — |
| 8 | DataCumprimento | date | Y | — | — | — |
| 9 | OrgaoResponsavel | varchar(MAX) | Y | — | — | — |
| 10 | IdOrgaoResponsavel | int | Y | — | — | — |
| 11 | TemMultaCominatoria | bit | Y | — | ((0)) | — |
| 12 | NomeResponsavelMultaCominatoria | varchar(MAX) | Y | — | — | — |
| 13 | DocumentoResponsavelMultaCominatoria | varchar(MAX) | Y | — | — | — |
| 14 | IdPessoaMultaCominatoria | int | Y | — | — | — |
| 15 | ValorMultaCominatoria | float | Y | — | — | — |
| 16 | PeriodoMultaCominatoria | varchar(MAX) | Y | — | — | — |
| 17 | EMultaCominatoriaSolidaria | bit | Y | — | ((0)) | — |
| 18 | SolidariosMultaCominatoria | nvarchar(MAX) | Y | — | — | — |
| 19 | Status | varchar(8) | N | — | ('pending') | — |
| 20 | Revisor | varchar(255) | Y | — | — | — |
| 21 | DataRevisao | datetime | Y | — | — | — |
| 22 | ReservadoPor | varchar(255) | Y | — | — | — |
| 23 | DataReserva | datetime | Y | — | — | — |
| 24 | PayloadOriginal | nvarchar(MAX) | Y | — | — | — |
| 25 | ObservacoesRevisao | varchar(MAX) | Y | — | — | — |
| 26 | IdNerObrigacao | int | Y | FK → dbo.NERObrigacao(IdNerObrigacao) | — | — |
| 27 | IdObrigacao | int | Y | FK → dbo.Obrigacao(IdObrigacao) | — | — |

## dbo.Recomendacao

Tabela · ~901 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRecomendacao | int | N | PK, IDENT | — | — |
| 2 | IdProcesso | int | N | — | — | — |
| 3 | IdComposicaoPauta | int | N | — | — | — |
| 4 | IdVotoPauta | int | N | — | — | — |
| 5 | DescricaoRecomendacao | varchar(MAX) | Y | — | — | — |
| 6 | PrazoCumprimentoRecomendacao | varchar(MAX) | Y | — | — | — |
| 7 | DataCumprimentoRecomendacao | date | Y | — | — | — |
| 8 | NomeResponsavel | varchar(MAX) | Y | — | — | — |
| 9 | IdPessoaResponsavel | int | Y | — | — | — |
| 10 | OrgaoResponsavel | varchar(MAX) | Y | — | — | — |
| 11 | IdOrgaoResponsavel | int | Y | — | — | — |
| 12 | Cancelado | bit | Y | — | — | — |
| 13 | ReservadoPor | varchar(255) | Y | — | — | — |
| 14 | DataReserva | datetime | Y | — | — | — |

## dbo.RecomendacaoProcessada

Tabela · ~32 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRecomendacaoProcessada | int | N | PK, IDENT | — | — |
| 2 | IdNerRecomendacao | int | N | FK → dbo.NERRecomendacao(IdNerRecomendacao) | — | — |
| 3 | IdRecomendacao | int | Y | FK → dbo.Recomendacao(IdRecomendacao) | — | — |
| 4 | DataProcessamento | datetime2(7) | N | — | — | — |

## dbo.RecomendacaoStaging

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRecomendacaoStaging | int | N | PK, IDENT | — | — |
| 2 | IdProcesso | int | N | — | — | — |
| 3 | IdComposicaoPauta | int | N | — | — | — |
| 4 | IdVotoPauta | int | N | — | — | — |
| 5 | DescricaoRecomendacao | varchar(MAX) | Y | — | — | — |
| 6 | PrazoCumprimentoRecomendacao | varchar(MAX) | Y | — | — | — |
| 7 | DataCumprimentoRecomendacao | date | Y | — | — | — |
| 8 | NomeResponsavel | varchar(MAX) | Y | — | — | — |
| 9 | IdPessoaResponsavel | int | Y | — | — | — |
| 10 | OrgaoResponsavel | varchar(MAX) | Y | — | — | — |
| 11 | IdOrgaoResponsavel | int | Y | — | — | — |
| 12 | Cancelado | bit | Y | — | — | — |
| 13 | Status | varchar(8) | N | — | ('pending') | — |
| 14 | Revisor | varchar(255) | Y | — | — | — |
| 15 | DataRevisao | datetime | Y | — | — | — |
| 16 | ReservadoPor | varchar(255) | Y | — | — | — |
| 17 | DataReserva | datetime | Y | — | — | — |
| 18 | PayloadOriginal | nvarchar(MAX) | Y | — | — | — |
| 19 | ObservacoesRevisao | varchar(MAX) | Y | — | — | — |
| 20 | IdNerRecomendacao | int | Y | FK → dbo.NERRecomendacao(IdNerRecomendacao) | — | — |
| 21 | IdRecomendacao | int | Y | FK → dbo.Recomendacao(IdRecomendacao) | — | — |

## dbo.RessarcimentoProcessado

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRessarcimentoProcessado | int | N | PK, IDENT | — | — |
| 2 | IdNerRessarcimento | int | N | FK → dbo.NERRessarcimento(IdNerRessarcimento) | — | — |
| 3 | DataProcessamento | datetime2(7) | N | — | — | — |

## dbo.Stage_Sincronia

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSincronia | int | N | PK, IDENT | — | — |
| 2 | DataUltimaAtualizacao | datetime2(7) | N | — | — | — |

## dbo.TokensRenovacao

Tabela · ~57 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTokenRenovacao | int | N | PK, IDENT | — | — |
| 2 | IdUsuario | int | N | FK → dbo.Usuarios(IdUsuario) | — | — |
| 3 | HashToken | varchar(255) | N | — | — | — |
| 4 | DataExpiracao | datetime | N | — | — | — |
| 5 | DataRevogacao | datetime | Y | — | — | — |
| 6 | DataCriacao | datetime | N | — | (getdate()) | — |

## dbo.Usuarios

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdUsuario | int | N | PK, IDENT | — | — |
| 2 | NomeUsuario | varchar(150) | N | — | — | — |
| 3 | Email | varchar(255) | N | — | — | — |
| 4 | SenhaHash | varchar(255) | N | — | — | — |
| 5 | Papel | varchar(8) | N | — | ('reviewer') | — |
| 6 | Ativo | bit | N | — | ((1)) | — |
| 7 | DataCriacao | datetime | N | — | (getdate()) | — |
| 8 | DataAtualizacao | datetime | N | — | (getdate()) | — |

## dbo.vwDecisao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdInformacao | int | N | — | — | — |
| 2 | numero_processo | char(6) | N | — | — | — |
| 3 | ano_processo | char(4) | N | — | — | — |
| 4 | codigo_tipo_processo | char(3) | N | — | — | — |
| 5 | assunto | char(255) | Y | — | — | — |
| 6 | setor | varchar(10) | N | — | — | — |
| 7 | resumo | varchar(8000) | Y | — | — | — |
| 8 | data_resumo | datetime | Y | — | — | — |
| 9 | arquivo | varchar(42) | N | — | — | — |
| 10 | datapublicacao | datetime | Y | — | — | — |

## dbo.vwDespesaELP

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | id_empenho | int | N | — | — | — |
| 2 | id_liquidacao | int | Y | — | — | — |
| 3 | id_pagamento | int | Y | — | — | — |
| 4 | numero_processo | varchar(30) | Y | — | — | — |
| 5 | fase_despesa | varchar(10) | N | — | — | — |
| 6 | tipo_documento | varchar(56) | Y | — | — | — |
| 7 | documento | varchar(50) | Y | — | — | — |
| 8 | data | date | Y | — | — | — |
| 9 | valor | decimal(14,2) | N | — | — | — |
| 10 | valor_anulado | decimal(38,2) | Y | — | — | — |
| 11 | justificativa | varchar(8000) | Y | — | — | — |
| 12 | categoria_contrato | varchar(100) | Y | — | — | — |
| 13 | tipo_favorecido | varchar(50) | Y | — | — | — |
| 14 | cpf_cnpj_favorecido | varchar(14) | Y | — | — | — |
| 15 | nome_favorecido | varchar(300) | Y | — | — | — |
| 16 | codigo_banco | varchar(30) | Y | — | — | — |
| 17 | codigo_agencia | varchar(30) | Y | — | — | — |
| 18 | conta_corrente | varchar(30) | Y | — | — | — |
| 19 | tipo_recurso_vinculado | varchar(107) | Y | — | — | — |
| 20 | fonte_recurso | nvarchar(4000) | Y | — | — | — |
| 21 | descricao_fonte_recurso | varchar(350) | Y | — | — | — |
| 22 | descricao_especificacao_fonte_recurso | varchar(150) | Y | — | — | — |
| 23 | descricao_detalhada_especificacao_fonte_recurso | varchar(600) | Y | — | — | — |
| 24 | codigo_funcao | char(2) | Y | — | — | — |
| 25 | funcao | varchar(50) | Y | — | — | — |
| 26 | codigo_subfuncao | char(3) | Y | — | — | — |
| 27 | subfuncao | varchar(50) | Y | — | — | — |
| 28 | classificacao_funcional | nvarchar(4000) | N | — | — | — |
| 29 | codigo_programa | char(5) | Y | — | — | — |
| 30 | programa | varchar(300) | Y | — | — | — |
| 31 | codigo_instrumento_programacao | char(5) | Y | — | — | — |
| 32 | instrumento_programacao | varchar(300) | Y | — | — | — |
| 33 | classificacao_programatica | nvarchar(4000) | N | — | — | — |
| 34 | codigo_categoria_economica | char(1) | Y | — | — | — |
| 35 | categoria_economica | varchar(30) | Y | — | — | — |
| 36 | codigo_grupo_despesa | char(1) | Y | — | — | — |
| 37 | grupo_despesa | varchar(100) | Y | — | — | — |
| 38 | codigo_modalidade_aplicacao | char(2) | Y | — | — | — |
| 39 | modalidade_aplicacao | varchar(250) | Y | — | — | — |
| 40 | codigo_elemento_despesa | char(2) | Y | — | — | — |
| 41 | elemento_despesa | varchar(8000) | Y | — | — | — |
| 42 | codigo_desdobramento_despesa | char(2) | Y | — | — | — |
| 43 | desdobramento_despesa | varchar(200) | Y | — | — | — |
| 44 | codigo_natureza_despesa | nvarchar(4000) | N | — | — | — |
| 45 | recibo_anexo_38 | int | Y | — | — | — |
| 46 | recibo_anexo_23 | int | Y | — | — | — |
| 47 | recibo_siai_obras | int | Y | — | — | — |
| 48 | contexto_uj | nvarchar(4000) | N | — | — | — |
| 49 | id_orgao_superior | int | Y | — | — | — |
| 50 | nome_orgao_superior | varchar(150) | Y | — | — | — |
| 51 | codigo_orgao_superior | varchar(10) | Y | — | — | — |
| 52 | id_orgao | int | N | — | — | — |
| 53 | nome_orgao | varchar(150) | N | — | — | — |
| 54 | codigo_orgao | varchar(10) | Y | — | — | — |
| 55 | codigo_unidade_institucional | varchar(11) | Y | — | — | — |
| 56 | nome_unidade_institucional | varchar(200) | Y | — | — | — |
| 57 | codigo_ibge | char(7) | Y | — | — | — |
| 58 | municipio | varchar(120) | Y | — | — | — |
| 59 | data_inclusao | smalldatetime | Y | — | — | — |
| 60 | hash | varchar(40) | Y | — | — | — |
| 61 | hash_edital | varchar(40) | Y | — | — | — |

## dbo.vwDespesaEmpenho

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | id_empenho | int | N | — | — | — |
| 2 | numero_processo | varchar(30) | Y | — | — | — |
| 3 | fase_despesa | varchar(7) | N | — | — | — |
| 4 | tipo_documento | varchar(24) | Y | — | — | — |
| 5 | documento | varchar(15) | Y | — | — | — |
| 6 | data | date | N | — | — | — |
| 7 | valor | decimal(14,2) | N | — | — | — |
| 8 | valor_anulado | decimal(38,2) | Y | — | — | — |
| 9 | justificativa | varchar(8000) | Y | — | — | — |
| 10 | categoria_contrato | varchar(100) | Y | — | — | — |
| 11 | id_tipo_documento_credor | tinyint | Y | — | — | — |
| 12 | tipo_favorecido | varchar(50) | Y | — | — | — |
| 13 | cpf_cnpj_favorecido | varchar(14) | Y | — | — | — |
| 14 | nome_favorecido | varchar(300) | Y | — | — | — |
| 15 | codigo_banco | varchar(30) | Y | — | — | — |
| 16 | codigo_agencia | varchar(30) | Y | — | — | — |
| 17 | conta_corrente | varchar(30) | Y | — | — | — |
| 18 | tipo_recurso_vinculado | varchar(107) | Y | — | — | — |
| 19 | fonte_recurso | nvarchar(4000) | Y | — | — | — |
| 20 | descricao_fonte_recurso | varchar(350) | Y | — | — | — |
| 21 | descricao_especificacao_fonte_recurso | varchar(150) | Y | — | — | — |
| 22 | descricao_detalhada_especificacao_fonte_recurso | varchar(600) | Y | — | — | — |
| 23 | codigo_funcao | char(2) | Y | — | — | — |
| 24 | funcao | varchar(50) | Y | — | — | — |
| 25 | codigo_subfuncao | char(3) | Y | — | — | — |
| 26 | subfuncao | varchar(50) | Y | — | — | — |
| 27 | classificacao_funcional | nvarchar(4000) | N | — | — | — |
| 28 | codigo_programa | char(5) | Y | — | — | — |
| 29 | programa | varchar(300) | Y | — | — | — |
| 30 | codigo_instrumento_programacao | char(5) | Y | — | — | — |
| 31 | instrumento_programacao | varchar(300) | Y | — | — | — |
| 32 | classificacao_programatica | nvarchar(4000) | N | — | — | — |
| 33 | codigo_categoria_economica | char(1) | Y | — | — | — |
| 34 | categoria_economica | varchar(30) | Y | — | — | — |
| 35 | codigo_grupo_despesa | char(1) | Y | — | — | — |
| 36 | grupo_despesa | varchar(100) | Y | — | — | — |
| 37 | codigo_modalidade_aplicacao | char(2) | Y | — | — | — |
| 38 | modalidade_aplicacao | varchar(250) | Y | — | — | — |
| 39 | id_elemento_despesa | tinyint | Y | — | — | — |
| 40 | codigo_elemento_despesa | char(2) | Y | — | — | — |
| 41 | elemento_despesa | varchar(8000) | Y | — | — | — |
| 42 | codigo_desdobramento_despesa | char(2) | Y | — | — | — |
| 43 | desdobramento_despesa | varchar(200) | Y | — | — | — |
| 44 | codigo_natureza_despesa | nvarchar(4000) | N | — | — | — |
| 45 | recibo_anexo_38 | int | Y | — | — | — |
| 46 | recibo_anexo_23 | int | Y | — | — | — |
| 47 | recibo_siai_obras | int | Y | — | — | — |
| 48 | contexto_uj | nvarchar(4000) | N | — | — | — |
| 49 | id_orgao_superior | int | Y | — | — | — |
| 50 | nome_orgao_superior | varchar(150) | Y | — | — | — |
| 51 | codigo_orgao_superior | varchar(10) | Y | — | — | — |
| 52 | id_orgao | int | N | — | — | — |
| 53 | nome_orgao | varchar(150) | N | — | — | — |
| 54 | codigo_orgao | varchar(10) | Y | — | — | — |
| 55 | codigo_unidade_institucional | varchar(11) | Y | — | — | — |
| 56 | nome_unidade_institucional | varchar(200) | Y | — | — | — |
| 57 | codigo_ibge | char(7) | Y | — | — | — |
| 58 | municipio | varchar(120) | Y | — | — | — |
| 59 | data_inclusao | smalldatetime | Y | — | — | — |
| 60 | hash | varchar(40) | Y | — | — | — |
| 61 | hash_edital | varchar(40) | Y | — | — | — |

## dbo.vwDespesaLiquidacao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | id_liquidacao | int | N | — | — | — |
| 2 | id_empenho | int | N | — | — | — |
| 3 | numero_processo | varchar(30) | Y | — | — | — |
| 4 | fase_despesa | varchar(10) | N | — | — | — |
| 5 | tipo_documento | varchar(56) | Y | — | — | — |
| 6 | documento | varchar(50) | Y | — | — | — |
| 7 | data | date | Y | — | — | — |
| 8 | valor | decimal(14,2) | N | — | — | — |
| 9 | valor_anulado | decimal(38,2) | Y | — | — | — |
| 10 | justificativa | varchar(30) | Y | — | — | — |
| 11 | categoria_contrato | varchar(100) | Y | — | — | — |
| 12 | id_tipo_documento_credor | tinyint | Y | — | — | — |
| 13 | tipo_favorecido | varchar(50) | Y | — | — | — |
| 14 | cpf_cnpj_favorecido | varchar(14) | Y | — | — | — |
| 15 | nome_favorecido | varchar(300) | Y | — | — | — |
| 16 | codigo_banco | varchar(30) | Y | — | — | — |
| 17 | codigo_agencia | varchar(30) | Y | — | — | — |
| 18 | conta_corrente | varchar(30) | Y | — | — | — |
| 19 | tipo_recurso_vinculado | varchar(107) | Y | — | — | — |
| 20 | fonte_recurso | nvarchar(4000) | Y | — | — | — |
| 21 | descricao_fonte_recurso | varchar(350) | Y | — | — | — |
| 22 | descricao_especificacao_fonte_recurso | varchar(150) | Y | — | — | — |
| 23 | descricao_detalhada_especificacao_fonte_recurso | varchar(600) | Y | — | — | — |
| 24 | codigo_funcao | char(2) | Y | — | — | — |
| 25 | funcao | varchar(50) | Y | — | — | — |
| 26 | codigo_subfuncao | char(3) | Y | — | — | — |
| 27 | subfuncao | varchar(50) | Y | — | — | — |
| 28 | classificacao_funcional | nvarchar(4000) | N | — | — | — |
| 29 | codigo_programa | char(5) | Y | — | — | — |
| 30 | programa | varchar(300) | Y | — | — | — |
| 31 | codigo_instrumento_programacao | char(5) | Y | — | — | — |
| 32 | instrumento_programacao | varchar(300) | Y | — | — | — |
| 33 | classificacao_programatica | nvarchar(4000) | N | — | — | — |
| 34 | codigo_categoria_economica | char(1) | Y | — | — | — |
| 35 | categoria_economica | varchar(30) | Y | — | — | — |
| 36 | codigo_grupo_despesa | char(1) | Y | — | — | — |
| 37 | grupo_despesa | varchar(100) | Y | — | — | — |
| 38 | codigo_modalidade_aplicacao | char(2) | Y | — | — | — |
| 39 | modalidade_aplicacao | varchar(250) | Y | — | — | — |
| 40 | id_elemento_despesa | tinyint | Y | — | — | — |
| 41 | codigo_elemento_despesa | char(2) | Y | — | — | — |
| 42 | elemento_despesa | varchar(8000) | Y | — | — | — |
| 43 | codigo_desdobramento_despesa | char(2) | Y | — | — | — |
| 44 | desdobramento_despesa | varchar(200) | Y | — | — | — |
| 45 | codigo_natureza_despesa | nvarchar(4000) | N | — | — | — |
| 46 | recibo_anexo_38 | int | Y | — | — | — |
| 47 | recibo_anexo_23 | int | Y | — | — | — |
| 48 | recibo_siai_obras | int | Y | — | — | — |
| 49 | contexto_uj | nvarchar(4000) | N | — | — | — |
| 50 | id_orgao_superior | int | Y | — | — | — |
| 51 | nome_orgao_superior | varchar(150) | Y | — | — | — |
| 52 | codigo_orgao_superior | varchar(10) | Y | — | — | — |
| 53 | id_orgao | int | N | — | — | — |
| 54 | nome_orgao | varchar(150) | N | — | — | — |
| 55 | codigo_orgao | varchar(10) | Y | — | — | — |
| 56 | codigo_unidade_institucional | varchar(11) | Y | — | — | — |
| 57 | nome_unidade_institucional | varchar(200) | Y | — | — | — |
| 58 | codigo_ibge | char(7) | Y | — | — | — |
| 59 | municipio | varchar(120) | Y | — | — | — |
| 60 | data_inclusao | smalldatetime | Y | — | — | — |
| 61 | hash | varchar(40) | Y | — | — | — |
| 62 | hash_edital | varchar(40) | Y | — | — | — |

## dbo.vwDespesaPagamento

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | id_pagamento | int | N | — | — | — |
| 2 | id_liquidacao | int | Y | — | — | — |
| 3 | id_empenho | int | N | — | — | — |
| 4 | numero_processo | varchar(30) | Y | — | — | — |
| 5 | fase_despesa | varchar(9) | N | — | — | — |
| 6 | tipo_documento | varchar(26) | Y | — | — | — |
| 7 | documento | varchar(30) | N | — | — | — |
| 8 | data | date | N | — | — | — |
| 9 | valor | decimal(14,2) | N | — | — | — |
| 10 | valor_anulado | decimal(38,2) | Y | — | — | — |
| 11 | justificativa | varchar(8000) | Y | — | — | — |
| 12 | categoria_contrato | varchar(100) | Y | — | — | — |
| 13 | id_tipo_documento_credor | tinyint | Y | — | — | — |
| 14 | tipo_favorecido | varchar(50) | Y | — | — | — |
| 15 | cpf_cnpj_favorecido | varchar(14) | Y | — | — | — |
| 16 | nome_favorecido | varchar(300) | Y | — | — | — |
| 17 | codigo_banco | varchar(5) | Y | — | — | — |
| 18 | codigo_agencia | varchar(10) | Y | — | — | — |
| 19 | conta_corrente | varchar(20) | Y | — | — | — |
| 20 | tipo_recurso_vinculado | varchar(107) | Y | — | — | — |
| 21 | fonte_recurso | nvarchar(4000) | Y | — | — | — |
| 22 | descricao_fonte_recurso | varchar(350) | Y | — | — | — |
| 23 | descricao_especificacao_fonte_recurso | varchar(150) | Y | — | — | — |
| 24 | descricao_detalhada_especificacao_fonte_recurso | varchar(600) | Y | — | — | — |
| 25 | codigo_funcao | char(2) | Y | — | — | — |
| 26 | funcao | varchar(50) | Y | — | — | — |
| 27 | codigo_subfuncao | char(3) | Y | — | — | — |
| 28 | subfuncao | varchar(50) | Y | — | — | — |
| 29 | classificacao_funcional | nvarchar(4000) | N | — | — | — |
| 30 | codigo_programa | char(5) | Y | — | — | — |
| 31 | programa | varchar(300) | Y | — | — | — |
| 32 | codigo_instrumento_programacao | char(5) | Y | — | — | — |
| 33 | instrumento_programacao | varchar(300) | Y | — | — | — |
| 34 | classificacao_programatica | nvarchar(4000) | N | — | — | — |
| 35 | codigo_categoria_economica | char(1) | Y | — | — | — |
| 36 | categoria_economica | varchar(30) | Y | — | — | — |
| 37 | codigo_grupo_despesa | char(1) | Y | — | — | — |
| 38 | grupo_despesa | varchar(100) | Y | — | — | — |
| 39 | codigo_modalidade_aplicacao | char(2) | Y | — | — | — |
| 40 | modalidade_aplicacao | varchar(250) | Y | — | — | — |
| 41 | id_elemento_despesa | tinyint | Y | — | — | — |
| 42 | codigo_elemento_despesa | char(2) | Y | — | — | — |
| 43 | elemento_despesa | varchar(8000) | Y | — | — | — |
| 44 | codigo_desdobramento_despesa | char(2) | Y | — | — | — |
| 45 | desdobramento_despesa | varchar(200) | Y | — | — | — |
| 46 | codigo_natureza_despesa | nvarchar(4000) | N | — | — | — |
| 47 | recibo_anexo_38 | int | Y | — | — | — |
| 48 | recibo_anexo_23 | int | Y | — | — | — |
| 49 | recibo_siai_obras | int | Y | — | — | — |
| 50 | contexto_uj | nvarchar(4000) | N | — | — | — |
| 51 | id_orgao_superior | int | Y | — | — | — |
| 52 | nome_orgao_superior | varchar(150) | Y | — | — | — |
| 53 | codigo_orgao_superior | varchar(10) | Y | — | — | — |
| 54 | id_orgao | int | N | — | — | — |
| 55 | nome_orgao | varchar(150) | N | — | — | — |
| 56 | codigo_orgao | varchar(10) | Y | — | — | — |
| 57 | codigo_unidade_institucional | varchar(11) | Y | — | — | — |
| 58 | nome_unidade_institucional | varchar(200) | Y | — | — | — |
| 59 | codigo_ibge | char(7) | Y | — | — | — |
| 60 | municipio | varchar(120) | Y | — | — | — |
| 61 | data_inclusao | smalldatetime | Y | — | — | — |
| 62 | hash | varchar(40) | Y | — | — | — |
| 63 | hash_edital | varchar(40) | Y | — | — | — |

## dbo.vwEdital

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | id_edital | int | N | — | — | — |
| 2 | codigo_orgao | varchar(10) | Y | — | — | — |
| 3 | codigo_ibge | char(7) | Y | — | — | — |
| 4 | fundamento_legal | varchar(200) | Y | — | — | — |
| 5 | nome | varchar(8000) | N | — | — | — |
| 6 | numero_processo | varchar(20) | N | — | — | — |
| 7 | ano_processo | smallint | N | — | — | — |
| 8 | hash | varchar(40) | Y | — | — | — |

## dbo.vwLicitacao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | id_edital | int | N | — | — | — |
| 2 | natureza_orgao | varchar(100) | Y | — | — | — |
| 3 | id_orgao_superior | int | Y | — | — | — |
| 4 | id_orgao | int | N | — | — | — |
| 5 | codigo_ibge | char(7) | Y | — | — | — |
| 6 | municipio | varchar(120) | Y | — | — | — |
| 7 | codigo_orgao_superior | varchar(10) | Y | — | — | — |
| 8 | nome_orgao_superior | varchar(150) | Y | — | — | — |
| 9 | cnpj_orgao | char(14) | Y | — | — | — |
| 10 | codigo_orgao | varchar(10) | Y | — | — | — |
| 11 | nome_orgao | varchar(150) | N | — | — | — |
| 12 | codigo_unidade_orcamentaria | varchar(10) | Y | — | — | — |
| 13 | nome_unidade_orcamentaria | varchar(200) | Y | — | — | — |
| 14 | esfera | char(1) | N | — | — | — |
| 15 | procedimento_licitatorio | varchar(8000) | Y | — | — | — |
| 16 | modalidade_licitacao | varchar(50) | Y | — | — | — |
| 17 | fundamento_legal | varchar(200) | Y | — | — | — |
| 18 | tipo_aplicacao_mpe | varchar(100) | Y | — | — | — |
| 19 | criterio_adjudicacao | varchar(150) | Y | — | — | — |
| 20 | criterio_julgamento | varchar(90) | Y | — | — | — |
| 21 | edital | varchar(8000) | N | — | — | — |
| 22 | objeto | varchar(8000) | Y | — | — | — |
| 23 | classificacao_objeto | varchar(8000) | Y | — | — | — |
| 24 | data_disponibilizacao_inicio | datetime | Y | — | — | — |
| 25 | data_disponibilizacao_fim | datetime | Y | — | — | — |
| 26 | data_publicacao | datetime | Y | — | — | — |
| 27 | data_julgamento | datetime | Y | — | — | — |
| 28 | data_habilitacao | datetime | Y | — | — | — |
| 29 | data_homologacao | datetime | Y | — | — | — |
| 30 | data_atualizacao | datetime | Y | — | — | — |
| 31 | id_licitacao | nvarchar(4000) | N | — | — | — |
| 32 | numero_processo | varchar(20) | N | — | — | — |
| 33 | ano_processo | smallint | N | — | — | — |
| 34 | local_disponibilizacao | varchar(8000) | Y | — | — | — |
| 35 | id_procedimento_licitatorio | tinyint | N | — | — | — |
| 36 | participantes | nvarchar(MAX) | Y | — | — | — |
| 37 | lotes | nvarchar(MAX) | Y | — | — | — |
| 38 | total_orcado | decimal(14,2) | N | — | — | — |
| 39 | total_recurso_proprio | decimal(14,2) | N | — | — | — |
| 40 | total_recurso_federal | decimal(14,2) | N | — | — | — |
| 41 | total_recurso_estadual | decimal(14,2) | N | — | — | — |
| 42 | total_recurso_municipal | decimal(14,2) | N | — | — | — |
| 43 | situacao | varchar(50) | Y | — | — | — |
| 44 | data_situacao | datetime | Y | — | — | — |
| 45 | qtd_arquivos_anexos | int | Y | — | — | — |
| 46 | data_inclusao | datetime | Y | — | — | — |
| 47 | fonte_recurso | nvarchar(MAX) | Y | — | — | — |
| 48 | favorecidos | nvarchar(MAX) | Y | — | — | — |
| 49 | hash | varchar(40) | Y | — | — | — |

## dbo.vwPaineisDimDebitoOriginal

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDebitoOriginal | int | N | — | — | — |
| 2 | IdProcessoOrigem | int | Y | — | — | — |
| 3 | ProcessoOrigem | varchar(11) | Y | — | — | — |
| 4 | IdProcessoExecucao | int | Y | — | — | — |
| 5 | ProcessoExecucao | varchar(11) | Y | — | — | — |
| 6 | DataDecisao | datetime | Y | — | — | — |
| 7 | DataAto | datetime | Y | — | — | — |
| 8 | DataTransito | datetime | Y | — | — | — |
| 9 | IdTempoTransito | int | Y | — | — | — |
| 10 | IdTempoDecisao | int | Y | — | — | — |
| 11 | ValorOriginalDebito | money | N | — | — | — |
| 12 | ValorAtualizado | money | Y | — | — | — |
| 13 | CodigoSituacaoDivida | int | Y | — | — | — |
| 14 | CodigoTipoDebito | int | Y | — | — | — |
| 15 | CodigoStatusDivida | int | Y | — | — | — |
| 16 | IdOrgaoCredor | int | Y | — | — | — |

## dbo.vwPaineisDimPessoa

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPessoa | int | Y | — | — | — |
| 2 | CPF | varchar(30) | Y | — | — | — |
| 3 | CNPJ | varchar(30) | Y | — | — | — |
| 4 | Documento | varchar(30) | Y | — | — | — |
| 5 | Nome | varchar(100) | Y | — | — | — |

## dbo.vwPaineisDimTempo

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | N | — | — | — |
| 2 | IdAno | int | N | — | — | — |
| 3 | Ano | int | N | — | — | — |
| 4 | IdSemestre | int | N | — | — | — |
| 5 | NSemestre | int | N | — | — | — |
| 6 | Semestre | varchar(100) | N | — | — | — |
| 7 | IdQuadrimestre | int | N | — | — | — |
| 8 | NQuadrimestre | int | N | — | — | — |
| 9 | Quadrimestre | varchar(100) | N | — | — | — |
| 10 | IdTrimestre | int | N | — | — | — |
| 11 | NTrimestre | int | N | — | — | — |
| 12 | Trimestre | varchar(100) | N | — | — | — |
| 13 | IdBimestre | int | N | — | — | — |
| 14 | NBimestre | int | N | — | — | — |
| 15 | Bimestre | varchar(100) | N | — | — | — |
| 16 | IdMes | int | N | — | — | — |
| 17 | NMes | int | N | — | — | — |
| 18 | Mes | varchar(100) | N | — | — | — |
| 19 | Aconteceu | int | N | — | — | — |

## dbo.vwPaineisFatoDebitoOriginalPessoa

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDebitoOriginalPessoa | int | N | — | — | — |
| 2 | IdDebitoOriginal | int | Y | — | — | — |
| 3 | IdPessoa | int | Y | — | — | — |

## dbo.vwPrescicaoProcessoExecucao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | DiasPrescricaoCITACAO | int | Y | — | — | — |
| 2 | IdProcessoExecucao | int | N | — | — | — |
| 3 | ProcessoExecucao | varchar(11) | N | — | — | — |
| 4 | IdCitacao | int | Y | — | — | — |
| 5 | Citacao | varchar(11) | Y | — | — | — |
| 6 | CincoDiasAposCitacao | date | Y | — | — | — |
| 7 | CodigoSetorAtual | char(10) | Y | — | — | — |
| 8 | NomeSetorAtual | varchar(140) | Y | — | — | — |
| 9 | Marcador | varchar(150) | Y | — | — | — |
| 10 | IdPessoa | int | Y | — | — | — |
| 11 | Nome | varchar(100) | Y | — | — | — |
| 12 | DataTransitoProcessoOriginal | date | Y | — | — | — |

## dbo.vwSiaiDPFolhaResumida

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | ano | int | Y | — | — | — |
| 2 | mes | int | Y | — | — | — |
| 3 | cpf | char(11) | Y | — | — | — |
| 4 | nome_servidor | char(100) | Y | — | — | — |
| 5 | descricao_rubrica | char(150) | Y | — | — | — |
| 6 | valor_rubrica | money | Y | — | — | — |
| 7 | id_orgao | int | N | — | — | — |
| 8 | codigo_orgao | varchar(10) | Y | — | — | — |
| 9 | nome_orgao | varchar(150) | N | — | — | — |
| 10 | codigo_orgao_superior | int | Y | — | — | — |
| 11 | tipo_orgao_natureza | int | Y | — | — | — |
| 12 | matricula | char(20) | Y | — | — | — |
| 13 | datanascimento | datetime | Y | — | — | — |
| 14 | data_admissao | char(10) | Y | — | — | — |
| 15 | data_desligamento | char(10) | Y | — | — | — |
| 16 | cargo | char(50) | Y | — | — | — |
| 17 | lotacao | char(150) | Y | — | — | — |
| 18 | pne | char(1) | Y | — | — | — |
| 19 | de | char(1) | Y | — | — | — |
| 20 | ch | char(2) | Y | — | — | — |
| 21 | forma_ingresso | varchar(80) | Y | — | — | — |
| 22 | regime_juridico | varchar(50) | Y | — | — | — |
| 23 | vinculo | varchar(50) | Y | — | — | — |
| 24 | situacao_funcional | varchar(50) | Y | — | — | — |
| 25 | tipo_folha | varchar(150) | Y | — | — | — |
| 26 | id_contracheque | int | N | — | — | — |
| 27 | total_descontos | numeric(32,2) | Y | — | — | — |
| 28 | total_vantagens | numeric(32,2) | Y | — | — | — |
| 29 | data_inclusao | datetime | Y | — | — | — |
| 30 | retificacao | int | N | — | — | — |

## dbo.vwSiaiPessoalFolhaCompleta

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | ano | char(4) | N | — | — | — |
| 2 | mes | char(2) | N | — | — | — |
| 3 | codigo_orgao | char(10) | N | — | — | — |
| 4 | nome_orgao | varchar(150) | N | — | — | — |
| 5 | codigo_orgao_superior | char(10) | Y | — | — | — |
| 6 | tipo_orgao_natureza | char(1) | Y | — | — | — |
| 7 | cpf | varchar(11) | Y | — | — | — |
| 8 | matricula | varchar(20) | Y | — | — | — |
| 9 | nome | varchar(200) | Y | — | — | — |
| 10 | sexo | char(1) | Y | — | — | — |
| 11 | data_nascimento | char(10) | Y | — | — | — |
| 12 | data_admissao | char(10) | Y | — | — | — |
| 13 | data_desligamento | char(10) | Y | — | — | — |
| 14 | cargo | varchar(200) | Y | — | — | — |
| 15 | lotacao | varchar(150) | Y | — | — | — |
| 16 | pne | varchar(1) | N | — | — | — |
| 17 | de | varchar(1) | N | — | — | — |
| 18 | ch | tinyint | Y | — | — | — |
| 19 | forma_ingresso | int | Y | — | — | — |
| 20 | regime_juridico | varchar(200) | Y | — | — | — |
| 21 | vinculo | varchar(100) | Y | — | — | — |
| 22 | situacao_funcional | varchar(7) | N | — | — | — |
| 23 | tipo_folha | varchar(100) | Y | — | — | — |
| 24 | id_contracheque | int | Y | — | — | — |
| 25 | codigo_rubrica | varchar(20) | Y | — | — | — |
| 26 | nome_rubrica | varchar(100) | Y | — | — | — |
| 27 | vantagem_desconto | varchar(1) | N | — | — | — |
| 28 | valor_rubrica | decimal(14,2) | N | — | — | — |
| 29 | total_descontos | numeric(32,2) | Y | — | — | — |
| 30 | total_vantagens | numeric(32,2) | Y | — | — | — |
| 31 | descricao_fonte_recursos | varchar(350) | Y | — | — | — |
| 32 | codigo_fonte_recursos | char(12) | Y | — | — | — |
| 33 | data_inclusao | smalldatetime | N | — | — | — |
| 34 | data_exportacao | datetime | N | — | — | — |

## dbo.vwSiaiPessoalFolhaCompletaTodas

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | ano | int | Y | — | — | — |
| 2 | mes | int | Y | — | — | — |
| 3 | id_orgao | int | N | — | — | — |
| 4 | codigo_orgao | varchar(10) | Y | — | — | — |
| 5 | nome_orgao | varchar(150) | N | — | — | — |
| 6 | codigo_orgao_superior | varchar(50) | Y | — | — | — |
| 7 | tipo_orgao_natureza | varchar(100) | Y | — | — | — |
| 8 | cpf | varchar(11) | Y | — | — | — |
| 9 | matricula | varchar(20) | Y | — | — | — |
| 10 | nome | varchar(200) | Y | — | — | — |
| 11 | sexo | varchar(1) | Y | — | — | — |
| 12 | data_nascimento | char(10) | Y | — | — | — |
| 13 | data_admissao | char(10) | Y | — | — | — |
| 14 | data_desligamento | char(10) | Y | — | — | — |
| 15 | cargo | varchar(200) | Y | — | — | — |
| 16 | lotacao | varchar(150) | Y | — | — | — |
| 17 | pne | varchar(1) | Y | — | — | — |
| 18 | de | varchar(1) | Y | — | — | — |
| 19 | ch | tinyint | Y | — | — | — |
| 20 | forma_ingresso | varchar(200) | Y | — | — | — |
| 21 | regime_juridico | varchar(200) | Y | — | — | — |
| 22 | vinculo | varchar(100) | Y | — | — | — |
| 23 | situacao_funcional | varchar(50) | Y | — | — | — |
| 24 | tipo_folha | varchar(150) | Y | — | — | — |
| 25 | id_contracheque | int | Y | — | — | — |
| 26 | codigo_rubrica | varchar(50) | Y | — | — | — |
| 27 | nome_rubrica | varchar(150) | Y | — | — | — |
| 28 | vantagem_desconto | varchar(1) | Y | — | — | — |
| 29 | valor_rubrica | decimal(19,4) | Y | — | — | — |
| 30 | total_descontos | numeric(32,2) | Y | — | — | — |
| 31 | total_vantagens | numeric(32,2) | Y | — | — | — |
| 32 | descricao_fonte_recursos | varchar(350) | Y | — | — | — |
| 33 | codigo_fonte_recursos | varchar(50) | Y | — | — | — |
| 34 | data_inclusao | datetime | Y | — | — | — |
| 35 | data_exportacao | datetime | N | — | — | — |

## dbo.vwSiaiPessoalFolhaResumida

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | ano | int | Y | — | — | — |
| 2 | mes | int | Y | — | — | — |
| 3 | id_orgao | int | N | — | — | — |
| 4 | codigo_orgao | varchar(10) | Y | — | — | — |
| 5 | nome_orgao | varchar(150) | N | — | — | — |
| 6 | codigo_orgao_superior | char(10) | Y | — | — | — |
| 7 | tipo_orgao_natureza | char(1) | Y | — | — | — |
| 8 | cpf | varchar(11) | Y | — | — | — |
| 9 | matricula | varchar(20) | Y | — | — | — |
| 10 | nome | varchar(200) | Y | — | — | — |
| 11 | data_nascimento | datetime | Y | — | — | — |
| 12 | data_admissao | char(10) | Y | — | — | — |
| 13 | data_desligamento | char(10) | Y | — | — | — |
| 14 | cargo | varchar(200) | Y | — | — | — |
| 15 | lotacao | varchar(150) | Y | — | — | — |
| 16 | pne | varchar(1) | Y | — | — | — |
| 17 | de | varchar(1) | Y | — | — | — |
| 18 | ch | tinyint | Y | — | — | — |
| 19 | forma_ingresso | varchar(80) | Y | — | — | — |
| 20 | regime_juridico | varchar(200) | Y | — | — | — |
| 21 | vinculo | varchar(100) | Y | — | — | — |
| 22 | situacao_funcional | varchar(50) | Y | — | — | — |
| 23 | tipo_folha | varchar(150) | Y | — | — | — |
| 24 | id_contracheque | int | Y | — | — | — |
| 25 | total_descontos | numeric(32,2) | Y | — | — | — |
| 26 | total_vantagens | numeric(32,2) | Y | — | — | — |
| 27 | data_inclusao | datetime | Y | — | — | — |
| 28 | retificacao | int | Y | — | — | — |

## dbo.vwTceNumerosMultaDefinitivo

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | Y | — | — | — |
| 2 | Ano | int | Y | — | — | — |
| 3 | Semestre | int | N | — | — | — |
| 4 | Trimestre | int | Y | — | — | — |
| 5 | Mes | int | Y | — | — | — |
| 6 | Quantidade | int | Y | — | — | — |
| 7 | SomaValorOriginal | money | Y | — | — | — |
| 8 | SomaValorAtualizado | money | Y | — | — | — |

## dbo.vwTceNumerosMultaProvisorio

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | Y | — | — | — |
| 2 | Ano | int | Y | — | — | — |
| 3 | Semestre | int | N | — | — | — |
| 4 | Trimestre | int | Y | — | — | — |
| 5 | Mes | int | Y | — | — | — |
| 6 | Quantidade | int | Y | — | — | — |
| 7 | SomaValorOriginal | money | Y | — | — | — |
| 8 | SomaValorAtualizado | money | Y | — | — | — |

## dbo.vwTceNumerosMultaRecolhidas

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | Y | — | — | — |
| 2 | Ano | int | Y | — | — | — |
| 3 | Semestre | int | N | — | — | — |
| 4 | Trimestre | int | Y | — | — | — |
| 5 | Bimestre | int | Y | — | — | — |
| 6 | Mes | int | Y | — | — | — |
| 7 | QtdMultasTotaisMES | int | Y | — | — | — |
| 8 | QtdMultasDistintasMES | int | Y | — | — | — |
| 9 | SomaValorPagoMES | money | Y | — | — | — |
| 10 | QtdMultasTotaisBIMESTRE | int | Y | — | — | — |
| 11 | QtdMultasDistintasBIMESTRE | int | Y | — | — | — |
| 12 | SomaValorPagoBIMESTRE | money | Y | — | — | — |
| 13 | QtdMultasTotaisTRIMESTRE | int | Y | — | — | — |
| 14 | QtdMultasDistintasTRIMESTRE | int | Y | — | — | — |
| 15 | SomaValorPagoTRIMESTRE | money | Y | — | — | — |
| 16 | QtdMultasTotaisSEMESTRE | int | Y | — | — | — |
| 17 | QtdMultasDistintasSEMESTRE | int | Y | — | — | — |
| 18 | SomaValorPagoSEMESTRE | money | Y | — | — | — |
| 19 | QtdMultasTotaisANO | int | Y | — | — | — |
| 20 | QtdMultasDistintasANO | int | Y | — | — | — |
| 21 | SomaValorPagoANO | money | Y | — | — | — |

## dbo.vwTceNumerosProcessoExecucaoInstaurados

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | Y | — | — | — |
| 2 | Ano | int | Y | — | — | — |
| 3 | Semestre | int | N | — | — | — |
| 4 | Trimestre | int | Y | — | — | — |
| 5 | Mes | int | Y | — | — | — |
| 6 | Quantidade | int | Y | — | — | — |

## dbo.vwTceNumerosRepasseDividaAtiva

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | Y | — | — | — |
| 2 | Ano | int | Y | — | — | — |
| 3 | Semestre | int | N | — | — | — |
| 4 | Trimestre | int | Y | — | — | — |
| 5 | Mes | int | Y | — | — | — |
| 6 | Quantidade | int | Y | — | — | — |
| 7 | SomaValorPagamentos | money | Y | — | — | — |

## dbo.vwTceNumerosRessarcimentoDefinitivo

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | Y | — | — | — |
| 2 | Ano | int | Y | — | — | — |
| 3 | Semestre | int | N | — | — | — |
| 4 | Trimestre | int | Y | — | — | — |
| 5 | Mes | int | Y | — | — | — |
| 6 | Quantidade | int | Y | — | — | — |
| 7 | SomaValorOriginal | money | Y | — | — | — |
| 8 | SomaValorAtualizado | money | Y | — | — | — |

## dbo.vwTceNumerosRessarcimentoProvisorio

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempo | int | Y | — | — | — |
| 2 | Ano | int | Y | — | — | — |
| 3 | Semestre | int | N | — | — | — |
| 4 | Trimestre | int | Y | — | — | — |
| 5 | Mes | int | Y | — | — | — |
| 6 | Quantidade | int | Y | — | — | — |
| 7 | SomaValorOriginal | money | Y | — | — | — |
| 8 | SomaValorAtualizado | money | Y | — | — | — |

## dbo.vwUnidadeInstitucional

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | id_unidade_institucional | int | N | — | — | — |
| 2 | codigo_unidade_institucional | nvarchar(4000) | Y | — | — | — |
| 3 | descricao_unidade_institucional | varchar(200) | Y | — | — | — |
| 4 | id_orgao_superior | int | Y | — | — | — |
| 5 | id_orgao | int | N | — | — | — |
| 6 | codigo_orgao | char(10) | N | — | — | — |
| 7 | nome_orgao | varchar(150) | N | — | — | — |

