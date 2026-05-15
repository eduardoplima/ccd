# Dicionário de dados — BdSIAI

Gerado em 2026-05-13. 490 objetos · 3802 colunas.

## dbo._column_details_extended_property

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | Database | nvarchar(128) | Y | — | — | — |
| 2 | Owner | nvarchar(128) | Y | — | — | — |
| 3 | TableType | varchar(10) | Y | — | — | — |
| 4 | TableName | sysname | N | — | — | — |
| 5 | ColumnName | sysname | Y | — | — | — |
| 6 | OrdinalPosition | int | Y | — | — | — |
| 7 | DefaultSetting | nvarchar(4000) | Y | — | — | — |
| 8 | DataType | nvarchar(128) | Y | — | — | — |
| 9 | MaxLength | int | Y | — | — | — |
| 10 | DatePrecision | smallint | Y | — | — | — |
| 11 | IsNullable | bit | Y | — | — | — |
| 12 | IsPrimaryKey | bit | Y | — | — | — |
| 13 | IsError | bit | N | — | — | — |
| 14 | Description | varchar(512) | Y | — | — | — |

## dbo._database_audit

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | AuditID | int | N | PK, IDENT | — | — |
| 2 | TableName | varchar(255) | Y | — | — | — |
| 3 | Action | char(3) | Y | — | — | — |
| 4 | AuditDate | datetime2(7) | Y | — | — | — |
| 5 | UserName | varchar(255) | Y | — | — | — |
| 6 | OldValues | varchar(MAX) | Y | — | — | — |
| 7 | NewValues | varchar(MAX) | Y | — | — | — |

## dbo._database_smells

Tabela · ~3.815 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDatabaseSmells | int | N | IDENT | — | — |
| 2 | EvidenceOf | varchar(16) | Y | — | — | — |
| 3 | TypeObjectOf | varchar(32) | Y | — | — | — |
| 4 | ObjectName | sysname | N | — | — | — |
| 5 | Problem | varchar(1024) | Y | — | — | — |
| 6 | Explication | varchar(1024) | Y | — | — | — |
| 7 | Command | varchar(1024) | Y | — | — | — |

## dbo._flyway_schema_history

Tabela · ~1.001 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | installed_rank | int | N | PK | — | — |
| 2 | version | nvarchar(50) | Y | — | — | — |
| 3 | description | nvarchar(200) | Y | — | — | — |
| 4 | type | nvarchar(20) | N | — | — | — |
| 5 | script | nvarchar(1000) | N | — | — | — |
| 6 | checksum | int | Y | — | — | — |
| 7 | installed_by | nvarchar(100) | N | — | — | — |
| 8 | installed_on | datetime | N | — | — | — |
| 9 | execution_time | int | N | — | — | — |
| 10 | success | bit | N | — | — | — |

## dbo._flyway_schema_history_BKP

Tabela · ~948 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | installed_rank | int | N | PK | — | — |
| 2 | version | nvarchar(50) | Y | — | — | — |
| 3 | description | nvarchar(200) | Y | — | — | — |
| 4 | type | nvarchar(20) | N | — | — | — |
| 5 | script | nvarchar(1000) | N | — | — | — |
| 6 | checksum | int | Y | — | — | — |
| 7 | installed_by | nvarchar(100) | N | — | — | — |
| 8 | installed_on | datetime | N | — | — | — |
| 9 | execution_time | int | N | — | — | — |
| 10 | success | bit | N | — | — | — |

## dbo.ActiveSubscriptions

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | ActiveID | uniqueidentifier | N | PK | — | — |
| 2 | SubscriptionID | uniqueidentifier | N | — | — | — |
| 3 | TotalNotifications | int | Y | — | — | — |
| 4 | TotalSuccesses | int | N | — | — | — |
| 5 | TotalFailures | int | N | — | — | — |

## dbo.Anexo01_DespesaCategoriaEconomica

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaCategoriaEconomica | tinyint | N | PK | — | — |
| 2 | CodigoDespesaCategoriaEconomica | char(1) | N | — | — | — |
| 3 | NomeDespesaCategoriaEconomica | varchar(30) | N | — | — | — |

## dbo.Anexo01_DespesaClassificacao

Tabela · ~915 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaClassificacao | smallint | N | PK | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | CodigoDespesaClassificacao | char(8) | N | — | — | — |
| 5 | DescricaoDespesaClassificacao | varchar(200) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_DespesaDesdobramentoDespesa

Tabela · ~31 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaDesdobramentoDespesa | smallint | N | PK | — | — |
| 2 | CodigoDespesaDesdobramentoDespesa | char(2) | N | — | — | — |
| 3 | DescricaoDespesaDesdobramentoDespesa | varchar(200) | N | — | — | — |
| 4 | IdDespesaElementoDespesa | tinyint | Y | FK → dbo.Anexo01_DespesaElementoDespesa(IdDespesaElementoDespesa) | — | — |
| 5 | IdDespesaModalidadeAplicacao | tinyint | Y | FK → dbo.Anexo01_DespesaModalidadeAplicacao(IdDespesaModalidadeAplicacao) | — | — |
| 6 | IdDespesaTipoDesdobramentoDespesa | tinyint | N | FK → dbo.Anexo01_DespesaTipoDesdobramentoDespesa(IdDespesaTipoDesdobramentoDespesa) | — | — |
| 7 | AnoReferenciaInicial | smallint | N | — | — | — |
| 8 | AnoReferenciaFinal | smallint | N | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_DespesaElementoDespesa

Tabela · ~87 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaElementoDespesa | tinyint | N | PK | — | — |
| 2 | CodigoDespesaElementoDespesa | char(2) | N | — | — | — |
| 3 | NomeDespesaElementoDespesa | varchar(250) | N | — | — | — |
| 4 | AnoReferenciaInicial | smallint | N | — | — | — |
| 5 | AnoReferenciaFinal | smallint | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_DespesaFuncionalFuncao

Tabela · ~30 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaFuncionalFuncao | tinyint | N | PK | — | — |
| 2 | CodigoDespesaFuncionalFuncao | char(2) | N | — | — | — |
| 3 | DescricaoDespesaFuncionalFuncao | varchar(50) | N | — | — | — |

## dbo.Anexo01_DespesaFuncionalSubFuncao

Tabela · ~118 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaFuncionalSubFuncao | tinyint | N | PK | — | — |
| 3 | CodigoDespesaFuncionalSubFuncao | char(3) | N | — | — | — |
| 4 | DescricaoDespesaFuncionalSubFuncao | varchar(50) | N | — | — | — |
| 5 | Extinta | bit | N | — | — | — |
| 6 | NormaExtincao | varchar(100) | Y | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_DespesaGrupoDespesa

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaGrupoDespesa | tinyint | N | PK | — | — |
| 2 | CodigoDespesaGrupoDespesa | char(1) | N | — | — | — |
| 3 | NomeDespesaGrupoDespesa | varchar(100) | N | — | — | — |
| 4 | IdDespesaCategoriaEconomica | tinyint | N | FK → dbo.Anexo01_DespesaCategoriaEconomica(IdDespesaCategoriaEconomica) | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_DespesaModalidadeAplicacao

Tabela · ~36 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaModalidadeAplicacao | tinyint | N | PK | — | — |
| 2 | CodigoDespesaModalidadeAplicacao | char(2) | N | — | — | — |
| 3 | NomeDespesaModalidadeAplicacao | varchar(250) | N | — | — | — |
| 4 | AnoReferenciaInicial | smallint | N | — | — | — |
| 5 | AnoReferenciaFinal | smallint | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_DespesaMovimento

Tabela · ~14.996.632 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaMovimento | int | N | PK, IDENT | — | — |
| 2 | IdFonteRecurso | int | N | FK → dbo.Anexo01_Fontes(IdFonteRecurso) | — | — |
| 3 | IdDespesaGrupoDespesa | tinyint | N | FK → dbo.Anexo01_DespesaGrupoDespesa(IdDespesaGrupoDespesa) | — | — |
| 4 | IdDespesaModalidadeAplicacao | tinyint | N | FK → dbo.Anexo01_DespesaModalidadeAplicacao(IdDespesaModalidadeAplicacao) | — | — |
| 5 | IdDespesaElementoDespesa | tinyint | N | FK → dbo.Anexo01_DespesaElementoDespesa(IdDespesaElementoDespesa) | — | — |
| 6 | IdUnidadeInstitucional | int | N | FK → dbo.Anexo01_UnidadeInstitucional(IdUnidadeInstitucional) | — | — |
| 7 | IdDespesaFuncionalFuncao | tinyint | N | FK → dbo.Anexo01_DespesaFuncionalFuncao(IdDespesaFuncionalFuncao) | — | — |
| 8 | IdDespesaFuncionalSubFuncao | tinyint | N | FK → dbo.Anexo01_DespesaFuncionalSubFuncao(IdDespesaFuncionalSubFuncao) | — | — |
| 9 | IdInstrumentoProgramacao | int | N | FK → dbo.Anexo01_InstrumentoProgramacao(IdInstrumentoProgramacao) | — | — |
| 10 | ValorCreditoAdicional | decimal(14,2) | N | — | — | — |
| 11 | ValorDotacaoInicial | decimal(14,2) | N | — | — | — |
| 12 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 13 | ValorEmpenhadoBimestre | decimal(14,2) | N | — | — | — |
| 14 | ValorEmpenhadoExercicio | decimal(14,2) | N | — | — | — |
| 15 | ValorLiquidadoBimestre | decimal(14,2) | N | — | — | — |
| 16 | ValorLiquidadoExercicio | decimal(14,2) | N | — | — | — |
| 17 | ValorRestosPagarNaoProcessados | decimal(14,2) | N | — | — | — |
| 18 | ValorPagoExercicio | decimal(14,2) | N | — | — | — |
| 19 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo01_DespesaReservaRPPS

Tabela · ~8.529 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaReservaRPPS | int | N | PK, IDENT | — | — |
| 2 | ValorDotacaoInicial | decimal(14,2) | N | — | — | — |
| 3 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 4 | ValorSaldoDespesasEmpenhadas | decimal(14,2) | N | — | — | — |
| 5 | ValorSaldoDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 6 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo01_DespesaTipoDesdobramentoDespesa

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDespesaTipoDesdobramentoDespesa | tinyint | N | PK | — | — |
| 2 | DescricaoDespesaTipoDesdobramentoDespesa | varchar(50) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_Fontes

Tabela · ~4.457.466 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteRecurso | int | N | PK, IDENT | — | — |
| 2 | IdFonteGovernoEstadual | int | Y | FK → dbo.Anexo01_FontesGovernoEstadual(IdFonteGovernoEstadual) | — | — |
| 3 | IdFonteGovernoMunicipal | int | Y | FK → dbo.Anexo01_FontesGovernoMunicipal(IdFonteGovernoMunicipal) | — | — |
| 4 | IdFonteTipoGrupoExercicio | tinyint | Y | FK → dbo.Anexo01_FontesTipoGrupoExercicio(IdFonteTipoGrupoExercicio) | — | — |
| 5 | IdFonteTipoEspecificacaoDestinacao | int | Y | FK → dbo.Anexo01_FontesTipoEspecificacaoDestinacao(IdFonteTipoEspecificacaoDestinacao) | — | — |
| 6 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 7 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo01_FontesGovernoEstadual

Tabela · ~9.251 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteGovernoEstadual | int | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | CodigoFonteGovernoEstadual | char(12) | N | — | — | — |
| 5 | DescricaoFonteGovernoEstadual | varchar(150) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo01_FontesGovernoMunicipal

Tabela · ~1.563.394 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteGovernoMunicipal | int | N | PK, IDENT | — | — |
| 2 | IdFonteGovernoMunicipalIdentificadorUso | int | Y | FK → dbo.Anexo01_FontesGovernoMunicipalIdentificadorUso(IdFonteGovernoMunicipalIdentificadorUso) | — | — |
| 3 | IdFonteGovernoMunicipalDestinacaoRecursos | int | Y | FK → dbo.Anexo01_FontesGovernoMunicipalGrupoDestinacaoRecursos(IdFonteGovernoMunicipalDestinacaoRecursos) | — | — |
| 4 | IdFonteGovernoMunicipalEspecificacaoFontesRecursos | int | Y | FK → dbo.Anexo01_FontesGovernoMunicipalEspecificacaoFontesRecursos(IdFonteGovernoMunicipalEspecificacaoFontesRecursos) | — | — |
| 5 | CodigoFonteGovernoMunicipal | char(10) | N | — | — | — |
| 6 | DescricaoFonteGovernoMunicipal | varchar(350) | N | — | — | — |
| 7 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo01_FontesGovernoMunicipalEspecificacaoFontesRecursos

Tabela · ~62 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteGovernoMunicipalEspecificacaoFontesRecursos | int | N | PK | — | — |
| 2 | IdFonteGovernoMunicipalTipoEspecificacaoFontesRecurso | int | N | FK → dbo.Anexo01_FontesGovernoMunicipalTipoEspecificacaoFontesRecurso(IdFonteGovernoMunicipalTipoEspecificacaoFontesRecurso) | — | — |
| 3 | AnoReferenciaInicial | smallint | N | — | — | — |
| 4 | AnoReferenciaFinal | smallint | N | — | — | — |
| 5 | CodigoEspecificacaoFontesRecurso | char(3) | N | — | — | — |
| 6 | DescricaoEspecificacaoFontesRecurso | varchar(150) | N | — | — | — |
| 7 | DescricaoDetalhadaEspecificacaoFontesRecurso | varchar(600) | Y | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo01_FontesGovernoMunicipalGrupoDestinacaoRecursos

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteGovernoMunicipalDestinacaoRecursos | int | N | PK | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | CodigoGrupoDestinacaoRecursos | char(1) | N | — | — | — |
| 5 | DescricaoGrupoDestinacaoRecursos | varchar(150) | N | — | — | — |
| 6 | DescricaoDetalhadaGrupoDestinacaoRecursos | varchar(350) | Y | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo01_FontesGovernoMunicipalIdentificadorUso

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteGovernoMunicipalIdentificadorUso | int | N | PK | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | CodigoIdentificadorUso | char(1) | N | — | — | — |
| 5 | DescricaoIdentificadorUso | varchar(150) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo01_FontesGovernoMunicipalTipoEspecificacaoFontesRecurso

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteGovernoMunicipalTipoEspecificacaoFontesRecurso | int | N | PK | — | — |
| 2 | DescricaoTipoEspecificacaoFontesRecurso | varchar(45) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | IdSessao | int | N | — | — | — |
| 6 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo01_FontesRecursoVinculado

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteRecursoVinculado | int | N | PK, IDENT | — | — |
| 2 | DescricaoRecursoVinculado | varchar(200) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Descrição de recurso Vinculado para Anexo01_FontesTipoEspecificacaoDestinacao |

## dbo.Anexo01_FontesSIOPE

Tabela · ~14 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteSIOPE | tinyint | N | PK | — | — |
| 2 | CodigoFonteSIOPE | char(3) | N | — | — | — |
| 3 | DescricaoFonteSIOPE | varchar(150) | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_FontesTipoEspecificacaoDestinacao

Tabela · ~1.187 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteTipoEspecificacaoDestinacao | int | N | PK | — | — |
| 2 | IdFonteRecursoVinculado | int | N | FK → dbo.Anexo01_FontesRecursoVinculado(IdFonteRecursoVinculado) | — | — |
| 3 | AnoReferenciaInicial | smallint | N | — | — | — |
| 4 | AnoReferenciaFinal | smallint | N | — | — | — |
| 5 | CodigoClassificacao | char(3) | N | — | — | — |
| 6 | CodigoDetalhamento | char(4) | N | — | — | — |
| 7 | DescricaoEspecificacaoDestinacao | varchar(250) | N | — | — | — |
| 8 | IdFonteSIOPE | tinyint | Y | FK → dbo.Anexo01_FontesSIOPE(IdFonteSIOPE) | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_FontesTipoGrupoExercicio

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFonteTipoGrupoExercicio | tinyint | N | PK | — | — |
| 2 | CodigoTipoGrupoExercicio | char(1) | N | — | — | — |
| 3 | DescricaoTipoGrupoExercicio | varchar(150) | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_InstrumentoProgramacao

Tabela · ~11.893.221 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdInstrumentoProgramacao | int | N | PK, IDENT | — | — |
| 2 | IdPrograma | int | N | FK → dbo.Anexo01_Programa(IdPrograma) | — | — |
| 3 | IdTipoInstrumentoProgramacao | tinyint | N | FK → dbo.Anexo01_TipoInstrumentoProgramacao(IdTipoInstrumentoProgramacao) | — | — |
| 4 | CodigoInstrumentoProgramacao | char(5) | N | — | — | — |
| 5 | Descricao | varchar(300) | N | — | — | — |
| 6 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 7 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo01_Programa

Tabela · ~1.897.595 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrograma | int | N | PK, IDENT | — | — |
| 2 | CodigoPrograma | char(5) | N | — | — | — |
| 3 | DescricaoPrograma | varchar(300) | N | — | — | — |
| 4 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 5 | IdArquivoXML | int | Y | — | — | — |

## dbo.Anexo01_ReceitaClassificacao

Tabela · ~24.464 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdReceitaClassificacao | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | CodigoReceitaClassificacao | char(10) | N | — | — | — |
| 5 | DescricaoReceitaClassificacao | varchar(250) | N | — | — | — |
| 6 | CodigoRecebeMovimento | bit | N | — | — | — |
| 7 | GrupoSTN | varchar(10) | Y | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo01_ReceitaClassificacaoRecursosExerciciosAnteriores

Tabela · ~17 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdReceitaClassificacaoRecursosExerciciosAnteriores | int | N | PK, IDENT | — | — |
| 2 | Descricao | varchar(250) | N | — | — | — |
| 3 | CodigoEspecieReceita | tinyint | N | — | — | — |
| 4 | CodigoCategoriaEconomica | tinyint | N | — | — | — |
| 5 | CodigoOrigemReceita | tinyint | N | — | — | — |
| 6 | CodigoDesdobramento1 | tinyint | N | — | — | — |
| 7 | CodigoDesdobramento2 | tinyint | N | — | — | — |
| 8 | CodigoDesdobramento3 | tinyint | N | — | — | — |
| 9 | CodigoTipoReceita | tinyint | N | — | — | — |
| 10 | CodigoEstendidoNivel8 | tinyint | N | — | — | — |
| 11 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo01_ReceitaMovimento

Tabela · ~1.594.542 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdReceitaMovimento | int | N | PK, IDENT | — | — |
| 2 | IdFonteRecurso | int | N | FK → dbo.Anexo01_Fontes(IdFonteRecurso) | — | — |
| 3 | IdReceitaClassificacao | smallint | N | FK → dbo.Anexo01_ReceitaClassificacao(IdReceitaClassificacao) | — | — |
| 4 | IdTipoOperacaoReceita | tinyint | Y | FK → dbo.Anexo01_TipoOperacaoReceita(IdTipoOperacaoReceita) | — | — |
| 5 | ValorPrevistoInicial | decimal(14,2) | N | — | — | — |
| 6 | ValorPrevistoAtualizado | decimal(14,2) | N | — | — | — |
| 7 | ValorRealizadoBimestre | decimal(14,2) | N | — | — | — |
| 8 | ValorRealizadoExercicio | decimal(14,2) | N | — | — | — |
| 9 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo01_ReceitaMovimentoRecursosExerciciosAnteriores

Tabela · ~17 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdReceitaMovimentoRecursosExerciciosAnteriores | int | N | PK, IDENT | — | — |
| 2 | IdFonteRecurso | int | N | FK → dbo.Anexo01_Fontes(IdFonteRecurso) | — | — |
| 3 | IdReceitaClassificacaoRecursosExerciciosAnteriores | int | N | FK → dbo.Anexo01_ReceitaClassificacaoRecursosExerciciosAnteriores(IdReceitaClassificacaoRecursosExerciciosAnteriores) | — | — |
| 4 | ValorPrevistoInicial | decimal(14,2) | N | — | — | — |
| 5 | ValorPrevistoAtualizado | decimal(14,2) | N | — | — | — |
| 6 | ValorRealizadoBimestre | decimal(14,2) | N | — | — | — |
| 7 | ValorRealizadoExercicio | decimal(14,2) | N | — | — | — |
| 8 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo01_ReceitaSuperavitFinanceiro

Tabela · ~7.779 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdReceitaSuperavitFinanceiro | int | N | PK, IDENT | — | — |
| 2 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 3 | ValorReceitasRealizadasExercicio | decimal(14,2) | N | — | — | — |
| 4 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo01_TipoInstrumentoProgramacao

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoInstrumentoProgramacao | tinyint | N | PK | — | — |
| 2 | DescricaoTipoInstrumentoProgramacao | varchar(50) | N | — | — | — |

## dbo.Anexo01_TipoOperacaoReceita

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoOperacaoReceita | tinyint | N | PK, IDENT | — | — |
| 2 | CodigoTipoOperacaoReceita | varchar(2) | N | — | — | — |
| 3 | DescricaoTipoOperacaoReceita | varchar(50) | N | — | — | — |

## dbo.Anexo01_UnidadeInstitucional

Tabela · ~879.433 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdUnidadeInstitucional | int | N | PK, IDENT | — | — |
| 2 | CodigoUnidadeInstitucional | varchar(11) | N | — | — | — |
| 3 | DescricaoUnidadeInstitucional | varchar(200) | N | — | — | — |
| 4 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 5 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo03_Campos

Tabela · ~124 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | OrdemCampo | tinyint | N | — | — | — |
| 5 | Campo | smallint | N | — | — | — |
| 6 | CodigoReceitaClassificacao | varchar(8) | Y | — | — | — |
| 7 | Descricao | varchar(200) | N | — | — | — |
| 8 | Grupo | bit | N | — | — | — |
| 9 | EsferaEstadual | bit | N | — | — | — |
| 10 | EsferaMunicipal | bit | N | — | — | — |
| 11 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 12 | DataInclusao | smalldatetime | N | — | — | — |
| 13 | IdSessao | int | N | — | — | — |
| 14 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo03_Movimento

Tabela · ~282.965 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo03_Campos(IdCampo) | — | — |
| 3 | MesReferencia11 | decimal(14,2) | N | — | — | — |
| 4 | MesReferencia10 | decimal(14,2) | N | — | — | — |
| 5 | MesReferencia9 | decimal(14,2) | N | — | — | — |
| 6 | MesReferencia8 | decimal(14,2) | N | — | — | — |
| 7 | MesReferencia7 | decimal(14,2) | N | — | — | — |
| 8 | MesReferencia6 | decimal(14,2) | N | — | — | — |
| 9 | MesReferencia5 | decimal(14,2) | N | — | — | — |
| 10 | MesReferencia4 | decimal(14,2) | N | — | — | — |
| 11 | MesReferencia3 | decimal(14,2) | N | — | — | — |
| 12 | MesReferencia2 | decimal(14,2) | N | — | — | — |
| 13 | MesReferencia1 | decimal(14,2) | N | — | — | — |
| 14 | MesReferencia | decimal(14,2) | N | — | — | — |
| 15 | PrevisaoAtualizadaExercicio | decimal(14,2) | N | — | — | — |

## dbo.Anexo04_AportesRecursosRPPS

Tabela · ~53.219 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | IdTipoPlano | tinyint | N | FK → dbo.Anexo04_TipoPlano(IdTipoPlano) | — | — |
| 4 | ValorAportesRealizados | decimal(14,2) | Y | — | — | — |

## dbo.Anexo04_BensDireitosRPPS

Tabela · ~47.158 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | ValorPeriodoReferenciaExercicio | decimal(14,2) | N | — | — | — |
| 4 | ValorPeriodoReferenciaExercicioAnterior | decimal(14,2) | Y | — | — | — |

## dbo.Anexo04_Campos

Tabela · ~620 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | SubGrupo | tinyint | N | — | — | — |
| 6 | Descricao | varchar(150) | N | — | — | — |
| 7 | ApenasEsferaEstadual | bit | N | — | — | — |
| 8 | Grupo | bit | N | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |
| 12 | CompensacaoEntreRegimes | bit | N | — | — | — |
| 13 | ReceitaCorrente | bit | N | — | — | — |
| 14 | OutrasReceitaCorrente | bit | N | — | — | — |
| 15 | ReceitaCapital | bit | N | — | — | — |
| 16 | ReceitaContribuicaoSegurado | bit | N | — | — | — |
| 17 | ReceitaContribuicaoPatronal | bit | N | — | — | — |
| 18 | ReceitaServico | bit | N | — | — | — |
| 19 | ReceitaValorMobiliario | bit | N | — | — | — |
| 20 | ReceitaPatrimonial | bit | N | — | — | — |
| 21 | DespesaPrevidenciaria | bit | N | — | — | — |
| 22 | ReceitaPrevidenciaria | bit | N | — | — | — |

## dbo.Anexo04_Despesas

Tabela · ~238.013 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | IdTipoPlano | tinyint | N | FK → dbo.Anexo04_TipoPlano(IdTipoPlano) | — | — |
| 4 | ValorDotacaoInicial | decimal(14,2) | Y | — | — | — |
| 5 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasEmpenhadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasEmpenhadasAteoBimestreExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 8 | ValorDespesasLiquidadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 9 | ValorDespesasLiquidadasAteoBimestreExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 10 | ValorDespesasInscritasEmRestosAPagarNaoProcessadosEmExercicio | decimal(14,2) | N | — | — | — |
| 11 | ValorDespesasInscritasEmRestosAPagarNaoProcessadosEmExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 12 | ValorDespesasPagasAteoBimestreExercicio | decimal(14,2) | Y | — | — | — |

## dbo.Anexo04_DespesasAdministracaoRPPS

Tabela · ~15.324 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoInicial | decimal(14,2) | Y | — | — | — |
| 4 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasEmpenhadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasEmpenhadasAteoBimestreExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 7 | ValorDespesasLiquidadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 8 | ValorDespesasLiquidadasAteoBimestreExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 9 | ValorDespesasInscritasEmRestosAPagarNaoProcessadosEmExercicio | decimal(14,2) | N | — | — | — |
| 10 | ValorDespesasInscritasEmRestosAPagarNaoProcessadosEmExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 11 | ValorDespesasPagasAteoBimestreExercicio | decimal(14,2) | Y | — | — | — |

## dbo.Anexo04_DespesasIntraOrcamentariasRPPS

Tabela · ~1.552 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoInicial | decimal(14,2) | N | — | — | — |
| 4 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasEmpenhadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasEmpenhadasAteoBimestreExercicioAnterior | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasLiquidadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 8 | ValorDespesasLiquidadasAteoBimestreExercicioAnterior | decimal(14,2) | N | — | — | — |
| 9 | ValorDespesasInscritasEmRestosAPagarEmExercicio | decimal(14,2) | N | — | — | — |
| 10 | ValorDespesasInscritasEmRestosAPagarEmExercicioAnterior | decimal(14,2) | N | — | — | — |

## dbo.Anexo04_Receitas

Tabela · ~481.000 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | IdTipoPlano | tinyint | N | FK → dbo.Anexo04_TipoPlano(IdTipoPlano) | — | — |
| 4 | ValorPrevisaoInicial | decimal(14,2) | Y | — | — | — |
| 5 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 6 | ValorReceitasRealizadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 7 | ValorReceitasRealizadasAteoBimestreExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 8 | ValorReceitasRealizadasNoBimestre | decimal(14,2) | Y | — | — | Utilizado até 2014 |

## dbo.Anexo04_ReceitasAdministracaoRPPS

Tabela · ~6.088 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoInicial | decimal(14,2) | Y | — | — | — |
| 4 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 5 | ValorReceitasRealizadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 6 | ValorReceitasRealizadasAteoBimestreExercicioAnterior | decimal(14,2) | Y | — | — | — |

## dbo.Anexo04_ReceitasIntraOrcamentariasRPPS

Tabela · ~8.148 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoInicial | decimal(14,2) | N | — | — | — |
| 4 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 5 | ValorReceitasRealizadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 6 | ValorReceitasRealizadasAteoBimestreExercicioAnterior | decimal(14,2) | N | — | — | — |
| 7 | ValorReceitasRealizadasNoBimestre | decimal(14,2) | N | — | — | — |

## dbo.Anexo04_ReservaOrcamentariaRPPS

Tabela · ~16.952 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo04_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoOrcamentaria | decimal(14,2) | N | — | — | — |

## dbo.Anexo04_TipoCampo

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCampo | tinyint | N | PK | — | — |
| 2 | NomeTipoCampo | varchar(100) | N | — | — | — |

## dbo.Anexo04_TipoPlano

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoPlano | tinyint | N | PK | — | — |
| 2 | NomeTipoPlano | varchar(150) | N | — | — | — |

## dbo.Anexo05_Campos

Tabela · ~34 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(100) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo05_DiscriminacaoMetaFiscal

Tabela · ~388 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo05_Campos(IdCampo) | — | — |
| 3 | ValorCorrente | decimal(14,2) | N | — | — | — |

## dbo.Anexo05_DividaFiscalLiquida

Tabela · ~8.226 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo05_Campos(IdCampo) | — | — |
| 3 | ValorEm31DezembroExercicioAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorEmBimestreAnterior | decimal(14,2) | N | — | — | — |
| 5 | ValorEmBimestre | decimal(14,2) | N | — | — | — |

## dbo.Anexo05_DividaFiscalLiquidaPrevidenciaria

Tabela · ~5.320 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo05_Campos(IdCampo) | — | — |
| 3 | SaldoDividaFiscalEm31DezembroExercicioAnterior | decimal(14,2) | N | — | — | — |
| 4 | SaldoDividaFiscalEmBimestreAnterior | decimal(14,2) | N | — | — | — |
| 5 | SaldoDividaFiscalEmBimestre | decimal(14,2) | N | — | — | — |

## dbo.Anexo05_ResultadoNominal

Tabela · ~914 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo05_Campos(IdCampo) | — | — |
| 3 | ValorPeriodoReferenciaNoBimestre | decimal(14,2) | Y | — | — | — |
| 4 | ValorPeriodoReferenciaAteOBimestre | decimal(14,2) | Y | — | — | — |

## dbo.Anexo06_AjusteMetodologico

Tabela · ~56.972 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorAteoBimestre | decimal(14,2) | N | — | — | — |

## dbo.Anexo06_CalculoResultadoNominal

Tabela · ~69.137 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorSaldoExercicioAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorSaldoAteoBimestre | decimal(14,2) | N | — | — | — |
| 5 | ValorResultadoNominal | decimal(14,2) | N | — | — | — |

## dbo.Anexo06_Campos

Tabela · ~439 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | SubGrupo | tinyint | N | — | — | — |
| 6 | Descricao | varchar(200) | N | — | — | — |
| 7 | Grupo | bit | N | — | — | — |
| 8 | EsferaEstadual | bit | N | — | — | — |
| 9 | EsferaMunicipal | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo06_CumprimentoLimiteDespesasPrimariasCorrentes

Tabela · ~304 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorDespesasEmpenhadasAteoBimestreAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorDespesasEmpenhadasAteoBimestre | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasLiquidadasAteoBimestre | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasLiquidadasAteoBimestreAnterior | decimal(14,2) | N | — | — | — |
| 7 | ValorInscritasRestosAPagarNaoProcessadosAteoBimestre | decimal(14,2) | N | — | — | — |
| 8 | ValorInscritasRestosAPagarNaoProcessadosAteoBimestreAnterior | decimal(14,2) | N | — | — | — |

## dbo.Anexo06_DespesasPrimarias

Tabela · ~162.979 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 4 | ValorDespesasEmpenhadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasEmpenhadasAteoBimestreExercicioAnterior | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasLiquidadasAteoBimestreExercicio | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasLiquidadasAteoBimestreExercicioAnterior | decimal(14,2) | N | — | — | — |
| 8 | ValorDespesasPagasAteoBimestreExercicio | decimal(14,2) | Y | — | — | — |
| 9 | ValorDespesasInscritasEmRestosAPagarNaoProcessadosEmExercicio | decimal(14,2) | N | — | — | — |
| 10 | ValorDespesasInscritasEmRestosAPagarNaoProcessadosEmExercicioAnterior | decimal(14,2) | N | — | — | — |
| 11 | ValorRestosAPagarProcessadosPagos | decimal(14,2) | Y | — | — | — |
| 12 | ValorRestosAPagarNaoProcessadosLiquidados | decimal(14,2) | Y | — | — | — |
| 13 | ValorRestosAPagarNaoProcessadosPagos | decimal(14,2) | Y | — | — | — |
| 14 | ValorResultadoPrimario | decimal(14,2) | Y | — | — | — |

## dbo.Anexo06_DiscriminacaoMetaFiscal

Tabela · ~16.171 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorCorrente | decimal(14,2) | N | — | — | — |

## dbo.Anexo06_InformacoesAdicionais

Tabela · ~30.366 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoOrcamentaria | decimal(14,2) | N | — | — | — |

## dbo.Anexo06_JurosNominais

Tabela · ~20.294 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorIncorrido | decimal(14,2) | N | — | — | — |

## dbo.Anexo06_ReceitasPrimarias

Tabela · ~328.247 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo06_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 4 | ValorReceitasRealizadasAteOBimestre | decimal(14,2) | N | — | — | — |
| 5 | ValorReceitasRealizadasAteOBimestreExercicioAnterior | decimal(14,2) | N | — | — | — |

## dbo.Anexo07_Movimento

Tabela · ~54.141 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | IdPoder | smallint | N | FK → dbo.Anexo07_Poderes(IdPoder) | — | — |
| 3 | Sequencial | smallint | N | — | — | — |
| 4 | NomeOrgao | varchar(50) | N | — | — | — |
| 5 | RPProcessadosInscritosExerciciosAnteriores | decimal(14,2) | N | — | — | — |
| 6 | RPProcessadosInscritosExercicioAnterior | decimal(14,2) | N | — | — | — |
| 7 | RPProcessadosPagos | decimal(14,2) | N | — | — | — |
| 8 | RPProcessadosCancelados | decimal(14,2) | N | — | — | — |
| 9 | RPNaoProcessadosInscritosExerciciosAnteriores | decimal(14,2) | N | — | — | — |
| 10 | RPNaoProcessadosInscritosExercicioAnterior | decimal(14,2) | N | — | — | — |
| 11 | RPNaoProcessadosLiquidados | decimal(14,2) | N | — | — | — |
| 12 | RPNaoProcessadosPagos | decimal(14,2) | N | — | — | — |
| 13 | RPNaoProcessadosCancelados | decimal(14,2) | N | — | — | — |
| 14 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo07_Poderes

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPoder | smallint | N | PK | — | — |
| 2 | NomePoder | varchar(50) | N | — | — | — |

## dbo.Anexo08_Campos

Tabela · ~15 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(80) | N | — | — | — |
| 6 | IdTipoCampo | tinyint | N | FK → dbo.Anexo08_TipoCampo(IdTipoCampo) | — | — |
| 7 | Grupo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo08_Despesas

Tabela · ~13.663 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo08_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 4 | ValorDespesasEmpenhadas | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasInscritasRPNP | decimal(14,2) | N | — | — | — |

## dbo.Anexo08_Receitas

Tabela · ~2.037 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo08_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 4 | ValorReceitasRealizadas | decimal(14,2) | N | — | — | — |

## dbo.Anexo08_TipoCampo

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCampo | tinyint | N | PK | — | — |
| 2 | DescricaoTipoCampo | varchar(60) | N | — | — | — |

## dbo.Anexo09_Movimento

Tabela · ~35.714 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 3 | Exercicio | smallint | N | — | — | — |
| 4 | IdTipoPlanoPrevidenciario | tinyint | Y | FK → dbo.Anexo09_TipoPlanoPrevidenciario(IdTipoPlanoPrevidenciario) | — | — |
| 5 | ValorReceitaPrevidenciaria | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesaPrevidenciaria | decimal(14,2) | N | — | — | — |
| 7 | ValorResultadoPrevidenciario | decimal(14,2) | N | — | — | — |
| 8 | ValorSaldoFinanceiroExercicio | decimal(14,2) | N | — | — | — |

## dbo.Anexo09_TipoPlanoPrevidenciario

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoPlanoPrevidenciario | tinyint | N | PK | — | — |
| 2 | DescricaoTipoPlanoPrevidenciario | varchar(250) | N | — | — | — |

## dbo.Anexo10_Campos

Tabela · ~38 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(160) | N | — | — | — |
| 6 | IdTipoCampo | tinyint | N | FK → dbo.Anexo10_TipoCampo(IdTipoCampo) | — | — |
| 7 | Grupo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo10_Despesas

Tabela · ~14.843 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo10_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 4 | ValorDespesasEmpenhadas | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasPagas | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasInscritasRPNP | decimal(14,2) | N | — | — | — |
| 8 | ValorPagamentoRP | decimal(14,2) | N | — | — | — |
| 9 | DespesasEmpenhadasSuperiorTotalReceitas | decimal(18,0) | Y | — | — | — |

## dbo.Anexo10_Receitas

Tabela · ~9.017 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo10_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 4 | ValorReceitasRealizadas | decimal(14,2) | N | — | — | — |

## dbo.Anexo10_SaldoFinanceiro

Tabela · ~555 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo10_Campos(IdCampo) | — | — |
| 3 | ValorNoExercicioAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorNoExercicio | decimal(14,2) | N | — | — | — |

## dbo.Anexo10_TipoCampo

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCampo | tinyint | N | PK | — | — |
| 2 | DescricaoTipoCampo | varchar(50) | N | — | — | — |

## dbo.Anexo11_ApuracaoDoLimiteMinimoConstitucional

Tabela · ~5.879 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorExigido | decimal(14,2) | N | — | — | — |
| 4 | ValorAplicado | decimal(14,2) | N | — | — | — |
| 5 | PercentualAplicado | decimal(14,2) | N | — | — | — |

## dbo.Anexo11_Campos

Tabela · ~1.866 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | EsferaEstadual | bit | N | — | — | — |
| 6 | SubGrupo | tinyint | N | — | — | — |
| 7 | IdTipoCampo | int | Y | FK → dbo.Anexo11_TipoCampo(IdTipoCampo) | — | — |
| 8 | Descricao | varchar(200) | N | — | — | — |
| 9 | Grupo | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo11_CamposEnteFederacaoConsorciado

Tabela · ~47 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(150) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo11_ControleUtilizacaoRecursos

Tabela · ~14.056 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Anexo11_DeducoesEnteFederacaoConsorciado

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_CamposEnteFederacaoConsorciado(IdCampo) | — | — |
| 3 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Anexo11_DeducoesFinsLimiteConstitucional

Tabela · ~56.741 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Anexo11_DeducoesLimiteFUNDEB

Tabela · ~31.848 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Anexo11_Despesas

Tabela · ~293.206 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoAtualizada | decimal(14,2) | Y | — | — | — |
| 4 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 5 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 6 | ValorDespesasPagasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 7 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | Y | — | — | — |
| 8 | ValorDespesasInscritasRestosAPagarNaoProcessadosSemDisponibilidadeCaixa | decimal(14,2) | Y | — | — | — |
| 9 | DespesasEmpenhadasSuperiorTotalReceitas | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_DespesasAcoesTipicasMDE

Tabela · ~60.715 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoInicial | decimal(14,2) | N | — | — | — |
| 4 | ValorDotacaoAtualizada | decimal(14,2) | Y | — | — | — |
| 5 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 6 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 7 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_DespesasDoFUNDEB

Tabela · ~32.505 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoInicial | decimal(14,2) | Y | — | — | — |
| 4 | ValorDotacaoAtualizada | decimal(14,2) | Y | — | — | — |
| 5 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 6 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 7 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_DespesasEnteFederacaoConsorciado

Tabela · ~100 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_CamposEnteFederacaoConsorciado(IdCampo) | — | — |
| 3 | CNPJConsorcio | char(14) | N | — | — | — |
| 4 | NomeConsorcio | varchar(150) | N | — | — | — |
| 5 | ValorTransferido | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | N | — | — | — |
| 8 | ValorDespesasPagasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 9 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |

## dbo.Anexo11_DespesasPrecatorios

Tabela · ~2.590 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 4 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 5 | ValorDespesasPagasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 6 | ValorDespesasInscritasRestosAPagarProcessadosPagos | decimal(14,2) | Y | — | — | — |
| 7 | ValorDespesasInscritasRestosAPagarNaoProcessadosLiquidados | decimal(14,2) | Y | — | — | — |
| 8 | ValorDespesasInscritasRestosAPagarNaoProcessadosPagos | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_FluxoFinanceiroRecursosFUNDEB

Tabela · ~96.266 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | Valor | decimal(14,2) | Y | — | — | — |
| 4 | ValorSalarioEducacao | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_IndicadoresAplicacaoSuperavitExercicioAnterior

Tabela · ~18.131 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorSuperavitPermitidoExercicioAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorNaoAplicadoExercicioAnterior | decimal(14,2) | N | — | — | — |
| 5 | ValorSuperavitAplicadoAtePrimeiroQuadrimestre | decimal(14,2) | N | — | — | — |
| 6 | ValorAplicadoAtePrimeiroQuadrimestre | decimal(14,2) | N | — | — | — |
| 7 | ValorAplicadoAposPrimeiroQuadrimestre | decimal(14,2) | N | — | — | — |
| 8 | ValorNaoAplicado | decimal(14,2) | N | — | — | — |
| 9 | ValorSuperavitPermitidoExercicioAnteriorNaoAplicado | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_IndicadoresConstituicaoFederal

Tabela · ~18.510 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorExigido | decimal(14,2) | N | — | — | — |
| 4 | ValorAplicado | decimal(14,2) | N | — | — | — |
| 5 | ValorConsideradoAposDeducoes | decimal(14,2) | N | — | — | — |
| 6 | PercentualAplicado | decimal(14,2) | N | — | — | — |
| 7 | ValorNaoAplicadoExcedenteMaximoPermitido | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_IndicadoresFUNDEB

Tabela · ~18.212 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | Valor | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_IndicadoresMaximoDeSuperavit

Tabela · ~5.931 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorMaximoPermitido | decimal(14,2) | N | — | — | — |
| 4 | ValorNaoAplicado | decimal(14,2) | N | — | — | — |
| 5 | ValorNaoAplicadoAposAjuste | decimal(14,2) | N | — | — | — |
| 6 | PercentualNaoAplicado | decimal(14,2) | N | — | — | — |
| 7 | ValorNaoAplicadoExcedenteMaximoPermitido | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_InformacaoComplementarSIOPE

Tabela · ~54 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdInformacaoComplementarSIOPE | tinyint | N | PK, IDENT | — | — |
| 2 | CodigoInformacaoComplementarSIOPE | varchar(10) | N | — | — | — |
| 3 | DescricaoInformacaoComplementarSIOPE | varchar(250) | N | — | — | — |

## dbo.Anexo11_MapeamentoSIOPE

Tabela · ~116 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMapeamentoSIOPE | int | N | PK, IDENT | — | — |
| 2 | IdCampo | smallint | N | FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | LinhaSIOPE | varchar(10) | N | — | — | — |
| 4 | IdInformacaoComplementarSIOPE | tinyint | Y | FK → dbo.Anexo11_InformacaoComplementarSIOPE(IdInformacaoComplementarSIOPE) | — | — |

## dbo.Anexo11_OutrasDespesasFinanciamentoEnsino

Tabela · ~42.003 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoInicial | decimal(14,2) | Y | — | — | — |
| 4 | ValorDotacaoAtualizada | decimal(14,2) | Y | — | — | — |
| 5 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 6 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 7 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_Receitas

Tabela · ~270.366 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoAtualizada | decimal(14,2) | Y | — | — | — |
| 4 | ValorReceitasRealizadasAteOBimestre | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_ReceitasAcoesTipicasMDE

Tabela · ~8.075 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoInicial | decimal(14,2) | Y | — | — | — |
| 4 | ValorPrevisaoAtualizada | decimal(14,2) | Y | — | — | — |
| 5 | ValorReceitasRealizadasAteOBimestre | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_ReceitasdoEnsino

Tabela · ~235.418 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoInicial | decimal(14,2) | Y | — | — | — |
| 4 | ValorPrevisaoAtualizada | decimal(14,2) | Y | — | — | — |
| 5 | ValorReceitasRealizadasAteOBimestre | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_ReceitasPrecatorios

Tabela · ~1.480 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | ValorSaldoExercicioAnterior | decimal(14,2) | Y | — | — | — |
| 4 | ValorReceitasRealizadasAteOBimestre | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_RecursosRecebidosExerciciosAnterioresNaoUtilizados

Tabela · ~50.147 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Anexo11_RestosAPagarInscritosRecursosImpostosVinculadosAoEnsino

Tabela · ~38.090 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo11_Campos(IdCampo) | — | — |
| 3 | SaldoInicial | decimal(14,2) | Y | — | — | — |
| 4 | RestosAPagarLiquidados | decimal(14,2) | Y | — | — | — |
| 5 | RestosAPagarPagos | decimal(14,2) | Y | — | — | — |
| 6 | RestosAPagarCancelados | decimal(14,2) | Y | — | — | — |
| 7 | SaldoFinal | decimal(14,2) | Y | — | — | — |
| 8 | SaldoAteoBimestre | decimal(14,2) | Y | — | — | — |
| 9 | ValorCanceladoEmExercicio | decimal(14,2) | Y | — | — | — |

## dbo.Anexo11_TipoCampo

Tabela · ~20 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCampo | int | N | PK | — | — |
| 2 | DescricaoTipoCampo | varchar(200) | N | — | — | — |

## dbo.Anexo12_Campos

Tabela · ~352 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | IdGrupoCampo | tinyint | N | FK → dbo.Anexo12_GrupoCampos(IdGrupoCampo) | — | — |
| 3 | AnoReferenciaInicial | smallint | N | — | — | — |
| 4 | AnoReferenciaFinal | smallint | N | — | — | — |
| 5 | Campo | tinyint | N | — | — | — |
| 6 | EsferaEstadual | bit | N | — | — | — |
| 7 | SubGrupo | tinyint | N | — | — | — |
| 8 | Descricao | varchar(500) | Y | — | — | — |
| 9 | Grupo | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo12_CamposEnteFederacaoConsorciado

Tabela · ~26 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(150) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo12_ControleExecucaoRestosAPagar

Tabela · ~58.208 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdControleExecucaoRestosAPagar | int | N | PK, IDENT | — | — |
| 2 | IdCampo | smallint | Y | FK → dbo.Anexo12_Campos(IdCampo) | — | — |
| 3 | IdGrupoCampo | tinyint | N | FK → dbo.Anexo12_GrupoCampos(IdGrupoCampo) | — | — |
| 4 | Descricao | varchar(200) | N | — | — | — |
| 5 | ValorMinimoAplicacaoEmASPS | decimal(14,2) | N | — | — | — |
| 6 | ValorAplicadoEmASPSNoExercicio | decimal(14,2) | N | — | — | — |
| 7 | ValorInscritoEmRPConsideradoLimite | decimal(14,2) | N | — | — | — |
| 8 | ValorAplicadoAlemLimiteMinimo | decimal(14,2) | N | — | — | — |
| 9 | ValorTotalInscritoEmRPNoExercicio | decimal(14,2) | N | — | — | — |
| 10 | RPNPInscritosSemDisponibilidade | decimal(14,2) | Y | — | — | — |
| 11 | ValorTotalDeRPPagos | decimal(14,2) | N | — | — | — |
| 12 | ValorTotalDeRPAPagar | decimal(14,2) | N | — | — | — |
| 13 | ValorTotalDeRPCancelados | decimal(14,2) | N | — | — | — |
| 14 | ValorTotalDaCompensacaoDeRPCancelados | decimal(14,2) | N | — | — | — |
| 15 | SaldoValorAplicado | decimal(14,2) | N | — | — | — |
| 16 | TotalRestosPagarCanceladosPrescritos | decimal(14,2) | Y | — | — | — |
| 17 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo12_Controles

Tabela · ~125.439 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdControle | int | N | PK, IDENT | — | — |
| 2 | IdGrupoCampo | tinyint | N | FK → dbo.Anexo12_GrupoCampos(IdGrupoCampo) | — | — |
| 3 | Descricao | varchar(200) | Y | — | — | — |
| 4 | ValorSaldoInicial | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasCusteadasExercicioReferencia | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasCusteadasLiquidadas | decimal(14,2) | Y | — | — | — |
| 7 | ValorDespesasCusteadasPagas | decimal(14,2) | Y | — | — | — |
| 8 | ValorSaldoFinalNaoAplicado | decimal(14,2) | N | — | — | — |
| 9 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo12_DespesaPercentualAplicacao

Tabela · ~4.415 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo12_Campos(IdCampo) | — | — |
| 3 | PercentualAplicacao | decimal(5,2) | Y | — | — | — |

## dbo.Anexo12_Despesas

Tabela · ~590.686 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo12_Campos(IdCampo) | — | — |
| 3 | ValorDotacaoInicial | decimal(14,2) | N | — | — | — |
| 4 | ValorDotacaoAtualizada | decimal(14,2) | N | — | — | — |
| 5 | ValorTransferidoContratoRateio | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | N | — | — | — |
| 8 | ValorDespesasPagasAteOBimestre | decimal(14,2) | Y | — | — | — |
| 9 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |

## dbo.Anexo12_DespesasEnteFederacaoConsorciado

Tabela · ~26 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo12_CamposEnteFederacaoConsorciado(IdCampo) | — | — |
| 3 | CNPJConsorcio | char(14) | N | — | — | — |
| 4 | NomeConsorcio | varchar(150) | N | — | — | — |
| 5 | ValorTransferido | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasEmpenhadasAteOBimestre | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasLiquidadasAteOBimestre | decimal(14,2) | N | — | — | — |
| 8 | ValorDespesasPagasAteOBimestre | decimal(14,2) | N | — | — | — |
| 9 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |

## dbo.Anexo12_DespesaValorExecutadoLimiteMinimo

Tabela · ~12.961 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo12_Campos(IdCampo) | — | — |
| 3 | ValorExecutadoLimiteMinimo | decimal(14,2) | Y | — | — | — |

## dbo.Anexo12_ExecucaoRestosAPagar

Tabela · ~33.645 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdExecucaoRestosAPagar | int | N | PK, IDENT | — | — |
| 2 | IdGrupoCampo | tinyint | N | FK → dbo.Anexo12_GrupoCampos(IdGrupoCampo) | — | — |
| 3 | Descricao | varchar(255) | Y | — | — | — |
| 4 | ValorRestosAPagarInscritos | decimal(14,2) | N | — | — | — |
| 5 | ValorRestosAPagarCanceladosPrescritos | decimal(14,2) | N | — | — | — |
| 6 | ValorRestosAPagarPagos | decimal(14,2) | N | — | — | — |
| 7 | ValorRestosAPagarAPagar | decimal(14,2) | N | — | — | — |
| 8 | ValorRestosAPagarParcelaConsideradoNoLimite | decimal(14,2) | N | — | — | — |
| 9 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo12_GrupoCampos

Tabela · ~22 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoCampo | tinyint | N | PK | — | — |
| 2 | Descricao | varchar(200) | N | — | — | — |

## dbo.Anexo12_Receitas

Tabela · ~307.750 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo12_Campos(IdCampo) | — | — |
| 3 | ValorPrevisaoInicial | decimal(14,2) | N | — | — | — |
| 4 | ValorPrevisaoAtualizada | decimal(14,2) | N | — | — | — |
| 5 | ValorReceitasRealizadasAteOBimestre | decimal(14,2) | N | — | — | — |

## dbo.Anexo13_Aditivos

Tabela · ~90.375 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAditivo | int | N | PK, IDENT | — | — |
| 2 | IdContrato | int | N | FK → dbo.Anexo13_Contratos(IdContrato) | — | — |
| 3 | NumeroTermo | varchar(16) | N | — | — | — |
| 4 | AnoTermo | smallint | Y | — | — | — |
| 5 | Objetivo | varchar(150) | Y | — | — | — |
| 6 | IdBaseLegal | smallint | N | FK → dbo.Anexo13_BaseLegal(IdBaseLegal) | — | — |
| 7 | ValorAditivo | decimal(14,2) | Y | — | — | — |
| 8 | DataInicioVigencia | date | Y | — | — | — |
| 9 | DataTerminoVigencia | date | Y | — | — | — |
| 10 | DataDataAssinatura | date | Y | — | — | — |
| 11 | DataDataPublicacao | date | Y | — | — | — |
| 12 | JustificativaAditivo | varchar(450) | Y | — | — | — |
| 13 | NomeArquivoAditivo | varchar(200) | Y | — | — | — |
| 14 | HashArquivoAditivo | char(32) | Y | — | — | — |
| 15 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 16 | DataInclusao | smalldatetime | N | — | — | — |
| 17 | IdSessao | int | Y | — | — | — |
| 18 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_BaseLegal

Tabela · ~134 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdBaseLegal | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | DescricaoBaseLegal | varchar(100) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo13_ContratoFestividade

Tabela · ~11.872 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContratoFestividade | int | N | PK, IDENT | — | — |
| 2 | IdContrato | int | N | FK → dbo.Anexo13_Contratos(IdContrato) | — | — |
| 3 | IdTipoNaturezaFestividade | tinyint | Y | FK → dbo.Anexo13_TipoNaturezaFestividade(IdTipoNaturezaFestividade) | — | — |
| 4 | OutraDescricaoTipoNaturezaFestividade | varchar(100) | Y | — | — | — |
| 5 | DenominacaoFestividade | varchar(100) | Y | — | — | — |
| 6 | IdTipoServicoContratado | tinyint | Y | FK → dbo.Anexo13_TipoServicoContratado(IdTipoServicoContratado) | — | — |
| 7 | DenominacaoAtracaoArtisticaContratada | varchar(200) | Y | — | — | — |
| 8 | NomeFiscalAtracaoArtisticaContratada | varchar(200) | Y | — | — | — |
| 9 | IdTipoPessoaAtracaoArtisticaContratada | tinyint | Y | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 10 | CpfCnpjAtracaoArtisticaContratada | varchar(14) | Y | — | — | — |
| 11 | NomeRepresentanteLegalAtracaoArtistica | varchar(200) | Y | — | — | — |
| 12 | IdTipoPessoaRepresentanteLegalAtracaoArtistica | tinyint | Y | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 13 | CpfCnpjRepresentanteLegalAtracaoArtistica | varchar(14) | Y | — | — | — |
| 14 | DataApresentacaoAtracaoArtistica | date | Y | — | — | — |
| 15 | HoraApresentacaoAtracaoArtistica | varchar(5) | Y | — | — | — |
| 16 | DuracaoApresentacaoArtistica | varchar(5) | Y | — | — | — |
| 17 | DataInclusao | smalldatetime | N | — | — | — |
| 18 | IdSessao | int | N | — | — | — |
| 19 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_Contratos

Tabela · ~207.327 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContrato | int | N | PK, FK → dbo.Anexo13_Contratos(IdContrato), IDENT | — | — |
| 2 | NumeroProcessoDespesa | varchar(24) | Y | — | — | — |
| 3 | IdProcessoDespesa | int | Y | FK → dbo.Anexo13_ProcessoDespesa(IdProcessoDespesa) | — | — |
| 4 | ReciboAnexo38 | int | Y | — | — | — |
| 5 | NumeroContrato | varchar(30) | N | — | — | — |
| 6 | AnoContrato | smallint | Y | — | — | — |
| 7 | ValorContrato | decimal(14,2) | N | — | — | — |
| 8 | DataInicioVigencia | date | Y | — | — | — |
| 9 | DataTerminoVigencia | date | Y | — | — | — |
| 10 | DataDataAssinatura | date | N | — | — | — |
| 11 | DataDataPublicacao | date | Y | — | — | — |
| 12 | IdTipoDocumentoContratado | tinyint | Y | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 13 | CPFCNPJContratado | varchar(14) | Y | — | — | — |
| 14 | NomeContratado | varchar(150) | Y | — | — | — |
| 15 | PrazoMaximoLiquidacao | smallint | Y | — | — | — |
| 16 | PrazoMaximoPagamento | smallint | Y | — | — | — |
| 17 | MotivoNaoEscolhaPrimeiroColocado | varchar(450) | Y | — | — | — |
| 18 | JustificativaContrato | varchar(450) | Y | — | — | — |
| 19 | ObjetoContrato | varchar(500) | Y | — | — | — |
| 20 | NomeArquivoContrato | varchar(200) | Y | — | — | — |
| 21 | HashArquivoContrato | char(32) | Y | — | — | — |
| 22 | Ativo | bit | N | — | — | — |
| 23 | OrdemServicoPrevistaNoContrato | bit | N | — | — | — |
| 24 | ServicoNaturezaContinuada | bit | N | — | — | — |
| 25 | IdContratoLegado | int | Y | — | — | — |
| 26 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 27 | ContratacaoAssociadaFestividade | bit | N | — | — | — |
| 28 | DataInclusao | smalldatetime | Y | — | — | — |
| 29 | IdSessao | int | Y | — | — | — |
| 30 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_FiscalContrato

Tabela · ~54.750 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFiscalContrato | int | N | PK, IDENT | — | — |
| 2 | IdContrato | int | N | FK → dbo.Anexo13_Contratos(IdContrato) | — | — |
| 3 | CpfFsicalContrato | char(11) | N | — | — | — |
| 4 | NomeFiscalContrato | varchar(150) | N | — | — | — |
| 5 | DataInicioVigencia | date | N | — | — | — |
| 6 | DataTerminoVigencia | date | Y | — | — | — |
| 7 | NomeArquivoDesignacao | varchar(500) | N | — | — | — |
| 8 | HashArquivoDesignacao | char(32) | N | — | — | — |
| 9 | Ativo | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_LoteLicitacaoPublicaContrato

Tabela · ~94.500 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContrato | int | N | PK, FK → dbo.Anexo13_Contratos(IdContrato) | — | — |
| 2 | IdLoteLicitacaoPublica | int | N | PK, FK → dbo.Anexo38_ResultadoLicitacaoPublicaLoteParticipante(IdLoteParticipanteClassificado) | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | IdSessao | int | N | — | — | — |
| 5 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_OrdemServico

Tabela · ~2.000 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrdemServico | int | N | PK, IDENT | — | — |
| 2 | IdContrato | int | N | FK → dbo.Anexo13_Contratos(IdContrato) | — | — |
| 3 | NumeroOrdemServico | varchar(20) | N | — | — | — |
| 4 | AnoOrdemServico | smallint | N | — | — | — |
| 5 | DescricaoOrdemServico | varchar(500) | N | — | — | — |
| 6 | PrazoExecucaoDias | int | N | — | — | — |
| 7 | DataInicioExecucao | date | N | — | — | — |
| 8 | DataTerminoExecucao | date | N | — | — | — |
| 9 | NomeArquivo | varchar(500) | N | — | — | — |
| 10 | HashArquivo | char(32) | N | — | — | — |
| 11 | Ativo | bit | N | — | — | — |
| 12 | DataInclusao | smalldatetime | N | — | — | — |
| 13 | IdSessao | int | N | — | — | — |
| 14 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_ProcessoDespesa

Tabela · ~132.153 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProcessoDespesa | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | IdUnidadeGestora | int | Y | FK → dbo.Anexo42_UnidadeJurisdicionada(IdUnidadeJurisdicionada) | — | — |
| 4 | NumeroProcessoDespesa | varchar(30) | N | — | — | — |
| 5 | AnoProcessoDespesa | smallint | N | — | — | — |
| 6 | Ativo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | DataAtualizacao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_ProrrogacoesContratuais

Tabela · ~1.279 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProrrogacao | int | N | PK, IDENT | — | — |
| 2 | IdContrato | int | N | FK → dbo.Anexo13_Contratos(IdContrato) | — | — |
| 3 | NovoPrazo | date | N | — | — | — |
| 4 | NovoValor | decimal(14,2) | N | — | — | — |
| 5 | Ativo | bit | N | — | — | — |
| 6 | NomeArquivoProrrogacao | varchar(250) | Y | — | — | — |
| 7 | HashArquivoProrrogacao | char(32) | Y | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_TipoAditamento

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAditamento | tinyint | N | PK | — | — |
| 2 | NomeTipoAditamento | varchar(50) | N | — | — | — |

## dbo.Anexo13_TipoAditamentoAditivo

Tabela · ~60.700 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAditivo | int | N | PK, FK → dbo.Anexo13_Aditivos(IdAditivo) | — | — |
| 2 | IdTipoAditamento | tinyint | N | PK, FK → dbo.Anexo13_TipoAditamento(IdTipoAditamento) | — | — |
| 3 | Dotacao | varchar(50) | Y | — | — | — |
| 4 | PrazoExecucao | date | Y | — | — | — |
| 5 | PrazoVigencia | date | Y | — | — | — |
| 6 | AcrescimoValor | decimal(14,2) | Y | — | — | — |
| 7 | SupressaoValor | decimal(14,2) | Y | — | — | — |
| 8 | OutrasClausulas | varchar(500) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo13_TipoNaturezaFestividade

Tabela · ~11 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoNaturezaFestividade | tinyint | N | PK, IDENT | — | — |
| 2 | DescricaoTipoNaturezaFestividade | varchar(50) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |

## dbo.Anexo13_TipoServicoContratado

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoServicoContratado | tinyint | N | PK, IDENT | — | — |
| 2 | DescricaoTipoServicoContratado | varchar(200) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |

## dbo.Anexo14_AnulacaoEmpenho

Tabela · ~1.132.577 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnulacaoEmpenho | int | N | PK, IDENT | — | — |
| 2 | IdEmpenho | int | N | FK → dbo.Anexo14_Empenho(IdEmpenho) | — | — |
| 3 | DataAnulacaoEmpenho | date | N | — | — | — |
| 4 | ValorAnuladoEmpenho | decimal(14,2) | N | — | — | — |
| 5 | MotivoAnulacaoEmpenho | varchar(2000) | Y | — | — | — |
| 6 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 7 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |
| 8 | NotaAnulacao | varchar(50) | Y | — | — | — |

## dbo.Anexo14_AnulacaoLiquidacao

Tabela · ~518.420 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnulacaoLiquidacao | int | N | PK, IDENT | — | — |
| 2 | IdLiquidacao | int | N | FK → dbo.Anexo14_Liquidacao(IdLiquidacao) | — | — |
| 3 | DataAnulacaoLiquidacao | date | N | — | — | — |
| 4 | ValorAnuladoLiquidacao | decimal(14,2) | N | — | — | — |
| 5 | MotivoAnulacaoLiquidacao | varchar(2000) | Y | — | — | — |
| 6 | NotaAnulacao | varchar(50) | Y | — | — | — |
| 7 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 8 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_AnulacaoPagamento

Tabela · ~67.559 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnulacaoPagamento | int | N | PK, IDENT | — | — |
| 2 | IdPagamento | int | N | FK → dbo.Anexo14_Pagamento(IdPagamento) | — | — |
| 3 | DataAnulacaoPagamento | date | N | — | — | — |
| 4 | ValorAnuladoPagamento | decimal(14,2) | N | — | — | — |
| 5 | MotivoAnulacaoPagamento | varchar(2000) | Y | — | — | — |
| 6 | NotaAnulacao | varchar(50) | Y | — | — | — |
| 7 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 8 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_AnulacaoRetencao

Tabela · ~27.243 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnulacaoRetencao | int | N | PK, IDENT | — | — |
| 2 | IdRetencao | int | N | FK → dbo.Anexo14_Retencao(IdRetencao) | — | — |
| 3 | DataAnulacaoRetencao | date | N | — | — | — |
| 4 | ValorAnuladoRetencao | decimal(14,2) | N | — | — | — |
| 5 | MotivoAnulacaoRetencao | varchar(2000) | Y | — | — | — |
| 6 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 7 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_CategoriaContrato

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCategoriaContrato | tinyint | N | PK | — | — |
| 2 | DescricaoCategoriaContrato | varchar(100) | N | — | — | — |

## dbo.Anexo14_Empenho

Tabela · ~15.060.712 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEmpenho | int | N | PK, IDENT | — | — |
| 2 | IdTipoProcedimentoLicitatorio | tinyint | Y | FK → dbo.Anexo14_TipoProcedimentoLicitatorio(IdTipoProcedimentoLicitatorio) | — | 09Nov16 - Set NULL   Imposi��o do coleta; |
| 3 | IdUnidadeInstitucional | int | Y | FK → dbo.Anexo01_UnidadeInstitucional(IdUnidadeInstitucional) | — | — |
| 4 | IdDespesaFuncionalFuncao | tinyint | Y | FK → dbo.Anexo01_DespesaFuncionalFuncao(IdDespesaFuncionalFuncao) | — | — |
| 5 | IdDespesaFuncionalSubFuncao | tinyint | Y | FK → dbo.Anexo01_DespesaFuncionalSubFuncao(IdDespesaFuncionalSubFuncao) | — | — |
| 6 | IdDespesaCategoriaEconomica | tinyint | Y | FK → dbo.Anexo01_DespesaCategoriaEconomica(IdDespesaCategoriaEconomica) | — | — |
| 7 | IdDespesaGrupoDespesa | tinyint | Y | FK → dbo.Anexo01_DespesaGrupoDespesa(IdDespesaGrupoDespesa) | — | — |
| 8 | IdDespesaModalidadeAplicacao | tinyint | Y | FK → dbo.Anexo01_DespesaModalidadeAplicacao(IdDespesaModalidadeAplicacao) | — | — |
| 9 | IdDespesaElementoDespesa | tinyint | Y | FK → dbo.Anexo01_DespesaElementoDespesa(IdDespesaElementoDespesa) | — | — |
| 10 | IdDespesaDesdobramentoDespesa | smallint | Y | FK → dbo.Anexo01_DespesaDesdobramentoDespesa(IdDespesaDesdobramentoDespesa) | — | — |
| 11 | IdInstrumentoProgramacao | int | Y | FK → dbo.Anexo01_InstrumentoProgramacao(IdInstrumentoProgramacao) | — | — |
| 12 | IdTipoEmpenho | tinyint | Y | FK → dbo.Anexo14_TipoEmpenho(IdTipoEmpenho) | — | 08Dez16 - Set NULL   Imposi��o do coleta; |
| 13 | IdResponsavelOrdenador | int | Y | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 14 | IdFonteRecurso | int | Y | FK → dbo.Anexo01_Fontes(IdFonteRecurso) | — | — |
| 15 | IdTipoRecursoVinculado | tinyint | Y | FK → dbo.Anexo14_TipoRecursoVinculado(IdTipoRecursoVinculado) | — | — |
| 16 | IdCategoriaContrato | tinyint | Y | FK → dbo.Anexo14_CategoriaContrato(IdCategoriaContrato) | — | — |
| 17 | NumeroProcessoDespesa | varchar(90) | Y | — | — | 08Dez16 - Set NULL   Imposi��o do coleta; |
| 18 | ReciboAnexo38 | int | Y | — | — | — |
| 19 | ReciboAnexo23 | int | Y | — | — | — |
| 20 | ReciboSiaiObras | int | Y | — | — | — |
| 21 | DataProcedimentoLicitatorio | date | Y | — | — | — |
| 22 | NotaEmpenho | varchar(15) | Y | — | — | — |
| 23 | DataEmpenho | date | N | — | — | — |
| 24 | ValorEmpenho | decimal(14,2) | N | — | — | — |
| 25 | IdTipoDocumentoCredor | tinyint | Y | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 26 | CPFCNPJCredor | varchar(14) | Y | — | — | — |
| 27 | NomeCredor | varchar(300) | Y | — | — | — |
| 28 | Justificativa | varchar(500) | Y | — | — | — |
| 29 | PrazoMaximoLiquidacao | smallint | Y | — | — | — |
| 30 | PrazoMaximoPagamento | smallint | Y | — | — | — |
| 31 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 32 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_EmpenhoReforco

Tabela · ~237.326 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEmpenhoReforco | int | N | PK, IDENT | — | — |
| 2 | IdEmpenho | int | N | FK → dbo.Anexo14_Empenho(IdEmpenho) | — | — |
| 3 | IdUnidadeInstitucional | int | N | FK → dbo.Anexo01_UnidadeInstitucional(IdUnidadeInstitucional) | — | — |
| 4 | NotaEmpenhoReforco | varchar(15) | N | — | — | — |
| 5 | DataEmpenhoReforco | date | N | — | — | — |
| 6 | ValorEmpenhoReforco | decimal(14,2) | N | — | — | — |
| 7 | JustificativaReforco | varchar(500) | Y | — | — | — |
| 8 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 9 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_EmpenhoValorMinimoObraObrigatorio

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEmpenhoValorMinimoObra | int | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | ValorMinimoEmpenho | decimal(14,2) | N | — | — | — |

## dbo.Anexo14_Liquidacao

Tabela · ~26.114.698 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLiquidacao | int | N | PK, IDENT | — | — |
| 2 | IdEmpenho | int | N | FK → dbo.Anexo14_Empenho(IdEmpenho) | — | — |
| 3 | IdTipoDocumentoFiscal | tinyint | Y | FK → dbo.Anexo14_TipoDocumentoFiscal(IdTipoDocumentoFiscal) | — | — |
| 4 | NumeroProcessoPagamento | varchar(90) | Y | — | — | — |
| 5 | NumeroDocumentoFiscal | varchar(50) | Y | — | — | — |
| 6 | NumeroSerieDocumentoFiscal | char(3) | Y | — | — | — |
| 7 | DataEmissaoDocumentoFiscal | date | Y | — | — | — |
| 8 | NumeroChaveNFE | char(44) | Y | — | — | — |
| 9 | ValorFaturado | decimal(14,2) | Y | — | — | — |
| 10 | NumeroDocumentoLiquidacao | varchar(50) | Y | — | — | — |
| 11 | DataRecebimentoNotaFiscal | date | Y | — | — | — |
| 12 | DataAtestoNotaFiscal | date | Y | — | — | — |
| 13 | DataLiquidacao | date | Y | — | — | — |
| 14 | ValorLiquidacao | decimal(14,2) | N | — | — | — |
| 15 | IdTipoDocumentoCredor | tinyint | Y | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 16 | CPFCNPJCredor | varchar(14) | Y | — | — | — |
| 17 | NomeCredor | varchar(300) | Y | — | — | — |
| 18 | CPFLiquidante | char(11) | Y | — | — | — |
| 19 | NomeLiquidante | varchar(300) | Y | — | — | — |
| 20 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 21 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_LiquidacaoNotaFiscal

Tabela · ~27.432.801 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLiquidacaoNotaFiscal | int | N | PK, IDENT | — | — |
| 2 | IdLiquidacao | int | N | — | — | — |
| 3 | IdTipoDocumentoFiscal | tinyint | Y | — | — | — |
| 4 | NumeroDocumentoFiscal | varchar(50) | Y | — | — | — |
| 5 | NumeroSerieDocumentoFiscal | char(10) | Y | — | — | — |
| 6 | DataEmissaoDocumentoFiscal | date | Y | — | — | — |
| 7 | NumeroChaveNFE | char(44) | Y | — | — | — |
| 8 | ValorFaturado | decimal(14,2) | Y | — | — | — |
| 9 | DataRecebimentoNotaFiscal | date | Y | — | — | — |
| 10 | DataAtestoNotaFiscal | date | Y | — | — | — |
| 11 | IdArquivoLRF | int | Y | — | — | — |
| 12 | IdArquivoXML | int | Y | — | — | — |

## dbo.Anexo14_Pagamento

Tabela · ~30.953.437 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPagamento | int | N | PK, IDENT | — | — |
| 2 | IdLiquidacao | int | Y | FK → dbo.Anexo14_Liquidacao(IdLiquidacao) | — | — |
| 3 | IdContaBancaria | int | N | FK → dbo.Anexo26_ContaBancaria(IdContaBancaria) | — | — |
| 4 | IdTipoDocumentoPagamento | tinyint | N | FK → dbo.Anexo14_TipoDocumentoPagamento(IdTipoDocumentoPagamento) | — | — |
| 5 | NumeroDocumentoPagamento | varchar(90) | Y | — | — | — |
| 6 | DataPagamento | date | N | — | — | — |
| 7 | ValorPagamento | decimal(14,2) | N | — | — | — |
| 8 | IdTipoDocumentoCredor | tinyint | N | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 9 | CPFOrdenadorDespesa | char(11) | Y | — | — | — |
| 10 | NomeOrdenadorDespesa | varchar(300) | Y | — | — | — |
| 11 | CPFCNPJCredor | varchar(14) | N | — | — | — |
| 12 | NomeCredor | varchar(300) | N | — | — | — |
| 13 | IdTipoRetencao | tinyint | Y | FK → dbo.Anexo14_TipoRetencao(IdTipoRetencao) | — | — |
| 14 | DataEfetivaTransferencia | date | Y | — | — | — |
| 15 | JustificativaQuebraDaOrdem | varchar(500) | Y | — | — | — |
| 16 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 17 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_Retencao

Tabela · ~10.341.814 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRetencao | int | N | PK, IDENT | — | — |
| 2 | IdLiquidacao | int | Y | FK → dbo.Anexo14_Liquidacao(IdLiquidacao) | — | — |
| 3 | IdPagamento | int | Y | FK → dbo.Anexo14_Pagamento(IdPagamento) | — | — |
| 4 | NumeroDocumentoRetencao | varchar(30) | Y | — | — | — |
| 5 | ValorRetencao | decimal(14,2) | N | — | — | — |
| 6 | IdTipoRetencao | tinyint | N | FK → dbo.Anexo14_TipoRetencao(IdTipoRetencao) | — | — |
| 7 | IdTipoDocumentoRetentor | tinyint | N | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 8 | DataRetencao | date | Y | — | — | — |
| 9 | CPFCNPJRetentor | varchar(14) | N | — | — | — |
| 10 | NomeRetentor | varchar(300) | N | — | — | — |
| 11 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 12 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Anexo14_TipoDocumento

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumento | tinyint | N | PK | — | — |
| 2 | DescricaoTipoDocumento | varchar(50) | N | — | — | — |

## dbo.Anexo14_TipoDocumentoFiscal

Tabela · ~42 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumentoFiscal | tinyint | N | PK | — | — |
| 2 | CodigoDocumentoFiscal | char(3) | N | — | — | — |
| 3 | SiglaDocumentoFiscal | varchar(50) | N | — | — | — |
| 4 | DescricaoDocumentoFiscal | varchar(120) | N | — | — | — |
| 5 | ModeloDocumentoFiscal | varchar(50) | Y | — | — | — |

## dbo.Anexo14_TipoDocumentoPagamento

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumentoPagamento | tinyint | N | PK | — | — |
| 2 | CodigoTipoDocumentoPagamento | char(3) | N | — | — | — |
| 3 | NomeTipoDocumentoPagamento | varchar(20) | N | — | — | — |

## dbo.Anexo14_TipoEmpenho

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoEmpenho | tinyint | N | PK | — | — |
| 2 | CodigoEmpenho | char(1) | N | — | — | — |
| 3 | DescricaoEmpenho | varchar(20) | N | — | — | — |

## dbo.Anexo14_TipoProcedimentoLicitatorio

Tabela · ~50 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoProcedimentoLicitatorio | tinyint | N | PK | — | — |
| 2 | DescricaoTipoProcedimentoLicitatorio | varchar(50) | N | — | — | — |
| 3 | EntregaLicitacaoDispensaInexigibilidade | bit | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo14_TipoRecursoVinculado

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoRecursoVinculado | tinyint | N | PK | — | — |
| 2 | CodigoRecursoVinculado | char(4) | N | — | — | — |
| 3 | DescricaoRecursoVinculado | varchar(100) | N | — | — | — |

## dbo.Anexo14_TipoRetencao

Tabela · ~43 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoRetencao | tinyint | N | PK | — | — |
| 2 | CodigoTipoRetencao | char(3) | N | — | — | — |
| 3 | DescricaoTipoRetencao | varchar(100) | N | — | — | — |

## dbo.Anexo14_UgPermitidaEstado

Tabela · ~199 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdUgPermitidaEstado | int | N | PK, IDENT | — | — |
| 2 | CodigoUgPermitidaEstado | char(12) | N | — | — | — |
| 3 | DescricaoUgPermitidaEstado | varchar(100) | N | — | — | — |

## dbo.Anexo15_CampoLimite

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampoLimite | smallint | N | PK | — | — |
| 2 | IdCampoEnteFederacao | smallint | N | FK → dbo.Anexo15_CamposEnteFederacao(IdCampo) | — | — |
| 3 | Ordem | tinyint | N | — | — | — |
| 4 | AnoExercicioInicial | smallint | N | — | — | — |
| 5 | AnoExercicioFinal | smallint | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo15_CamposConsorcioPublico

Tabela · ~76 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(200) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 8 | DespesaBrutaPessoal | bit | N | — | — | — |
| 9 | DespesaTotalPessoal | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo15_CamposDefensoriaPublica

Tabela · ~100 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(200) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 8 | DespesaBrutaPessoal | bit | N | — | — | — |
| 9 | DespesaTotalPessoal | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo15_CamposEnteFederacao

Tabela · ~162 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(200) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 8 | ReceitaCorrenteLiquidaAjustada | bit | N | — | — | — |
| 9 | DespesaBrutaPessoal | bit | N | — | — | — |
| 10 | DespesaTotalPessoal | bit | N | — | — | — |
| 11 | DataInclusao | smalldatetime | N | — | — | — |
| 12 | IdSessao | int | N | — | — | — |
| 13 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo15_CamposEnteFederacaoConsorciado

Tabela · ~64 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(200) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 8 | DespesaBrutaPessoal | bit | N | — | — | — |
| 9 | DespesaTotalPessoal | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo15_CumprimentoLimiteLegal

Tabela · ~87.400 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo15_CamposEnteFederacao(IdCampo) | — | — |
| 3 | ValorDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 4 | PercentualSobreRCL | decimal(5,2) | N | — | — | — |

## dbo.Anexo15_LimitesLegais

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLimite | tinyint | N | PK | — | — |
| 2 | IdOrgaoNatureza | tinyint | N | — | — | — |
| 3 | PercentualLimiteMaximo | decimal(5,2) | N | — | — | — |
| 4 | PercentualLimitePrudencial | decimal(5,2) | N | — | — | — |
| 5 | PercentualLimiteAlerta | decimal(5,2) | N | — | — | — |
| 6 | AnoExercicioInicial | smallint | N | — | — | — |
| 7 | AnoExercicioFinal | smallint | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo15_MovimentoConsorcioPublico

Tabela · ~1.777 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo15_CamposConsorcioPublico(IdCampo) | — | — |
| 3 | ValorDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 4 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |
| 5 | MesReferencia11 | decimal(14,2) | Y | — | — | — |
| 6 | MesReferencia10 | decimal(14,2) | Y | — | — | — |
| 7 | MesReferencia9 | decimal(14,2) | Y | — | — | — |
| 8 | MesReferencia8 | decimal(14,2) | Y | — | — | — |
| 9 | MesReferencia7 | decimal(14,2) | Y | — | — | — |
| 10 | MesReferencia6 | decimal(14,2) | Y | — | — | — |
| 11 | MesReferencia5 | decimal(14,2) | Y | — | — | — |
| 12 | MesReferencia4 | decimal(14,2) | Y | — | — | — |
| 13 | MesReferencia3 | decimal(14,2) | Y | — | — | — |
| 14 | MesReferencia2 | decimal(14,2) | Y | — | — | — |
| 15 | MesReferencia1 | decimal(14,2) | Y | — | — | — |
| 16 | MesReferencia | decimal(14,2) | Y | — | — | — |
| 17 | TotalMesesReferencia | decimal(14,2) | Y | — | — | — |

## dbo.Anexo15_MovimentoConsorcioPublicoEnteConsorciado

Tabela · ~376 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimentoConsorcioPublicoEnteConsorciado | int | N | PK, IDENT | — | — |
| 2 | CNPJEnteConsorciado | char(14) | N | — | — | — |
| 3 | NomeEnteConsorciado | varchar(150) | N | — | — | — |
| 4 | ValorTransferido | decimal(14,2) | N | — | — | — |
| 5 | ValorExecutado | decimal(14,2) | N | — | — | — |
| 6 | MesReferencia11 | decimal(14,2) | Y | — | — | — |
| 7 | MesReferencia10 | decimal(14,2) | Y | — | — | — |
| 8 | MesReferencia9 | decimal(14,2) | Y | — | — | — |
| 9 | MesReferencia8 | decimal(14,2) | Y | — | — | — |
| 10 | MesReferencia7 | decimal(14,2) | Y | — | — | — |
| 11 | MesReferencia6 | decimal(14,2) | Y | — | — | — |
| 12 | MesReferencia5 | decimal(14,2) | Y | — | — | — |
| 13 | MesReferencia4 | decimal(14,2) | Y | — | — | — |
| 14 | MesReferencia3 | decimal(14,2) | Y | — | — | — |
| 15 | MesReferencia2 | decimal(14,2) | Y | — | — | — |
| 16 | MesReferencia1 | decimal(14,2) | Y | — | — | — |
| 17 | MesReferencia | decimal(14,2) | Y | — | — | — |
| 18 | TotalMesesReferencia | decimal(14,2) | Y | — | — | — |
| 19 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo15_MovimentoDefensoriaPublica

Tabela · ~610 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo15_CamposDefensoriaPublica(IdCampo) | — | — |
| 3 | ValorDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 4 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |
| 5 | MesReferencia11 | decimal(14,2) | Y | — | — | — |
| 6 | MesReferencia10 | decimal(14,2) | Y | — | — | — |
| 7 | MesReferencia9 | decimal(14,2) | Y | — | — | — |
| 8 | MesReferencia8 | decimal(14,2) | Y | — | — | — |
| 9 | MesReferencia7 | decimal(14,2) | Y | — | — | — |
| 10 | MesReferencia6 | decimal(14,2) | Y | — | — | — |
| 11 | MesReferencia5 | decimal(14,2) | Y | — | — | — |
| 12 | MesReferencia4 | decimal(14,2) | Y | — | — | — |
| 13 | MesReferencia3 | decimal(14,2) | Y | — | — | — |
| 14 | MesReferencia2 | decimal(14,2) | Y | — | — | — |
| 15 | MesReferencia1 | decimal(14,2) | Y | — | — | — |
| 16 | MesReferencia | decimal(14,2) | Y | — | — | — |
| 17 | TotalMesesReferencia | decimal(14,2) | Y | — | — | — |

## dbo.Anexo15_MovimentoEnteFederacao

Tabela · ~166.555 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo15_CamposEnteFederacao(IdCampo) | — | — |
| 3 | IdTipoLimite | tinyint | Y | FK → dbo.RGF_TipoLimite(IdTipoLimite) | — | — |
| 4 | ValorDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 5 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |
| 6 | MesReferencia11 | decimal(14,2) | Y | — | — | — |
| 7 | MesReferencia10 | decimal(14,2) | Y | — | — | — |
| 8 | MesReferencia9 | decimal(14,2) | Y | — | — | — |
| 9 | MesReferencia8 | decimal(14,2) | Y | — | — | — |
| 10 | MesReferencia7 | decimal(14,2) | Y | — | — | — |
| 11 | MesReferencia6 | decimal(14,2) | Y | — | — | — |
| 12 | MesReferencia5 | decimal(14,2) | Y | — | — | — |
| 13 | MesReferencia4 | decimal(14,2) | Y | — | — | — |
| 14 | MesReferencia3 | decimal(14,2) | Y | — | — | — |
| 15 | MesReferencia2 | decimal(14,2) | Y | — | — | — |
| 16 | MesReferencia1 | decimal(14,2) | Y | — | — | — |
| 17 | MesReferencia | decimal(14,2) | Y | — | — | — |
| 18 | TotalMesesReferencia | decimal(14,2) | Y | — | — | — |

## dbo.Anexo15_MovimentoEnteFederacaoConsorciado

Tabela · ~2.038 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo15_CamposEnteFederacaoConsorciado(IdCampo) | — | — |
| 3 | CNPJConsorciado | varchar(14) | N | — | — | — |
| 4 | NomeConsorciado | varchar(150) | N | — | — | — |
| 5 | ValorTransferido | decimal(14,2) | N | — | — | — |
| 6 | ValorDespesasLiquidadas | decimal(14,2) | N | — | — | — |
| 7 | ValorDespesasInscritasRestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |
| 8 | MesReferencia11 | decimal(14,2) | Y | — | — | — |
| 9 | MesReferencia10 | decimal(14,2) | Y | — | — | — |
| 10 | MesReferencia9 | decimal(14,2) | Y | — | — | — |
| 11 | MesReferencia8 | decimal(14,2) | Y | — | — | — |
| 12 | MesReferencia7 | decimal(14,2) | Y | — | — | — |
| 13 | MesReferencia6 | decimal(14,2) | Y | — | — | — |
| 14 | MesReferencia5 | decimal(14,2) | Y | — | — | — |
| 15 | MesReferencia4 | decimal(14,2) | Y | — | — | — |
| 16 | MesReferencia3 | decimal(14,2) | Y | — | — | — |
| 17 | MesReferencia2 | decimal(14,2) | Y | — | — | — |
| 18 | MesReferencia1 | decimal(14,2) | Y | — | — | — |
| 19 | MesReferencia | decimal(14,2) | Y | — | — | — |
| 20 | TotalMesesReferencia | decimal(14,2) | Y | — | — | — |

## dbo.Anexo16_Campos

Tabela · ~202 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(200) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 8 | DividaConsolidadaLiquida | bit | N | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo16_LimitesLegais

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLimite | smallint | N | PK | — | — |
| 2 | IdNaturezaOrgao | smallint | N | — | — | — |
| 3 | LimiteMaximo | decimal(5,2) | N | — | — | — |
| 4 | LimiteAlerta | decimal(5,2) | N | — | — | — |
| 5 | AnoExercicioInicial | smallint | N | — | — | — |
| 6 | AnoExercicioFinal | smallint | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo16_Movimento

Tabela · ~207.973 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo16_Campos(IdCampo) | — | — |
| 3 | ValorSaldoExercicioAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorSaldoAte1Quadrimestre | decimal(14,2) | N | — | — | — |
| 5 | ValorSaldoAte2Quadrimestre | decimal(14,2) | N | — | — | — |
| 6 | ValorSaldoAte3Quadrimestre | decimal(14,2) | N | — | — | — |

## dbo.Anexo17_Campos

Tabela · ~72 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | SubGrupo | tinyint | N | — | — | — |
| 6 | Descricao | varchar(160) | N | — | — | — |
| 7 | Grupo | bit | N | — | — | — |
| 8 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 9 | TotalGarantiasConcedidas | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo17_LimitesLegais

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLimite | smallint | N | PK | — | — |
| 2 | IdNaturezaOrgao | smallint | N | — | — | — |
| 3 | LimiteMaximo | decimal(5,2) | N | — | — | — |
| 4 | LimiteAlerta | decimal(5,2) | N | — | — | — |
| 5 | AnoExercicioInicial | smallint | N | — | — | — |
| 6 | AnoExercicioFinal | smallint | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo17_MedidaCorretiva

Tabela · ~2.568 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMedidaCorretiva | int | N | PK, IDENT | — | — |
| 2 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 3 | DescricaoMedidaCorretiva | varchar(MAX) | N | — | — | — |

## dbo.Anexo17_Movimento

Tabela · ~135.186 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo17_Campos(IdCampo) | — | — |
| 3 | ValorSaldoAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorSaldoAte1Quadrimestre | decimal(14,2) | N | — | — | — |
| 5 | ValorSaldoAte2Quadrimestre | decimal(14,2) | Y | — | — | — |
| 6 | ValorSaldoAte3Quadrimestre | decimal(14,2) | Y | — | — | — |

## dbo.Anexo18_Campos

Tabela · ~160 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(200) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | ReceitaCorrenteLiquida | bit | N | — | — | — |
| 8 | OperacaoCreditoAntecipacao | bit | N | — | — | — |
| 9 | ApuracaoCumprimentoLimite | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo18_LimitesLegaisOperacoesDeCredito

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLimite | smallint | N | PK | — | — |
| 2 | IdNaturezaOrgao | smallint | N | — | — | — |
| 3 | LimiteMaximo | decimal(5,2) | N | — | — | — |
| 4 | LimiteAlerta | decimal(5,2) | N | — | — | — |
| 5 | AnoExercicioInicial | smallint | N | — | — | — |
| 6 | AnoExercicioFinal | smallint | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo18_Movimento

Tabela · ~162.180 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | IdCampo | smallint | N | FK → dbo.Anexo18_Campos(IdCampo) | — | — |
| 3 | IdTipoOperacao | tinyint | Y | FK → dbo.Anexo18_TipoOperacao(IdTipoOperacao) | — | — |
| 4 | ValorAteQuadrimestre | decimal(14,2) | N | — | — | — |
| 5 | ValorNoQuadrimestre | decimal(14,2) | N | — | — | — |
| 6 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo18_TipoOperacao

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoOperacao | tinyint | N | PK | — | — |
| 2 | CodigoTipoOperacao | tinyint | N | — | — | — |
| 3 | DescricaoTipoOperacao | varchar(120) | N | — | — | — |

## dbo.Anexo19_Campos

Tabela · ~226 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | IdTipoCampo | tinyint | N | FK → dbo.Anexo19_TipoCampo(IdTipoCampo) | — | — |
| 6 | Descricao | varchar(200) | N | — | — | — |
| 7 | Grupo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo19_Movimento

Tabela · ~61.445 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | DescricaoRecurso | varchar(255) | Y | — | — | — |
| 3 | ValorDisponibilidaDeCaixa | decimal(14,2) | N | — | — | — |
| 4 | ValorRPLiquidadosNaoPagosDeExerciciosAnteriores | decimal(14,2) | N | — | — | — |
| 5 | ValorRPLiquidadosNaoPagosDoExercicio | decimal(14,2) | N | — | — | — |
| 6 | ValorRPEmpenhadosNaoLiquidadosDeExerciciosAnteriores | decimal(14,2) | N | — | — | — |
| 7 | ValorDemaisObrigacoesFinanceiras | decimal(14,2) | N | — | — | — |
| 8 | ValorInsuficienciaConsorcio | decimal(14,2) | N | — | — | — |
| 10 | ValorDisponibilidaDeCaixaLiquidaAposRPNP | decimal(14,2) | Y | — | — | — |
| 11 | ValorDisponibilidaDeCaixaLiquida | decimal(14,2) | N | — | — | — |
| 12 | ValorRPEmpenhadosNaoLiquidadosDoExercicio | decimal(14,2) | N | — | — | — |
| 13 | ValorEmpenhosNaoLiquidadosCancelados | decimal(14,2) | N | — | — | — |
| 14 | IdTipoRecurso | tinyint | Y | FK → dbo.Anexo19_TipoRecurso(IdTipoRecurso) | — | — |
| 15 | TipoTotalizador | bit | N | — | — | — |
| 16 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 17 | IdCampo | smallint | Y | FK → dbo.Anexo19_Campos(IdCampo) | — | — |

## dbo.Anexo19_TipoCampo

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCampo | tinyint | N | PK | — | — |
| 2 | NomeTipoCampo | varchar(100) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo19_TipoRecurso

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoRecurso | tinyint | N | PK | — | — |
| 2 | DescricaoTipoRecurso | varchar(50) | N | — | — | — |

## dbo.Anexo20_Movimento

Tabela · ~6.234 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | SaldoExercicioAnteriorNoBimestre | decimal(14,2) | Y | — | — | — |
| 3 | SaldoExercicioAnteriorAteBimentre | decimal(14,2) | Y | — | — | — |
| 4 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo21_Aditivos

Tabela · ~363 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAditivos | int | N | PK, IDENT | — | — |
| 2 | IdMovimento | int | N | FK → dbo.Anexo21_Movimento(IdMovimento) | — | — |
| 3 | NumeroAnoProcesso | varchar(12) | N | — | — | — |
| 4 | NumeroAnoAditivo | varchar(12) | N | — | — | — |
| 5 | ElementoDespesa | char(6) | Y | — | — | — |
| 6 | TermoAditivo | varchar(MAX) | Y | — | — | — |
| 7 | DataAssinatura | date | Y | — | — | — |
| 8 | DataPublicacao | date | Y | — | — | — |
| 9 | NumeroTermo | varchar(30) | Y | — | — | — |
| 10 | Objetivo | varchar(150) | Y | — | — | — |
| 11 | InicioVigencia | date | Y | — | — | — |
| 12 | TerminoVigencia | date | Y | — | — | — |
| 13 | ValorAditivo | decimal(14,2) | Y | — | — | — |
| 14 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo21_Execucao

Tabela · ~2.091 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdExecucao | int | N | PK, IDENT | — | — |
| 2 | IdMovimento | int | N | FK → dbo.Anexo21_Movimento(IdMovimento) | — | — |
| 3 | CodigoContaEspecifica | varchar(30) | Y | — | — | — |
| 4 | DataEntregaRecurso | date | Y | — | — | — |
| 5 | ValorRepasse | decimal(14,2) | Y | — | — | — |
| 6 | ValorReceitaAplicacaoFinanceira | decimal(14,2) | Y | — | — | — |
| 7 | ValorExecutado | decimal(14,2) | Y | — | — | — |
| 8 | DataRecebimentoSaldo | date | Y | — | — | — |
| 9 | DataPrestacaoContas | date | Y | — | — | — |
| 10 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo21_Movimento

Tabela · ~2.763 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | NumeroAnoProcesso | varchar(12) | N | — | — | — |
| 10 | CNPJRecebedor | char(14) | Y | — | — | — |
| 11 | NomeRecebedor | varchar(100) | Y | — | — | — |
| 12 | DataAssinatura | date | Y | — | — | — |
| 13 | DataPublicacao | date | Y | — | — | — |
| 14 | FonteRecurso01 | varchar(30) | Y | — | — | — |
| 15 | FonteRecurso02 | varchar(30) | Y | — | — | — |
| 16 | FonteRecurso03 | varchar(30) | Y | — | — | — |
| 17 | ValorFonte01 | decimal(14,2) | Y | — | — | — |
| 18 | ValorFonte02 | decimal(14,2) | Y | — | — | — |
| 19 | ValorFonte03 | decimal(14,2) | Y | — | — | — |
| 20 | Objeto | varchar(150) | Y | — | — | — |
| 21 | InicioVigencia | date | Y | — | — | — |
| 22 | TerminoVigencia | date | Y | — | — | — |
| 23 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo22_Campos

Tabela · ~44 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(200) | N | — | — | — |
| 6 | IdGrupo | tinyint | N | FK → dbo.Anexo22_Grupos(IdGrupo) | — | — |
| 7 | ApenasExecutivo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo22_Grupos

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupo | tinyint | N | PK | — | — |
| 2 | NomeGrupo | varchar(50) | N | — | — | — |

## dbo.Anexo22_Movimento

Tabela · ~78.979 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | Valor | decimal(14,2) | N | — | — | — |
| 3 | Percentual | decimal(5,2) | N | — | — | — |
| 4 | IdCampo | tinyint | N | FK → dbo.Anexo22_Campos(IdCampo) | — | — |
| 5 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo22_RestosAPagar

Tabela · ~6.747 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRestosAPagar | int | N | PK, IDENT | — | — |
| 2 | ValorInscricaorestosAPagarNaoProcessados | decimal(14,2) | N | — | — | — |
| 3 | ValorDisponibilidadeCaixaLiquida | decimal(14,2) | N | — | — | — |
| 4 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo23_DocumentacaoAnexada

Tabela · ~13.995 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDocumentacaoAnexada | int | N | PK, IDENT | — | — |
| 2 | IdTipoSituacaoObraServico | tinyint | N | FK → dbo.Anexo23_TipoSituacaoObraServico(IdTipoSituacaoObraServico) | — | — |
| 3 | IdObraServico | int | N | FK → dbo.Anexo23_ObraServico(IdObraServico) | — | — |
| 4 | IdTipoDocumentacao | tinyint | N | FK → dbo.Anexo23_TipoDocumentacao(IdTipoDocumentacao) | — | — |
| 5 | NomeArquivo | varchar(500) | N | — | — | — |
| 6 | HashArquivo | char(32) | N | — | — | — |
| 7 | Ativo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemAcompanhamentoObraServico

Tabela · ~9.038 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdItemAcompanhamentoObraServico | int | N | PK, IDENT | — | — |
| 2 | IdObraServico | int | N | FK → dbo.Anexo23_ObraServico(IdObraServico) | — | — |
| 3 | IdTipoSituacaoExecucao | tinyint | N | FK → dbo.Anexo23_TipoSituacaoExecucao(IdTipoSituacaoExecucao) | — | — |
| 4 | NumeroMedicaoAPI | int | Y | — | — | — |
| 5 | NumeroMedicaoReajuste | int | Y | — | — | — |
| 6 | DataMedicaoAPI | date | Y | — | — | — |
| 7 | DataMedicaoReajuste | date | Y | — | — | — |
| 8 | ValorMedicaoAPI | decimal(14,2) | Y | — | — | — |
| 9 | ValorMedicaoReajuste | decimal(14,2) | Y | — | — | — |
| 10 | DataRecebimentoProvisorio | date | Y | — | — | — |
| 11 | DataRecebimentoDefinitivo | date | Y | — | — | — |
| 12 | Ativo | bit | N | — | — | — |
| 13 | DataInclusao | smalldatetime | N | — | — | — |
| 14 | IdSessao | int | N | — | — | — |
| 15 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemAditamento

Tabela · ~3.942 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdItemAditamento | int | N | PK, IDENT | — | — |
| 2 | IdObraServico | int | N | FK → dbo.Anexo23_ObraServico(IdObraServico) | — | — |
| 3 | NumeroTermo | int | N | — | — | — |
| 4 | AnoTermo | smallint | N | — | — | — |
| 5 | Ativo | bit | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemContrato

Tabela · ~3.874 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdItemContrato | int | N | PK, IDENT | — | — |
| 2 | IdObraServico | int | N | FK → dbo.Anexo23_ObraServico(IdObraServico) | — | — |
| 3 | NumeroContrato | int | N | — | — | — |
| 4 | AnoContrato | smallint | N | — | — | — |
| 5 | ValorContrato | decimal(14,2) | N | — | — | — |
| 6 | DataTerminoVigencia | date | N | — | — | — |
| 7 | NumeroOrdemServico | int | N | — | — | — |
| 8 | AnoOrdemServico | smallint | N | — | — | — |
| 9 | PrazoExecucao | int | N | — | — | — |
| 10 | DataInicioExecucao | date | N | — | — | — |
| 11 | CPFGestorContrato | char(11) | N | — | — | — |
| 12 | NomeGestorContrato | varchar(150) | N | — | — | — |
| 13 | Ativo | bit | N | — | — | — |
| 14 | DataInclusao | smalldatetime | N | — | — | — |
| 15 | IdSessao | int | N | — | — | — |
| 16 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemFiscalObraServico

Tabela · ~3.930 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFiscalObraServico | int | N | PK, IDENT | — | — |
| 2 | IdObraServico | int | N | FK → dbo.Anexo23_ObraServico(IdObraServico) | — | — |
| 3 | CPFFiscalContrato | char(11) | N | — | — | — |
| 4 | NomeFiscalContrato | varchar(150) | N | — | — | — |
| 5 | Ativo | bit | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemFotoVideo

Tabela · ~41.970 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdItemFotoVideo | int | N | PK, IDENT | — | — |
| 2 | IdDocumentacaoAnexada | int | N | FK → dbo.Anexo23_DocumentacaoAnexada(IdDocumentacaoAnexada) | — | — |
| 3 | IdTipoMidia | tinyint | N | FK → dbo.Anexo23_TipoMidia(IdTipoMidia) | — | — |
| 4 | NomeArquivo | varchar(500) | N | — | — | — |
| 5 | HashArquivo | char(32) | N | — | — | — |
| 6 | DescricaoFotoVideo | varchar(200) | Y | — | — | — |
| 7 | Ativo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemJustificativaObraServico

Tabela · ~1.442 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdJustificativaObraServico | int | N | PK, IDENT | — | — |
| 2 | IdObraServico | int | N | FK → dbo.Anexo23_ObraServico(IdObraServico) | — | — |
| 3 | IdTipoSituacaoObraServico | tinyint | N | FK → dbo.Anexo23_TipoSituacaoObraServico(IdTipoSituacaoObraServico) | — | — |
| 4 | Justificativa | varchar(500) | N | — | — | — |
| 5 | Ativo | bit | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemLocalizacaoObra

Tabela · ~8.217 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdItemLocalizacaoObra | int | N | PK, IDENT | — | — |
| 2 | IdObraServico | int | N | FK → dbo.Anexo23_ObraServico(IdObraServico) | — | — |
| 3 | NumeroItem | int | N | — | — | — |
| 4 | Objeto | varchar(100) | N | — | — | — |
| 5 | Endereco | varchar(100) | N | — | — | — |
| 6 | LatitudeUTM | varchar(20) | N | — | — | — |
| 7 | LongitudeUTM | varchar(20) | N | — | — | — |
| 8 | Ativo | bit | N | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ItemTipoAditamento

Tabela · ~4.570 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdItemTipoAditamento | int | N | PK, IDENT | — | — |
| 2 | IdItemAditamento | int | N | FK → dbo.Anexo23_ItemAditamento(IdItemAditamento) | — | — |
| 3 | IdTipoAditamento | tinyint | N | FK → dbo.Anexo23_TipoAditamento(IdTipoAditamento) | — | — |
| 4 | Valor | varchar(100) | N | — | — | — |
| 5 | Ativo | bit | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_ObraServico

Tabela · ~3.634 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdObraServico | int | N | PK, IDENT | — | — |
| 2 | NumeroProcessoDespesa | varchar(20) | N | — | — | — |
| 3 | AnoProcessoDespesa | smallint | N | — | — | — |
| 4 | IdUnidadeGestora | int | Y | FK → dbo.Anexo42_UnidadeJurisdicionada(IdUnidadeJurisdicionada) | — | — |
| 5 | IdOrgao | int | N | — | — | — |
| 6 | IdTipoRegimeExecucao | tinyint | N | FK → dbo.Anexo23_TipoRegimeExecucao(IdTipoRegimeExecucao) | — | — |
| 7 | IdTipoIntervencao | tinyint | N | FK → dbo.Anexo23_TipoIntervencao(IdTipoIntervencao) | — | — |
| 8 | OutroTipoIntervencao | varchar(100) | Y | — | — | — |
| 9 | IdTipoObraServico | tinyint | N | FK → dbo.Anexo23_TipoObraServico(IdTipoObraServico) | — | — |
| 10 | OutroTipoObraServico | varchar(100) | Y | — | — | — |
| 11 | IdTipoSituacaoObraServico | tinyint | N | FK → dbo.Anexo23_TipoSituacaoObraServico(IdTipoSituacaoObraServico) | — | — |
| 12 | DescricaoObraServico | varchar(500) | N | — | — | — |
| 13 | NumeroContrato | int | Y | — | — | — |
| 14 | AnoContrato | smallint | Y | — | — | — |
| 15 | ValorContrato | decimal(14,2) | Y | — | — | — |
| 16 | DataTerminoVigencia | date | Y | — | — | — |
| 17 | NumeroOrdemServico | int | Y | — | — | — |
| 18 | AnoOrdemServico | smallint | Y | — | — | — |
| 19 | PrazoExecucao | int | Y | — | — | — |
| 20 | DataInicioExecucao | date | Y | — | — | — |
| 21 | CPFGestorContrato | char(11) | Y | — | — | — |
| 22 | NomeGestorContrato | varchar(150) | Y | — | — | — |
| 23 | Ativo | bit | N | — | — | — |
| 24 | DataInclusao | smalldatetime | N | — | — | — |
| 25 | IdSessao | int | N | — | — | — |
| 26 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo23_TipoAditamento

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAditamento | tinyint | N | PK | — | — |
| 2 | NomeTipoAditamento | varchar(50) | N | — | — | — |

## dbo.Anexo23_TipoDocumentacao

Tabela · ~12 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumentacao | tinyint | N | PK | — | — |
| 2 | NomeTipoDocumentacao | varchar(50) | N | — | — | — |
| 3 | IdTipoSituacaoObraServico | tinyint | N | FK → dbo.Anexo23_TipoSituacaoObraServico(IdTipoSituacaoObraServico) | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo23_TipoIntervencao

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoIntervencao | tinyint | N | PK | — | — |
| 2 | NomeTipoIntervencao | varchar(50) | N | — | — | — |

## dbo.Anexo23_TipoMidia

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoMidia | tinyint | N | PK | — | — |
| 2 | NomeTipoMidia | varchar(20) | N | — | — | — |

## dbo.Anexo23_TipoObraServico

Tabela · ~36 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoObraServico | tinyint | N | PK | — | — |
| 2 | NomeTipoObraServico | varchar(70) | N | — | — | — |

## dbo.Anexo23_TipoRegimeExecucao

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoRegimeExecucao | tinyint | N | PK | — | — |
| 2 | NomeTipoRegimeExecucao | varchar(50) | N | — | — | — |

## dbo.Anexo23_TipoSituacaoExecucao

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoExecucao | tinyint | N | PK | — | — |
| 2 | NomeTipoSituacaoExecucao | varchar(50) | N | — | — | — |

## dbo.Anexo23_TipoSituacaoObraServico

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoObraServico | tinyint | N | PK | — | — |
| 2 | NomeTipoSituacaoObraServico | varchar(70) | N | — | — | — |

## dbo.Anexo24_Movimento

Tabela · ~897 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | NumeroHabitantes | int | N | — | — | — |
| 3 | NumeroVereadores | int | N | — | — | — |
| 4 | RemuneracaoVereadores | decimal(14,2) | N | — | — | — |
| 5 | RemuneracaoPresidente | decimal(14,2) | N | — | — | — |
| 6 | AtoNormativo | varchar(500) | N | — | — | — |
| 7 | ReceitasEfetivas | decimal(14,2) | N | — | — | — |
| 8 | DespesasLegislativos | decimal(14,2) | N | — | — | — |
| 9 | DGLimiteLegal | decimal(14,2) | N | — | — | — |
| 10 | DGLimiteAtingido | decimal(14,2) | N | — | — | — |
| 11 | ReceitaLegistlativo | decimal(14,2) | N | — | — | — |
| 12 | DespesasFolhaPagamento | decimal(14,2) | N | — | — | — |
| 13 | DPLimiteLegal | decimal(14,2) | N | — | — | — |
| 14 | DPLimiteAtingido | decimal(14,2) | N | — | — | — |
| 15 | ReceitaMunicipio | decimal(14,2) | N | — | — | — |
| 16 | RemuneracaoTotalVereadores | decimal(14,2) | N | — | — | — |
| 17 | RTVLimiteLegal | decimal(14,2) | N | — | — | — |
| 18 | RTVLimiteAtingido | decimal(14,2) | N | — | — | — |
| 19 | TotalReceita | decimal(14,2) | N | — | — | — |
| 20 | DespesasPessoal | decimal(14,2) | N | — | — | — |
| 21 | DTPLimiteLegal | decimal(14,2) | N | — | — | — |
| 22 | DTPLimiteAtingido | decimal(14,2) | N | — | — | — |
| 23 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo25_BaseLegal

Tabela · ~20 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdBaseLegal | smallint | N | PK | — | — |
| 2 | CodigoBaseLegal | char(2) | N | — | — | — |
| 3 | DescricaoBaseLegal | varchar(100) | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo25_Movimento

Tabela · ~2.914 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | NumeroAnoProcesso | varchar(20) | N | — | — | — |
| 3 | CPFDoSuprido | char(11) | Y | — | — | — |
| 4 | NomeDoSuprido | varchar(50) | Y | — | — | — |
| 5 | FuncaoDoSuprido | varchar(40) | Y | — | — | — |
| 6 | DataConcessao | date | Y | — | — | — |
| 7 | ValorDoSuprimento | decimal(14,2) | N | — | — | — |
| 8 | ElementoDespesa | char(6) | Y | — | — | — |
| 9 | FonteRecurso | char(3) | Y | — | — | — |
| 10 | Beneficiado | varchar(50) | Y | — | — | — |
| 11 | IdBaseLegal | smallint | Y | FK → dbo.Anexo25_BaseLegal(IdBaseLegal) | — | — |
| 12 | NumeroEmpenho | varchar(15) | Y | — | — | — |
| 13 | Matricula | varchar(20) | Y | — | — | — |
| 14 | ObjetoSolicitacao | varchar(50) | Y | — | — | — |
| 15 | OrgaoBeneficiado | varchar(50) | Y | — | — | — |
| 16 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo25_PrestacaoDeContas

Tabela · ~78.198 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrestacaoDeContas | int | N | PK, IDENT | — | — |
| 2 | IdMovimento | int | N | FK → dbo.Anexo25_Movimento(IdMovimento) | — | — |
| 3 | NumeroAnoProcesso | varchar(20) | N | — | — | — |
| 4 | ElementoDespesa | char(6) | Y | — | — | — |
| 5 | Prazo | smallint | Y | — | — | — |
| 6 | DataEntrega | date | Y | — | — | — |
| 7 | Destino | varchar(50) | Y | — | — | — |
| 8 | DataPrestacao | date | Y | — | — | — |
| 9 | DataRecolhimento | date | Y | — | — | — |
| 10 | ValorAplicado | decimal(14,2) | Y | — | — | — |
| 11 | ValorSaldoNaoAplicado | decimal(14,2) | N | — | — | — |
| 12 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo26_Banco

Tabela · ~114 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdBanco | int | N | PK | — | — |
| 2 | CodigoFebraban | varchar(5) | N | — | — | — |
| 3 | NomeBanco | varchar(100) | N | — | — | — |

## dbo.Anexo26_ContaBancaria

Tabela · ~405.185 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContaBancaria | int | N | PK, IDENT | — | — |
| 2 | IdBanco | int | N | FK → dbo.Anexo26_Banco(IdBanco) | — | — |
| 3 | CodigoAgencia | varchar(10) | Y | — | — | — |
| 4 | ContaCorrente | varchar(20) | Y | — | — | — |
| 5 | DescricaoConta | varchar(200) | Y | — | — | — |
| 6 | IdTipoDocumentoResponsavelConta | tinyint | Y | FK → dbo.Anexo14_TipoDocumento(IdTipoDocumento) | — | — |
| 7 | CPFCNPJResponsavelConta | varchar(14) | Y | — | — | — |
| 8 | NomeResponsavelConta | varchar(150) | Y | — | — | — |
| 9 | DataAbertura | date | Y | — | — | — |
| 10 | DataEncerramento | date | Y | — | — | — |
| 11 | Ativo | bit | N | — | — | — |
| 12 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 13 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |
| 14 | IdOrgao | int | Y | — | — | — |
| 15 | DataInclusao | smalldatetime | N | — | — | — |
| 16 | IdSessao | int | Y | — | — | — |
| 17 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo27_Cargo

Tabela · ~255.593 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCargo | int | N | PK, IDENT | — | — |
| 2 | CodigoCargo | varchar(10) | N | — | — | — |
| 3 | DescricaoCargo | varchar(60) | N | — | — | — |
| 4 | IdTipoCargo | tinyint | Y | FK → dbo.Anexo27_TipoCargo(IdTipoCargo) | — | — |
| 5 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo27_FormaAfastamento

Tabela · ~10 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFormaAfastamento | tinyint | N | PK | — | — |
| 2 | CodigoFormaAfastamento | char(2) | N | — | — | — |
| 3 | DescricaoFormaAfastamento | varchar(50) | N | — | — | — |

## dbo.Anexo27_FormaIngresso

Tabela · ~12 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFormaIngresso | tinyint | N | PK | — | — |
| 2 | CodigoFormaIngresso | char(2) | N | — | — | — |
| 3 | DescricaoFormaIngresso | varchar(40) | N | — | — | — |

## dbo.Anexo27_GrauInstrucao

Tabela · ~11 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrauInstrucao | tinyint | N | PK | — | — |
| 2 | CodigoGrauInstrucao | char(2) | N | — | — | — |
| 3 | DescricaoGrauInstrucao | varchar(40) | N | — | — | — |

## dbo.Anexo27_Lotacao

Tabela · ~71.036 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLotacao | int | N | PK, IDENT | — | — |
| 2 | CodigoLotacao | varchar(10) | N | — | — | — |
| 3 | DescricaoLotacao | varchar(60) | N | — | — | — |
| 4 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo27_Movimento

Tabela · ~435.629 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | Matricula | varchar(10) | Y | — | — | — |
| 3 | IdPessoal | int | N | FK → dbo.Anexo27_Pessoal(IdPessoal) | — | — |
| 4 | Vinculo | varchar(10) | Y | — | — | — |
| 5 | DataAdmissao | date | Y | — | — | — |
| 6 | DataAfastamento | date | Y | — | — | — |
| 7 | IdCargo | int | N | FK → dbo.Anexo27_Cargo(IdCargo) | — | — |
| 8 | IdNivelFuncional | int | Y | FK → dbo.Anexo27_NivelFuncional(IdNivelFuncional) | — | — |
| 9 | IdLotacao | int | N | FK → dbo.Anexo27_Lotacao(IdLotacao) | — | — |
| 10 | IdFormaIngresso | tinyint | N | FK → dbo.Anexo27_FormaIngresso(IdFormaIngresso) | — | — |
| 11 | IdFormaAfastamento | tinyint | Y | FK → dbo.Anexo27_FormaAfastamento(IdFormaAfastamento) | — | — |
| 12 | IdSituacaoFuncional | tinyint | Y | FK → dbo.Anexo27_SituacaoFuncional(IdSituacaoFuncional) | — | — |
| 13 | ValorVencimentoBasico | decimal(14,2) | Y | — | — | — |
| 14 | TotalOutrasVantagens | decimal(14,2) | Y | — | — | — |
| 15 | ValorINSS | decimal(14,2) | Y | — | — | — |
| 16 | ValorIRPF | decimal(14,2) | Y | — | — | — |
| 17 | TotalOutrosDescontos | decimal(14,2) | Y | — | — | — |
| 18 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo27_NivelFuncional

Tabela · ~101.734 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNivelFuncional | int | N | PK, IDENT | — | — |
| 2 | CodigoNivelFuncional | varchar(10) | N | — | — | — |
| 3 | DescricaoNivelFuncional | varchar(40) | N | — | — | — |
| 4 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo27_Pessoal

Tabela · ~428.127 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPessoal | int | N | PK, IDENT | — | — |
| 2 | CPF | char(11) | N | — | — | — |
| 3 | Nome | varchar(60) | N | — | — | — |
| 4 | Identidade | varchar(15) | Y | — | — | — |
| 5 | TituloEleitor | varchar(15) | Y | — | — | — |
| 6 | DataNascimento | date | Y | — | — | — |
| 7 | Sexo | char(1) | Y | — | — | — |
| 8 | IdGrauInstrucao | tinyint | Y | FK → dbo.Anexo27_GrauInstrucao(IdGrauInstrucao) | — | — |
| 9 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo27_SituacaoFuncional

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoFuncional | tinyint | N | PK | — | — |
| 2 | DescricaoSituacaoFuncional | varchar(15) | N | — | — | — |

## dbo.Anexo27_TipoCargo

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCargo | tinyint | N | PK | — | — |
| 2 | CodigoTipoCargo | char(2) | N | — | — | — |
| 3 | DescricaoTipoCargo | varchar(40) | N | — | — | — |

## dbo.Anexo28_Aquisicao

Tabela · ~37.311 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAquisicao | int | N | PK, FK → dbo.Anexo28_Frota(IdFrota) | — | — |
| 2 | ProcessoOrigem | varchar(24) | Y | — | — | — |
| 3 | AnoProcesso | smallint | Y | — | — | — |
| 5 | IdTipoDocumentoContratado | tinyint | Y | — | — | — |
| 6 | CNPJContratado | char(14) | N | — | — | — |
| 7 | NomeContratado | varchar(50) | N | — | — | — |
| 8 | DataAquisicao | date | N | — | — | — |
| 9 | ValorArquisicao | decimal(14,2) | N | — | — | — |
| 10 | ReciboAnexo38 | int | Y | FK → dbo.Anexo38_Edital(IdEdital) | — | — |
| 11 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 12 | DataInclusao | smalldatetime | N | — | — | — |
| 13 | IdSessao | int | Y | — | — | — |
| 14 | IdSessaoOperacao | int | Y | — | — | — |
| 15 | DeclaraVeiculoAdquiridoAntesDe2016 | bit | Y | — | — | — |

## dbo.Anexo28_Cessao

Tabela · ~1.461 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCessao | int | N | PK, FK → dbo.Anexo28_Frota(IdFrota) | — | — |
| 2 | ProcessoOrigem | varchar(24) | Y | — | — | — |
| 3 | AnoProcesso | smallint | Y | — | — | — |
| 4 | OrgaoCedente | varchar(100) | N | — | — | — |
| 5 | IdTipoDocumentoCedente | tinyint | Y | — | — | — |
| 6 | CNPJCedente | char(14) | N | — | — | — |
| 7 | NomeCedente | varchar(100) | Y | — | — | — |
| 8 | DataInicioCessao | date | N | — | — | — |
| 9 | DataTerminoCessao | date | N | — | — | — |
| 10 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 11 | DataInclusao | smalldatetime | Y | — | — | — |
| 12 | IdSessao | int | Y | — | — | — |
| 13 | IdSessaoOperacao | int | Y | — | — | — |
| 14 | DeclaraVeiculoAdquiridoAntesDe2016 | bit | Y | — | — | — |

## dbo.Anexo28_Doacao

Tabela · ~334 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDoacao | int | N | PK, FK → dbo.Anexo28_Frota(IdFrota) | — | — |
| 2 | DocumentoDoador | varchar(14) | N | — | — | — |
| 3 | IdTipoDocumentoDoador | tinyint | N | — | — | — |
| 4 | NomeDoador | varchar(100) | N | — | — | — |
| 5 | DataDoacao | date | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | Y | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo28_Frota

Tabela · ~49.523 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFrota | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | Y | — | — | — |
| 3 | IdTipoFrota | tinyint | N | FK → dbo.Anexo28_TipoFrota(IdTipoFrota) | — | — |
| 4 | Ativo | bit | N | — | — | — |
| 5 | JustificativasObservacoesGerais | varchar(300) | Y | — | — | — |
| 6 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 7 | DataInclusao | smalldatetime | Y | — | — | — |
| 8 | IdSessao | int | Y | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo28_Locacao

Tabela · ~10.417 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLocacao | int | N | PK, FK → dbo.Anexo28_Frota(IdFrota) | — | — |
| 2 | ProcessoOrigem | varchar(24) | Y | — | — | — |
| 3 | AnoLocacao | smallint | Y | — | — | — |
| 4 | IdTipoDocumentoLocatario | tinyint | Y | — | — | — |
| 5 | CNPJLocatario | char(14) | N | — | — | — |
| 6 | NomeLocatario | varchar(100) | N | — | — | — |
| 7 | DataContratoLocacao | date | N | — | — | — |
| 8 | DataInicioLocacao | date | N | — | — | — |
| 9 | DataTerminoLocacao | date | N | — | — | — |
| 10 | ValorLocacao | decimal(14,2) | N | — | — | — |
| 11 | ReciboAnexo13 | int | Y | FK → dbo.Anexo13_Contratos(IdContrato) | — | — |
| 12 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 13 | DataInclusao | smalldatetime | Y | — | — | — |
| 14 | IdSessao | int | Y | — | — | — |
| 15 | IdSessaoOperacao | int | Y | — | — | — |
| 16 | DeclaraVeiculoAdquiridoAntesDe2016 | bit | Y | — | — | — |

## dbo.Anexo28_TipoCategoria

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCategoria | tinyint | N | PK | — | — |
| 2 | NomeTipoCategoria | varchar(20) | N | — | — | — |

## dbo.Anexo28_TipoCombustivel

Tabela · ~15 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCombustivel | tinyint | N | PK | — | — |
| 2 | NomeTipoCombustivel | varchar(20) | N | — | — | — |

## dbo.Anexo28_TipoEspecieVeiculo

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoEspecieVeiculo | tinyint | N | PK | — | — |
| 2 | NomeEspecieVeiculo | varchar(20) | N | — | — | — |

## dbo.Anexo28_TipoFrota

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoFrota | tinyint | N | PK | — | — |
| 2 | DescricaoTipoFrota | varchar(100) | N | — | — | — |

## dbo.Anexo28_TipoMarcaModelo

Tabela · ~31.626 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoMarcaModelo | int | N | PK | — | — |
| 2 | NomeMarcaModelo | varchar(50) | N | — | — | — |

## dbo.Anexo28_TipoMotivoBaixaVeiculo

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoMotivoBaixaVeiculo | tinyint | N | PK | — | — |
| 2 | DescricaoTipoMotivoBaixaVeiculo | varchar(50) | N | — | — | — |

## dbo.Anexo28_TipoSituacaoVeiculo

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoVeiculo | tinyint | N | PK | — | — |
| 2 | NomeSituacaoVeiculo | varchar(10) | N | — | — | — |

## dbo.Anexo28_TipoVeiculo

Tabela · ~27 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoVeiculo | tinyint | N | PK | — | — |
| 2 | NomeTipoVeiculo | varchar(50) | N | — | — | — |
| 3 | AnoReferenciaInicial | smallint | N | — | — | — |
| 4 | AnoReferenciaFinal | smallint | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo28_Veiculo

Tabela · ~866.640 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdVeiculo | int | N | PK, IDENT | — | — |
| 2 | ProcessoOrigem | varchar(20) | Y | — | — | — |
| 3 | IdTipoSituacaoVeiculo | tinyint | Y | FK → dbo.Anexo28_TipoSituacaoVeiculo(IdTipoSituacaoVeiculo) | — | — |
| 4 | IdTipoEspecieVeiculo | tinyint | Y | FK → dbo.Anexo28_TipoEspecieVeiculo(IdTipoEspecieVeiculo) | — | — |
| 5 | IdTipoVeiculo | tinyint | N | FK → dbo.Anexo28_TipoVeiculo(IdTipoVeiculo) | — | — |
| 6 | IdTipoMarcaModelo | int | Y | FK → dbo.Anexo28_TipoMarcaModelo(IdTipoMarcaModelo) | — | — |
| 7 | IdTipoCategoria | tinyint | Y | FK → dbo.Anexo28_TipoCategoria(IdTipoCategoria) | — | — |
| 8 | IdTipoCombustivel | tinyint | N | FK → dbo.Anexo28_TipoCombustivel(IdTipoCombustivel) | — | — |
| 9 | CapacidadeTanque | smallint | N | — | — | — |
| 10 | AnoFabricacao | smallint | N | — | — | — |
| 11 | Placa | char(7) | Y | — | — | — |
| 12 | Renavan | varchar(15) | Y | — | — | — |
| 13 | IdEstado | tinyint | Y | — | — | — |
| 14 | CodigoFIPE | varchar(10) | Y | — | — | — |
| 15 | AnoModelo | smallint | Y | — | — | — |
| 16 | Valor | decimal(14,2) | Y | — | — | — |
| 17 | DataBaixaVeiculo | date | Y | — | — | — |
| 18 | DescricaoVeiculo | varchar(100) | Y | — | — | — |
| 19 | IdTipoMotivoBaixaVeiculo | tinyint | Y | FK → dbo.Anexo28_TipoMotivoBaixaVeiculo(IdTipoMotivoBaixaVeiculo) | — | — |
| 20 | IdFrota | int | Y | FK → dbo.Anexo28_Frota(IdFrota) | — | — |
| 21 | IdArquivoLRF | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 22 | DataInclusao | smalldatetime | N | — | — | — |
| 23 | IdSessao | int | Y | — | — | — |
| 24 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo29_Campos

Tabela · ~11 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(50) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo29_Movimento

Tabela · ~6.171 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | tinyint | N | PK, FK → dbo.Anexo29_Campos(IdCampo) | — | — |
| 3 | ValorCorrenteAnoReferencia | decimal(14,2) | N | — | — | — |
| 4 | ValorConstanteAnoReferencia | decimal(14,2) | N | — | — | — |
| 5 | PercentualPIBAnoReferencia | decimal(5,3) | N | — | — | — |
| 6 | PercentualRCLAnoReferencia | decimal(5,2) | Y | — | — | — |
| 7 | ValorCorrenteAnoSubsequente1 | decimal(14,2) | N | — | — | — |
| 8 | ValorConstanteAnoSubsequente1 | decimal(14,2) | N | — | — | — |
| 9 | PercentualPIBAnoSubsequente1 | decimal(5,3) | N | — | — | — |
| 10 | PercentualRCLAnoSubsequente1 | decimal(5,2) | Y | — | — | — |
| 11 | ValorCorrenteAnoSubsequente2 | decimal(14,2) | N | — | — | — |
| 12 | ValorConstanteAnoSubsequente2 | decimal(14,2) | N | — | — | — |
| 13 | PercentualPIBAnoSubsequente2 | decimal(5,3) | N | — | — | — |
| 14 | PercentualRCLAnoSubsequente2 | decimal(5,2) | Y | — | — | — |

## dbo.Anexo30_Campos

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(50) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo30_Movimento

Tabela · ~4.488 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | tinyint | N | PK, FK → dbo.Anexo30_Campos(IdCampo) | — | — |
| 3 | ValorMetasPrevistasSegundoAnoAnterior | decimal(14,2) | N | — | — | — |
| 4 | PercentualMetasPrevistasPIB | decimal(5,2) | N | — | — | — |
| 5 | PercentualMetasPrevistasRCL | decimal(5,2) | Y | — | — | — |
| 6 | ValorMetasRealizadasSegundoAnoAnterior | decimal(14,2) | N | — | — | — |
| 7 | PercentualMetasRealizadasPIB | decimal(5,2) | N | — | — | — |
| 8 | PercentualMetasRealizadasRCL | decimal(5,2) | Y | — | — | — |

## dbo.Anexo31_Campos

Tabela · ~16 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(50) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo31_ValoresPrecosConstantes

Tabela · ~4.488 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | tinyint | N | PK, FK → dbo.Anexo31_Campos(IdCampo) | — | — |
| 3 | ValorTerceiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorSegundoAnoAnterior | decimal(14,2) | N | — | — | — |
| 5 | PercentualPrimeiraComparacao | decimal(7,2) | N | — | — | — |
| 6 | ValorPrimeiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 7 | PercentualSegundaComparacao | decimal(7,2) | N | — | — | — |
| 8 | ValorAnoReferencia | decimal(14,2) | N | — | — | — |
| 9 | PercentualTerceiraComparacao | decimal(7,2) | N | — | — | — |
| 10 | ValorPrimeiroAnoSubsequente | decimal(14,2) | N | — | — | — |
| 11 | PercentualQuartaComparacao | decimal(7,2) | N | — | — | — |
| 12 | ValorSegundoAnoSubsequente | decimal(14,2) | N | — | — | — |
| 13 | PercentualQuintaComparacao | decimal(7,2) | N | — | — | — |

## dbo.Anexo31_ValoresPrecosCorrentes

Tabela · ~4.488 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | tinyint | N | PK, FK → dbo.Anexo31_Campos(IdCampo) | — | — |
| 3 | ValorTerceiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorSegundoAnoAnterior | decimal(14,2) | N | — | — | — |
| 5 | PercentualPrimeiraComparacao | decimal(7,2) | N | — | — | — |
| 6 | ValorPrimeiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 7 | PercentualSegundaComparacao | decimal(7,2) | N | — | — | — |
| 8 | ValorAnoReferencia | decimal(14,2) | N | — | — | — |
| 9 | PercentualTerceiraComparacao | decimal(7,2) | N | — | — | — |
| 10 | ValorPrimeiroAnoSubsequente | decimal(14,2) | N | — | — | — |
| 11 | PercentualQuartaComparacao | decimal(7,2) | N | — | — | — |
| 12 | ValorSegundoAnoSubsequente | decimal(14,2) | N | — | — | — |
| 13 | PercentualQuintaComparacao | decimal(7,2) | N | — | — | — |

## dbo.Anexo32_Campos

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(50) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo32_CamposRegimePrevidenciario

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampoRegimePrevidenciario | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(50) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo32_Movimento

Tabela · ~1.683 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | tinyint | N | PK, FK → dbo.Anexo32_Campos(IdCampo) | — | — |
| 3 | ValorSergundoAnoAnterior | decimal(14,2) | N | — | — | — |
| 4 | PercentualSegundoAnoAnterior | decimal(5,2) | N | — | — | — |
| 5 | ValorTerceiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 6 | PercentualTerceiroAnoAnterior | decimal(5,2) | N | — | — | — |
| 7 | ValorQuartoAnoAnterior | decimal(14,2) | N | — | — | — |
| 8 | PercentualQuartoAnoAnterior | decimal(5,2) | N | — | — | — |

## dbo.Anexo32_MovimentoRegimePrevidenciario

Tabela · ~1.683 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampoRegimePrevidenciario | tinyint | N | PK, FK → dbo.Anexo32_CamposRegimePrevidenciario(IdCampoRegimePrevidenciario) | — | — |
| 3 | ValorSergundoAnoAnterior | decimal(14,2) | N | — | — | — |
| 4 | PercentualSegundoAnoAnterior | decimal(5,2) | N | — | — | — |
| 5 | ValorTerceiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 6 | PercentualTerceiroAnoAnterior | decimal(5,2) | N | — | — | — |
| 7 | ValorQuartoAnoAnterior | decimal(14,2) | N | — | — | — |
| 8 | PercentualQuartoAnoAnterior | decimal(5,2) | N | — | — | — |

## dbo.Anexo33_Campos

Tabela · ~25 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(50) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | IdTipoCampo | tinyint | N | FK → dbo.Anexo33_TipoCampo(IdTipoCampo) | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo33_Movimento

Tabela · ~6.732 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | tinyint | N | PK, FK → dbo.Anexo33_Campos(IdCampo) | — | — |
| 3 | ValorSegundoAnoAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorTerceiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 5 | ValorQuartoAnoAnterior | decimal(14,2) | N | — | — | — |

## dbo.Anexo33_TipoCampo

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCampo | tinyint | N | PK | — | — |
| 2 | Descricao | varchar(50) | N | — | — | — |

## dbo.Anexo34_Campos

Tabela · ~170 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | smallint | N | — | — | — |
| 5 | Descricao | varchar(80) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo34_Movimento

Tabela · ~49.417 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo34_Campos(IdCampo) | — | — |
| 3 | ValorQuartoAnoAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorTerceiroAnoAnterior | decimal(14,2) | N | — | — | — |
| 5 | ValorSegundoAnoAnterior | decimal(14,2) | N | — | — | — |

## dbo.Anexo34_ProjecaoAtuarial

Tabela · ~700 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProjecaoAtuarial | int | N | PK, IDENT | — | — |
| 2 | Exercicio | smallint | N | — | — | — |
| 3 | ValorReceitasPrevidenciarias | decimal(14,2) | N | — | — | — |
| 4 | ValorDespesasPrevidenciarias | decimal(14,2) | N | — | — | — |
| 5 | ValorResultadoPrevidenciario | decimal(14,2) | N | — | — | — |
| 6 | ValorSaldoFinanceiroDoExercicio | decimal(14,2) | N | — | — | — |
| 7 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo35_Movimento

Tabela · ~809 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | Tributo | varchar(50) | N | — | — | — |
| 3 | Modalidade | varchar(50) | N | — | — | — |
| 4 | SetorProgramaBeneficiario | varchar(50) | N | — | — | — |
| 5 | ValorRenunciaAnoReferencia | decimal(14,2) | N | — | — | — |
| 6 | ValorRenunciaPrimeiroAnoSubsequente | decimal(14,2) | Y | — | — | — |
| 7 | ValorRenunciaSegundoAnoSubsequente | decimal(14,2) | Y | — | — | — |
| 8 | ValorCompensacao | decimal(14,2) | N | — | — | — |
| 9 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo36_Campos

Tabela · ~10 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | tinyint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | Descricao | varchar(50) | N | — | — | — |
| 6 | Grupo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo36_Movimento

Tabela · ~5.610 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | tinyint | N | PK, FK → dbo.Anexo36_Campos(IdCampo) | — | — |
| 3 | ValorPrevistoAnoReferencia | decimal(14,2) | N | — | — | — |

## dbo.Anexo37_Movimento

Tabela · ~715 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | DescricaoRiscos | varchar(250) | N | — | — | — |
| 3 | ValorRiscos | decimal(14,2) | N | — | — | — |
| 4 | DescricaoProvidencias | varchar(250) | Y | — | — | — |
| 5 | ValorProvidencias | decimal(14,2) | Y | — | — | — |
| 6 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Anexo38_CriterioAdjudicacao

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriterioAdjudicacao | tinyint | N | PK | — | — |
| 2 | DescricaoCriterioAdjudicacao | varchar(150) | N | — | — | — |

## dbo.Anexo38_CriterioJulgamento

Tabela · ~25 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriterioJulgamento | int | N | PK | — | — |
| 2 | NomeCriterioJulgamento | varchar(90) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_Edital

Tabela · ~398.954 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEdital | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | NumeroProcessoDespesa | varchar(24) | N | — | — | — |
| 4 | AnoProcessoDespesa | smallint | N | — | — | — |
| 5 | IdUnidadeGestora | int | Y | FK → dbo.Anexo42_UnidadeJurisdicionada(IdUnidadeJurisdicionada) | — | — |
| 6 | IdProcedimentoLicitatorio | tinyint | N | FK → dbo.Anexo38_ProcedimentoLicitatorio(IdProcedimentoLicitatorio) | — | — |
| 7 | Ativo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | DataAtualizacao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_EditalAnexo

Tabela · ~1.130.905 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEditalAnexo | int | N | PK, IDENT | — | — |
| 2 | IdEditalLicitacaoPublica | int | Y | FK → dbo.Anexo38_EditalLicitacaoPublica(IdEditalLicitacaoPublica) | — | — |
| 3 | IdEditalLicitacaoDispensada | int | Y | FK → dbo.Anexo38_EditalLicitacaoDispensada(IdEditalLicitacaoDispensada) | — | — |
| 4 | IdEditalSRP | int | Y | FK → dbo.Anexo38_EditalSRP(IdEditalSRP) | — | — |
| 5 | IdEditalLicitacaoRegimeEstatal | int | Y | FK → dbo.Anexo38_EditalLicitacaoRegimeEstatal(IdEditalLicitacaoRegimeEstatal) | — | — |
| 6 | IdEditalLicitacaoInaplicabilidade | int | Y | FK → dbo.Anexo38_EditalLicitacaoInaplicabilidade(IdEditalLicitacaoInaplicabilidade) | — | — |
| 7 | NomeArquivoAnexo | varchar(500) | N | — | — | — |
| 8 | HashArquivoAnexo | char(32) | N | — | — | — |
| 9 | IdTipoDocumentacao | tinyint | N | FK → dbo.Anexo38_TipoDocumentacao(IdTipoDocumentacao) | — | — |
| 10 | Ativo | bit | N | — | — | — |
| 11 | DataInclusao | smalldatetime | N | — | — | — |
| 12 | IdSessao | int | N | — | — | — |
| 13 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_EditalJustificativa

Tabela · ~66.441 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEditalJustificativa | int | N | PK, IDENT | — | — |
| 2 | IdEdital | int | Y | — | — | — |
| 3 | IdEditalLicitacaoPublica | int | Y | FK → dbo.Anexo38_EditalLicitacaoPublica(IdEditalLicitacaoPublica) | — | — |
| 4 | IdEditalLicitacaoDispensada | int | Y | FK → dbo.Anexo38_EditalLicitacaoDispensada(IdEditalLicitacaoDispensada) | — | — |
| 5 | IdEditalSRP | int | Y | FK → dbo.Anexo38_EditalSRP(IdEditalSRP) | — | — |
| 6 | IdEditalLicitacaoRegimeEstatal | int | Y | FK → dbo.Anexo38_EditalLicitacaoRegimeEstatal(IdEditalLicitacaoRegimeEstatal) | — | — |
| 7 | IdEditalLicitacaoInaplicabilidade | int | Y | FK → dbo.Anexo38_EditalLicitacaoInaplicabilidade(IdEditalLicitacaoInaplicabilidade) | — | — |
| 8 | Justificativa | varchar(500) | N | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_EditalLicitacaoDispensada

Tabela · ~290.572 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEditalLicitacaoDispensada | int | N | PK, IDENT | — | — |
| 2 | IdEdital | int | N | FK → dbo.Anexo38_Edital(IdEdital) | — | — |
| 3 | IdResponsavelOrdenadorDespesa | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 4 | NumeroTermoDispensa | varchar(10) | N | — | — | — |
| 5 | AnoTermoDispensa | smallint | N | — | — | — |
| 6 | DataExpedicaoTermoDispensa | date | N | — | — | — |
| 7 | DataPublicacaoTermoDispensa | date | N | — | — | — |
| 8 | IdFundamentoLegal | smallint | Y | FK → dbo.Anexo38_FundamentoLegal(IdFundamentoLegal) | — | — |
| 9 | ObjetoTermoDispensa | varchar(500) | Y | — | — | — |
| 10 | IdTipoObjeto | tinyint | Y | FK → dbo.Anexo38_TipoObjeto(IdTipoObjeto) | — | — |
| 11 | OutroTipoObjeto | varchar(500) | Y | — | — | — |
| 12 | ValorAvaliacaoBem | decimal(14,2) | Y | — | — | — |
| 13 | ValorAlienacaoBem | decimal(14,2) | Y | — | — | — |
| 14 | ValorTotalContratadoTermoDispensa | decimal(14,2) | N | — | — | — |
| 15 | PercentualValorContratadoTermoDispensa | decimal(5,2) | N | — | — | — |
| 16 | ValorRecursoProprioTermoDispensa | decimal(14,2) | N | — | — | — |
| 17 | ValorRecursoFederalTermoDispensa | decimal(14,2) | N | — | — | — |
| 18 | ValorRecursoEstadualTermoDispensa | decimal(14,2) | N | — | — | — |
| 19 | ValorRecursoMunicipalTermoDispensa | decimal(14,2) | N | — | — | — |
| 20 | DataInclusao | smalldatetime | N | — | — | — |
| 21 | IdSessao | int | N | — | — | — |
| 22 | IdSessaoOperacao | int | Y | — | — | — |
| 23 | DataExclusao | datetime | Y | — | — | — |

## dbo.Anexo38_EditalLicitacaoInaplicabilidade

Tabela · ~73 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEditalLicitacaoInaplicabilidade | int | N | PK, FK → dbo.Anexo38_EditalLicitacaoInaplicabilidade(IdEditalLicitacaoInaplicabilidade), IDENT | — | — |
| 2 | IdEdital | int | N | FK → dbo.Anexo38_Edital(IdEdital) | — | — |
| 3 | IdResponsavelOrdenadorDespesa | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 4 | NumeroLicitacao | varchar(10) | N | — | — | — |
| 5 | AnoLicitacao | smallint | N | — | — | — |
| 6 | DataExpedicaoLicitacao | date | N | — | — | — |
| 7 | DataPublicacaoLicitacao | date | N | — | — | — |
| 8 | IdFundamentoLegal | smallint | N | FK → dbo.Anexo38_FundamentoLegal(IdFundamentoLegal) | — | — |
| 9 | IdTipoObjeto | tinyint | N | FK → dbo.Anexo38_TipoObjeto(IdTipoObjeto) | — | — |
| 10 | OutroTipoObjeto | varchar(500) | Y | — | — | — |
| 11 | ValorTotalOrcadoLicitacao | decimal(14,2) | N | — | — | — |
| 12 | PercentualValorContratadoLicitacao | decimal(14,2) | N | — | — | — |
| 13 | ValorRecursoProprio | decimal(14,2) | N | — | — | — |
| 14 | ValorRecursoFederal | decimal(14,2) | N | — | — | — |
| 15 | ValorRecursoEstadual | decimal(14,2) | N | — | — | — |
| 16 | ValorRecursoMunicipal | decimal(14,2) | N | — | — | — |
| 17 | DataInclusao | smalldatetime | N | — | — | — |
| 18 | IdSessao | int | N | — | — | — |
| 19 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_EditalLicitacaoPublica

Tabela · ~94.860 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEditalLicitacaoPublica | int | N | PK, IDENT | — | — |
| 2 | IdEdital | int | N | FK → dbo.Anexo38_Edital(IdEdital) | — | — |
| 3 | IdResponsavelOrdenadorDespesa | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 4 | NumeroLicitacaoPublica | varchar(10) | N | — | — | — |
| 5 | AnoLicitacaoPublica | smallint | N | — | — | — |
| 6 | IdSituacaoDivulgacaoLicitacaoPublica | tinyint | N | FK → dbo.Anexo38_SituacaoDivulgacaoLicitacaoPublica(IdSituacaoDivulgacaoLicitacaoPublica) | — | — |
| 7 | DataPublicacaoLicitacaoPublica | date | N | — | — | — |
| 8 | IdModalidadeLicitacao_REMOVER | tinyint | Y | — | — | — |
| 9 | IdModalidadeLicitacaoFundamentoLegal | smallint | N | FK → dbo.Anexo38_ModalidadeLicitacaoFundamentoLegal(IdModalidadeLicitacaoFundamentoLegal) | — | — |
| 10 | IdModalidadeLicitacaoCriterioJulgamento | int | Y | FK → dbo.Anexo38_ModalidadeLicitacaoCriterioJulgamento(IdModalidadeLicitacaoCriterioJulgamento) | — | — |
| 11 | IdInstituicaoFinanciadora | tinyint | Y | FK → dbo.Anexo38_InstituicaoFinanciadora(IdInstituicaoFinanciadora) | — | — |
| 12 | OutraInstituicaoFinanciadora | varchar(100) | Y | — | — | — |
| 13 | MetodoAquisicaoInstituicaoFinanceira | varchar(200) | Y | — | — | — |
| 14 | FundamentoLegalChamadaPublica | varchar(200) | Y | — | — | — |
| 15 | FinalidadeChamadaPublica | varchar(200) | Y | — | — | — |
| 16 | IdCriterioAdjudicacao | tinyint | Y | FK → dbo.Anexo38_CriterioAdjudicacao(IdCriterioAdjudicacao) | — | — |
| 17 | IdTipoAplicacaoMPE | tinyint | Y | FK → dbo.Anexo38_TipoAplicacaoMPE(IdTipoAplicacaoMPE) | — | — |
| 18 | ObjetoLicitacaoPublica | varchar(500) | Y | — | — | — |
| 19 | IdTipoObjeto | tinyint | Y | FK → dbo.Anexo38_TipoObjeto(IdTipoObjeto) | — | — |
| 20 | OutroTipoObjeto | varchar(500) | Y | — | — | — |
| 21 | ValorTotalOrcadoLicitacao | decimal(14,2) | N | — | — | — |
| 22 | PercentualValorContratadoLicitacao | decimal(5,2) | N | — | — | — |
| 23 | ValorRecursoProprio | decimal(14,2) | N | — | — | — |
| 24 | ValorRecursoFederal | decimal(14,2) | N | — | — | — |
| 25 | ValorRecursoEstadual | decimal(14,2) | N | — | — | — |
| 26 | ValorRecursoMunicipal | decimal(14,2) | N | — | — | — |
| 27 | DataDisponibilizacaoInicial | date | Y | — | — | — |
| 28 | DataDisponibilizacaoFinal | date | Y | — | — | — |
| 29 | HoraDisponibilizacaoInicial | char(5) | Y | — | — | — |
| 30 | HoraDisponibilizacaoFinal | char(5) | Y | — | — | — |
| 31 | HoraDisponibilizacaoInicial2 | char(5) | Y | — | — | — |
| 32 | HoraDisponibilizacaoFinal2 | char(5) | Y | — | — | — |
| 33 | LocalDisponibilizacao | varchar(250) | Y | — | — | — |
| 34 | DataRecebimentoInicial | date | Y | — | — | — |
| 35 | DataRecebimentoFinal | date | Y | — | — | — |
| 36 | HoraRecebimentoInicial | char(5) | Y | — | — | — |
| 37 | HoraRecebimentoFinal | char(5) | Y | — | — | — |
| 38 | HoraRecebimentoInicial2 | char(5) | Y | — | — | — |
| 39 | HoraRecebimentoFinal2 | char(5) | Y | — | — | — |
| 40 | HoraAberturaRecebimento | char(5) | Y | — | — | — |
| 41 | DataAberturaRecebimento | date | Y | — | — | — |
| 42 | LocalRecebimento | varchar(250) | Y | — | — | — |
| 43 | DataInclusao | smalldatetime | N | — | — | — |
| 44 | IdSessao | int | N | — | — | — |
| 45 | IdSessaoOperacao | int | Y | — | — | — |
| 46 | DataExclusao | datetime | Y | — | — | — |

## dbo.Anexo38_EditalLicitacaoRegimeEstatal

Tabela · ~1.122 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEditalLicitacaoRegimeEstatal | int | N | PK, FK → dbo.Anexo38_EditalLicitacaoRegimeEstatal(IdEditalLicitacaoRegimeEstatal), IDENT | — | — |
| 2 | IdEdital | int | N | FK → dbo.Anexo38_Edital(IdEdital) | — | — |
| 3 | IdResponsavelOrdenadorDespesa | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 4 | NumeroLicitacao | varchar(10) | N | — | — | — |
| 5 | AnoLicitacao | smallint | N | — | — | — |
| 6 | IdSituacaoDivulgacaoLicitacao | tinyint | N | FK → dbo.Anexo38_SituacaoDivulgacaoLicitacaoPublica(IdSituacaoDivulgacaoLicitacaoPublica) | — | — |
| 7 | DataPublicacaoLicitacao | date | N | — | — | — |
| 8 | IdModalidadeLicitacaoFundamentoLegal | smallint | N | FK → dbo.Anexo38_ModalidadeLicitacaoFundamentoLegal(IdModalidadeLicitacaoFundamentoLegal) | — | — |
| 9 | IdModalidadeLicitacaoCriterioJulgamento | int | N | FK → dbo.Anexo38_ModalidadeLicitacaoCriterioJulgamento(IdModalidadeLicitacaoCriterioJulgamento) | — | — |
| 10 | IdCriterioAdjudicacao | tinyint | N | FK → dbo.Anexo38_CriterioAdjudicacao(IdCriterioAdjudicacao) | — | — |
| 11 | IdTipoObjeto | tinyint | N | FK → dbo.Anexo38_TipoObjeto(IdTipoObjeto) | — | — |
| 12 | OutroTipoObjeto | varchar(500) | Y | — | — | — |
| 13 | ValorTotalOrcadoLicitacao | decimal(14,2) | N | — | — | — |
| 14 | PercentualValorContratadoLicitacao | decimal(14,2) | N | — | — | — |
| 15 | ValorRecursoProprio | decimal(14,2) | N | — | — | — |
| 16 | ValorRecursoFederal | decimal(14,2) | N | — | — | — |
| 17 | ValorRecursoEstadual | decimal(14,2) | N | — | — | — |
| 18 | ValorRecursoMunicipal | decimal(14,2) | N | — | — | — |
| 19 | DataDisponibilizacaoInicial | date | Y | — | — | — |
| 20 | DataDisponibilizacaoFinal | date | Y | — | — | — |
| 21 | HoraDisponibilizacaoInicial | char(5) | Y | — | — | — |
| 22 | HoraDisponibilizacaoFinal | char(5) | Y | — | — | — |
| 23 | HoraDisponibilizacaoInicial2 | char(5) | Y | — | — | — |
| 24 | HoraDisponibilizacaoFinal2 | char(5) | Y | — | — | — |
| 25 | LocalDisponibilizacao | varchar(200) | Y | — | — | — |
| 26 | DataInclusao | smalldatetime | N | — | — | — |
| 27 | IdSessao | int | N | — | — | — |
| 28 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_EditalSRP

Tabela · ~16.290 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEditalSRP | int | N | PK, IDENT | — | — |
| 2 | IdEdital | int | N | FK → dbo.Anexo38_Edital(IdEdital) | — | — |
| 3 | IdResponsavelOrdenadorDespesa | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 4 | UnidadeMantenedoraAta | varchar(200) | N | — | — | — |
| 5 | NumeroAta | varchar(10) | N | — | — | — |
| 6 | AnoAta | smallint | N | — | — | — |
| 7 | DataPublicacaoAta | date | N | — | — | — |
| 8 | DataVigenciaAtaInicio | date | N | — | — | — |
| 9 | DataVigenciaAtaFim | date | N | — | — | — |
| 10 | LocalDivulgacaoAta | varchar(200) | N | — | — | — |
| 11 | DataContratacao | date | N | — | — | — |
| 12 | DataPublicacaoContrato | date | Y | — | — | — |
| 13 | FundamentoLegal | varchar(200) | N | — | — | — |
| 14 | Objeto | varchar(500) | N | — | — | — |
| 15 | IdTipoObjeto | tinyint | N | FK → dbo.Anexo38_TipoObjeto(IdTipoObjeto) | — | — |
| 16 | OutroTipoObjeto | varchar(500) | Y | — | — | — |
| 17 | ValorTotalOrcado | decimal(14,2) | N | — | — | — |
| 18 | ValorContratado | decimal(14,2) | N | — | — | — |
| 19 | ValorRecursoProprio | decimal(14,2) | N | — | — | — |
| 20 | ValorRecursoFederal | decimal(14,2) | N | — | — | — |
| 21 | ValorRecursoEstadual | decimal(14,2) | N | — | — | — |
| 22 | ValorRecursoMunicipal | decimal(14,2) | N | — | — | — |
| 23 | DataInclusao | smalldatetime | N | — | — | — |
| 24 | IdSessao | int | N | — | — | — |
| 25 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_FundamentoLegal

Tabela · ~201 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFundamentoLegal | smallint | N | PK | — | — |
| 2 | NomeFundamentoLegal | varchar(90) | N | — | — | — |
| 3 | IdProcedimentoLicitatorio | tinyint | Y | FK → dbo.Anexo38_ProcedimentoLicitatorio(IdProcedimentoLicitatorio) | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_InstituicaoFinanciadora

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdInstituicaoFinanciadora | tinyint | N | PK | — | — |
| 2 | NomeInstituicaoFinanciadora | varchar(100) | N | — | — | — |
| 3 | SiglaInstituicaoFinanciadora | varchar(20) | N | — | — | — |
| 4 | Ativo | bit | N | — | — | — |

## dbo.Anexo38_ModalidadeLicitacao

Tabela · ~41 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdModalidadeLicitacao | tinyint | N | PK | — | — |
| 2 | NomeModalidadeLicitacao | varchar(50) | N | — | — | — |
| 3 | IdFundamentoLegal | smallint | Y | FK → dbo.Anexo38_FundamentoLegal(IdFundamentoLegal) | — | — |

## dbo.Anexo38_ModalidadeLicitacaoCriterioJulgamento

Tabela · ~162 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdModalidadeLicitacaoCriterioJulgamento | int | N | PK | — | — |
| 2 | IdModalidadeLicitacao | tinyint | N | FK → dbo.Anexo38_ModalidadeLicitacao(IdModalidadeLicitacao) | — | — |
| 3 | IdCriterioJulgamento | int | N | FK → dbo.Anexo38_CriterioJulgamento(IdCriterioJulgamento) | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_ModalidadeLicitacaoFundamentoLegal

Tabela · ~53 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdModalidadeLicitacaoFundamentoLegal | smallint | N | PK, IDENT | — | — |
| 2 | IdModalidadeLicitacao | tinyint | N | FK → dbo.Anexo38_ModalidadeLicitacao(IdModalidadeLicitacao) | — | — |
| 3 | IdFundamentoLegal | smallint | N | FK → dbo.Anexo38_FundamentoLegal(IdFundamentoLegal) | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_ProcedimentoLicitatorio

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProcedimentoLicitatorio | tinyint | N | PK | — | — |
| 2 | NomeProcedimentoLicitatorio | varchar(50) | N | — | — | — |
| 3 | FundamentoLegal | varchar(100) | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_ProcedimentoLicitatorioTipoObjeto

Tabela · ~105 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProcedimentoLicitatorio | tinyint | N | PK, FK → dbo.Anexo38_ProcedimentoLicitatorio(IdProcedimentoLicitatorio) | — | — |
| 2 | IdTipoObjeto | tinyint | N | PK, FK → dbo.Anexo38_TipoObjeto(IdTipoObjeto) | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_ResponsavelLicitacaoPublica

Tabela · ~139.816 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelLicitacaoPublica | int | N | PK, IDENT | — | — |
| 2 | CpfResponsavelLicitacaoPublica | char(11) | N | — | — | — |
| 3 | NomeResponsavelLicitacaoPublica | varchar(150) | N | — | — | — |
| 4 | AtoNomeacao | varchar(50) | N | — | — | — |
| 5 | DataNomeacao | date | N | — | — | — |
| 6 | IdResponsavelTipoFuncao | tinyint | N | FK → dbo.Anexo38_ResponsavelTipoFuncao(IdResponsavelTipoFuncao) | — | — |
| 7 | IdResponsavelTipoVinculo | tinyint | N | FK → dbo.Anexo38_ResponsavelTipoVinculo(IdResponsavelTipoVinculo) | — | — |
| 8 | IdEditalLicitacaoPublica | int | Y | FK → dbo.Anexo38_EditalLicitacaoPublica(IdEditalLicitacaoPublica) | — | — |
| 9 | IdEditalLicitacaoRegimeEstatal | int | Y | FK → dbo.Anexo38_EditalLicitacaoRegimeEstatal(IdEditalLicitacaoRegimeEstatal) | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_ResponsavelTipoFuncao

Tabela · ~16 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelTipoFuncao | tinyint | N | PK | — | — |
| 2 | NomeResponsavelTipoFuncao | varchar(50) | N | — | — | — |

## dbo.Anexo38_ResponsavelTipoVinculo

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelTipoVinculo | tinyint | N | PK | — | — |
| 2 | NomeResponsavelTipoVinculo | varchar(60) | N | — | — | — |

## dbo.Anexo38_ResultadoLicitacaoPublica

Tabela · ~75.717 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResultadoLicitacaoPublica | int | N | PK, FK → dbo.Anexo38_EditalLicitacaoPublica(IdEditalLicitacaoPublica) | — | — |
| 2 | IdTipoSituacaoProcedimentoLicitacao | tinyint | N | FK → dbo.Anexo38_TipoSituacaoProcedimentoLicitacao(IdTipoSituacaoProcedimentoLicitacao) | — | — |
| 3 | DataExpedicaoAto | date | N | — | — | — |
| 4 | DataPublicacaoAto | date | N | — | — | — |
| 5 | IdResponsavelOrdenadorHomologacao | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_ResultadoLicitacaoPublicaAnexo

Tabela · ~249.298 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResultadoLicitacaoPublicaAnexo | int | N | PK, IDENT | — | — |
| 2 | IdResultadoLicitacaoPublica | int | N | FK → dbo.Anexo38_ResultadoLicitacaoPublica(IdResultadoLicitacaoPublica) | — | — |
| 3 | NomeArquivoAnexo | varchar(500) | N | — | — | — |
| 4 | HashArquivoAnexo | char(32) | N | — | — | — |
| 5 | IdTipoDocumentacaoResultadoLicitacao | tinyint | N | FK → dbo.Anexo38_TipoDocumentacaoResultadoLicitacao(IdTipoDocumentacaoResultadoLicitacao) | — | — |
| 6 | Ativo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_ResultadoLicitacaoPublicaLoteParticipante

Tabela · ~1.325.871 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLoteParticipanteClassificado | int | N | PK, IDENT | — | — |
| 2 | IdResultadoLicitacaoPublica | int | N | FK → dbo.Anexo38_ResultadoLicitacaoPublica(IdResultadoLicitacaoPublica) | — | — |
| 3 | NumeroLote | varchar(10) | N | — | — | — |
| 4 | DescricaoLote | varchar(500) | Y | — | — | — |
| 5 | ValorPrecoReferencia | decimal(14,2) | Y | — | — | — |
| 6 | Quantidade | int | Y | — | — | — |
| 7 | IdTipoUnidadeMedida | tinyint | Y | — | — | — |
| 8 | IdTipoAplicacaoMPE | tinyint | Y | — | — | — |
| 9 | QuantidadeParticipantes | tinyint | Y | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_ResultadoLicitacaoPublicaParticipante

Tabela · ~2.642.011 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdParticipanteClassificado | int | N | PK, IDENT | — | — |
| 2 | IdLoteParticipanteClassificado | int | N | FK → dbo.Anexo38_ResultadoLicitacaoPublicaLoteParticipante(IdLoteParticipanteClassificado) | — | — |
| 3 | OrdemClassificatoria | tinyint | Y | — | — | — |
| 4 | IdTipoPropostaVencedora | tinyint | Y | FK → dbo.Anexo38_TipoPropostaVencedora(IdTipoPropostaVencedora) | — | — |
| 5 | ValorProposta | decimal(14,2) | Y | — | — | — |
| 6 | NomeParticipante | varchar(150) | Y | — | — | — |
| 7 | IdTipoDocumento | tinyint | Y | — | — | — |
| 8 | NumeroDocumento | varchar(14) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo38_SituacaoDivulgacaoLicitacaoPublica

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoDivulgacaoLicitacaoPublica | tinyint | N | PK | — | — |
| 2 | DescricaoSituacaoDivulgacaoLicitacaoPublica | varchar(50) | N | — | — | — |

## dbo.Anexo38_TipoAplicacaoMPE

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAplicacaoMPE | tinyint | N | PK | — | — |
| 2 | DescricaoTipoAplicacaoMPE | varchar(100) | N | — | — | — |

## dbo.Anexo38_TipoDocumentacao

Tabela · ~113 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumentacao | tinyint | N | PK | — | — |
| 2 | DescricaoTipoDocumentacao | varchar(100) | N | — | — | — |

## dbo.Anexo38_TipoDocumentacaoProcedimentoLicitatorio

Tabela · ~141 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProcedimentoLicitatorio | tinyint | N | PK, FK → dbo.Anexo38_ProcedimentoLicitatorio(IdProcedimentoLicitatorio) | — | — |
| 2 | IdTipoDocumentacao | tinyint | N | PK, FK → dbo.Anexo38_TipoDocumentacao(IdTipoDocumentacao) | — | — |

## dbo.Anexo38_TipoDocumentacaoResultadoLicitacao

Tabela · ~13 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumentacaoResultadoLicitacao | tinyint | N | PK | — | — |
| 2 | DescricaoTipoDocumentacaoResultadoLicitacao | varchar(50) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_TipoObjeto

Tabela · ~25 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoObjeto | tinyint | N | PK | — | — |
| 2 | DescricaoTipoObjeto | varchar(100) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_TipoPropostaVencedora

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoPropostaVencedora | tinyint | N | PK | — | — |
| 2 | DescricaoTipoPropostaVencedora | varchar(50) | N | — | — | — |

## dbo.Anexo38_TipoSituacaoProcedimentoLicitacao

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoProcedimentoLicitacao | tinyint | N | PK | — | — |
| 2 | DescricaoSituacaoProcedimentoLicitacao | varchar(50) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo38_TipoUnidadeMedida

Tabela · ~47 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoUnidadeMedida | tinyint | N | PK | — | — |
| 2 | DescricaoUnidadeMedida | varchar(100) | N | — | — | — |

## dbo.Anexo39_Campos

Tabela · ~69 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | smallint | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | Campo | tinyint | N | — | — | — |
| 5 | IdTipoCampo | tinyint | N | FK → dbo.Anexo39_TipoCampo(IdTipoCampo) | — | — |
| 6 | Descricao | varchar(80) | N | — | — | — |
| 7 | Grupo | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo39_ImpactoContratacao

Tabela · ~30.984 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | smallint | N | PK, FK → dbo.Anexo39_Campos(IdCampo) | — | — |
| 3 | ValorSaldoExercicioAnterior | decimal(14,2) | N | — | — | — |
| 4 | ValorNoBimestre | decimal(18,0) | Y | — | — | — |
| 5 | ValorAteBimestre | decimal(14,2) | N | — | — | — |

## dbo.Anexo39_Movimento

Tabela · ~7.139 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMovimento | int | N | PK, IDENT | — | — |
| 2 | NomeDespesaPPP | varchar(255) | Y | — | — | — |
| 3 | IdTipoGrupoMovimento | tinyint | Y | FK → dbo.Anexo39_TipoGrupoMovimento(IdTipoGrupoMovimento) | — | — |
| 4 | IdTipoSituacaoDespesa | tinyint | Y | FK → dbo.Anexo39_TipoSituacaoDespesa(IdTipoSituacaoDespesa) | — | — |
| 5 | ValorAnoAnterior | decimal(14,2) | N | — | — | — |
| 6 | ValorAnoCorrente | decimal(14,2) | N | — | — | — |
| 7 | ValorAnoSubsequente1 | decimal(14,2) | N | — | — | — |
| 8 | ValorAnoSubsequente2 | decimal(14,2) | N | — | — | — |
| 9 | ValorAnoSubsequente3 | decimal(14,2) | N | — | — | — |
| 10 | ValorAnoSubsequente4 | decimal(14,2) | N | — | — | — |
| 11 | ValorAnoSubsequente5 | decimal(14,2) | N | — | — | — |
| 12 | ValorAnoSubsequente6 | decimal(14,2) | N | — | — | — |
| 13 | ValorAnoSubsequente7 | decimal(14,2) | N | — | — | — |
| 14 | ValorAnoSubsequente8 | decimal(14,2) | N | — | — | — |
| 15 | ValorAnoSubsequente9 | decimal(14,2) | N | — | — | — |
| 16 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 17 | IdCampo | smallint | Y | FK → dbo.Anexo39_Campos(IdCampo) | — | — |

## dbo.Anexo39_TipoCampo

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCampo | tinyint | N | PK | — | — |
| 2 | NomeTipoCampo | varchar(100) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Anexo39_TipoGrupoMovimento

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoGrupoMovimento | tinyint | N | PK | — | — |
| 2 | NomeTipoGrupoMovimento | varchar(100) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | IdSessao | int | N | — | — | — |
| 5 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo39_TipoSituacaoDespesa

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoDespesa | tinyint | N | PK | — | — |
| 2 | NomeTipoSituacaoDespesa | varchar(50) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | IdSessao | int | N | — | — | — |
| 5 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo40_InstrumentoNormativo

Tabela · ~759 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdInstrumentoNormativo | int | N | PK, IDENT | — | — |
| 2 | IdTipoNormaInstituidora | tinyint | Y | FK → dbo.Anexo40_TipoNormaInstituidora(IdTipoNormaInstituidora) | — | — |
| 3 | IdUCCI | int | Y | FK → dbo.Anexo40_UCCI(IdUCCI) | — | — |
| 4 | NumeroNorma | varchar(10) | Y | — | — | — |
| 5 | AnoNorma | smallint | Y | — | — | — |
| 6 | DataPublicacaoNorma | date | Y | — | — | — |
| 7 | VeiculoPublicacaoNorma | varchar(50) | Y | — | — | — |
| 8 | ArquivoNorma | varchar(8000) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo40_PessoaUCCI

Tabela · ~2.145 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPessoaUCCI | int | N | PK, IDENT | — | — |
| 2 | IdTipoUnidade | tinyint | N | FK → dbo.Anexo40_TipoUnidade(IdTipoUnidade) | — | — |
| 3 | IdTipoVinculo | tinyint | N | FK → dbo.Anexo40_TipoVinculo(IdTipoVinculo) | — | — |
| 4 | IdTipoAreaFormacao | tinyint | N | FK → dbo.Anexo40_TipoAreaFormacao(IdTipoAreaFormacao) | — | — |
| 5 | IdUCCI | int | N | FK → dbo.Anexo40_UCCI(IdUCCI) | — | — |
| 6 | DescricaoOutroTipoAreaFormacao | varchar(50) | Y | — | — | — |
| 7 | DesignacaoUnidade | varchar(100) | Y | — | — | — |
| 8 | NomePessoa | varchar(150) | Y | — | — | — |
| 9 | FuncaoPessoa | varchar(100) | Y | — | — | — |
| 10 | MatriculaPessoa | varchar(20) | Y | — | — | — |
| 11 | CpfPessoa | char(11) | N | — | — | — |
| 12 | TelefoneInstitucional | varchar(30) | Y | — | — | — |
| 13 | TelefoneCelular | varchar(30) | Y | — | — | — |
| 14 | Email | varchar(50) | Y | — | — | — |
| 15 | Ativo | bit | N | — | — | — |
| 16 | DataInclusao | smalldatetime | N | — | — | — |
| 17 | IdSessao | int | N | — | — | — |
| 18 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo40_TipoAreaFormacao

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAreaFormacao | tinyint | N | PK | — | — |
| 2 | NomeTipoAreaFormacao | varchar(50) | N | — | — | — |

## dbo.Anexo40_TipoFuncionamentoEfetivo

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoFuncionamentoEfetivo | tinyint | N | PK | — | — |
| 2 | NomeTipoFuncionamentoEfetivo | varchar(50) | N | — | — | — |

## dbo.Anexo40_TipoNormaInstituidora

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoNormaInstituidora | tinyint | N | PK | — | — |
| 2 | NomeTipoNormaInstituidora | varchar(50) | N | — | — | — |

## dbo.Anexo40_TipoProvidencia

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoProvidencia | tinyint | N | PK | — | — |
| 2 | NomeTipoProvidencia | varchar(50) | N | — | — | — |

## dbo.Anexo40_TipoSituacao

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacao | tinyint | N | PK | — | — |
| 2 | NomeTipoSituacao | varchar(50) | N | — | — | — |

## dbo.Anexo40_TipoUnidade

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoUnidade | tinyint | N | PK | — | — |
| 2 | NomeTipoUnidade | varchar(50) | N | — | — | — |
| 3 | SiglaTipoUnidade | char(4) | N | — | — | — |

## dbo.Anexo40_TipoVinculo

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoVinculo | tinyint | N | PK | — | — |
| 2 | NomeTipoVinculo | varchar(50) | N | — | — | — |

## dbo.Anexo40_UCCI

Tabela · ~506 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdUCCI | int | N | PK, IDENT | — | — |
| 2 | IdTipoSituacao | tinyint | N | FK → dbo.Anexo40_TipoSituacao(IdTipoSituacao) | — | — |
| 3 | IdTipoProvidencia | tinyint | Y | FK → dbo.Anexo40_TipoProvidencia(IdTipoProvidencia) | — | — |
| 4 | IdTipoFuncionamentoEfetivo | tinyint | Y | FK → dbo.Anexo40_TipoFuncionamentoEfetivo(IdTipoFuncionamentoEfetivo) | — | — |
| 5 | IdOrgao | int | N | — | — | — |
| 6 | DescricaoOutroTipoProvidencia | varchar(50) | Y | — | — | — |
| 7 | DescricaoOutroTipoFuncionamentoEfetivo | varchar(50) | Y | — | — | — |
| 8 | Justificativa | varchar(500) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo42_FuncaoResponsavel

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFuncaoResponsavel | tinyint | N | PK | — | — |
| 2 | NomeFuncaoResponsavel | varchar(50) | N | — | — | — |

## dbo.Anexo42_NaturezaUnidade

Tabela · ~18 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNaturezaUnidade | tinyint | N | PK | — | — |
| 2 | IdTipoAdministracaoUnidade | tinyint | N | FK → dbo.Anexo42_TipoAdministracaoUnidade(IdTipoAdministracaoUnidade) | — | — |
| 3 | NomeNaturezaUnidade | varchar(150) | N | — | — | — |

## dbo.Anexo42_PersonalidadeJuridicaUnidade

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPersonalidadeJuridicaUnidade | tinyint | N | PK | — | — |
| 2 | NomePersonalidadeJuridicaUnidade | varchar(20) | N | — | — | — |

## dbo.Anexo42_Responsavel

Tabela · ~4.127 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavel | int | N | PK, IDENT | — | — |
| 2 | CPF | char(11) | N | — | — | — |
| 3 | Nome | varchar(150) | N | — | — | — |
| 4 | CEP | char(9) | N | — | — | — |
| 5 | Logradouro | varchar(100) | N | — | — | — |
| 6 | Complemento | varchar(100) | Y | — | — | — |
| 7 | Bairro | varchar(50) | N | — | — | — |
| 8 | IdCidade | int | N | — | — | — |
| 9 | Telefone | varchar(30) | Y | — | — | — |
| 10 | Email | varchar(50) | Y | — | — | — |
| 11 | DataInclusao | smalldatetime | N | — | — | — |
| 12 | IdSessao | int | N | — | — | — |
| 13 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo42_ResponsavelUnidade

Tabela · ~9.005 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelUnidade | int | N | PK, IDENT | — | — |
| 2 | IdResponsavel | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 3 | IdUnidadeJurisdicionada | int | N | FK → dbo.Anexo42_UnidadeJurisdicionada(IdUnidadeJurisdicionada) | — | — |
| 4 | IdFuncaoResponsavel | tinyint | N | FK → dbo.Anexo42_FuncaoResponsavel(IdFuncaoResponsavel) | — | — |
| 5 | Cargo | varchar(50) | N | — | — | — |
| 6 | DataInicioGestao | date | N | — | — | — |
| 7 | DataTerminoGestao | date | Y | — | — | — |
| 8 | NomeArquivoAtoNomeacao | varchar(200) | Y | — | — | — |
| 9 | HashArquivoAtoNomeacao | char(32) | Y | — | — | — |
| 10 | NomeArquivoAtoExoneracao | varchar(200) | Y | — | — | — |
| 11 | HashArquivoAtoExoneracao | char(32) | Y | — | — | — |
| 12 | NomeArquivoFoto | varchar(200) | Y | — | — | — |
| 13 | HashArquivoFoto | char(32) | Y | — | — | — |
| 14 | Ativo | bit | N | — | — | — |
| 15 | DataInclusao | smalldatetime | N | — | — | — |
| 16 | IdSessao | int | N | — | — | — |
| 17 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo42_SituacaoUnidade

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoUnidade | tinyint | N | PK | — | — |
| 2 | NomeSituacaoUnidade | varchar(10) | N | — | — | — |

## dbo.Anexo42_TipoAdministracaoUnidade

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAdministracaoUnidade | tinyint | N | PK | — | — |
| 2 | NomeTipoAdministracaoUnidade | varchar(50) | N | — | — | — |

## dbo.Anexo42_UnidadeJurisdicionada

Tabela · ~3.485 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdUnidadeJurisdicionada | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | CNPJ | char(14) | N | — | — | — |
| 4 | NomeUnidade | varchar(200) | N | — | — | — |
| 5 | CodigoUnidadeGestora | char(11) | N | — | — | — |
| 6 | IdTipoAdministracaoUnidade | tinyint | N | FK → dbo.Anexo42_TipoAdministracaoUnidade(IdTipoAdministracaoUnidade) | — | — |
| 7 | IdSituacaoUnidade | tinyint | N | FK → dbo.Anexo42_SituacaoUnidade(IdSituacaoUnidade) | — | — |
| 8 | IdNaturezaUnidade | tinyint | N | FK → dbo.Anexo42_NaturezaUnidade(IdNaturezaUnidade) | — | — |
| 9 | OutraNatureza | varchar(100) | Y | — | — | — |
| 10 | ArquivoNorma | varchar(200) | Y | — | — | — |
| 11 | HashArquivoNorma | char(32) | Y | — | — | — |
| 12 | CEP | char(9) | N | — | — | — |
| 13 | Logradouro | varchar(100) | N | — | — | — |
| 14 | Complemento | varchar(100) | Y | — | — | — |
| 15 | Bairro | varchar(100) | N | — | — | — |
| 16 | IdCidade | int | N | — | — | — |
| 17 | Telefone | varchar(30) | Y | — | — | — |
| 18 | Email | varchar(50) | Y | — | — | — |
| 19 | Ativo | bit | N | — | — | — |
| 20 | DataInclusao | smalldatetime | N | — | — | — |
| 21 | DataAtualizacao | smalldatetime | N | — | — | — |
| 22 | IdSessao | int | N | — | — | — |
| 23 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Anexo42_UnidadeOrcamentaria

Tabela · ~9.404 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdUnidadeOrcamentaria | int | N | PK, IDENT | — | — |
| 2 | ClassificacaoInstitucional | char(10) | N | — | — | — |
| 3 | NomeUnidadeOrcamentaria | varchar(200) | N | — | — | — |
| 4 | IdUnidadeJurisdicionada | int | N | FK → dbo.Anexo42_UnidadeJurisdicionada(IdUnidadeJurisdicionada) | — | — |
| 5 | Ativo | bit | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.ContasAnuais

Tabela · ~45.647 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasAnuais | int | N | PK, IDENT | — | — |
| 2 | IdTipoEnvio | tinyint | N | FK → dbo.ContasAnuais_TipoEnvio(IdTipoEnvio) | — | — |
| 3 | IdNormaOrcamentaria | int | Y | FK → dbo.Documento_NormaOrcamentaria(IdNormaOrcamentaria) | — | — |
| 4 | IdContasDeGoverno | int | Y | FK → dbo.Documento_ContasDeGoverno(IdContasDeGoverno) | — | — |

## dbo.ContasAnuais_Anexo

Tabela · ~55 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnexo | int | N | PK, IDENT | — | — |
| 2 | AnoReferenciaInicial | smallint | N | — | — | — |
| 3 | AnoReferenciaFinal | smallint | N | — | — | — |
| 4 | IdTipoEnvio | tinyint | N | FK → dbo.ContasAnuais_TipoEnvio(IdTipoEnvio) | — | — |
| 5 | NomeAnexo | varchar(150) | N | — | — | — |
| 6 | Ordem | tinyint | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 12 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.ContasAnuais_Atributo

Tabela · ~4.133.866 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtributo | int | N | PK, IDENT | — | — |
| 2 | IdCampo | int | N | FK → dbo.ContasAnuais_Campo(IdCampo) | — | — |
| 3 | Texto | varchar(40) | Y | — | — | — |
| 4 | ImprimirTexto | char(1) | Y | — | — | — |
| 5 | Tipo | char(1) | N | — | — | — |
| 6 | Ordem | tinyint | N | — | — | — |
| 7 | Posicao | tinyint | N | — | — | — |
| 8 | Colunas | tinyint | N | — | — | — |
| 9 | Formula | varchar(MAX) | N | — | — | — |
| 10 | NumeroCasasDecimais | tinyint | N | — | — | — |
| 11 | DataInclusao | smalldatetime | N | — | — | — |
| 15 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.ContasAnuais_AtributoMovimentoData

Tabela · ~2.067.193 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasAnuais | int | N | PK, FK → dbo.ContasAnuais(IdContasAnuais) | — | — |
| 2 | IdTabelaCampo | int | N | PK, FK → dbo.ContasAnuais_TabelaCampo(IdTabelaCampo) | — | — |
| 3 | IdAtributo | int | N | PK, FK → dbo.ContasAnuais_Atributo(IdAtributo) | — | — |
| 4 | Valor | date | N | — | — | — |

## dbo.ContasAnuais_AtributoMovimentoLongo

Tabela · ~6.785.339 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasAnuais | int | N | PK, FK → dbo.ContasAnuais(IdContasAnuais) | — | — |
| 2 | IdTabelaCampo | int | N | PK, FK → dbo.ContasAnuais_TabelaCampo(IdTabelaCampo) | — | — |
| 3 | IdAtributo | int | N | PK, FK → dbo.ContasAnuais_Atributo(IdAtributo) | — | — |
| 4 | Valor | bigint | N | — | — | — |

## dbo.ContasAnuais_AtributoMovimentoNumero

Tabela · ~22.562.881 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasAnuais | int | N | PK, FK → dbo.ContasAnuais(IdContasAnuais) | — | — |
| 2 | IdTabelaCampo | int | N | PK, FK → dbo.ContasAnuais_TabelaCampo(IdTabelaCampo) | — | — |
| 3 | IdAtributo | int | N | PK, FK → dbo.ContasAnuais_Atributo(IdAtributo) | — | — |
| 4 | Valor | decimal(18,6) | N | — | — | — |

## dbo.ContasAnuais_AtributoMovimentoTexto

Tabela · ~11.306.374 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasAnuais | int | N | PK, FK → dbo.ContasAnuais(IdContasAnuais) | — | — |
| 2 | IdTabelaCampo | int | N | PK, FK → dbo.ContasAnuais_TabelaCampo(IdTabelaCampo) | — | — |
| 3 | IdAtributo | int | N | PK, FK → dbo.ContasAnuais_Atributo(IdAtributo) | — | — |
| 4 | Valor | varchar(MAX) | N | — | — | — |

## dbo.ContasAnuais_Campo

Tabela · ~1.364.024 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | int | N | PK, IDENT | — | — |
| 2 | NomeCampo | varchar(8000) | N | — | — | — |
| 3 | CodigoCampo | varchar(50) | Y | — | — | — |
| 4 | IdReferencia | tinyint | Y | FK → dbo.ContasAnuais_CampoReferencia(IdReferencia) | — | — |
| 5 | Grupo | bit | N | — | — | — |
| 6 | ImprimirCodigo | char(1) | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.ContasAnuais_CampoReferencia

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdReferencia | tinyint | N | PK | — | — |
| 2 | NomeReferencia | varchar(40) | N | — | — | — |

## dbo.ContasAnuais_Coluna

Tabela · ~678 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnexo | int | N | PK, FK → dbo.ContasAnuais_Anexo(IdAnexo) | — | — |
| 2 | IdTabela | int | N | PK, FK → dbo.ContasAnuais_Tabela(IdTabela) | — | — |
| 3 | NumeroColuna | tinyint | N | PK | — | — |
| 4 | AnoReferenciaInicial | smallint | N | — | — | — |
| 5 | AnoReferenciaFinal | smallint | N | — | — | — |
| 6 | NomeColuna | varchar(100) | N | — | — | — |
| 7 | Visivel | bit | N | — | — | — |
| 8 | Colunas | tinyint | N | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 13 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.ContasAnuais_Justificativa

Tabela · ~5.438 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnexo | int | N | PK, FK → dbo.ContasAnuais_Anexo(IdAnexo) | — | — |
| 2 | IdContasAnuais | int | N | PK, FK → dbo.ContasAnuais(IdContasAnuais) | — | — |
| 3 | Justificativa | varchar(MAX) | N | — | — | — |

## dbo.ContasAnuais_Tabela

Tabela · ~138 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTabela | int | N | PK, IDENT | — | — |
| 2 | IdAnexo | int | N | FK → dbo.ContasAnuais_Anexo(IdAnexo) | — | — |
| 3 | AnoReferenciaInicial | smallint | N | — | — | — |
| 4 | AnoReferenciaFinal | smallint | N | — | — | — |
| 5 | NomeTabela | varchar(150) | N | — | — | — |
| 6 | IncluirNome | bit | N | — | — | — |
| 7 | Ordem | tinyint | N | — | — | — |
| 8 | NumeroColunas | tinyint | N | — | — | — |
| 9 | NumeroNiveisMultiplasTabelas | tinyint | N | — | — | — |
| 10 | FiltrarIdContasAnuais | bit | N | — | — | — |
| 11 | DataInclusao | smalldatetime | N | — | — | — |
| 15 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.ContasAnuais_TabelaCampo

Tabela · ~19.944.950 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTabelaCampo | int | N | PK, IDENT | — | — |
| 2 | IdAnexo | int | N | FK → dbo.ContasAnuais_Anexo(IdAnexo) | — | — |
| 3 | IdTabela | int | N | FK → dbo.ContasAnuais_Tabela(IdTabela) | — | — |
| 4 | IdCampo | int | N | FK → dbo.ContasAnuais_Campo(IdCampo) | — | — |
| 5 | IdContasAnuais | int | Y | FK → dbo.ContasAnuais(IdContasAnuais) | — | — |
| 6 | IdOrgao | int | Y | — | — | — |
| 7 | AnoReferenciaInicial | smallint | N | — | — | — |
| 8 | AnoReferenciaFinal | smallint | N | — | — | — |
| 9 | Hierarquia | varchar(17) | N | — | — | — |
| 10 | Linha | int | N | — | — | — |
| 11 | Coluna | tinyint | N | — | — | — |
| 12 | Colunas | tinyint | N | — | — | — |
| 13 | DataInclusao | smalldatetime | N | — | — | — |
| 14 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.ContasAnuais_TipoEnvio

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoEnvio | tinyint | N | PK | — | — |
| 2 | NomeTipoEnvio | varchar(40) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Demonstrativo_Anexo01Movimento

Tabela · ~233.122 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo02Movimento

Tabela · ~763.224 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo03Movimento

Tabela · ~48.986 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo04Movimento

Tabela · ~25.240 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo06Movimento

Tabela · ~26.910 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo07Movimento

Tabela · ~14.544 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo08Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo09Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo10Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo15Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo16Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo17Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo18Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo19Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo20Movimento

Tabela · ~14.422 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo22Movimento

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Anexo39Movimento

Tabela · ~12.114 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdCampo | int | N | PK, FK → dbo.Demonstrativo_Campo(IdCampo) | — | — |
| 3 | IdColuna | int | N | PK, FK → dbo.Demonstrativo_Coluna(IdColuna) | — | — |
| 4 | Valor | decimal(14,2) | N | — | — | — |

## dbo.Demonstrativo_Campo

Tabela · ~2.363 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampo | int | N | PK, IDENT | — | — |
| 2 | IdQuadro | int | N | FK → dbo.Demonstrativo_Quadro(IdQuadro) | — | — |
| 3 | CodCampoSTN | varchar(150) | Y | — | — | — |
| 4 | DescricaoCampoSTN | varchar(200) | N | — | — | — |
| 5 | DescricaoCampoTCE | varchar(200) | Y | — | — | — |
| 6 | InsereValor | bit | N | — | — | — |
| 7 | Ordem | smallint | N | — | — | — |
| 8 | Nivel | tinyint | N | — | — | — |
| 9 | IntraOrcamentaria | bit | N | — | — | — |
| 10 | CampoDinamico | bit | N | — | — | — |
| 11 | CampoDescricaoComFormula | bit | N | — | — | — |
| 12 | DataInclusao | smalldatetime | N | — | — | — |
| 13 | IdSessao | int | N | — | — | — |
| 14 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Demonstrativo_Coluna

Tabela · ~815 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdColuna | int | N | PK, IDENT | — | — |
| 2 | IdQuadro | int | N | FK → dbo.Demonstrativo_Quadro(IdQuadro) | — | — |
| 3 | CodColunaSTN | varchar(150) | Y | — | — | — |
| 4 | DescricaoColunaSTN | varchar(200) | N | — | — | — |
| 5 | DescricaoColunaTCE | varchar(200) | Y | — | — | — |
| 6 | Ordem | tinyint | N | — | — | — |
| 7 | ColunaDescricaoComFormula | bit | N | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Demonstrativo_ImportacaoArquivoSTN

Tabela · ~2.644 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdImportacaoArquivoSTN | int | N | PK, IDENT | — | — |
| 2 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 3 | NomeArquivoSTN | varchar(100) | Y | — | — | — |
| 4 | IdTipoArquivo | tinyint | N | FK → dbo.Demonstrativo_TipoArquivo(IdTipoArquivo) | — | — |
| 5 | IdTipoSituacaoColeta | tinyint | N | FK → dbo.Demonstrativo_TipoSituacaoColeta(IdTipoSituacaoColeta) | — | — |
| 6 | DataColetaArquivo | smalldatetime | Y | — | — | — |

## dbo.Demonstrativo_Layout

Tabela · ~42 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLayout | int | N | PK, IDENT | — | — |
| 2 | IdAnexoLRF | tinyint | N | FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 3 | AnoReferenciaInicial | smallint | N | — | — | — |
| 4 | AnoReferenciaFinal | smallint | Y | — | — | — |
| 5 | DescricaoLayout | varchar(200) | Y | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Demonstrativo_LayoutOrgaoNatureza

Tabela · ~92 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLayoutOrgaoNatureza | int | N | PK, IDENT | — | — |
| 2 | IdLayout | int | N | FK → dbo.Demonstrativo_Layout(IdLayout) | — | — |
| 3 | IdOrgaoNatureza | tinyint | N | — | — | — |
| 4 | IdTipoPeriodo | tinyint | Y | FK → dbo.Envio_TipoPeriodo(IdTipoPeriodo) | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Demonstrativo_Quadro

Tabela · ~183 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdQuadro | int | N | PK, IDENT | — | — |
| 2 | IdLayout | int | N | FK → dbo.Demonstrativo_Layout(IdLayout) | — | — |
| 3 | CodQuadroSTN | varchar(150) | Y | — | — | — |
| 4 | DescricaoQuadroSTN | varchar(200) | N | — | — | — |
| 5 | DescricaoQuadroTCE | varchar(200) | Y | — | — | — |
| 6 | Ordem | tinyint | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |
| 10 | QuadroDinamico | bit | N | — | — | — |

## dbo.Demonstrativo_TipoArquivo

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoArquivo | tinyint | N | PK | — | — |
| 2 | DescricaoTipoArquivo | varchar(30) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |

## dbo.Demonstrativo_TipoSituacaoColeta

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoColeta | tinyint | N | PK | — | — |
| 2 | DescricaoTipoSituacaoColeta | varchar(30) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |

## dbo.Documento_AnexoContasDeGestao

Tabela · ~146.696 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnexoContasDeGestao | int | N | PK, IDENT | — | — |
| 2 | IdContasDeGestao | int | N | FK → dbo.Documento_ContasDeGestao(IdContasDeGestao) | — | — |
| 3 | IdTipoAnexoContasDeGestao | tinyint | N | FK → dbo.Documento_TipoAnexoContasDeGestao(IdTipoAnexoContasDeGestao) | — | — |
| 4 | NomeArquivo | varchar(500) | Y | — | — | — |
| 5 | HashArquivo | char(32) | Y | — | — | — |
| 6 | CPFAssinador | char(11) | Y | — | — | — |
| 7 | NomeAssinador | varchar(100) | Y | — | — | — |
| 8 | Observacoes | varchar(500) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_AnexoContasDeGoverno

Tabela · ~72.974 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnexoContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | IdContasDeGoverno | int | N | FK → dbo.Documento_ContasDeGoverno(IdContasDeGoverno) | — | — |
| 3 | IdTipoAnexoContasDeGoverno | tinyint | N | FK → dbo.Documento_TipoAnexoContasDeGoverno(IdTipoAnexoContasDeGoverno) | — | — |
| 4 | NomeArquivo | varchar(500) | N | — | — | — |
| 5 | HashArquivo | char(32) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |
| 9 | NomeGestor | varchar(255) | Y | — | — | — |
| 10 | CpfGestor | varchar(11) | Y | — | — | — |
| 11 | NomeContabilista | varchar(255) | Y | — | — | — |
| 12 | CpfContabilista | varchar(11) | Y | — | — | — |

## dbo.Documento_AssinadorAnexoContasDeGoverno

Tabela · ~136.597 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAssinadorAnexoContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | IdAnexoContasDeGoverno | int | N | FK → dbo.Documento_AnexoContasDeGoverno(IdAnexoContasDeGoverno) | — | — |
| 3 | IdTipoAssinadorAnexoContasDeGoverno | tinyint | N | FK → dbo.Documento_TipoAssinadorAnexoContasDeGoverno(IdTipoAssinadorAnexoContasDeGoverno) | — | — |
| 4 | CPFAssinador | char(11) | N | — | — | — |
| 5 | NomeAssinador | varchar(150) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_AssinadorDeclaracaoContasDeGoverno

Tabela · ~24 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAssinadorDeclaracaoContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | IdDeclaracaoContasDeGoverno | int | N | FK → dbo.Documento_DeclaracaoContasDeGoverno(IdDeclaracaoContasDeGoverno) | — | — |
| 3 | IdTipoAssinadorAnexoContasDeGoverno | tinyint | N | FK → dbo.Documento_TipoAssinadorAnexoContasDeGoverno(IdTipoAssinadorAnexoContasDeGoverno) | — | — |
| 4 | CPFAssinador | char(11) | N | — | — | — |
| 5 | NomeAssinador | varchar(150) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_AssinadorNotaContasDeGoverno

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAssinadorNotaContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | IdNotaContasDeGoverno | int | N | FK → dbo.Documento_NotaContasDeGoverno(IdNotaContasDeGoverno) | — | — |
| 3 | IdTipoAssinadorAnexoContasDeGoverno | tinyint | N | FK → dbo.Documento_TipoAssinadorAnexoContasDeGoverno(IdTipoAssinadorAnexoContasDeGoverno) | — | — |
| 4 | CPFAssinador | char(11) | N | — | — | — |
| 5 | NomeAssinador | varchar(150) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_ComprovacaoPublicacao

Tabela · ~22.213 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdComprovacaoPublicacao | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | IdPeriodo | tinyint | N | FK → dbo.Envio_Periodo(IdPeriodo) | — | — |
| 4 | IdTipoPublicacao | tinyint | N | FK → dbo.Documento_TipoPublicacao(IdTipoPublicacao) | — | — |
| 5 | IdResponsavel | int | Y | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 6 | AnoReferencia | smallint | N | — | — | — |
| 7 | VeiculoPublicacao | varchar(150) | N | — | — | — |
| 8 | DataPublicacao | date | N | — | — | — |
| 9 | NumeroPagina | varchar(50) | Y | — | — | — |
| 10 | NumeroEdicao | varchar(50) | Y | — | — | — |
| 11 | EnderecoEletronico | varchar(500) | Y | — | — | — |
| 12 | Justificativa | varchar(500) | Y | — | — | — |
| 13 | NomeArquivo | varchar(500) | N | — | — | — |
| 14 | HashArquivo | char(32) | N | — | — | — |
| 15 | DataInativacao | smalldatetime | Y | — | — | — |
| 16 | DataInclusao | smalldatetime | N | — | — | — |
| 17 | IdSessao | int | N | — | — | — |
| 18 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_ContasDeGestao

Tabela · ~5.951 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasDeGestao | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | AnoReferencia | smallint | N | — | — | — |
| 4 | IdResponsavel | int | N | — | — | — |
| 5 | Enviado | bit | N | — | — | — |
| 6 | IdContasDeGestaoRetificadora | int | Y | — | — | — |
| 7 | DataEnvio | smalldatetime | Y | — | — | — |
| 8 | PermiteRetificacao | bit | N | — | — | — |
| 9 | JustificativaRetificacao | varchar(500) | Y | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_ContasDeGoverno

Tabela · ~1.902 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | AnoReferencia | smallint | N | — | — | — |
| 4 | IdResponsavel | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 5 | NomeArquivoXml | varchar(500) | Y | — | — | — |
| 6 | HashArquivoXml | char(32) | Y | — | — | — |
| 7 | CPFAssinadorGestor | char(11) | Y | — | — | — |
| 8 | NomeAssinadorGestor | varchar(150) | Y | — | — | — |
| 9 | CPFAssinadorContabilista | char(11) | Y | — | — | — |
| 10 | NomeAssinadorContabilista | varchar(150) | Y | — | — | — |
| 11 | IdSituacaoProcessamentoXml | tinyint | Y | FK → dbo.Envio_SituacaoProcessamento(IdSituacaoProcessamento) | — | — |
| 12 | Enviado | bit | N | — | — | — |
| 13 | PermiteRetificacao | bit | N | — | — | — |
| 14 | JustificativaRetificacao | varchar(500) | Y | — | — | — |
| 15 | DataEnvio | smalldatetime | Y | — | — | — |
| 16 | DataProcessamentoXml | datetime | Y | — | — | — |
| 17 | Retificadora | bit | N | — | — | — |
| 18 | DataInclusao | smalldatetime | N | — | — | — |
| 19 | IdSessao | int | N | — | — | — |
| 20 | IdSessaoOperacao | int | Y | — | — | — |
| 21 | IdProcesso | int | Y | — | — | Chamado-40558 - Identificador do processo - Criado quando a conta de governo estoura o prazo de envio |
| 22 | NumeroProcesso | char(6) | Y | — | — | Chamado-40558 - Número do processo - Criado quando a conta de governo estoura o prazo de envio |
| 23 | AnoProcesso | char(4) | Y | — | — | Chamado-40558 - Ano do processo - Criado quando a conta de governo estoura o prazo de envio |

## dbo.Documento_ContasDeGoverno_Autuacao_Processual_Notificacoes

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | Id | int | N | PK, IDENT | — | — |
| 2 | MensagensSucesso | nvarchar(MAX) | Y | — | — | — |
| 3 | MensagensErro | nvarchar(MAX) | Y | — | — | — |
| 4 | HouveErros | bit | N | — | — | — |
| 5 | QtdTotalContasGoverno | int | Y | — | — | — |
| 6 | QtdTotalContasGovernoProtocoladasComSucesso | int | Y | — | — | — |
| 7 | QtdTotalContasGovernoTramitadasComSucesso | int | Y | — | — | — |
| 8 | QtdTotalContasGovernoAnexos | int | Y | — | — | — |
| 9 | QtdTotalContasGovernoAnexosEnviados | int | Y | — | — | — |
| 10 | SegundosDeTimeout | int | Y | — | — | — |
| 11 | Timeout | nvarchar(8) | Y | — | — | — |
| 12 | DataInicioProcessamento | smalldatetime | N | — | — | — |
| 13 | DataInclusao | smalldatetime | N | — | — | — |
| 14 | IdSessao | int | N | — | — | — |
| 15 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Documento_ContasDeGovernoHistorico

Tabela · ~799 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContasDeGovernoHistorico | int | N | PK, IDENT | — | — |
| 2 | IdContasDeGoverno | int | N | — | — | — |
| 3 | IdAnexoContasGovernoAntigo | int | Y | — | — | — |
| 4 | NomeArquivoXml | varchar(500) | Y | — | — | — |
| 5 | HashArquivoXml | char(32) | Y | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_CriticaXmlContasDeGoverno

Tabela · ~301 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriticaXmlContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | MensagemCriticaXmlContasDeGoverno | varchar(MAX) | N | — | — | — |
| 3 | IdTipoCriticaProcessamento | tinyint | N | FK → dbo.Envio_TipoCriticaProcessamento(IdTipoCriticaProcessamento) | — | — |
| 4 | IdContasDeGoverno | int | N | FK → dbo.Documento_ContasDeGoverno(IdContasDeGoverno) | — | — |

## dbo.Documento_CriticaXmlNormaOrcamentaria

Tabela · ~1.536 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriticaXmlNormaOrcamentaria | int | N | PK, IDENT | — | — |
| 2 | MensagemCriticaXmlNormaOrcamentaria | varchar(MAX) | N | — | — | — |
| 3 | IdTipoCriticaProcessamento | tinyint | N | FK → dbo.Envio_TipoCriticaProcessamento(IdTipoCriticaProcessamento) | — | — |
| 4 | IdNormaOrcamentaria | int | N | FK → dbo.Documento_NormaOrcamentaria(IdNormaOrcamentaria) | — | — |

## dbo.Documento_DeclaracaoContasDeGestao

Tabela · ~51.103 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDeclaracaoContasDeGestao | int | N | PK, IDENT | — | — |
| 2 | IdContasDeGestao | int | N | FK → dbo.Documento_ContasDeGestao(IdContasDeGestao) | — | — |
| 3 | IdTipoAnexoContasDeGestao | tinyint | N | FK → dbo.Documento_TipoAnexoContasDeGestao(IdTipoAnexoContasDeGestao) | — | — |
| 4 | DeclaracaoNegativa | varchar(1000) | Y | — | — | — |
| 5 | NomeArquivo | varchar(500) | Y | — | — | — |
| 6 | HashArquivo | char(32) | Y | — | — | — |
| 7 | CPFAssinador | char(11) | Y | — | — | — |
| 8 | NomeAssinador | varchar(100) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_DeclaracaoContasDeGoverno

Tabela · ~126 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDeclaracaoContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | IdContasDeGoverno | int | N | FK → dbo.Documento_ContasDeGoverno(IdContasDeGoverno) | — | — |
| 3 | IdTipoAnexoContasDeGoverno | tinyint | N | FK → dbo.Documento_TipoAnexoContasDeGoverno(IdTipoAnexoContasDeGoverno) | — | — |
| 4 | DeclaracaoNegativa | varchar(1000) | Y | — | — | — |
| 5 | NomeArquivo | varchar(500) | Y | — | — | — |
| 6 | HashArquivo | char(32) | Y | — | — | — |
| 7 | CPFAssinador | char(11) | Y | — | — | — |
| 8 | NomeAssinador | varchar(100) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_DiarioOficial

Tabela · ~787.411 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDiarioOficial | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | IdEnviador | int | Y | FK → dbo.Documento_DiarioOficialEnviador(IdEnviador) | — | — |
| 4 | Numero | varchar(50) | N | — | — | — |
| 5 | AnoReferencia | smallint | N | — | — | — |
| 6 | DataPublicacao | date | N | — | — | — |
| 7 | DataDisponibilizacao | date | N | — | — | — |
| 8 | NomeArquivo | varchar(500) | N | — | — | — |
| 9 | HashArquivo | char(32) | N | — | — | — |
| 10 | CPFCNPJAssinador | varchar(14) | N | — | — | — |
| 11 | NomeAssinador | varchar(100) | N | — | — | — |
| 12 | Observacoes | varchar(500) | Y | — | — | — |
| 13 | DataInclusao | smalldatetime | N | — | — | — |
| 14 | IdSessao | int | N | — | — | — |
| 15 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_DiarioOficialEnviador

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEnviador | int | N | PK, IDENT | — | — |
| 2 | NomeEnviador | varchar(100) | N | — | — | — |
| 3 | HashEnviador | char(32) | N | — | — | — |
| 4 | ResponsavelEnviador | varchar(100) | N | — | — | — |
| 5 | CPFEnviador | char(11) | N | — | — | — |
| 6 | Ativo | bit | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |
| 12 | EnderecoEletronicoEnviador | varchar(150) | N | — | — | — |

## dbo.Documento_DiarioOficialOrgaosEnviador

Tabela · ~593 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgaosEnviador | int | N | PK, IDENT | — | — |
| 2 | IdEnviador | int | N | FK → dbo.Documento_DiarioOficialEnviador(IdEnviador) | — | — |
| 3 | IdOrgao | int | N | — | — | — |
| 4 | Ativo | bit | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_DocumentacaoDiversa

Tabela · ~15.102 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDocumentacaoDiversa | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | AnoReferencia | smallint | N | — | — | — |
| 4 | IdTipoDocumentacaoDiversa | tinyint | N | FK → dbo.Documento_TipoDocumentacaoDiversa(IdTipoDocumentacaoDiversa) | — | — |
| 5 | IdResponsavel | int | Y | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 6 | DataElaboracaoRealizacao | date | N | — | — | — |
| 7 | NomeArquivo | varchar(500) | N | — | — | — |
| 8 | HashArquivo | char(32) | N | — | — | — |
| 9 | Ativo | bit | N | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_GrupoAnexoContasDeGestao

Tabela · ~369 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoContasDeGestao | tinyint | N | PK, FK → dbo.Documento_GrupoContasDeGestao(IdGrupoContasDeGestao) | — | — |
| 2 | IdTipoAnexoContasDeGestao | tinyint | N | PK, FK → dbo.Documento_TipoAnexoContasDeGestao(IdTipoAnexoContasDeGestao) | — | — |
| 3 | Ordem | tinyint | N | — | — | — |
| 4 | NumeroAnexo | varchar(5) | Y | — | — | Campo utilizado para identifica��o do numero Anexo, devido 1 anexo ter numero diferente para grupos de orgaos. |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Documento_GrupoAnexoContasDeGoverno

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoContasDeGoverno | tinyint | N | PK, FK → dbo.Documento_GrupoContasDeGoverno(IdGrupoContasDeGoverno) | — | — |
| 2 | IdTipoAnexoContasDeGoverno | tinyint | N | PK, FK → dbo.Documento_TipoAnexoContasDeGoverno(IdTipoAnexoContasDeGoverno) | — | — |
| 3 | Ordem | tinyint | N | — | — | — |
| 4 | NumeroAnexo | varchar(5) | Y | — | — | Campo utilizado para identificao do numero Anexo, devido 1 anexo ter numero diferente para grupos de orgaos. |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Documento_GrupoContasDeGestao

Tabela · ~10 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoContasDeGestao | tinyint | N | PK | — | — |
| 2 | NumeroGrupoContasDeGestao | tinyint | N | — | — | — |
| 3 | DescricaoGrupoContasDeGestao | varchar(500) | N | — | — | — |

## dbo.Documento_GrupoContasDeGoverno

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoContasDeGoverno | tinyint | N | PK | — | — |
| 2 | NumeroGrupoContasDeGoverno | tinyint | N | — | — | — |
| 3 | DescricaoGrupoContasDeGoverno | varchar(500) | N | — | — | — |

## dbo.Documento_GrupoDocumentacaoDiversa

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoDocumentacaoDiversa | tinyint | N | PK | — | — |
| 2 | NomeGrupoDocumentacaoDiversa | varchar(200) | N | — | — | — |

## dbo.Documento_GrupoOrgaoContasDeGestao

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgao | int | N | PK | — | — |
| 2 | IdGrupoContasDeGestao | tinyint | N | PK, FK → dbo.Documento_GrupoContasDeGestao(IdGrupoContasDeGestao) | — | — |

## dbo.Documento_GrupoUnidadeJurisdicionadaContasDeGestao

Tabela · ~21 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoUnidadeJurisdicionadaContasDeGestao | int | N | PK | — | — |
| 2 | IdGrupoContasDeGestao | tinyint | N | PK, FK → dbo.Documento_GrupoContasDeGestao(IdGrupoContasDeGestao) | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Documento_GrupoUnidadeJurisdicionadaContasDeGoverno

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupoUnidadeJurisdicionadaContasDeGoverno | int | N | PK | — | — |
| 2 | IdGrupoContasDeGoverno | tinyint | N | PK, FK → dbo.Documento_GrupoContasDeGoverno(IdGrupoContasDeGoverno) | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Documento_NormaOrcamentaria

Tabela · ~46.441 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNormaOrcamentaria | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | IdTipoNormaOrcamentaria | tinyint | N | FK → dbo.Documento_TipoNormaOrcamentaria(IdTipoNormaOrcamentaria) | — | — |
| 4 | IdResponsavel | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 5 | IdSituacaoProcessamento | tinyint | N | FK → dbo.Envio_SituacaoProcessamento(IdSituacaoProcessamento) | — | — |
| 6 | AnoReferencia | smallint | Y | — | — | — |
| 7 | PeriodoReferenciaInicial | smallint | Y | — | — | — |
| 8 | PeriodoReferenciaFinal | smallint | Y | — | — | — |
| 9 | VeiculoPublicacao | varchar(150) | N | — | — | — |
| 10 | DataPublicacao | date | N | — | — | — |
| 11 | NumeroPagina | varchar(50) | Y | — | — | — |
| 12 | NumeroEdicao | varchar(10) | Y | — | — | — |
| 13 | EnderecoEletronico | varchar(500) | Y | — | — | — |
| 14 | NomeArquivo | varchar(500) | N | — | — | — |
| 15 | HashArquivo | char(32) | N | — | — | — |
| 16 | NomeArquivoXml | varchar(500) | Y | — | — | — |
| 17 | HashArquivoXml | char(32) | Y | — | — | — |
| 18 | DataProcessamentoXml | datetime | Y | — | — | — |
| 19 | Ativo | bit | N | — | — | — |
| 20 | DataInclusao | smalldatetime | N | — | — | — |
| 21 | IdSessao | int | N | — | — | — |
| 22 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_NotaContasDeGoverno

Tabela · ~171 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdNotaContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | IdContasDeGoverno | int | N | FK → dbo.Documento_ContasDeGoverno(IdContasDeGoverno) | — | — |
| 3 | IdTipoAnexoContasDeGoverno | tinyint | N | FK → dbo.Documento_TipoAnexoContasDeGoverno(IdTipoAnexoContasDeGoverno) | — | — |
| 4 | NotaExplicativa | varchar(1000) | Y | — | — | — |
| 5 | NomeArquivo | varchar(500) | Y | — | — | — |
| 6 | HashArquivo | char(32) | Y | — | — | — |
| 7 | CPFAssinador | char(11) | Y | — | — | — |
| 8 | NomeAssinador | varchar(100) | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_PeriodoPublicacao

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPeriodoPublicacao | tinyint | N | PK | — | — |
| 2 | IdTipoPublicacao | tinyint | N | FK → dbo.Documento_TipoPublicacao(IdTipoPublicacao) | — | — |
| 3 | IdTipoPeriodo | tinyint | N | FK → dbo.Envio_TipoPeriodo(IdTipoPeriodo) | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | IdSessao | int | N | — | — | — |
| 6 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_PrazoContasDeGestao

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoContasDeGestao | int | N | PK, IDENT | — | — |
| 2 | AnoReferencia | smallint | N | — | — | — |
| 3 | DataPrazoEnvio | date | N | — | — | — |
| 4 | DataPrazoTempestivo | date | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_PrazoContasDeGoverno

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoContasDeGoverno | int | N | PK, IDENT | — | — |
| 2 | AnoReferencia | smallint | N | — | — | — |
| 3 | DataPrazoEnvio | date | N | — | — | — |
| 4 | DataPrazoTempestivo | date | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Documento_TipoAnexoContasDeGestao

Tabela · ~66 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoContasDeGestao | tinyint | N | PK | — | — |
| 2 | NumeroAnexo | varchar(5) | Y | — | — | — |
| 3 | NomeTipoAnexoContasDeGestao | varchar(150) | Y | — | — | — |
| 4 | DescricaoTipoAnexoContasDeGestao | varchar(800) | Y | — | — | — |
| 5 | IdTipoFormatoAnexo | tinyint | Y | — | — | — |
| 6 | PossuiDadosSensiveis | bit | N | — | — | — |

## dbo.Documento_TipoAnexoContasDeGestaoAnexoLRF

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoContasDeGestao | tinyint | N | PK, FK → dbo.Documento_TipoAnexoContasDeGestao(IdTipoAnexoContasDeGestao) | — | — |
| 2 | IdAnexoLRF | tinyint | N | PK, FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |

## dbo.Documento_TipoAnexoContasDeGoverno

Tabela · ~114 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoContasDeGoverno | tinyint | N | PK | — | — |
| 2 | NumeroAnexo | varchar(5) | Y | — | — | — |
| 3 | NomeTipoAnexoContasDeGoverno | varchar(150) | N | — | — | — |
| 4 | DescricaoTipoAnexoContasDeGoverno | varchar(MAX) | Y | — | — | — |
| 5 | EnvioObrigatorio | bit | N | — | — | — |
| 6 | AnoReferenciaInicial | smallint | Y | — | — | — |
| 7 | AnoReferenciaFinal | smallint | Y | — | — | — |
| 8 | IdTipoFormatoAnexo | tinyint | Y | — | — | — |
| 9 | DocumentoEstadual | bit | N | — | — | — |

## dbo.Documento_TipoAnexoContasDeGovernoContasAnuaisAnexo

Tabela · ~49 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoContasDeGoverno | tinyint | N | PK, FK → dbo.Documento_TipoAnexoContasDeGoverno(IdTipoAnexoContasDeGoverno) | — | — |
| 2 | IdAnexoContasAnuais | int | N | PK, FK → dbo.ContasAnuais_Anexo(IdAnexo) | — | — |

## dbo.Documento_TipoAnexoTipoAssinadorContasDeGestao

Tabela · ~64 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoContasDeGestao | tinyint | N | PK, FK → dbo.Documento_TipoAnexoContasDeGestao(IdTipoAnexoContasDeGestao) | — | — |
| 2 | IdTipoAssinadorAnexoContasDeGestao | tinyint | N | PK, FK → dbo.Documento_TipoAssinadorAnexoContasDeGestao(IdTipoAssinadorAnexoContasDeGestao) | — | — |

## dbo.Documento_TipoAnexoTipoAssinadorContasDeGoverno

Tabela · ~216 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoContasDeGoverno | tinyint | N | PK, FK → dbo.Documento_TipoAnexoContasDeGoverno(IdTipoAnexoContasDeGoverno) | — | — |
| 2 | IdTipoAssinadorAnexoContasDeGoverno | tinyint | N | PK, FK → dbo.Documento_TipoAssinadorAnexoContasDeGoverno(IdTipoAssinadorAnexoContasDeGoverno) | — | — |

## dbo.Documento_TipoAnexoTipoFormatoContasDeGoverno

Tabela · ~114 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoContasDeGoverno | tinyint | N | PK, FK → dbo.Documento_TipoAnexoContasDeGoverno(IdTipoAnexoContasDeGoverno) | — | — |
| 2 | IdTipoFormatoAnexo | tinyint | N | PK, FK → dbo.Documento_TipoFormatoAnexo(IdTipoFormatoAnexo) | — | — |

## dbo.Documento_TipoAssinadorAnexoContasDeGestao

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAssinadorAnexoContasDeGestao | tinyint | N | PK | — | — |
| 2 | NomeTipoAssinadorAnexoContasDeGestao | varchar(50) | N | — | — | — |

## dbo.Documento_TipoAssinadorAnexoContasDeGoverno

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAssinadorAnexoContasDeGoverno | tinyint | N | PK | — | — |
| 2 | NomeTipoAssinadorAnexoContasDeGoverno | varchar(50) | N | — | — | — |

## dbo.Documento_TipoDocumentacaoDiversa

Tabela · ~20 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumentacaoDiversa | tinyint | N | PK | — | — |
| 2 | NomeTipoDocumentacaoDiversa | varchar(150) | N | — | — | — |
| 3 | IdGrupoDocumentacaoDiversa | tinyint | Y | FK → dbo.Documento_GrupoDocumentacaoDiversa(IdGrupoDocumentacaoDiversa) | — | — |
| 4 | Ativo | bit | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Documento_TipoFormatoAnexo

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoFormatoAnexo | tinyint | N | PK | — | — |
| 2 | ExtensaoFormatoAnexo | varchar(20) | N | — | — | — |

## dbo.Documento_TipoNormaOrcamentaria

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoNormaOrcamentaria | tinyint | N | PK | — | — |
| 2 | SiglaTipoNormaOrcamentaria | varchar(20) | N | — | — | — |
| 3 | NomeTipoNormaOrcamentaria | varchar(100) | N | — | — | — |

## dbo.Documento_TipoPublicacao

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoPublicacao | tinyint | N | PK | — | — |
| 2 | SiglaTipoPublicacao | varchar(10) | N | — | — | — |
| 3 | NomeTipoPublicacao | varchar(100) | N | — | — | — |

## dbo.EmendaParlamentar_AnaliseEnvio

Tabela · ~162 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnaliseEnvio | int | N | PK, IDENT | — | — |
| 2 | IdEnvio | int | N | FK → dbo.EmendaParlamentar_Envio(IdEnvio) | — | — |
| 3 | AnaliseAutomatica | bit | N | — | — | — |
| 4 | IdTipoSituacaoAnalise | tinyint | N | FK → dbo.EmendaParlamentar_TipoSituacaoAnalise(IdTipoSituacaoAnalise) | — | — |
| 5 | IdOperadorInternoAnalise | int | N | — | — | — |
| 6 | NomeAnexoAnalise | varchar(250) | Y | — | — | — |
| 7 | MotivoNaoCertificada | varchar(8000) | Y | — | — | — |
| 8 | DataInclusao | datetime2(7) | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |
| 11 | NomeOperadorInternoAnalise | varchar(100) | Y | — | — | — |

## dbo.EmendaParlamentar_AnaliseEnvioResposta

Tabela · ~1.581 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnaliseEnvioResposta | int | N | PK, IDENT | — | — |
| 2 | IdAnaliseEnvio | int | N | FK → dbo.EmendaParlamentar_AnaliseEnvio(IdAnaliseEnvio) | — | — |
| 3 | IdEnvioResposta | int | N | FK → dbo.EmendaParlamentar_EnvioResposta(IdEnvioResposta) | — | — |
| 4 | IdTipoResultadoAnalise | tinyint | N | FK → dbo.EmendaParlamentar_TipoResultadoAnalise(IdTipoResultadoAnalise) | — | — |
| 5 | TextoAnalise | varchar(5000) | Y | — | — | — |
| 6 | DataInclusao | datetime2(7) | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.EmendaParlamentar_Envio

Tabela · ~174 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEnvio | int | N | PK, FK → dbo.EmendaParlamentar_Envio(IdEnvio), IDENT | — | — |
| 2 | IdUnidadeJurisdicionada | int | N | — | — | — |
| 3 | IdTipoSituacao | tinyint | N | — | — | — |
| 4 | PossuiEmendaParlamentar | bit | N | — | — | — |
| 5 | IdPessoaGestor | int | N | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 6 | IdPessoaControlador | int | N | FK → dbo.Anexo40_PessoaUCCI(IdPessoaUCCI) | — | — |
| 7 | TextoComplementar | varchar(8000) | Y | — | — | — |
| 8 | HashArquivoRecibo | char(64) | N | — | — | — |
| 9 | NomeArquivoRecibo | varchar(100) | Y | — | — | — |
| 10 | MotivoNaoCertificada | varchar(8000) | Y | — | — | — |
| 11 | CPFAssinaturaGestor | char(11) | Y | — | — | — |
| 12 | CPFAssinaturaControleInterno | char(11) | Y | — | — | — |
| 13 | URLPortalTransparencia | varchar(250) | Y | — | — | — |
| 14 | DataUltimaAtualizacao | datetime2(7) | Y | — | — | — |
| 15 | DataInclusao | datetime2(7) | N | — | — | — |
| 16 | IdSessao | int | N | — | — | — |
| 17 | IdSessaoOperacao | int | Y | — | — | — |
| 18 | DataSubmissaoAnalise | datetime2(7) | Y | — | — | — |

## dbo.EmendaParlamentar_EnvioResposta

Tabela · ~1.632 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEnvioResposta | int | N | PK, IDENT | — | — |
| 2 | IdEnvio | int | N | FK → dbo.EmendaParlamentar_Envio(IdEnvio) | — | — |
| 3 | IdPergunta | int | N | FK → dbo.EmendaParlamentar_Pergunta(IdPergunta) | — | — |
| 4 | IdTipoOpcaoResposta | tinyint | N | FK → dbo.EmendaParlamentar_TipoOpcaoResposta(IdTipoOpcaoResposta) | — | — |
| 5 | RespostaLivre | varchar(8000) | Y | — | — | — |
| 6 | Observacao | varchar(8000) | Y | — | — | — |
| 7 | DataInclusao | datetime2(7) | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.EmendaParlamentar_EnvioRespostaAnexo

Tabela · ~1.498 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEnvioRespostaAnexo | int | N | PK, IDENT | — | — |
| 2 | IdEnvioResposta | int | N | FK → dbo.EmendaParlamentar_EnvioResposta(IdEnvioResposta) | — | — |
| 3 | NomeAnexo | varchar(250) | N | — | — | — |
| 4 | DataInclusao | datetime2(7) | N | — | — | — |
| 5 | IdSessao | int | N | — | — | — |
| 6 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.EmendaParlamentar_Pergunta

Tabela · ~17 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPergunta | int | N | PK, IDENT | — | — |
| 2 | IdTipoSecao | tinyint | N | FK → dbo.EmendaParlamentar_TipoSecao(IdTipoSecao) | — | — |
| 3 | IdTipoResposta | tinyint | N | FK → dbo.EmendaParlamentar_TipoResposta(IdTipoResposta) | — | — |
| 4 | DescricaoPerguntaPadrao | varchar(800) | Y | — | — | — |
| 5 | DescricaoPerguntaGoverno | varchar(800) | Y | — | — | — |
| 6 | Ordem | char(1) | Y | — | — | — |
| 7 | Ativo | bit | N | — | — | — |
| 8 | DataExclusao | datetime2(7) | Y | — | — | — |
| 9 | DataInclusao | datetime2(7) | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.EmendaParlamentar_TipoOpcaoResposta

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoOpcaoResposta | tinyint | N | PK | — | — |
| 2 | DescricaoTipoOpcaoResposta | varchar(20) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataExclusao | datetime2(7) | Y | — | — | — |

## dbo.EmendaParlamentar_TipoResposta

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoResposta | tinyint | N | PK | — | — |
| 2 | DescricaoTipoResposta | varchar(20) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataExclusao | datetime2(7) | Y | — | — | — |

## dbo.EmendaParlamentar_TipoResultadoAnalise

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoResultadoAnalise | tinyint | N | PK | — | — |
| 2 | DescricaoTipoResultadoAnalise | varchar(20) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataExclusao | datetime2(7) | Y | — | — | — |

## dbo.EmendaParlamentar_TipoSecao

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSecao | tinyint | N | PK | — | — |
| 2 | DescricaoTipoSecao | varchar(20) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataExclusao | datetime2(7) | Y | — | — | — |

## dbo.EmendaParlamentar_TipoSituacao

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacao | tinyint | N | PK | — | — |
| 2 | DescricaoTipoSituacao | varchar(30) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataExclusao | datetime2(7) | Y | — | — | — |

## dbo.EmendaParlamentar_TipoSituacaoAnalise

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoAnalise | tinyint | N | PK | — | — |
| 2 | DescricaoTipoSituacaoAnalise | varchar(30) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataExclusao | datetime2(7) | Y | — | — | — |

## dbo.Envio_AnexoImportado

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdAnexoLRF | tinyint | N | PK, FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 3 | Importado | bit | N | — | — | — |

## dbo.Envio_AnexoLRF

Tabela · ~51 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAnexoLRF | tinyint | N | PK | — | — |
| 2 | NomeAnexoLRF | varchar(100) | N | — | — | — |
| 3 | NumeroAnexoLRF | tinyint | N | — | — | — |
| 4 | NumeroAnexoMDF | tinyint | Y | — | — | — |
| 5 | IdTipoAnexoLRF | tinyint | N | FK → dbo.Envio_TipoAnexoLRF(IdTipoAnexoLRF) | — | — |
| 6 | AnoReferenciaInicial | smallint | N | — | — | — |
| 7 | AnoReferenciaFinal | smallint | N | — | — | — |
| 8 | OpcionalidadeEnvio | bit | N | — | — | — |
| 9 | SiaiFiscal | bit | N | — | — | — |

## dbo.Envio_ArquivoLRF

Tabela · ~44.290 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | Ano | smallint | N | — | — | — |
| 4 | Bimestre | tinyint | N | — | — | — |
| 5 | VersaoSIAIColeta | varchar(10) | Y | — | — | — |
| 6 | IdSituacaoArquivoLRF | tinyint | N | FK → dbo.Envio_SituacaoArquivoLRF(IdSituacaoArquivoLRF) | — | — |
| 7 | IdGestorResponsavel | int | Y | FK → dbo.Anexo42_Responsavel(IdResponsavel) | — | — |
| 8 | IdResponsavelControleInterno | int | Y | FK → dbo.Anexo40_PessoaUCCI(IdPessoaUCCI) | — | — |
| 9 | NomeResponsavelPreenchimento | varchar(100) | Y | — | — | — |
| 10 | CPFResponsavelPreenchimento | char(11) | Y | — | — | — |
| 11 | NomeResponsavelInformacao | varchar(100) | Y | — | — | — |
| 12 | CPFResponsavelInformacao | char(11) | Y | — | — | — |
| 13 | HashArquivoLRF | char(32) | N | — | — | — |
| 14 | Observacoes | varchar(500) | Y | — | — | — |
| 15 | DataProcessamento | datetime | Y | — | — | — |
| 16 | VersaoLrfService | varchar(12) | Y | — | — | — |
| 17 | IdProcesso | int | Y | — | — | — |
| 18 | NumeroProcesso | char(6) | Y | — | — | — |
| 19 | AnoProcesso | smallint | Y | — | — | — |
| 20 | IdArquivoLRFCorrecao | int | Y | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 21 | IdArquivoRecepcaoLegado | int | Y | — | — | — |
| 22 | DataInclusao | smalldatetime | N | — | — | — |
| 23 | IdSessao | int | N | — | — | — |

## dbo.Envio_ArquivoXML

Tabela · ~225.557 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoXML | int | N | PK, IDENT | — | — |
| 2 | IdUnidadeJurisdicionada | int | N | — | — | — |
| 3 | IdAnexo | tinyint | N | FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 4 | DataReferenciaInicial | date | N | — | — | — |
| 5 | DataReferenciaFinal | date | N | — | — | — |
| 6 | IdSituacaoProcessamento | tinyint | N | FK → dbo.Envio_SituacaoProcessamento(IdSituacaoProcessamento) | — | — |
| 7 | HashArquivoXML | char(32) | N | — | — | — |
| 8 | EnvioComplementar | bit | N | — | — | — |
| 9 | NomeSistemaGeradorXML | varchar(300) | Y | — | — | — |
| 10 | Observacoes | varchar(500) | Y | — | — | — |
| 11 | DataProcessamento | datetime | Y | — | — | — |
| 12 | IdArquivoXMLCorrecao | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |
| 13 | RetificacaoAutorizada | bit | N | — | — | — |
| 14 | DataInativacao | smalldatetime | Y | — | — | — |
| 15 | DataInclusao | smalldatetime | N | — | — | — |
| 16 | IdSessao | int | N | — | — | — |
| 17 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_AssinadorImportacaoAnexoLRF

Tabela · ~73.902 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAssinadorImportacaoAnexoLRF | int | N | PK, IDENT | — | — |
| 2 | IdImportacaoAnexoLRF | int | N | FK → dbo.Envio_ImportacaoAnexoLRF(IdImportacaoAnexoLRF) | — | — |
| 3 | IdTipoAssinadorArquivo | tinyint | N | FK → dbo.Envio_TipoAssinadorArquivo(IdTipoAssinadorArquivo) | — | — |
| 4 | CPFAssinador | char(11) | N | — | — | — |
| 5 | NomeAssinador | varchar(150) | N | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_AutorizacaoRetificacao

Tabela · ~15 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAutorizacaoRetificacao | int | N | PK, IDENT | — | — |
| 2 | IdTipoAutorizacaoRetificacao | tinyint | N | FK → dbo.Envio_TipoAutorizacaoRetificacao(IdTipoAutorizacaoRetificacao) | — | — |
| 3 | IdOrgao | int | N | — | — | — |
| 4 | IdPeriodo | tinyint | Y | FK → dbo.Envio_Periodo(IdPeriodo) | — | — |
| 5 | AnoReferencia | smallint | N | — | — | — |
| 6 | JustificativaRetificacao | varchar(8000) | N | — | — | — |
| 7 | RetificacaoEfetivada | bit | N | — | — | — |
| 8 | IdRemessaAutorizada | int | N | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_CalendarioOpcionalidadeRGF

Tabela · ~11 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCalendarioOpcionalidadeRGF | int | N | PK, IDENT | — | — |
| 2 | Ano | smallint | N | — | — | — |
| 3 | DataInicio | date | N | — | — | — |
| 4 | DataTermino | date | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_CriticaArquivoLRF

Tabela · ~2.348.611 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriticaArquivoLRF | int | N | PK, IDENT | — | — |
| 2 | MensagemCriticaArquivoLRF | varchar(500) | Y | — | — | — |
| 3 | IdAnexoLRF | tinyint | N | FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 4 | IdTipoCriticaArquivoLRF | tinyint | Y | FK → dbo.Envio_TipoCriticaArquivoLRF(IdTipoCriticaArquivoLRF) | — | — |
| 5 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Envio_CriticaArquivoXML

Tabela · ~2.550.566 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriticaArquivoXML | int | N | PK, IDENT | — | — |
| 2 | MensagemCriticaArquivoXML | varchar(MAX) | N | — | — | — |
| 3 | IdTipoCriticaProcessamento | tinyint | N | FK → dbo.Envio_TipoCriticaProcessamento(IdTipoCriticaProcessamento) | — | — |
| 4 | IdArquivoXML | int | N | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |
| 5 | IdTipoCriticaArquivoXML | tinyint | N | FK → dbo.Envio_TipoCriticaArquivoXML(IdTipoCriticaArquivoXML) | — | — |

## dbo.Envio_CriticaImportacaoAnexoLRF

Tabela · ~542.773 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriticaImportacaoAnexoLRF | int | N | PK, IDENT | — | — |
| 2 | IdImportacaoAnexoLRF | int | N | FK → dbo.Envio_ImportacaoAnexoLRF(IdImportacaoAnexoLRF) | — | — |
| 3 | MensagemCriticaImportacaoAnexoLRF | varchar(500) | N | — | — | — |
| 4 | IdTipoCriticaArquivoLRF | tinyint | N | FK → dbo.Envio_TipoCriticaArquivoLRF(IdTipoCriticaArquivoLRF) | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |

## dbo.Envio_DadosComplementaresArquivoXML

Tabela · ~104.607 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoXML | int | N | PK, FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |
| 2 | HashDadosComplementaresArquivoXML | char(32) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | IdSessao | int | N | — | — | — |

## dbo.Envio_ImportacaoAnexoLRF

Tabela · ~61.162 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdImportacaoAnexoLRF | int | N | PK, IDENT | — | — |
| 2 | IdAnexoLRF | tinyint | N | FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 3 | IdSituacaoImportacaoAnexoLRF | tinyint | N | FK → dbo.Envio_SituacaoImportacaoAnexoLRF(IdSituacaoImportacaoAnexoLRF) | — | — |
| 4 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 5 | NomeArquivo | varchar(500) | Y | — | — | — |
| 6 | HashArquivo | char(32) | Y | — | — | — |
| 7 | IdImportacaoAnexoLRFCorrecao | int | Y | FK → dbo.Envio_ImportacaoAnexoLRF(IdImportacaoAnexoLRF) | — | — |
| 8 | Observacoes | varchar(500) | Y | — | — | — |
| 9 | NotaExplicativaAnexoLRF | varchar(MAX) | Y | — | — | — |
| 10 | DataInclusao | smalldatetime | N | — | — | — |
| 11 | IdSessao | int | N | — | — | — |
| 12 | IdSessaoOperacao | int | Y | — | — | — |
| 13 | OrigemImportacaoSTN | bit | N | — | — | — |
| 14 | DataHomologacaoRetificacaoSTN | datetime | Y | — | — | — |

## dbo.Envio_LimiteAlerta

Tabela · ~171 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLimiteAlerta | int | N | PK, IDENT | — | — |
| 2 | ValorReceitaCorrenteLiquida | decimal(14,2) | N | — | — | — |
| 3 | ValorGastoTotalComPessoal | decimal(14,2) | N | — | — | — |
| 4 | PercentualAtingido | decimal(14,2) | N | — | — | — |
| 5 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Envio_MensagemPendenciaEnvio

Tabela · ~80.723 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMensagemPendenciaEnvio | int | N | PK, IDENT | — | — |
| 2 | DescricaoMensagemPendenciaEnvio | varchar(500) | N | — | — | — |
| 3 | NumeroRecibo | int | N | — | — | — |
| 4 | IdAnexoLRF | tinyint | N | FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 5 | IdOrgao | int | N | — | — | — |
| 6 | IdTipoPendenciaEnvio | tinyint | N | FK → dbo.Envio_TipoPendenciaEnvio(IdTipoPendenciaEnvio) | — | — |
| 7 | IdTipoMensagemPendenciaEnvio | tinyint | Y | FK → dbo.Envio_TipoMensagemPendenciaEnvio(IdTipoMensagemPendenciaEnvio) | — | — |
| 8 | DataInclusaoPendencia | date | N | — | — | — |
| 9 | DataResolucaoPendencia | date | Y | — | — | — |
| 10 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |

## dbo.Envio_MotivoOpcionalidadeRGF

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMotivoOpcionalidadeRGF | tinyint | N | PK | — | — |
| 2 | NomeMotivoOpcionalidadeRGF | varchar(100) | Y | — | — | — |

## dbo.Envio_NotaExplicativa

Tabela · ~25.048 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | PK, FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |
| 2 | IdAnexoLRF | tinyint | N | PK, FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 3 | NotaExplicativa | varchar(MAX) | N | — | — | — |

## dbo.Envio_OpcionalidadeRGF

Tabela · ~1.990 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOpcionalidadeRGF | int | N | PK, IDENT | — | — |
| 2 | AnoReferencia | smallint | N | — | — | — |
| 3 | IdTipoPeriodoRGF | tinyint | N | FK → dbo.Envio_TipoPeriodo(IdTipoPeriodo) | — | — |
| 4 | IdTipoPeriodoRREO | tinyint | Y | FK → dbo.Envio_TipoPeriodo(IdTipoPeriodo) | — | — |
| 5 | IdOrgao | int | N | — | — | — |
| 6 | IdMotivoOpcionalidadeRGF | tinyint | N | FK → dbo.Envio_MotivoOpcionalidadeRGF(IdMotivoOpcionalidadeRGF) | — | — |
| 7 | DataInicioVigencia | date | Y | — | — | — |
| 8 | DataFimVigencia | date | Y | — | — | — |
| 9 | DataInclusao | smalldatetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_PeriodicidadeLRF

Tabela · ~195 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPeriodicidadeLRF | int | N | PK, IDENT | — | — |
| 2 | IdAnexoLRF | tinyint | N | FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 3 | IdOrgaoNatureza | tinyint | N | — | — | — |
| 4 | IdTipoPeriodo | tinyint | N | FK → dbo.Envio_TipoPeriodo(IdTipoPeriodo) | — | — |
| 5 | DataInicioVigencia | date | N | — | — | — |
| 6 | DataTerminoVigencia | date | Y | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_Periodo

Tabela · ~27 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPeriodo | tinyint | N | PK | — | — |
| 2 | NumeroPeriodo | tinyint | N | — | — | — |
| 3 | NomePeriodo | varchar(20) | N | — | — | — |
| 4 | IdTipoPeriodo | tinyint | N | FK → dbo.Envio_TipoPeriodo(IdTipoPeriodo) | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_PortalTransparencia

Tabela · ~31.633 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPortalTransparencia | int | N | PK, IDENT | — | — |
| 2 | PossuiPortalTransparencia | bit | N | — | — | — |
| 3 | LinkPortalTransparencia | varchar(255) | Y | — | — | — |
| 4 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Envio_PrazoArquivoLRF

Tabela · ~126 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoArquivoLRF | int | N | PK, IDENT | — | — |
| 2 | BimestreReferencia | tinyint | N | — | — | — |
| 3 | AnoReferencia | smallint | N | — | — | — |
| 4 | DataFinalBimestre | date | N | — | — | — |
| 5 | DataPrazoEnvio | date | N | — | — | — |
| 6 | DataPrazoTempestivo | date | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_PrazoArquivoXML

Tabela · ~24 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoArquivoXML | int | N | PK, IDENT | — | — |
| 2 | IdAnexo | tinyint | N | FK → dbo.Envio_AnexoLRF(IdAnexoLRF) | — | — |
| 3 | PeriodoReferencia | tinyint | N | — | — | — |
| 4 | AnoReferencia | smallint | N | — | — | — |
| 5 | DataPrazoEnvio | date | N | — | — | — |
| 6 | DataPrazoTempestivo | date | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Envio_ResponsavelContabilidade

Tabela · ~31.815 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelContabilidade | int | N | PK, IDENT | — | — |
| 2 | CPF | char(11) | N | — | — | — |
| 3 | Nome | varchar(100) | N | — | — | — |
| 4 | Profissao | varchar(40) | Y | — | — | — |
| 5 | Email | varchar(60) | Y | — | — | — |
| 6 | Telefone | varchar(30) | N | — | — | — |
| 7 | Celular | varchar(10) | Y | — | — | — |
| 8 | Logradouro | varchar(100) | Y | — | — | — |
| 9 | Complemento | varchar(30) | Y | — | — | — |
| 10 | CEP | varchar(10) | Y | — | — | — |
| 11 | Bairro | varchar(30) | Y | — | — | — |
| 12 | Cidade | varchar(50) | Y | — | — | — |
| 13 | UF | char(2) | Y | — | — | — |
| 14 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Envio_ResponsavelInformacao

Tabela · ~26.692 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelInformacao | int | N | PK, IDENT | — | — |
| 2 | CPF | char(11) | N | — | — | — |
| 3 | Nome | varchar(100) | N | — | — | — |
| 4 | Funcao | varchar(40) | Y | — | — | — |
| 5 | Email | varchar(60) | Y | — | — | — |
| 6 | Telefone | varchar(10) | N | — | — | — |
| 7 | Celular | varchar(10) | Y | — | — | — |
| 8 | Logradouro | varchar(100) | Y | — | — | — |
| 9 | Complemento | varchar(30) | Y | — | — | — |
| 10 | CEP | varchar(10) | Y | — | — | — |
| 11 | Bairro | varchar(30) | Y | — | — | — |
| 12 | Cidade | varchar(50) | Y | — | — | — |
| 13 | UF | char(2) | Y | — | — | — |
| 14 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Envio_ResponsavelPreenchimento

Tabela · ~26.692 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelPreenchimento | int | N | PK, IDENT | — | — |
| 2 | CPF | char(11) | N | — | — | — |
| 3 | Nome | varchar(100) | N | — | — | — |
| 4 | Funcao | varchar(40) | Y | — | — | — |
| 5 | Email | varchar(60) | Y | — | — | — |
| 6 | Telefone | varchar(10) | N | — | — | — |
| 7 | Celular | varchar(10) | Y | — | — | — |
| 8 | Logradouro | varchar(100) | Y | — | — | — |
| 9 | Complemento | varchar(30) | Y | — | — | — |
| 10 | CEP | varchar(10) | Y | — | — | — |
| 11 | Bairro | varchar(30) | Y | — | — | — |
| 12 | Cidade | varchar(50) | Y | — | — | — |
| 13 | UF | char(2) | Y | — | — | — |
| 14 | IdArquivoLRF | int | N | FK → dbo.Envio_ArquivoLRF(IdArquivoLRF) | — | — |

## dbo.Envio_SituacaoArquivoLRF

Tabela · ~17 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoArquivoLRF | tinyint | N | PK | — | — |
| 2 | DescricaoSituacaoArquivoLRF | varchar(150) | N | — | — | — |

## dbo.Envio_SituacaoImportacaoAnexoLRF

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoImportacaoAnexoLRF | tinyint | N | PK | — | — |
| 2 | NomeSituacaoImportacaoAnexoLRF | varchar(50) | N | — | — | — |

## dbo.Envio_SituacaoProcessamento

Tabela · ~10 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoProcessamento | tinyint | N | PK | — | — |
| 2 | DescricaoSituacaoArquivo | varchar(150) | N | — | — | — |

## dbo.Envio_TipoAnexoLRF

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexoLRF | tinyint | N | PK | — | — |
| 2 | NomeTipoAnexoLRF | varchar(100) | N | — | — | — |

## dbo.Envio_TipoAssinadorArquivo

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAssinadorArquivo | tinyint | N | PK | — | — |
| 2 | NomeTipoAssinadorArquivo | varchar(50) | N | — | — | — |

## dbo.Envio_TipoAutorizacaoRetificacao

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAutorizacaoRetificacao | tinyint | N | PK | — | — |
| 2 | NomeTipoAutorizacaoRetificacao | varchar(50) | N | — | — | — |

## dbo.Envio_TipoCriticaArquivoLRF

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCriticaArquivoLRF | tinyint | N | PK | — | — |
| 2 | NomeTipoCriticaArquivoLRF | varchar(50) | N | — | — | — |

## dbo.Envio_TipoCriticaArquivoXML

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCriticaArquivoXML | tinyint | N | PK | — | — |
| 2 | NomeTipoCriticaArquivoLRF | varchar(50) | N | — | — | — |

## dbo.Envio_TipoCriticaProcessamento

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoCriticaProcessamento | tinyint | N | PK | — | — |
| 2 | NomeTipoCriticaProcessamento | varchar(50) | N | — | — | — |

## dbo.Envio_TipoMensagemPendenciaEnvio

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoMensagemPendenciaEnvio | tinyint | N | PK | — | — |
| 2 | DescricaoTipoMensagemPendenciaEnvio | varchar(500) | Y | — | — | — |
| 3 | DataInicioVigencia | date | Y | — | — | — |
| 4 | Ativo | bit | N | — | — | — |

## dbo.Envio_TipoPendenciaEnvio

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoPendenciaEnvio | tinyint | N | PK | — | — |
| 2 | DescricaoTipoPendenciaEnvio | varchar(100) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |

## dbo.Envio_TipoPeriodo

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoPeriodo | tinyint | N | PK | — | — |
| 2 | NomeTipoPeriodo | varchar(20) | N | — | — | — |

## dbo.Envio_VersaoMinimaSiaiFiscal

Tabela · ~36 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdVersaoMinimaSiaiFiscal | int | N | PK, IDENT | — | — |
| 2 | BimestreReferencia | tinyint | N | — | — | — |
| 3 | AnoReferencia | smallint | N | — | — | — |
| 4 | VersaoMinima | varchar(10) | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.IEGM_ArquivoAnual

Tabela · ~677 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoAnual | int | N | PK, IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | Ano | smallint | N | — | — | — |
| 4 | NomeArquivo | varchar(500) | N | — | — | — |
| 5 | HashArquivo | char(32) | Y | — | — | — |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.LogAcessoArquivo

Tabela · ~1.032 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLogAcessoArquivo | int | N | PK, IDENT | — | — |
| 2 | IdOperadorExterno | int | N | — | — | — |
| 3 | NomeArquivo | varchar(250) | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | IdSessao | int | N | — | — | — |

## dbo.Mon_TBEspera

Tabela · ~117.350 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | idEspera | int | N | PK, IDENT | — | — |
| 2 | HoraDaCaptura | datetime2(7) | N | — | — | — |
| 3 | QuantidadeConsultasEmEspera | int | N | — | — | — |

## dbo.Questionario_AcessoQuestionarioGestor

Tabela · ~2.089 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoQuestionarioGestor | int | N | PK, FK → dbo.Questionario_TipoQuestionarioGestor(IdTipoQuestionarioGestor) | — | — |
| 2 | IdUnidadeJurisdicionada | int | N | PK | — | — |
| 3 | Senha | varchar(200) | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | IdSessao | int | N | — | — | — |
| 6 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Questionario_TipoQuestionarioGestor

Tabela · ~42 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoQuestionarioGestor | int | N | PK, IDENT | — | — |
| 2 | NomeTipoQuestionarioGestor | varchar(200) | N | — | — | — |
| 3 | LinkTipoQuestionarioGestor | varchar(200) | N | — | — | — |
| 4 | ConteudoPaginaInicial | varchar(2500) | Y | — | — | — |
| 5 | ConteudoPaginaQuestionario | varchar(MAX) | Y | — | — | — |
| 6 | NomeArquivoOficio | varchar(200) | N | — | — | — |
| 7 | DescricaoNomeArquivoOficio | varchar(200) | Y | — | — | — |
| 8 | ArquivoAdicional | varchar(200) | Y | — | — | — |
| 9 | DescricaoArquivoAdicional | varchar(200) | Y | — | — | — |
| 10 | DataInicioVigencia | date | N | — | — | — |
| 11 | DataTerminoVigencia | date | N | — | — | — |
| 12 | DataInicioVigenciaAviso | date | N | — | — | — |
| 13 | DataTerminoVigenciaAviso | date | N | — | — | — |
| 14 | DataInclusao | smalldatetime | N | — | — | — |
| 15 | IdSessao | int | N | — | — | — |
| 16 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_FaseProcesso

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFaseProcesso | tinyint | N | PK | — | — |
| 2 | DescricaoFaseProcesso | varchar(50) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataInclusao | datetime2(7) | N | — | — | — |
| 5 | IdSessao | int | N | — | — | — |
| 6 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_FundamentoLegal

Tabela · ~44 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFundamentoLegal | int | N | PK, IDENT | — | — |
| 2 | EstruturaFundamentoLegal | varchar(100) | N | — | — | — |
| 3 | TextoFundamentoLegal | varchar(500) | N | — | — | — |
| 4 | Ativo | bit | N | — | — | — |
| 5 | DataInclusao | datetime2(7) | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_Projeto

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProjeto | int | N | PK, IDENT | — | — |
| 2 | IdTipoDesestatizacao | tinyint | N | FK → dbo.RecepcaoDocumento_TipoDesestatizacao(IdTipoDesestatizacao) | — | — |
| 3 | IdFaseProcesso | tinyint | N | FK → dbo.RecepcaoDocumento_FaseProcesso(IdFaseProcesso) | — | — |
| 4 | IdSituacaoProjeto | tinyint | N | FK → dbo.RecepcaoDocumento_SituacaoProjeto(IdSituacaoProjeto) | — | — |
| 5 | IdEnteInteressado | int | N | — | — | — |
| 6 | IdAcao | int | Y | — | — | — |
| 7 | DescricaoProjeto | varchar(5120) | N | — | — | — |
| 8 | CPFResponsavel | char(11) | N | — | — | — |
| 9 | NomeResponsavel | varchar(150) | N | — | — | — |
| 10 | TelefoneContatoResponsavel | varchar(11) | Y | — | — | — |
| 11 | EmailContatoResponsavel | varchar(50) | Y | — | — | — |
| 12 | TemAudienciaPublica | bit | N | — | — | — |
| 13 | DataPrevisaoAudienciaPublica | date | Y | — | — | — |
| 14 | TemChamamentoPublicoViaPMI | bit | N | — | — | — |
| 15 | DataPrevisaoPublicacaoEdital | date | Y | — | — | — |
| 16 | DataPrevisaoLicitacao | date | Y | — | — | — |
| 17 | DataEnvioEnte | date | Y | — | — | — |
| 18 | DataRecebimentoTCE | date | Y | — | — | — |
| 19 | DataPrazoFinalAnaliseTCE | date | Y | — | — | — |
| 20 | DataInclusao | datetime2(7) | N | — | — | — |
| 21 | IdSessao | int | N | — | — | — |
| 22 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_ProjetoEnvio

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProjetoEnvio | int | N | PK | — | — |
| 2 | IdProjeto | int | N | FK → dbo.RecepcaoDocumento_Projeto(IdProjeto) | — | — |
| 3 | DataEnvioProjeto | date | N | — | — | — |
| 4 | DataRecebimentoTCE | date | Y | — | — | — |
| 5 | DataAvaliacaoTCE | date | Y | — | — | — |
| 6 | DataDevolucaoTCE | date | Y | — | — | — |
| 7 | DataInclusao | datetime2(7) | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_ProjetoLote

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProjetoLote | int | N | PK, IDENT | — | — |
| 2 | IdProjeto | int | N | FK → dbo.RecepcaoDocumento_Projeto(IdProjeto) | — | — |
| 3 | IdTipoDesestatizacaoFundamentoLegal | int | N | FK → dbo.RecepcaoDocumento_TipoDesestatizacaoFundamentoLegal(IdTipoDesestatizacaoFundamentoLegal) | — | — |
| 4 | Justificativa | varchar(MAX) | Y | — | — | — |
| 5 | IdProjetoLoteCorrecao | int | Y | FK → dbo.RecepcaoDocumento_ProjetoLote(IdProjetoLote) | — | — |
| 6 | DataInclusao | datetime2(7) | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_ProjetoLoteArquivo

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProjetoLoteArquivo | int | N | PK, IDENT | — | — |
| 2 | IdProjetoLote | int | N | FK → dbo.RecepcaoDocumento_ProjetoLote(IdProjetoLote) | — | — |
| 3 | IdSituacaoArquivo | tinyint | N | FK → dbo.RecepcaoDocumento_SituacaoArquivo(IdSituacaoArquivo) | — | — |
| 4 | DescricaoObjetoArquivo | varchar(100) | Y | — | — | — |
| 5 | NomeArquivoAnexo | varchar(150) | N | — | — | — |
| 6 | DataInclusao | datetime2(7) | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_SituacaoArquivo

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoArquivo | tinyint | N | PK | — | — |
| 2 | DescricaoSituacaoArquivo | varchar(50) | N | — | — | — |
| 3 | DataInclusao | datetime2(7) | N | — | — | — |
| 4 | IdSessao | int | N | — | — | — |
| 5 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_SituacaoProjeto

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoProjeto | tinyint | N | PK | — | — |
| 2 | DescricaoSituacaoProjeto | varchar(30) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataInclusao | datetime2(7) | N | — | — | — |
| 5 | IdSessao | int | N | — | — | — |
| 6 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RecepcaoDocumento_TipoDesestatizacao

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDesestatizacao | tinyint | N | PK, IDENT | — | — |
| 2 | DescricaoTipoDesestatizacao | varchar(30) | N | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataExclusao | datetime2(7) | Y | — | — | — |

## dbo.RecepcaoDocumento_TipoDesestatizacaoFundamentoLegal

Tabela · ~106 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDesestatizacaoFundamentoLegal | int | N | PK, IDENT | — | — |
| 2 | IdTipoDesestatizacao | tinyint | N | FK → dbo.RecepcaoDocumento_TipoDesestatizacao(IdTipoDesestatizacao) | — | — |
| 3 | IdFundamentoLegal | int | N | FK → dbo.RecepcaoDocumento_FundamentoLegal(IdFundamentoLegal) | — | — |
| 4 | FormatoArquivo | varchar(50) | N | — | — | — |
| 5 | ArquivoObrigatorio | bit | N | — | — | — |
| 6 | TemJustificativa | bit | N | — | — | — |
| 7 | PrazoSugeridoDias | smallint | Y | — | — | — |
| 8 | Ativo | bit | N | — | — | — |
| 9 | DataInclusao | datetime2(7) | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.RGF_TipoLimite

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoLimite | tinyint | N | PK | — | — |
| 2 | Descricao | varchar(20) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.SIGEF_ConexaoBanco

Tabela · ~69.198 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdConexaoBanco | int | N | PK, IDENT | — | — |
| 2 | DataConexao | datetime | N | — | — | — |
| 3 | MensagemErroConexaoBanco | varchar(500) | Y | — | — | — |
| 4 | IdTipoSituacaoConexaoBanco | tinyint | N | FK → dbo.SIGEF_TipoSituacaoConexaoBanco(IdTipoSituacaoConexaoBanco) | — | — |

## dbo.SIGEF_PendenciaErroOrgao

Tabela · ~234.997 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPendenciaErroOrgao | int | N | PK, IDENT | — | — |
| 2 | IdUnidadeJurisdicionada | int | N | — | — | — |
| 3 | IdTipoOrigemErro | tinyint | N | FK → dbo.SIGEF_TipoOrigemErro(IdTipoOrigemErro) | — | — |
| 4 | IdArquivoXML | int | Y | FK → dbo.Envio_ArquivoXML(IdArquivoXML) | — | — |
| 5 | MensagemErro | varchar(500) | N | — | — | — |
| 6 | Resolvido | bit | N | — | — | — |
| 7 | DataResolvido | smalldatetime | Y | — | — | — |
| 8 | DataInclusao | smalldatetime | N | — | — | — |

## dbo.SIGEF_TipoOrigemErro

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoOrigemErro | tinyint | N | PK | — | — |
| 2 | DescricaoTipoOrigemErro | varchar(50) | N | — | — | — |

## dbo.SIGEF_TipoSituacaoConexaoBanco

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoConexaoBanco | tinyint | N | PK | — | — |
| 2 | DescricaoTipoSituacaoConexaoBanco | varchar(50) | N | — | — | — |

## dbo.SINAQUE_AcessoQuestionarioOrgao

Tabela · ~169 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgao | int | N | PK | — | — |
| 2 | IdTipoQuestionario | int | N | PK, FK → dbo.SINAQUE_TipoQuestionario(IdTipoQuestionario) | — | — |
| 3 | Login | varchar(12) | N | — | — | — |
| 4 | Senha | varchar(64) | N | — | — | — |

## dbo.SINAQUE_CalendarioQuestionario

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCalendarioQuestionario | int | N | PK, IDENT | — | — |
| 2 | IdTipoQuestionario | int | N | FK → dbo.SINAQUE_TipoQuestionario(IdTipoQuestionario) | — | — |
| 3 | DataInicio | date | N | — | — | — |
| 4 | DataTermino | date | N | — | — | — |

## dbo.SINAQUE_TipoQuestionario

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoQuestionario | int | N | PK, IDENT | — | — |
| 2 | NomeTipoQuestionario | varchar(50) | N | — | — | — |
| 3 | LinkTipoQuestionario | varchar(50) | N | — | — | — |

## dbo.sysdiagrams

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | name | sysname | N | — | — | — |
| 2 | principal_id | int | N | — | — | — |
| 3 | diagram_id | int | N | PK, IDENT | — | — |
| 4 | version | int | Y | — | — | — |
| 5 | definition | varbinary(MAX) | Y | — | — | — |

## dbo.vw_Anexo38_Edital

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEdital | int | N | — | — | — |
| 2 | TipoBasedeDados | int | N | — | — | — |
| 3 | NumeroDespesa | varchar(24) | N | — | — | — |
| 4 | AnoProcessoDespesa | varchar(30) | Y | — | — | — |
| 5 | OrgNome | varchar(150) | N | — | — | — |
| 6 | OrgCodigo | char(10) | N | — | — | — |
| 7 | NumeroLicitacao | varchar(10) | Y | — | — | — |
| 8 | AnoLicitacao | varchar(30) | Y | — | — | — |
| 9 | DataPublicacao | date | Y | — | — | — |
| 10 | DataRealizacao | date | Y | — | — | — |
| 11 | Objeto | varchar(500) | Y | — | — | — |
| 12 | ValorOrcado | decimal(14,2) | Y | — | — | — |
| 13 | ValorFederal | decimal(14,2) | Y | — | — | — |
| 14 | ValorEstadual | decimal(14,2) | Y | — | — | — |
| 15 | ValorMunicipal | decimal(14,2) | Y | — | — | — |
| 16 | ValorProprio | decimal(14,2) | Y | — | — | — |
| 17 | Modalidade | tinyint | Y | — | — | — |
| 18 | ModalidadeDescricao | varchar(50) | Y | — | — | — |
| 19 | DataEnvioTCE | smalldatetime | N | — | — | — |
| 20 | Nome | varchar(100) | N | — | — | — |
| 21 | Email | varchar(50) | Y | — | — | — |
| 22 | TelefoneTrabalho | varchar(30) | Y | — | — | — |
| 23 | IdOrgao | int | N | — | — | — |
| 24 | IdProcedimentoLicitatorio | tinyint | N | — | — | — |
| 25 | CodigoUnidadeGestora | char(11) | N | — | — | — |
| 26 | NomeUnidadeGestora | varchar(200) | N | — | — | — |
| 27 | DataInclusao | smalldatetime | N | — | — | — |
| 28 | Obrigatoriedade | int | Y | — | — | — |
| 29 | DescricaoFundamentoLegal | varchar(100) | N | — | — | — |
| 30 | DescricaoCriterioJulgamento | varchar(90) | Y | — | — | — |
| 31 | DataDisponibilizacao | date | Y | — | — | — |
| 32 | HoraDisponibilizacaoInicio | char(5) | Y | — | — | — |
| 33 | HoraDisponibilizacaoFim | char(5) | Y | — | — | — |
| 34 | LocalDisponibilizacao | varchar(250) | Y | — | — | — |
| 35 | HoraRealizacao | char(5) | Y | — | — | — |
| 36 | LocalRealizacao | varchar(250) | Y | — | — | — |
| 37 | Justificativa | varchar(500) | Y | — | — | — |
| 38 | NomeAnalise | int | Y | — | — | — |
| 39 | DataInicioAnalise | int | Y | — | — | — |
| 40 | DataFimAnalise | int | Y | — | — | — |

## dbo.vw_Anexo42_IAAdelia

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelUnidade | int | N | — | — | — |
| 2 | CargoReponsavelUnidade | varchar(50) | N | — | — | — |
| 3 | DataInicioGestao | date | N | — | — | — |
| 4 | DataTerminoGestao | date | Y | — | — | — |
| 5 | Ativo | bit | N | — | — | — |
| 6 | NomeResponsavel | varchar(150) | Y | — | — | — |
| 7 | CPFResponsavel | char(11) | Y | — | — | — |
| 8 | EmailResponsavel | varchar(50) | Y | — | — | — |
| 9 | TelefoneResponsavel | varchar(30) | Y | — | — | — |
| 10 | NomeFuncaoResponsavel | varchar(50) | Y | — | — | — |
| 11 | CNPJUnidadeJurisdicionada | char(14) | Y | — | — | — |
| 12 | NomeUnidadeJurisdicionada | varchar(200) | Y | — | — | — |
| 13 | CodigoUnidadeGestora | char(11) | Y | — | — | — |
| 14 | NomeTipoAdministracaoUnidade | varchar(50) | Y | — | — | — |
| 15 | NomeSituacaoUnidade | varchar(10) | Y | — | — | — |
| 16 | NomeNaturezaUnidade | varchar(150) | Y | — | — | — |
| 17 | NomeOrgao | varchar(150) | Y | — | — | — |
| 18 | NomeCidadeOrgao | varchar(120) | Y | — | — | — |

## dbo.vw_EntregaEletronica_PrazoAnexo14

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoArquivoXML | int | N | IDENT | — | — |
| 2 | IdAnexo | tinyint | Y | — | — | — |
| 3 | PeriodoReferencia | tinyint | Y | — | — | — |
| 4 | AnoReferencia | smallint | N | — | — | — |
| 5 | DataPrazoEnvio | date | N | — | — | — |
| 6 | DataPrazoTempestivo | date | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.vw_EntregaEletronica_PrazoArquivoLRF

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoArquivoLRF | int | N | IDENT | — | — |
| 2 | BimestreReferencia | tinyint | Y | — | — | — |
| 3 | AnoReferencia | smallint | N | — | — | — |
| 4 | DataFinalBimestre | date | Y | — | — | — |
| 5 | DataPrazoEnvio | date | N | — | — | — |
| 6 | DataPrazoTempestivo | date | N | — | — | — |
| 7 | DataInclusao | smalldatetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.vw_EntregaEletronica_PrazoContasDeGestao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoContasDeGestao | int | N | IDENT | — | — |
| 2 | AnoReferencia | smallint | N | — | — | — |
| 3 | DataPrazoEnvio | date | N | — | — | — |
| 4 | DataPrazoTempestivo | date | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.vw_EntregaEletronica_PrazoContasDeGoverno

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoContasDeGoverno | int | N | IDENT | — | — |
| 2 | AnoReferencia | smallint | N | — | — | — |
| 3 | DataPrazoEnvio | date | N | — | — | — |
| 4 | DataPrazoTempestivo | date | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.vw_EntregaEletronica_PrazoOrgao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgao | int | N | — | — | — |
| 2 | CodigoOrgao | char(10) | N | — | — | — |
| 3 | NomeOrgao | varchar(150) | N | — | — | — |
| 4 | IdTipoObrigacao | tinyint | N | — | — | — |
| 5 | NomeTipoObrigacao | varchar(100) | N | — | — | — |
| 6 | PeriodoReferencia | tinyint | Y | — | — | — |
| 7 | AnoReferencia | smallint | N | — | — | — |
| 8 | NovaDataPrazo | date | N | — | — | — |
| 9 | Justificativa | varchar(500) | N | — | — | — |
| 10 | ArquivoComprobatorioJustificativa | varchar(100) | N | — | — | — |
| 11 | NumeroProcesso | char(6) | N | — | — | — |
| 12 | AnoProcesso | char(4) | N | — | — | — |

## dbo.vw_Envio_ArquivoLRF

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | IDENT | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | Ano | smallint | N | — | — | — |
| 4 | Bimestre | tinyint | N | — | — | — |
| 5 | VersaoSIAIColeta | varchar(10) | Y | — | — | — |
| 6 | IdSituacaoArquivoLRF | tinyint | N | — | — | — |
| 7 | NomeResponsavelPreenchimento | varchar(100) | Y | — | — | — |
| 8 | NomeResponsavelInformacao | varchar(100) | Y | — | — | — |
| 9 | DataProcessamento | datetime | Y | — | — | — |
| 10 | VersaoLrfService | varchar(12) | Y | — | — | — |
| 11 | IdProcesso | int | Y | — | — | — |
| 12 | NumeroProcesso | char(6) | Y | — | — | — |
| 13 | AnoProcesso | smallint | Y | — | — | — |
| 14 | IdArquivoLRFCorrecao | int | Y | — | — | — |
| 15 | DataInclusao | smalldatetime | N | — | — | — |
| 16 | IdSessao | int | N | — | — | — |

## dbo.vw_Envio_ArquivoLRF_Opcionalidade

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | — | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | Ano | smallint | N | — | — | — |
| 4 | Bimestre | tinyint | N | — | — | — |
| 5 | IdSituacaoArquivoLRF | tinyint | N | — | — | — |
| 6 | HashArquivoLRF | char(32) | N | — | — | — |
| 7 | Observacoes | varchar(500) | Y | — | — | — |
| 8 | DataProcessamento | datetime | Y | — | — | — |
| 9 | VersaoSIAIColeta | varchar(10) | Y | — | — | — |
| 10 | VersaoLrfService | varchar(12) | Y | — | — | — |
| 11 | NomeResponsavelPreenchimento | varchar(100) | Y | — | — | — |
| 12 | CPFResponsavelPreenchimento | char(11) | Y | — | — | — |
| 13 | NomeResponsavelInformacao | varchar(100) | Y | — | — | — |
| 14 | CPFResponsavelInformacao | char(11) | Y | — | — | — |
| 15 | IdProcesso | int | Y | — | — | — |
| 16 | NumeroProcesso | char(6) | Y | — | — | — |
| 17 | AnoProcesso | smallint | Y | — | — | — |
| 18 | IdArquivoLRFCorrecao | int | Y | — | — | — |
| 19 | DataInclusao | smalldatetime | N | — | — | — |
| 20 | IdSessao | int | N | — | — | — |
| 21 | IdOpcionalidadeRGF | int | Y | — | — | — |
| 22 | IdTipoPeriodoRGF | tinyint | Y | — | — | — |
| 23 | IdTipoPeriodoRREO | tinyint | Y | — | — | — |
| 24 | IdMotivoOpcionalidadeRGF | tinyint | Y | — | — | — |

## dbo.vw_Envio_CriticaArquivoLRF

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivoLRF | int | N | — | — | — |
| 2 | IdOrgao | int | N | — | — | — |
| 3 | Ano | smallint | N | — | — | — |
| 4 | Bimestre | tinyint | N | — | — | — |
| 5 | VersaoSIAIColeta | varchar(10) | Y | — | — | — |
| 6 | IdSituacaoArquivoLRF | tinyint | N | — | — | — |
| 7 | IdGestorResponsavel | int | Y | — | — | — |
| 8 | IdResponsavelControleInterno | int | Y | — | — | — |
| 9 | NomeResponsavelPreenchimento | varchar(100) | Y | — | — | — |
| 10 | CPFResponsavelPreenchimento | char(11) | Y | — | — | — |
| 11 | NomeResponsavelInformacao | varchar(100) | Y | — | — | — |
| 12 | CPFResponsavelInformacao | char(11) | Y | — | — | — |
| 13 | HashArquivoLRF | char(32) | N | — | — | — |
| 14 | Observacoes | varchar(500) | Y | — | — | — |
| 15 | DataProcessamento | datetime | Y | — | — | — |
| 16 | VersaoLrfService | varchar(12) | Y | — | — | — |
| 17 | IdProcesso | int | Y | — | — | — |
| 18 | NumeroProcesso | char(6) | Y | — | — | — |
| 19 | AnoProcesso | smallint | Y | — | — | — |
| 20 | IdArquivoLRFCorrecao | int | Y | — | — | — |
| 21 | IdArquivoRecepcaoLegado | int | Y | — | — | — |
| 22 | DataInclusao | smalldatetime | N | — | — | — |
| 23 | IdSessao | int | N | — | — | — |

## dbo.vw_Gen_Banco

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdBanco | int | N | — | — | — |
| 2 | CodigoFebraban | char(10) | Y | — | — | — |
| 3 | NomeBanco | varchar(100) | Y | — | — | — |

## dbo.vw_Gen_Cidade

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCidade | int | N | — | — | — |
| 2 | NomeCidade | varchar(120) | N | — | — | — |
| 3 | IdEstado | tinyint | Y | — | — | — |
| 4 | CodigoIBGE | char(7) | Y | — | — | — |
| 5 | Populacao | int | Y | — | — | — |
| 6 | IdMicrorregiao | tinyint | Y | — | — | — |
| 7 | Latitude | numeric(10,5) | Y | — | — | — |
| 8 | Longitude | numeric(10,5) | Y | — | — | — |

## dbo.vw_Gen_CidadePopulacao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCidade | int | N | — | — | — |
| 2 | AnoReferencia | smallint | N | — | — | — |
| 3 | Populacao | int | N | — | — | — |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.vw_Gen_Estado

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEstado | tinyint | N | — | — | — |
| 2 | SiglaEstado | char(2) | N | — | — | — |
| 3 | NomeEstado | varchar(75) | N | — | — | — |
| 4 | Pais | int | N | — | — | — |

## dbo.vw_Gen_Orgao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgao | int | N | — | — | — |
| 2 | CodigoOrgao | char(10) | N | — | — | — |
| 3 | IdOrgaoSuperior | int | Y | — | — | — |
| 4 | SiglaOrgao | varchar(20) | Y | — | — | — |
| 5 | NomeOrgao | varchar(150) | N | — | — | — |
| 6 | CNPJ | char(14) | Y | — | — | — |
| 7 | IdCidadeOrgao | int | N | — | — | — |
| 8 | CEPOrgao | char(9) | Y | — | — | — |
| 9 | LogradouroOrgao | varchar(100) | Y | — | — | — |
| 10 | NumeroOrgao | varchar(10) | Y | — | — | — |
| 11 | ComplementoOrgao | varchar(100) | Y | — | — | — |
| 12 | BairroOrgao | varchar(50) | Y | — | — | — |
| 13 | TelefoneOrgao | varchar(30) | Y | — | — | — |
| 14 | EmailInstitucional | varchar(50) | N | — | — | — |
| 15 | OrgaoAtivo | bit | N | — | — | — |
| 16 | NomeCidade | varchar(120) | N | — | — | — |
| 17 | IdOrgaoNatureza | tinyint | Y | — | — | — |
| 18 | TipoSiglaLRF | char(1) | Y | — | — | — |
| 19 | Esfera | char(1) | Y | — | — | — |
| 20 | TipoOrgaoNatureza | char(1) | Y | — | — | — |
| 21 | IdGrupoUnidadeJurisdicionada | tinyint | Y | — | — | — |
| 22 | NomeGrupoUnidadeJurisdicionada | varchar(100) | Y | — | — | — |
| 23 | EnviaSIAIDP | bit | Y | — | — | — |
| 24 | EnviaSIAIFiscal | bit | Y | — | — | — |
| 25 | EnviaContasDeGestao | bit | Y | — | — | — |
| 26 | DataInclusao | smalldatetime | N | — | — | — |

## dbo.vw_Gen_OrgaoNatureza

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgaoNatureza | tinyint | N | — | — | — |
| 2 | TipoOrgaoNatureza | char(1) | N | — | — | — |
| 3 | DescricaoOrgaoNatureza | varchar(100) | N | — | — | — |

## dbo.vw_Gen_PessoaFisica

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPessoaFisica | int | N | — | — | — |
| 2 | CPF | char(11) | N | — | — | — |
| 3 | NomePessoaFisica | varchar(100) | N | — | — | — |
| 4 | Sexo | char(1) | Y | — | — | — |
| 5 | DataNascimento | date | Y | — | — | — |
| 6 | NumeroDocumento | varchar(15) | Y | — | — | — |
| 7 | DataEmissaoDocumento | date | Y | — | — | — |
| 8 | OrgaoExpedidorDocumento | varchar(20) | Y | — | — | — |
| 9 | IdEstadoOrgaoExpedidor | tinyint | Y | — | — | — |
| 10 | IdEstadoCivil | tinyint | N | — | — | — |
| 11 | EmailPessoaFisica | varchar(50) | Y | — | — | — |
| 12 | CEPPessoaFisica | char(9) | Y | — | — | — |
| 13 | LogradouroPessoaFisica | varchar(100) | Y | — | — | — |
| 14 | ComplementoPessoaFisica | varchar(100) | Y | — | — | — |
| 15 | BairroPessoaFisica | varchar(50) | Y | — | — | — |
| 16 | IdCidadePessoaFisica | int | N | — | — | — |
| 17 | TelefoneResidencialPessoaFisica | varchar(30) | Y | — | — | — |
| 18 | TelefoneComercialPessoaFisica | varchar(30) | Y | — | — | — |
| 19 | TelefoneCelularPessoaFisica | varchar(30) | Y | — | — | — |
| 20 | DataInclusao | smalldatetime | N | — | — | — |
| 21 | IdSessao | int | N | — | — | — |
| 22 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.vw_Gen_TipoDocumento

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDocumento | tinyint | N | — | — | — |
| 2 | DescricaoTipoDocumento | varchar(50) | N | — | — | — |

## dbo.vw_Gen_UnidadeJurisdicionada

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOrgao | int | N | — | — | — |
| 2 | CodigoOrgao | char(10) | N | — | — | — |
| 3 | IdOrgaoSuperior | int | Y | — | — | — |
| 4 | NomeOrgao | varchar(150) | N | — | — | — |
| 5 | CNPJ | char(14) | Y | — | — | — |
| 6 | IdCidadeOrgao | int | N | — | — | — |
| 7 | NomeCidade | varchar(120) | N | — | — | — |
| 8 | IdOrgaoNatureza | tinyint | N | — | — | — |
| 9 | TipoSiglaLRF | char(1) | Y | — | — | — |
| 10 | Esfera | char(1) | N | — | — | — |
| 11 | TipoOrgaoNatureza | char(1) | Y | — | — | — |
| 12 | IdGrupoUnidadeJurisdicionada | tinyint | Y | — | — | — |
| 13 | NomeGrupoUnidadeJurisdicionada | varchar(100) | Y | — | — | — |
| 14 | EnviaSIAIFiscal | bit | N | — | — | — |
| 15 | EnviaAnexo14 | bit | N | — | — | — |
| 16 | EnviaSIAIDP | bit | N | — | — | — |
| 17 | EnviaContasDeGestao | bit | N | — | — | — |
| 18 | UtilizaSIGEF | bit | N | — | — | — |
| 19 | DataInicioUtilizacaoSIGEF | date | Y | — | — | — |
| 20 | VerificaPendenciaEmCertidao | bit | N | — | — | — |
| 21 | EstatalIndependente | bit | N | — | — | — |
| 22 | InstitutoPrevidencia | bit | N | — | — | — |
| 23 | IdTipoADTS | tinyint | N | — | — | — |
| 24 | IdUnidadeJurisdicionada | int | N | — | — | — |
| 25 | DataInicioAtividade | date | Y | — | — | — |
| 26 | DataTerminoAtividade | date | Y | — | — | — |
| 27 | IdCamara | tinyint | Y | — | — | — |
| 28 | IdSiglaLRF | tinyint | N | — | — | — |
| 29 | CodigoLRF | char(4) | N | — | — | — |
| 30 | IdSetorResponsavel | int | Y | — | — | — |
| 31 | DataPublicacaoLei | date | Y | — | — | — |
| 32 | NumeroDiarioOficialPublicacao | numeric(6,0) | Y | — | — | — |
| 33 | AnexoDaLei | varchar(100) | Y | — | — | — |
| 34 | CodigoSiconfi | varchar(10) | Y | — | — | — |
| 35 | DataInclusao | smalldatetime | N | — | — | — |
| 36 | IdSessao | int | N | — | — | — |
| 37 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.vw_Seg_OperadorServico

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOperadorServico | int | N | IDENT | — | — |
| 2 | idTipoOperadorServico | tinyint | N | — | — | — |
| 3 | DescricaoServico | varchar(256) | N | — | — | — |
| 4 | ApplicationName | varchar(50) | N | — | — | — |
| 5 | ClientId | varchar(64) | N | — | — | — |
| 6 | AccessKey | varchar(64) | N | — | — | — |
| 7 | Token | varchar(512) | Y | — | — | — |
| 8 | NomeResponsavel | varchar(100) | N | — | — | — |
| 9 | CPFResponsavel | char(11) | Y | — | — | — |
| 10 | EmailResponsavel | varchar(50) | N | — | — | — |
| 11 | TelefoneResponsavel | varchar(30) | N | — | — | — |
| 12 | IdOrgaoUtilizador | int | Y | — | — | — |
| 13 | Ativo | bit | N | — | — | — |
| 14 | DataInclusao | smalldatetime | N | — | — | — |
| 15 | IdSessao | int | N | — | — | — |
| 16 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.vw_Seg_Sessao

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSessao | int | N | — | — | — |
| 2 | IdOperador | int | N | — | — | — |
| 3 | NomePessoaFisica | varchar(100) | N | — | — | — |
| 4 | CPF | char(11) | N | — | — | — |
| 5 | EmailPessoaFisica | varchar(50) | Y | — | — | — |
| 6 | DataSessao | smalldatetime | N | — | — | — |

