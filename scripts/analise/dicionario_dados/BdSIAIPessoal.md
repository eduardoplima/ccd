# Dicionário de dados — BdSIAIPessoal

Gerado em 2026-05-21. 134 objetos · 1024 colunas.

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

Tabela · ~1.325 linhas

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

Tabela · ~509 linhas

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

## dbo.Comum_Carreira

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCarreira | smallint | N | PK, IDENT | — | Identificador da Tabela Comum Carreira |
| 2 | NomeCarreira | varchar(200) | N | — | — | Nome da Carreira |
| 4 | IdOrgao | int | N | — | — | Identificador do Órgão da Carreira ({{ base_url_tceadmin2 }}/v2/UnidadeJurisdicionada/) |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 6 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 7 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Comum_CBO

Tabela · ~2.626 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | Codigo | int | N | PK | — | Código do CBO |
| 2 | Nome | varchar(150) | N | — | — | Nome do CBO |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_CIDCapitulo

Tabela · ~22 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCapitulo | tinyint | N | PK | — | Identificador do Capítulo |
| 2 | InicioCategoria | char(3) | N | — | — | Código do Início da Categoria |
| 3 | FimCategoria | char(3) | N | — | — | Código do Fim da Categoria |
| 4 | NomeCapitulo | varchar(150) | N | — | — | Nome do Capítulo |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 6 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_CIDCategoria

Tabela · ~2.045 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | CodigoCategoria | char(3) | N | PK | — | Código da Categoria |
| 2 | NomeCategoria | varchar(500) | Y | — | — | Nome da Categoria |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_CIDGrupo

Tabela · ~275 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdGrupo | smallint | N | PK | — | Identificador do Grupo |
| 2 | IdCapitulo | tinyint | N | FK → dbo.Comum_CIDCapitulo(IdCapitulo) | — | Identificador do Capítulo |
| 3 | InicioCategoria | char(3) | N | — | — | Código do Início da Categoria |
| 4 | FimCategoria | char(3) | N | — | — | Código do Fim da Categoria |
| 5 | NomeGrupo | varchar(200) | N | — | — | Nome do Grupo |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_CIDSubCategoria

Tabela · ~12.451 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | CodigoSubCategoria | char(4) | N | PK | — | Código da SubCategoria |
| 2 | NomeSubCategoria | varchar(500) | Y | — | — | Nome da SubCategoria |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_DoencaLei

Tabela · ~32 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDoencaLei | int | N | PK, IDENT | — | Identificador do Doença |
| 2 | IdLegis | int | Y | — | — | Identificador da Norma do LEGIS ( {{ base_url_legis }}/api/Legislacao/LegislacoesValidadas ) |
| 3 | NomeDoenca | varchar(500) | Y | — | — | Nome da Doença |
| 4 | FundamentoLegal | varchar(500) | Y | — | — | Fundamento Legal da Doença |
| 6 | IdCidade | int | Y | — | — | Identificador da Cidade. Se IdCidade == 0, ente é o estado do RN. |
| 7 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 8 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 9 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Comum_Endereco

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEndereco | int | N | PK, IDENT | — | Identificador do Endereço |
| 2 | TipoLogradouro | varchar(50) | Y | — | — | Tipo do Logradouro |
| 3 | Endereco | varchar(200) | Y | — | — | Logradouro |
| 4 | Numero | varchar(5) | Y | — | — | Número do imóvel |
| 5 | Complemento | varchar(500) | Y | — | — | Complemento do Endereço |
| 6 | Bairro | varchar(200) | Y | — | — | Nome do Bairro |
| 7 | CEP | varchar(8) | Y | — | — | Número do CEP |

## dbo.Comum_Escolaridade

Tabela · ~11 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEscolaridade | int | N | PK | — | Identificador da Escolaridade |
| 2 | NomeEscolaridade | varchar(100) | N | — | — | Nome da Escolaridade |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_EsferaOrigem

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEsferaOrigem | tinyint | N | PK | — | Identificador da Esfera Origem |
| 2 | NomeEsferaOrigem | varchar(20) | N | — | — | Nome da Esfera Origem |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_FatoGeradorInvalidez

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFatoGeradorInvalidez | int | N | PK, IDENT | — | Identificador do Fato Gerador de Invalidez |
| 2 | NomeFatoGeradorInvalidez | varchar(100) | N | — | — | Nome do Fato Gerador de Invalidez |
| 3 | IdAreaAtuacao | tinyint | Y | — | — | Identificador da Área de Atuação ({{ base_url_tceadmin2 }}/v2/AreaAtuacao) |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 6 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Comum_MotivoDesligamento

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMotivoDesligamento | int | N | PK | — | Identificador do Motivo do Desligamento |
| 2 | NomeMotivoDesligamento | varchar(50) | N | — | — | Nome do Motivo do Desligamento |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_Pessoa

Tabela · ~357.453 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPessoa | int | N | PK, FK → dbo.Comum_Pessoa(IdPessoa), IDENT | — | Identificador da Pessoa Física |
| 2 | CPF | varchar(11) | N | — | — | Número do CPF |
| 3 | Nome | varchar(200) | N | — | — | Nome completo |
| 4 | DataNascimento | date | N | — | — | Data de nascimento |
| 5 | Sexo | char(1) | N | — | — | Sexo |
| 6 | NomePai | varchar(200) | Y | — | — | Nome do pai |
| 7 | NomeMae | varchar(200) | N | — | — | Nome da mãe |
| 8 | PNE | bit | Y | — | — | Identifica se é Portador de Necessidades Especiais |
| 9 | IdEstadoCivil | tinyint | Y | — | — | Identificador do Estado Civil ({{ base_url_tceadmin2 }}/v2/EstadoCivil) |
| 10 | Identidade | varchar(25) | Y | — | — | Número da Identidade |
| 11 | UFIdentidade | nchar(2) | Y | — | — | Código do IBGE da Unidade Federativa da Identidade |
| 12 | OrgaoExpeditorIdentidade | varchar(20) | Y | — | — | Órgão expeditor da Identidade |
| 13 | TituloEleitor | varchar(20) | Y | — | — | Número do Título de Eleitor |
| 14 | PISPASEP | varchar(25) | Y | — | — | Número do PIS/PASEP |
| 15 | Agencia | char(6) | N | — | — | Número da Agência bancária |
| 16 | Conta | varchar(20) | N | — | — | Número da Conta bancária |
| 17 | IdBanco | int | N | — | — | Identificador do Banco ({{ base_url_tceadmin2 }}/v2/Banco) |
| 18 | IdEscolaridade | int | N | FK → dbo.Comum_Escolaridade(IdEscolaridade) | — | Identificador do nível de Escolaridade |
| 19 | IdEndereco | int | Y | FK → dbo.Comum_Endereco(IdEndereco) | — | Identificador do Endereço |
| 20 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |
| 21 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |

## dbo.Comum_RegimeJuridico

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRegimeJuridico | int | N | PK | — | Identificador do Regime Jurídico |
| 2 | NomeRegimeJuridico | varchar(200) | N | — | — | Nome do Regime Jurídico |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Comum_SalarioMinimo

Tabela · ~36 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | MesSalarioMinimo | char(2) | N | PK | — | Mês do Salário Minimo |
| 2 | AnoSalarioMinimo | char(4) | N | PK | — | Ano do do Salário Minimo |
| 3 | ValorSalarioMinimo | decimal(14,2) | N | — | — | Valor do Salário Minimo |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 6 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Comum_Subnivel

Tabela · ~120 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSubnivel | smallint | N | PK, IDENT | — | Identificador do Subnível |
| 2 | IdCargo | int | N | FK → dbo.SiaiDp_Cargo(IdCargo) | — | Identificador do Cargo associado ao Subnível |
| 3 | NomeSubnivel | varchar(70) | N | — | — | Nome do Subnível pode agrupar até três subníveis. Ex.: Sub 1 \| Sub 2 \| Sub 3 |
| 5 | Ordem | tinyint | N | — | — | Ordem do Subnível |
| 6 | Ativo | bit | N | — | — | Identifica se o subnível está ativo |
| 7 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 8 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 9 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 10 | ClasseSubnivel | varchar(50) | Y | — | — | — |

## dbo.Comum_TipoVinculo

Tabela · ~14 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoVinculo | int | N | PK | — | Identificador do Tipo de Vínculo |
| 2 | NomeTipoVinculo | varchar(100) | N | — | — | Nome do Tipo de Vínculo |
| 3 | IsSIAIAP | bit | N | — | — | Identifica se o Tipo de Vínculo está sendo utilizado nos sistemas do SIAIAP |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_AtoBeneficio

Tabela · ~24 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficio | int | N | PK, FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio), IDENT | — | Identificador do Ato de Benefício |
| 2 | IdFuncionarioBeneficiario | int | N | FK → dbo.SiaiDp_Funcionario(IdFuncionario) | — | Identificador do Servidor do Ato |
| 3 | IdTipoAto | tinyint | N | FK → dbo.Concessoes_TipoAto(IdTipoAto) | — | Identificador do Tipo do Ato |
| 4 | IdSituacaoAtoBeneficio | tinyint | N | FK → dbo.Concessoes_TipoSituacaoAtoBeneficio(IdSituacaoAtoBeneficio) | — | Identificador da Situação do Ato |
| 5 | IdAreaAtuacao | tinyint | N | — | — | Identificador da Área de Atuação ({{tceapi}}/api/v2/EsferaGovernamental) |
| 6 | IdOrgaoInstitutoPrevidencia | int | Y | — | — | Identificador do órgão do Instituto de Previdência |
| 7 | IdProcessoTCE | int | Y | — | — | Identificador do Processo vinculado do TCE-RN |
| 8 | AnoAto | char(4) | Y | — | — | Ano do cadastro do Ato |
| 9 | NumeroAto | char(6) | N | — | — | Número sequencial (por ano) do cadastro de atos no sistema |
| 10 | NumeroProcessoOrigem | varchar(40) | Y | — | — | Número do processo de Origem do Ato |
| 11 | ObservacoesAbaAnexos | varchar(4000) | Y | — | — | Campo observ]gerais presente na aba de anexos. |
| 13 | JustificativaAnulacao | varchar(200) | Y | — | — | Descrição |
| 14 | AtoValidado | bit | N | — | — | Descrição |
| 15 | IdTipoIndicacaoAto | tinyint | Y | FK → dbo.Concessoes_TipoIndicacaoAto(IdTipoIndicacaoAto) | — | Descrição |
| 16 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 17 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 18 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 19 | NumeroProcesso | varchar(6) | Y | — | — | Descrição |
| 20 | AnoProcesso | varchar(4) | Y | — | — | Descrição |
| 21 | DataEnvioTCE | date | Y | — | — | — |
| 22 | ResponsavelEnvioAoTCE | varchar(11) | Y | — | — | — |
| 23 | ObservacoesAbaAnexosDiligencia | varchar(4000) | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioArquivo

Tabela · ~82 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivo | int | N | PK, IDENT | — | Identificador do Arquivo |
| 2 | IdAtoBeneficio | int | N | — | — | Descrição |
| 3 | IdOrgaoIP | int | N | — | — | Identificador do Instituto de Previdência |
| 4 | AnoAto | char(4) | N | — | — | Ano do Ato |
| 5 | NumeroAto | char(6) | N | — | — | Número do Ato |
| 6 | NomeArquivo | varchar(500) | N | — | — | Nome do arquivo no formato GUID |
| 7 | ObservacoesArquivoAnexo | varchar(500) | Y | — | — | Descrição |
| 9 | HashArquivo | char(32) | N | — | — | Hash MD5 do arquivo |
| 10 | DataInclusao | smalldatetime | N | — | — | Data de inclusão do arquivo |
| 11 | IdSessao | int | Y | — | — | Identificador da Sessão do Registro |
| 12 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 14 | IdTipoComprovante | int | N | — | — | Descrição |
| 15 | IdTipoAnexo | int | Y | FK → dbo.Concessoes_TipoAnexo(IdTipoAnexo) | — | Descrição |

## dbo.Concessoes_AtoBeneficioArquivoAnexoIndicacao

Tabela · ~26 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivo | bigint | N | PK, IDENT | — | — |
| 3 | NomeArquivo | varchar(500) | N | — | — | — |
| 4 | HashArquivo | char(32) | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | Y | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |
| 8 | IdAtoBeneficio | int | N | FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | — |
| 9 | Envio_CE | bit | N | — | — | — |

## dbo.Concessoes_AtoBeneficioArquivoIndicacao

Tabela · ~27 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivo | bigint | N | PK, IDENT | — | — |
| 2 | IdAtoBeneficio | int | N | FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | — |
| 3 | NomeArquivo | varchar(500) | N | — | — | — |
| 4 | HashArquivo | char(32) | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | Y | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioCicloAnalise

Tabela · ~29 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCicloAnalise | int | N | PK, IDENT | — | — |
| 2 | IdAtoBeneficio | int | N | FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | — |
| 3 | CpfResponsavelAtual | char(11) | N | — | — | — |
| 4 | Concluido | bit | N | — | — | — |
| 5 | DataInicio | datetime | N | — | — | — |

## dbo.Concessoes_AtoBeneficioDadosConcessao

Tabela · ~23 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficio | int | N | PK, FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | Descrição |
| 2 | IdFundamentacaoJuridicaConcessao | int | N | FK → dbo.Concessoes_FundamentacaoJuridicaConcessao(IdFundamentacaoJuridicaConcessao) | — | Descrição |
| 3 | IdLaudoMedico | int | Y | FK → dbo.Concessoes_AtoBeneficioLaudoMedico(IdLaudoMedico) | — | Descrição |
| 4 | IdArquivoComprovantePublicacao | int | Y | FK → dbo.Concessoes_AtoBeneficioArquivo(IdArquivo) | — | Descrição |
| 5 | IdArquivoComprovanteObito | int | Y | FK → dbo.Concessoes_AtoBeneficioArquivo(IdArquivo) | — | Descrição |
| 6 | DataRequerimento | date | Y | — | — | Descrição |
| 7 | DataPublicacao | date | N | — | — | Descrição |
| 8 | DataInicioVigenciaConcessao | date | N | — | — | Descrição |
| 9 | DataRepublicacao | date | Y | — | — | Descrição |
| 10 | PossuiDecisaoJudicial | bit | N | — | — | Descrição |
| 16 | IdDecisaoJudicial | int | Y | FK → dbo.Concessoes_DecisaoJudicial(IdDecisaoJudicial) | — | Descrição |
| 17 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 18 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 19 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_AtoBeneficioDadosFuncionais

Tabela · ~23 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficio | int | N | PK, FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | Identificador da Aba de Dados Funcionais do Ato |
| 2 | IdSubnivel | smallint | Y | FK → dbo.Comum_Subnivel(IdSubnivel) | — | Identificador do Subnivel do Cargo |
| 3 | IdTipoVinculo | int | Y | FK → dbo.Comum_TipoVinculo(IdTipoVinculo) | — | Descrição |
| 4 | DataIngressoCargo | date | N | — | — | Data de Ingresso no cargo ao qual o servidor ir? cadastrar o ato |
| 5 | DataIngressoCarreira | date | N | — | — | Data de ingresso na carreira do servidor no ?rg?o em que o mesmo ir? cadastrar o ato |
| 6 | DataIngressoServicoPublico | date | N | — | — | Primeira data de ingresso do servidor na admintra?a? p?blica |
| 7 | CargaHoraria | tinyint | N | — | — | Descrição |
| 8 | IsInqueritoAdministrativo | bit | N | — | — | Descrição |
| 9 | NumeroProcessoInqueritoAdministrativo | varchar(30) | Y | — | — | Descrição |
| 10 | PossuiTransposicao | bit | Y | — | — | Descrição |
| 11 | DataTransposicao | smalldatetime | Y | — | — | Descrição |
| 12 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 13 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 14 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 15 | PossuiPrevidenciaComplementar | bit | Y | — | — | Descrição |
| 17 | IdOrgaoOrigem | int | N | — | — | — |
| 21 | CargoAposentadoriaDeNaturezaEfetiva | bit | Y | — | — | — |
| 22 | NivelClasseReferencia | varchar(30) | Y | — | — | — |
| 23 | NomeCargo | varchar(200) | N | — | — | — |

## dbo.Concessoes_AtoBeneficioDadosPessoais

Tabela · ~24 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficio | int | N | PK, FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | Identificador da tabela da Aba de Dados Pessoais do Servidor |
| 2 | IdPessoa | int | N | FK → dbo.Comum_Pessoa(IdPessoa) | — | Descrição |
| 3 | IdEstadoCivil | tinyint | N | — | — | Identificador da Pessoa (Servidor) <http://{{tceapi}}/api/v2/EstadoCivil> |
| 4 | CPF | varchar(11) | N | — | — | CPF do Servidor |
| 5 | Nome | varchar(200) | N | — | — | Nome do Servidor |
| 6 | Sexo | char(1) | Y | — | — | Sexo do Servidor |
| 7 | DataNascimento | date | N | — | — | Data de Nascimento do Servidor |
| 8 | Identidade | varchar(25) | Y | — | — | Identidade do Servidor |
| 9 | OrgaoExpeditorIdentidade | varchar(20) | Y | — | — | Orgao Expeditor da Identidade |
| 10 | UFOrgaoExpeditorIdentidade | nchar(10) | Y | — | — | Unidade Federativa do Orgao emissor da Identidade |
| 11 | NomeMae | varchar(200) | N | — | — | Nome da m?e do Servidor |
| 12 | DataObitoInstituidor | date | Y | — | — | Data do ?bito do instituidor (quando o tipo de ato for de pens?o) |
| 13 | FalecimentoNaAtividade | bit | Y | — | — | Verifica??o de obito foi durante atividade do instituidor (Data do ?bito do instituidor (quando o tipo de ato for de pens?o)) |
| 14 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 15 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 16 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 17 | PNE | bit | N | — | — | Valor booleano que define se usuário beneficiário da concessão é Portador de Necessidades Especiais |
| 18 | DataAquisicaoPNE | smalldatetime | Y | — | — | Se beneficiário não nasceu PNE quando foi a data que isso ocorreu. |
| 19 | IdArquivoComprovantePNE | int | Y | FK → dbo.Concessoes_AtoBeneficioArquivo(IdArquivo) | — | FK para um arquivo de um documento que demonstre algum laudo médico sobre a condição do PNE. |

## dbo.Concessoes_AtoBeneficioDadosProventos

Tabela · ~23 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficioDadosProventos | int | N | PK, IDENT | — | Descrição |
| 2 | IdAtoBeneficio | int | N | FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | Descrição |

## dbo.Concessoes_AtoBeneficioDadosTempos

Tabela · ~24 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficioDadosTempos | int | N | PK | — | Descrição |
| 2 | IdAtoBeneficio | int | N | FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | Descrição |
| 3 | InformacoesComplementares | varchar(5000) | N | — | — | Descrição |
| 8 | ValorPercentualADTS | decimal(5,2) | Y | — | — | Descrição |
| 14 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 15 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 16 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_AtoBeneficioIndicacao

Tabela · ~60 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficioIndicacao | bigint | N | PK, IDENT | — | Descrição |
| 2 | IdAtoBeneficio | int | N | FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | Descrição |
| 3 | CpfPessoaIndicacaoAto | varchar(11) | N | — | — | Descrição |
| 4 | IdTipoIndicacaoAto | tinyint | N | FK → dbo.Concessoes_TipoIndicacaoAto(IdTipoIndicacaoAto) | — | Descrição |
| 6 | DescricaoCabecalhoIndicacaoAto | varchar(MAX) | N | — | — | Descrição |
| 7 | DescricaoIndicacaoAto | varchar(MAX) | N | — | — | Descrição |
| 9 | DataInclusao | datetime | N | — | — | Data da Inclusão do Registro |
| 10 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 11 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 12 | IsRascunho | bit | N | — | — | — |
| 13 | IdCicloAnalise | int | N | FK → dbo.Concessoes_AtoBeneficioCicloAnalise(IdCicloAnalise) | — | — |
| 14 | NomePessoaIndicacaoAto | varchar(100) | N | — | — | — |
| 15 | IdOrgao | int | N | — | — | — |
| 16 | IdArquivoAnexoIndicacao | bigint | Y | FK → dbo.Concessoes_AtoBeneficioArquivoAnexoIndicacao(IdArquivo) | — | — |
| 17 | IdArquivoIndicacao | bigint | Y | FK → dbo.Concessoes_AtoBeneficioArquivoIndicacao(IdArquivo) | — | — |
| 18 | ValorMensalIrregularmentePago | decimal(14,2) | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioLaudoMedico

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdLaudoMedico | int | N | PK, IDENT | — | Identificador do Laudo M?dico de uma concess?o |
| 2 | IdFatoGeradorInvalidez | int | N | FK → dbo.Comum_FatoGeradorInvalidez(IdFatoGeradorInvalidez) | — | Identificador do Fato Gerador da Invalidez |
| 3 | IdDoencaLei | int | Y | FK → dbo.Comum_DoencaLei(IdDoencaLei) | — | Identifica??o da Doen?a ou Condi??o |
| 4 | CodigoCategoriaCID | char(3) | N | FK → dbo.Comum_CIDCategoria(CodigoCategoria) | — | Identificador da Classifica??o Internacional de Doen?as |
| 5 | CodigoSubCategoriaCID | char(4) | N | FK → dbo.Comum_CIDSubCategoria(CodigoSubCategoria) | — | Identificador do c?digo da Classifica??o Internacional de Doen?as |
| 6 | IdArquivoLaudo | int | Y | — | — | Descrição |
| 7 | DataEmissaoLaudo | date | N | — | — | Data de emiss?o do Laudo M?dico |
| 8 | DataVigenciaLaudo | date | Y | — | — | Data de Vig?ncia do Laudo M?dico |
| 9 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 10 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 11 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_AtoBeneficioMovimentacao

Tabela · ~100 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficioMovimentacao | bigint | N | PK, IDENT | — | Descrição |
| 2 | IdAtoBeneficio | int | N | FK → dbo.Concessoes_AtoBeneficio(IdAtoBeneficio) | — | Descrição |
| 3 | IdAtoBeneficioIndicacao | bigint | Y | FK → dbo.Concessoes_AtoBeneficioIndicacao(IdAtoBeneficioIndicacao) | — | Descrição |
| 4 | IdOrgao | int | N | — | — | Descrição |
| 5 | CpfPessoaMovimentacaoAto | varchar(11) | N | — | — | Descrição |
| 6 | IdSituacaoAtoBeneficio | tinyint | N | FK → dbo.Concessoes_TipoSituacaoAtoBeneficio(IdSituacaoAtoBeneficio) | — | Descrição |
| 7 | IdTipoMovimentacaoAto | tinyint | N | — | — | Descrição |
| 8 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 9 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 10 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 11 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |
| 12 | NomePessoaMovimentacaoAto | varchar(100) | N | — | — | — |

## dbo.Concessoes_AtoBeneficioProventosContribuicao

Tabela · ~469 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficioDadosProventos | int | N | PK, FK → dbo.Concessoes_AtoBeneficioDadosProventos(IdAtoBeneficioDadosProventos) | — | Descrição |
| 2 | MesContribuicao | char(2) | N | PK | — | Descrição |
| 3 | AnoContribuicao | char(4) | N | PK | — | Descrição |
| 4 | ValorContribuicao | decimal(14,2) | Y | — | — | Descrição |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 6 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 7 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_AtoBeneficioProventosVantagem

Tabela · ~112 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdProventosVantagem | int | N | PK, IDENT | — | Descrição |
| 2 | IdAtoBeneficioDadosProventos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosProventos(IdAtoBeneficioDadosProventos) | — | Descrição |
| 3 | IdLegislacaoVantagem | int | Y | — | — | Descrição |
| 4 | CodigoVantagem | varchar(20) | Y | — | — | Descrição |
| 5 | DescricaoVantagem | varchar(255) | N | — | — | Descrição |
| 6 | FundamentoJuridicoVantagem | varchar(255) | N | — | — | Descrição |
| 7 | ValorVantagem | decimal(14,2) | N | — | — | Descrição |
| 8 | PossuiADTS | bit | N | — | — | Descrição |
| 9 | PossuiDecisaoJudicial | bit | N | — | — | Descrição |
| 16 | IdDecisaoJudicial | int | Y | FK → dbo.Concessoes_DecisaoJudicial(IdDecisaoJudicial) | — | Descrição |
| 17 | IdTabela | tinyint | Y | — | — | Descrição |
| 18 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 19 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 20 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 21 | PercentualADTS | decimal(5,2) | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioResultadoCalculo

Tabela · ~14 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResultadoCalculo | int | N | PK, IDENT | — | — |
| 2 | IdAtoBeneficioDadosProventos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosProventos(IdAtoBeneficioDadosProventos) | — | — |
| 3 | IdentificadorResultado | varchar(100) | N | — | — | — |
| 4 | ValorResultado | decimal(14,2) | N | — | — | — |
| 6 | Ordem | tinyint | Y | — | — | — |
| 7 | Descricao | varchar(500) | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioRevisaoAnalise

Tabela · ~23 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRevisaoAnalise | bigint | N | PK, IDENT | — | — |
| 2 | ConcordouIndicacao | bit | N | — | — | — |
| 3 | CpfRevisor | varchar(11) | N | — | — | — |
| 4 | ComentariosRevisao | varchar(1000) | Y | — | — | — |
| 5 | IdAtoBeneficioIndicacao | bigint | N | FK → dbo.Concessoes_AtoBeneficioIndicacao(IdAtoBeneficioIndicacao) | — | — |
| 6 | NomeRevisor | varchar(100) | N | — | — | — |
| 7 | DataRevisao | date | N | — | — | — |

## dbo.Concessoes_AtoBeneficioTempoAfastamento

Tabela · ~142 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoAfastamento | int | N | PK, IDENT | — | Descrição |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Identificador do item de afastamento da aba de tempos |
| 3 | IdTipoAfastamento | int | N | FK → dbo.Concessoes_TipoAfastamento(IdTipoAfastamento) | — | Identificador do Tipo de Afastamento |
| 4 | DataInicioVigencia | date | Y | — | — | Data de inicio do afastamento |
| 5 | DataFimVigencia | date | Y | — | — | Data de término do afastamento |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 8 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 9 | InformarDias | bit | Y | — | — | — |
| 10 | Ano | char(4) | Y | — | — | — |
| 11 | QuantidadeDias | int | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioTempoAtividadeMilitar

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoAtividadeMilitar | int | N | PK, IDENT | — | Identificador de Atividade Militar de dados tempo |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Identificador de itens do tempo |
| 3 | DataInicialTempoServico | smalldatetime | N | — | — | Data de inicio da atividade |
| 4 | DataFinalTempoServico | smalldatetime | N | — | — | Data final da atividade |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |

## dbo.Concessoes_AtoBeneficioTempoAverbado

Tabela · ~19 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoAverbado | int | N | PK, IDENT | — | Descrição |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Identificador de itens do tempo averbado |
| 3 | IdIncidenciaTempoServico | tinyint | Y | FK → dbo.Concessoes_TipoIncidenciaTempoServico(IdTipoIncidenciaTempoServico) | — | Identificador do tipo de incidencia de tempo de servi?o |
| 4 | IdEsferaOrigem | tinyint | N | FK → dbo.Comum_EsferaOrigem(IdEsferaOrigem) | — | Identificador da Esfera Governamental |
| 5 | DataInicialTempoAverbado | date | N | — | — | Data inicial da averba??o |
| 6 | DataFinalTempoAverbado | date | N | — | — | Data final da averba??o |
| 7 | DeducaoAposentadoria | smallint | Y | — | — | Verifica se h? dedu??o na aposentadoria |
| 8 | DeducaoADTS | smallint | Y | — | — | Verifica se h? dedu??o do ADTS |
| 9 | Observacao | varchar(500) | Y | — | — | Observação da averbação |
| 10 | NumeroProcessoAverbacao | varchar(30) | Y | — | — | Número do processo da averbação |
| 11 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 12 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 13 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 14 | IdTipoVinculo | int | Y | FK → dbo.Comum_TipoVinculo(IdTipoVinculo) | — | Chave estrangeira para a tabela Comum_TipoVinculo. Este campo não é nullo quando umaa esfera de origem não privada é selecionada. |
| 15 | CargoProvidoPorConcurso | bit | Y | — | — | Flag que define setada quando o tipo de vínculo é EFETIVO. |
| 16 | ContribuicaoRGPS | bit | N | — | — | — |
| 17 | ProtocoloCertidao | varchar(100) | Y | — | — | — |
| 18 | NomeArquivo | varchar(300) | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioTempoContribuicaoInsalubridadePericulosidade

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoContribuicaoInsalubridadePericulosidade | int | N | PK, IDENT | — | — |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Identificador do item de afastamento da aba de tempos |
| 3 | Descricao | varchar(500) | Y | — | — | Descrição do serviço ou período em que o beneficiário esteve em trabalho perigoso ou insalubre. |
| 4 | DataInicio | smalldatetime | N | — | — | Data de inicio do período |
| 5 | DataFim | smalldatetime | N | — | — | Data de término do período |
| 6 | DataInclusao | smalldatetime | N | — | — | — |
| 7 | IdSessao | int | Y | — | — | — |
| 8 | FatorMultiplicacao | decimal(4,2) | Y | — | — | — |
| 9 | DecisaoJudicial | bit | N | — | — | — |
| 10 | IdDecisaoJudicial | int | Y | FK → dbo.Concessoes_DecisaoJudicial(IdDecisaoJudicial) | — | — |

## dbo.Concessoes_AtoBeneficioTempoContribuicaoMagisterio

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoContribuicaoMagisterio | int | N | PK, IDENT | — | — |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Identificador do item de afastamento da aba de tempos |
| 3 | Lotacao | varchar(255) | N | — | — | Descrição da lotação em que o beneficiário esteve em trabalho no magistério. |
| 4 | Funcao | varchar(255) | N | — | — | Descrição da função em que o beneficiário esteve em trabalho no magistério. |
| 5 | DataInicio | smalldatetime | N | — | — | Data de inicio do período |
| 6 | DataFim | smalldatetime | N | — | — | Data de término do período |
| 7 | PeriodoEmDias | int | N | — | — | Período em dias entre data início e fim |
| 8 | DataInclusao | smalldatetime | N | — | — | — |
| 9 | IdSessao | int | N | — | — | — |
| 10 | IdSessaoOperacao | int | Y | — | — | — |
| 11 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Concessoes_AtoBeneficioTempoContribuicaoRGPS

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoContribuicaoRGPS | int | N | PK, IDENT | — | — |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | — |
| 3 | DataInicio | smalldatetime | N | — | — | — |
| 4 | DataFim | smalldatetime | N | — | — | — |
| 5 | AverbacaoaAutomatica | bit | N | — | — | — |
| 6 | ProtocoloCTC | varchar(150) | Y | — | — | — |
| 7 | NomeArquivo | varchar(150) | Y | — | — | — |
| 8 | DataInclusao | datetime | N | — | — | — |
| 10 | IdSessao | int | N | — | — | — |
| 11 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioTempoDesaverbacao

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoDesaverbacao | int | N | PK, IDENT | — | — |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | — |
| 3 | DataInicial | smalldatetime | N | — | — | — |
| 4 | DataFinal | smalldatetime | N | — | — | — |
| 5 | Observacao | varchar(500) | Y | — | — | — |
| 6 | DataInclusao | datetime | N | — | — | — |
| 7 | IdSessao | int | N | — | — | — |
| 8 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Concessoes_AtoBeneficioTempoFeriasDobro

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoFeriasDobro | int | N | PK, IDENT | — | Identificador de ferias em dobro de dados tempo |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Identificador de itens do tempo |
| 3 | DataInicialFeriasDobro | smalldatetime | N | — | — | Data inicial das férias dobro |
| 4 | DataFinalFeriasDobro | smalldatetime | N | — | — | Data final das férias dobro |
| 5 | DiasGozados | int | N | — | — | Quantidade de dias de férias em dobro gozados pelo beneficiário, informados por ele. |
| 6 | DiasAdquiridos | int | N | — | — | Quantidade de dias de férias em dobro adquiridos. |
| 7 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |

## dbo.Concessoes_AtoBeneficioTempoLicencaPremio

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoLicencaPremio | int | N | PK, IDENT | — | Descrição |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Descrição |
| 3 | DataInicialTempoServico | smalldatetime | N | — | — | Descrição |
| 4 | DataFinalTempoServico | smalldatetime | N | — | — | Descrição |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 6 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 7 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 8 | DiasGozados | int | N | — | — | Quantidade de dias de licença prêmio gozados pelo beneficiário, informados por ele. |
| 9 | DiasAdquiridos | int | N | — | — | Quantidade de dias de licença prêmio adquiridos. São 30 dias a cada período de 5 anos de licença (dataFinal - dataInicial). |

## dbo.Concessoes_AtoBeneficioTempoServicoFicto

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTempoServicoFicto | int | N | PK, IDENT | — | Identificador de serviço ficto de dados tempo |
| 2 | IdAtoBeneficioDadosTempos | int | N | FK → dbo.Concessoes_AtoBeneficioDadosTempos(IdAtoBeneficioDadosTempos) | — | Identificador de itens do tempo |
| 3 | Descricao | varchar(1000) | Y | — | — | — |
| 4 | QuantidadeDias | int | N | — | — | Quantidade de dias de serviço ficto |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |

## dbo.Concessoes_AtualizacaoContribuicaoJan2016

Tabela · ~258 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | MesAtualizacao | char(2) | N | PK | — | Descrição |
| 2 | AnoAtualizacao | char(4) | N | PK | — | Descrição |
| 3 | ValorAtualizacao | decimal(12,6) | N | — | — | Descrição |

## dbo.Concessoes_CabecalhoTextoPadrao

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCabecalhoTextoPadrao | int | N | PK, IDENT | — | — |
| 2 | TituloCabecalho | varchar(250) | N | — | — | — |
| 3 | TextoCabecalho | nvarchar(500) | N | — | — | — |
| 4 | IdOrgao | int | N | — | — | — |
| 5 | DataInclusao | smalldatetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Concessoes_CampoRegra

Tabela · ~26 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCampoRegra | int | N | PK | — | Descrição |
| 2 | NomeCampoRegra | varchar(150) | N | — | — | Nome do campo de regra. Serve, basicamente, como um identificador para que o MVA possa achar ou calcular alguma informação. Pode ser um caminho pra algum atributo do Ato de benefício (AtoBeneficioDadosPessoais.DataNascimento) ou um nome identificador para a API realizar algum cálculo (Idade). |
| 3 | DescricaoCampoRegra | varchar(100) | N | — | — | Identificador do campo que aparecerá para o usuário final (Aplicação cliente). |
| 4 | TipoCampoRegra | char(1) | N | — | — | Determina se o campo de regra e do tipo data ou número. D \| N |
| 5 | Ativo | bit | N | — | — | (soft delete) ainda não funciona. |
| 6 | Referencia1CampoRegra | varchar(200) | Y | — | — | Se o campo de regra for um valor calculado (Idade) e não um caminho (AtoBeneficioDadosPessoais.DataNascimento), esse campo serve como parâmetro de entrada para a função do MVA que calcula o valor calculado do campo de regra. Sempre será um caminho (AtoBeneficioDadosPessoais.DataNascimento) ou vazio. |
| 7 | Referencia2CampoRegra | varchar(200) | Y | — | — | Se o campo de regra for um valor calculado (Idade) e não um caminho (AtoBeneficioDadosPessoais.DataNascimento), esse campo serve como um segundo parâmetro de entrada para a função do MVA que calcula o valor calculado do campo de regra. Sempre será um caminho (AtoBeneficioDadosConcessao.DataInicioVigenciaConcessao) ou vazio. |
| 8 | MetodoAuxiliarCalculoCampoRegra | varchar(50) | Y | — | — | Nome exato do método da API que calcula um campo calculado do campo de regra. Exemplo: CalcularPedagio100PorCento ou pode ser nullo. |
| 9 | ResultadoEm | char(1) | Y | — | — | Define o tipo do dado do resultado do cálculo do campo de regra. D = dias; M = meses; P = pontos/ano; A = anos. |
| 10 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 11 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_ConstanteTempo

Tabela · ~22 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdConstanteTempo | smallint | N | PK, IDENT | — | Descrição |
| 2 | DescricaoConstanteTempo | varchar(150) | N | — | — | Descrição |
| 3 | DataConstanteTempo | date | N | — | — | Descrição |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 6 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 7 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_DecisaoJudicial

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDecisaoJudicial | int | N | PK, IDENT | — | Descrição |
| 2 | NomeTribunalDecisaoJudicial | varchar(100) | N | — | — | Descrição |
| 3 | NumeroProcessoDecisaoJudicial | varchar(30) | N | — | — | Descrição |
| 4 | DataDecisaoJudicial | smalldatetime | N | — | — | Descrição |
| 5 | TransitadoJulgadoDecisaoJudicial | bit | N | — | — | Descrição |
| 6 | DataTransitadoJulgadoDecisaoJudicial | smalldatetime | Y | — | — | Descrição |
| 7 | TeorDecisaoJudicial | varchar(3000) | N | — | — | Descrição |
| 8 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 9 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 10 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_FundamentacaoJuridicaConcessao

Tabela · ~243 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFundamentacaoJuridicaConcessao | int | N | PK, IDENT | — | Descrição |
| 2 | DescricaoFundamentacaoJuridicaConcessao | varchar(500) | N | — | — | Descrição |
| 3 | Ementa | varchar(2000) | N | — | — | Descrição |
| 4 | DataInicioVigencia | date | N | — | — | Descrição |
| 5 | DataFimVigencia | date | Y | — | — | Se NULL, significa que essa fundamentação não tem data de expiração. |
| 7 | Ativo | bit | N | — | — | Descrição |
| 8 | ParaTodosEntes | bit | Y | — | — | Define se essa fundamentação vale para todos os entes do estado, incluindo o mesmo. (Natal, São Gonçalo do Amarante, RN) |
| 9 | IdRegraCalculo | int | Y | FK → dbo.Concessoes_RegraCalculo(IdRegraCalculo) | — | Identificador da regra de cálculo dessa fundamentação. |
| 10 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 11 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 12 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_FundamentacaoJuridicaConcessaoEnte

Tabela · ~1.700 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFundamentacaoJuridicaConcessao | int | N | PK | — | Descrição |
| 2 | IdCidade | int | N | PK | — | Descrição |

## dbo.Concessoes_FundamentacaoJuridicaConcessaoTipoAto

Tabela · ~243 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFundamentacaoJuridicaConcessao | int | N | PK, FK → dbo.Concessoes_FundamentacaoJuridicaConcessao(IdFundamentacaoJuridicaConcessao) | — | Descrição |
| 2 | IdTipoAto | tinyint | N | PK, FK → dbo.Concessoes_TipoAto(IdTipoAto) | — | Descrição |

## dbo.Concessoes_IndiceReajustamento

Tabela · ~124 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | MesIndice | char(2) | N | PK | — | Descrição |
| 2 | AnoIndice | char(4) | N | PK | — | Descrição |
| 3 | ValorIndice | decimal(12,6) | N | — | — | Até o presente momento esses valores podem ser consultados {{https://www.gov.br/previdencia/pt-br/assuntos/legislacao/indices-de-atualizacao-e-valores-medios-dos-beneficios}}, mais especificamente na seção de **Índice de atualização das contribuições para cálculo do salário-de-benefício**. |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 8 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 20 | FundamentacaoLegal | varchar(500) | Y | — | — | Portaria que delimita os valores das remunerações de contribuição. |
| 21 | NomeArquivo | varchar(255) | Y | — | — | — |

## dbo.Concessoes_InstitutoPrevidenciaControleInterno

Tabela · ~15 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 2 | IdOrgaoInstitutoPrevidencia | int | N | PK | — | Parte de chave primária composta que representa o órgão do IP. |
| 3 | IdOrgaoControleInterno | int | N | PK | — | Parte de chave primária composta que representa o CI de determinado IP. |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 6 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_RegraCalculo

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRegraCalculo | int | N | PK, IDENT | — | Descrição |
| 2 | NomeRegra | varchar(200) | N | — | — | Descrição |
| 3 | IdTipoCalculo | int | N | — | — | Identifica se o cálculo será por Média Aritmética ou por Integralidade. |
| 4 | PorcentagemContribuicao | int | Y | — | — | Valor percentual da contribuição, caso o cálculo seja limitado as maiores contribuições. (https://wiki.tce.rn.gov.br/doku.php?id=din:sistemas:produtos:siaipessoal:siaiapconcessoes:admin:regras_calculo#limita_as_maiores_contribuicoes) |
| 6 | IdValorReferencia | int | Y | — | — | Identificador do valor de referência. Se é última remuneração de cargo efetivo ou o Teto do RGPS. (https://wiki.tce.rn.gov.br/doku.php?id=din:sistemas:produtos:siaipessoal:siaiapconcessoes:admin:regras_calculo#aplicar_valor_de_referencia) |
| 9 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 10 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 11 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 12 | Proporcionalidade | bit | Y | — | — | Booleano para definir se cálculo aplicará fator de proporcionalidade. |
| 14 | FatorTempoContribuicaoPorcentagem | int | Y | — | — | Valor percentual do fator de tempo de contribuição. |
| 15 | FatorAposentadoriaCompulsoria | bit | Y | — | — | https://wiki.tce.rn.gov.br/doku.php?id=din:sistemas:produtos:siaipessoal:siaiapconcessoes:admin:regras_calculo#aplicar_fator_de_aposentadoria_compulsoria |
| 39 | FatorTempoContribuicao | int | Y | — | — | https://wiki.tce.rn.gov.br/doku.php?id=din:sistemas:produtos:siaipessoal:siaiapconcessoes:admin:regras_calculo#aplicar_fator_de_tempo_de_contribuicao |
| 40 | TipoRazao | char(1) | Y | — | — | Identificador do tipo de Razão de Proporcionalidade, A ou a (Anos), D ou d (dias) |

## dbo.Concessoes_RegraComposta

Tabela · ~178 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRegraComposta | smallint | N | PK, IDENT | — | Descrição |
| 3 | IdOperadorLogico | tinyint | N | FK → dbo.Concessoes_TipoOperadorLogico(IdOperadorLogico) | — | Descrição |
| 4 | Sexo | char(1) | N | — | — | Descrição |
| 7 | Ativo | bit | N | — | — | Descrição |
| 8 | IdFundamentacaoJuridicaConcessao | int | Y | FK → dbo.Concessoes_FundamentacaoJuridicaConcessao(IdFundamentacaoJuridicaConcessao) | — | Descrição |
| 9 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 10 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 11 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_RegraCompostaRegraSimples

Tabela · ~1.085 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRegraComposta | smallint | N | PK, FK → dbo.Concessoes_RegraComposta(IdRegraComposta) | — | Descrição |
| 2 | IdRegraSimples | smallint | N | PK, FK → dbo.Concessoes_RegraSimples(IdRegraSimples) | — | Descrição |

## dbo.Concessoes_RegraSimples

Tabela · ~371 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRegraSimples | smallint | N | PK, IDENT | — | Descrição |
| 2 | IdCampoRegraPre | int | N | FK → dbo.Concessoes_CampoRegra(IdCampoRegra) | — | Operando esquerdo da regra. |
| 3 | IdOperadorAritmetico | tinyint | N | FK → dbo.Concessoes_TipoOperadorAritmetico(IdOperadorAritmetico) | — | Operador relacional (igual a, maior que, menor que, maior ou igual a, etc.). |
| 4 | IdCampoRegraPos | int | Y | FK → dbo.Concessoes_CampoRegra(IdCampoRegra) | — | Operando direito da regra. |
| 5 | IdConstanteTempo | smallint | Y | FK → dbo.Concessoes_ConstanteTempo(IdConstanteTempo) | — | Data a qual modificará ou não o resultado da regra. Ex.: Regra: Idade do servidor >= 60 anos, na constante de 01/01/1990. A idade do servidor será calculada até 01/01/1990 e não até a data de início da vigência da concessão. |
| 6 | DescricaoRegraSimples | varchar(400) | N | — | — | Descrição editada pelo usuário que cadastra a regra. |
| 7 | DescricaoRegraSimplesUsuario | varchar(500) | N | — | — | Descrição gerada automaticamente de acordo com as configurações da regra. |
| 8 | Valor | varchar(200) | Y | — | — | Operando junto ao operador é comparado com esse valor. |
| 9 | Ativo | bit | N | — | — | Descrição |
| 10 | TextoAlerta | varchar(500) | Y | — | — | Texto a ser exibido no Motor de Validação, caso a regra não passe. |
| 11 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 12 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 13 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_TetoBeneficio

Tabela · ~13 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 2 | MesTetoBeneficio | char(2) | N | PK | — | Descrição |
| 3 | AnoTetoBeneficio | char(4) | N | PK | — | Descrição |
| 4 | ValorTetoBeneficio | decimal(14,2) | N | — | — | Descrição |
| 5 | FundamentoLegal | varchar(500) | Y | — | — | Lei Federal descrita pelo próprio usuário. Não há relação com o LEGIS ({{ base_url_legis }}) |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 8 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_TextoPadrao

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTextoPadrao | int | N | PK, IDENT | — | Descrição |
| 2 | TituloTextoPadrao | varchar(150) | N | — | — | Descrição |
| 3 | NomeTextoPadrao | varchar(MAX) | Y | — | — | Modelo de texto escrito pelo usuário. O conteúdo desse campo é em HTML. Pois dessa forma pode-se exibir, o texto, exatamente na formatação que o usuário definiu. |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 6 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 7 | IdOrgao | int | N | — | — | Relação entre um texto padrão e o órgão do usuário que o cadastrou. A tabela de órgão está na API de {{ base_url_tceAdmin2 }}, Bdc.dbo.Gen_Orgao. O valor -1 significa que o registro está relacionado com todos os órgãos. |
| 8 | IsTextoMalaDireta | bit | N | — | — | Se esse texto padrão pode ser utilizado para mala direta. |

## dbo.Concessoes_TipoAfastamento

Tabela · ~108 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAfastamento | int | N | PK, IDENT | — | Descrição |
| 2 | NomeTipoAfastamento | varchar(300) | N | — | — | Descrição |
| 3 | FundamentoLegal | varchar(100) | Y | — | — | Descrição |
| 4 | IdLegislacao | int | Y | — | — | Identificador de Legislação ({{ base_url_legis }}/api/Legislacao/LegislacoesValidadas?idEsferaGovernamental={{idEsfera}}) |
| 5 | IdEsferaGovernamental | tinyint | Y | — | — | Identificador do tipo de esfera governamental. Sua utilização se dá por ENUM no sistema porém sua definição está no banco BDC.Gen_TipoEsferaGovernamental |
| 6 | IdCidade | int | Y | — | — | Identificador de Cidade ({{ base_url_tceadmin2 }}/api/v2/Cidade/?idEstado=20). 20 == IdEstado RN \| Se IdCidade == NULL, pertence ao estado do RN |
| 7 | IdIncidencia | tinyint | Y | — | — | Identificador do tipo de incidência do afastamento. Sua definição está no banco BdSIAIPessoal.Concessoes_TipoIncidenciaAfastamento. Define se o período do afastamento, de um servidor beneficiário da concessão do benefício, é deduzido do seu período de serviço no cargo. |
| 8 | PossuiADTS | bit | Y | — | — | Descrição |
| 9 | IdSiaiDp | int | Y | — | — | Descrição |
| 10 | Ativo | bit | N | — | — | Descrição |
| 11 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 12 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 13 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concessoes_TipoAfastamentoOrgao

Tabela · ~909 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAfastamento | int | N | PK, FK → dbo.Concessoes_TipoAfastamento(IdTipoAfastamento) | — | Descrição |
| 2 | IdOrgao | int | N | PK | — | Descrição |

## dbo.Concessoes_TipoAnexo

Tabela · ~7 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAnexo | int | N | PK, IDENT | — | Descrição |
| 2 | NomeTipoAnexo | varchar(100) | N | — | — | Descrição |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |
| 5 | Obrigatorio | bit | N | — | — | — |

## dbo.Concessoes_TipoAto

Tabela · ~30 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAto | tinyint | N | PK | — | Descrição |
| 2 | IdAreaAtuacao | tinyint | N | — | — | Descrição |
| 3 | NomeTipoAto | varchar(200) | N | — | — | Descrição |
| 4 | CamposPensao | bit | N | — | — | Descrição |
| 5 | CamposLaudoMedico | bit | N | — | — | Descrição |
| 6 | CamposRequerimento | bit | N | — | — | Descrição |
| 7 | PossuiProporcionalidade | bit | N | — | — | Descrição |
| 8 | CodigoProcesso | varchar(3) | N | — | — | Descrição |
| 9 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 10 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |
| 11 | PrecisaValidarCalculosDeTempos | bit | N | — | — | Booleano que define se o tipo de ato precisa passar pela validação do MVA. |

## dbo.Concessoes_TipoComprovante

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoComprovante | int | N | PK | — | Identificador do tipo de comprovante |
| 2 | NomeTipoComprovante | varchar(150) | N | — | — | nome do tipo de comprovante |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_TipoIncidenciaAfastamento

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdIncidenciaAfastamento | tinyint | N | PK | — | Descrição |
| 2 | NomeIncidenciaAfastamento | varchar(300) | N | — | — | Descrição |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_TipoIncidenciaTempoServico

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoIncidenciaTempoServico | tinyint | N | PK | — | Descrição |
| 2 | NomeTipoIncidenciaTempoServico | varchar(30) | N | — | — | Descrição |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_TipoIndicacaoAto

Tabela · ~12 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoIndicacaoAto | tinyint | N | PK | — | Descrição |
| 2 | NomeTipoIndicacaoAto | varchar(100) | N | — | — | Descrição |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |
| 5 | Ativo | bit | N | — | — | — |

## dbo.Concessoes_TipoIndicacaoAto_SubIndicacao

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoBeneficioIndicacao | bigint | N | PK, FK → dbo.Concessoes_AtoBeneficioIndicacao(IdAtoBeneficioIndicacao) | — | — |
| 2 | IdSubIndicacaoAto | int | N | PK, FK → dbo.Concessoes_TipoSubIndicacaoAto(IdSubIndicacaoAto) | — | — |

## dbo.Concessoes_TipoMovimentacaoAto

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoMovimentacaoAto | tinyint | N | PK | — | Descrição |
| 2 | NomeTipoMovimentacaoAto | varchar(100) | N | — | — | Descrição |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_TipoOperadorAritmetico

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOperadorAritmetico | tinyint | N | PK | — | Descrição |
| 2 | SimboloOperadorAritmetico | varchar(2) | N | — | — | Descrição |
| 3 | NomeOperadorAritmetico | varchar(50) | N | — | — | Descrição |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_TipoOperadorLogico

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdOperadorLogico | tinyint | N | PK | — | Descrição |
| 2 | SimboloOperadorLogico | varchar(2) | N | — | — | Descrição |
| 3 | NomeOperadorLogico | varchar(100) | N | — | — | Descrição |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concessoes_TipoSituacaoAtoBeneficio

Tabela · ~21 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoAtoBeneficio | tinyint | N | PK | — | Descrição |
| 2 | NomeSituacao | varchar(50) | N | — | — | Descrição |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |
| 5 | Ativo | bit | N | — | — | — |

## dbo.Concessoes_TipoSubIndicacaoAto

Tabela · ~10 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSubIndicacaoAto | int | N | PK | — | — |
| 2 | NomeSubIndicacaoAto | varchar(250) | Y | — | — | — |
| 3 | Ativo | bit | N | — | — | — |
| 4 | DataInclusao | datetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | — |
| 6 | IdTipoIndicacaoAto | tinyint | Y | FK → dbo.Concessoes_TipoIndicacaoAto(IdTipoIndicacaoAto) | — | — |

## dbo.Concursos_ArquivoAtoConcurso

Tabela · ~807 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdArquivo | int | N | PK, IDENT | — | Identificador do Arquivo |
| 2 | IdAtoConcurso | int | N | FK → dbo.Concursos_AtoConcurso(IdAtoConcurso) | — | Identificador do Ato a qual o arquivo está relacionado |
| 3 | NomeArquivo | varchar(500) | N | — | — | Nome do Arquivo |
| 4 | ObservacoesArquivoAnexo | varchar(500) | Y | — | — | Observações |
| 5 | HashArquivo | char(32) | N | — | — | Hash |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | IdSessao | int | Y | — | — | Identificador da Sessão do Registro |
| 8 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Concursos_AtoConcurso

Tabela · ~953 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoConcurso | int | N | PK, IDENT | — | Identificador do Ato |
| 2 | IdConcurso | int | N | FK → dbo.Concursos_Concurso(IdConcurso) | — | Identificador do Concurso a qual o ato está vinculado |
| 3 | IdTipoAtoConcurso | tinyint | N | FK → dbo.Concursos_TipoAtoConcurso(IdTipoAtoConcurso) | — | Identificador do Tipo de Ato |
| 4 | DataPublicacaoAtoConcurso | smalldatetime | N | — | — | Data da Publicação do Ato, permitida a partir de 1950 até o dia atual |
| 5 | DescricaoAto | varchar(MAX) | Y | — | — | Descrição do Ato quando houver incidente procedimental |
| 6 | DataInclusao | smalldatetime | Y | — | — | Data da Inclusão do Registro |
| 7 | UsuarioInclusao | varchar(11) | Y | — | — | CPF do Usuário da Inclusão do Registro |
| 8 | CPFInclusao | varchar(11) | Y | — | — | CPF do Usuário da Inclusão do Registro |
| 9 | ObservacoesArquivoAnexo | varchar(MAX) | Y | — | — | Descrição dos arquivos anexados |

## dbo.Concursos_AtoConcursoAnulacao

Tabela · ~1 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoConcursoAnulacao | int | N | PK, IDENT | — | Identificador do Ato do tipo Anulação |
| 2 | IdAtoConcurso | int | N | FK → dbo.Concursos_AtoConcurso(IdAtoConcurso) | — | Identificador do Ato do Concurso |
| 3 | DataAnulacaoConcurso | smalldatetime | Y | — | — | Data de anulação do concurso |

## dbo.Concursos_AtoConcursoSuspensao

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdAtoConcursoSuspensao | int | N | PK, IDENT | — | Identificador do Ato do tipo Suspensão |
| 2 | IdAtoConcurso | int | N | FK → dbo.Concursos_AtoConcurso(IdAtoConcurso) | — | Identificador do Ato do Concurso |
| 3 | DataInicioSuspensaoConcurso | smalldatetime | Y | — | — | Data de início da suspensão do concurso |
| 4 | DataFimSuspensaoConcurso | smalldatetime | Y | — | — | Data de fim da suspensão do concurso |
| 5 | IdTipoSituacaoAnteriorConcurso | int | Y | — | — | — |

## dbo.Concursos_Classificados

Tabela · ~1.949 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdClassificado | int | N | PK, IDENT | — | — |
| 2 | IdConcurso | int | N | FK → dbo.Concursos_Concurso(IdConcurso) | — | — |
| 3 | IdCargo | int | N | — | — | — |
| 4 | Classificacao | smallint | N | — | — | — |
| 5 | Nome | varchar(150) | N | — | — | — |
| 6 | CPF | char(11) | N | — | — | — |
| 7 | DataInclusao | datetime | N | — | — | — |
| 8 | IdSessao | int | N | — | — | — |
| 9 | IdSessaoOperacao | int | Y | — | — | — |
| 10 | IdCotaConcurso | int | Y | FK → dbo.Concursos_CotaConcurso(IdCota) | — | FK para a tabela de cotaConcurso. Se null, significa que a classificação do candidato foi para ampla concorrência |

## dbo.Concursos_Concurso

Tabela · ~114 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdConcurso | int | N | PK, IDENT | — | Identificador do Concurso |
| 2 | IdUnidadeJurisdicionada | int | N | — | — | Identificador da Entidade Realizadora |
| 4 | IdTipoConcurso | tinyint | N | FK → dbo.Concursos_TipoConcurso(IdTipoConcurso) | — | Identificador do Tipo de Concurso |
| 5 | IdTipoSituacaoConcurso | tinyint | N | FK → dbo.Concursos_TipoSituacaoConcurso(IdTipoSituacaoConcurso) | — | Identificador da Situacao em que se encontra o concurso |
| 6 | DescricaoObjetivoConcurso | varchar(1000) | N | — | — | Descrição do Objetivo do Concurso |
| 7 | AnoEditalAbertura | char(4) | N | — | — | Ano do Edital de Abertura |
| 8 | NumeroEditalAbertura | varchar(6) | Y | — | — | Numero do Edital de Abertura |
| 9 | ComplementoEditalAbertura | varchar(50) | Y | — | — | Siglas e Informações que complementem a identficação do concurso |
| 10 | DataPublicacaoEditalAbertura | smalldatetime | N | — | — | Data da Publicação do Edital de Abertura |
| 11 | ValidadeMesesEditalAbertura | tinyint | N | — | — | Previsão da Validade do Concurso |
| 12 | PossuiReservaDeVagas | bit | N | — | — | Se possui cotas |
| 13 | DataAnulacaoConcurso | smalldatetime | Y | — | — | Data de Anulação do Concurso |
| 14 | DataInicioSuspensaoConcurso | smalldatetime | Y | — | — | Data de Suspensão do Concurso |
| 15 | DataFimSuspensaoConcurso | smalldatetime | Y | — | — | Data do Fim da Suspensão do Concurso |
| 16 | Ativo | bit | Y | — | — | Gerenciar Delete Lógico |
| 17 | DataInclusao | smalldatetime | Y | — | — | Data da Inclusão do Registro |
| 18 | UsuarioInclusao | varchar(11) | Y | — | — | CPF do Usuário da Inclusão do Registro |
| 19 | CPFInclusao | varchar(11) | Y | — | — | CPF do Usuário da Inclusão do Registro. |
| 20 | IsCalamidadePublica | bit | N | — | — | — |
| 21 | IdNormaCalamidadePublica | int | Y | — | — | — |
| 22 | DisponivelAdmissoes | bit | N | — | — | — |
| 23 | DataInicioPeriodoInscricoes | datetime | Y | — | — | — |
| 24 | DataFimPeriodoInscricoes | datetime | Y | — | — | — |
| 25 | DataAplicacaoProva | datetime | Y | — | — | — |
| 26 | PrazoProrrogacaoMeses | tinyint | Y | — | — | — |
| 27 | DataResultadoProva | datetime | Y | — | — | — |

## dbo.Concursos_ConcursoOrgaoSubalterno

Tabela · ~119 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdConcurso | int | N | PK, FK → dbo.Concursos_Concurso(IdConcurso) | — | Identificador do Concurso |
| 2 | IdUnidadeJurisdicionada | int | N | PK | — | Identificador das UJs subalternas a UJ que é entidade realizadora |

## dbo.Concursos_CotaConcurso

Tabela · ~95 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCota | int | N | PK, IDENT | — | Identificador da Cota |
| 2 | IdConcurso | int | N | FK → dbo.Concursos_Concurso(IdConcurso) | — | Identificador do Concurso |
| 6 | TipoCota | varchar(30) | Y | — | — | Descreve tipo da cota |

## dbo.Concursos_CotaDistribuicao

Tabela · ~9 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCotaDistribuicao | int | N | PK, IDENT | — | Identificador da tabela que relaciona cota a uma tipo de distribuição de vagas |
| 2 | IdDistribuicaoVaga | int | N | FK → dbo.Concursos_DistribuicaoVaga(IdDistribuicaoVaga) | — | Identificador da distribuição de vaga |
| 3 | IdCota | int | N | FK → dbo.Concursos_CotaConcurso(IdCota) | — | Identificador da cota |
| 4 | QuantidadeVaga | int | N | — | — | Quantidade de vagas destinadas aquele tipo de cota dentro daquela determinada distribuição |

## dbo.Concursos_CotaVaga

Tabela · ~208 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCotaVaga | int | N | PK, IDENT | — | Identificador da tabela que relaciona cota a vaga escolhida |
| 2 | IdVaga | int | N | FK → dbo.Concursos_VagaConcurso(IdVaga) | — | Identificador da vaga |
| 3 | IdCota | int | N | FK → dbo.Concursos_CotaConcurso(IdCota) | — | Identificador da cota |
| 4 | QuantidadeVaga | int | N | — | — | Quantidade de vagas destinadas aquele tipo de cota |

## dbo.Concursos_DistribuicaoVaga

Tabela · ~25 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDistribuicaoVaga | int | N | PK, IDENT | — | Identificador da Distribuição de Vagas |
| 2 | IdVaga | int | N | FK → dbo.Concursos_VagaConcurso(IdVaga) | — | Identificador da Vaga |
| 3 | IdTipoDistribuicaoVaga | int | N | FK → dbo.Concursos_TipoDistribuicaoVaga(IdTipoDistribuicaoVaga) | — | Identificador do Tipo de Distribuição de Vagas |
| 4 | DescricaoDistribuicaoVaga | varchar(200) | N | — | — | Descrição da Distribuição de Vagas |
| 5 | QuantidadeVagaAC | int | Y | — | — | Quantidade de Vagas AC |
| 9 | CodigoCargoConcurso | varchar(8) | Y | — | — | Código do Cargo do Concurso |

## dbo.Concursos_HomologacaoCargoConcurso

Tabela · ~285 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdHomologacaoCargo | int | N | PK, IDENT | — | Identificador da Homologação do Cargo |
| 2 | IdAtoConcurso | int | N | FK → dbo.Concursos_AtoConcurso(IdAtoConcurso) | — | Identificador do Ato do Concurso |
| 4 | DataHomologacao | smalldatetime | Y | — | — | Data de Homologação do Cargo |
| 5 | IdVaga | int | Y | FK → dbo.Concursos_VagaConcurso(IdVaga) | — | Identificador da Vaga |

## dbo.Concursos_MensagemConcurso

Tabela · ~220 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdMensagemConcurso | int | N | PK, IDENT | — | — |
| 2 | IdMensagem | int | N | — | — | — |
| 3 | IdConcurso | int | N | FK → dbo.Concursos_Concurso(IdConcurso) | — | — |
| 4 | IsSolicitacaoEdicaoAceita | bit | N | — | — | — |

## dbo.Concursos_Pendencia

Tabela · ~0 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPendencia | int | N | PK, IDENT | — | — |
| 2 | IdMensagemIda | int | Y | — | — | — |
| 3 | IdMensagemResposta | int | Y | — | — | — |
| 4 | IdAtoResposta | int | Y | — | — | — |
| 5 | IdOrgao | int | Y | — | — | — |
| 6 | IdTipoAto | int | Y | — | — | — |

## dbo.Concursos_Requisitos

Tabela · ~172 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRequisito | int | N | PK, IDENT | — | — |
| 2 | IdConcurso | int | N | FK → dbo.Concursos_Concurso(IdConcurso) | — | — |
| 3 | IdCargo | int | N | — | — | — |
| 4 | Documento | varchar(1000) | N | — | — | — |
| 5 | DataInclusao | datetime | N | — | — | — |
| 6 | IdSessao | int | N | — | — | — |
| 7 | IdSessaoOperacao | int | Y | — | — | — |

## dbo.Concursos_ResultadoFinalConcurso

Tabela · ~3.336 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResultadoFinal | int | N | PK, IDENT | — | Identificador do Resultado Final |
| 2 | IdAtoConcurso | int | N | FK → dbo.Concursos_AtoConcurso(IdAtoConcurso) | — | Identificador do Ato |
| 5 | NumeroInscricaoCandidato | varchar(50) | N | — | — | Número de Inscrição do Candidato |
| 6 | CPFCandidato | varchar(11) | N | — | — | CPF do Candidato |
| 7 | NomeCandidato | varchar(200) | Y | — | — | Nome do Candidato |
| 8 | NotaFinalCandidato | decimal(5,2) | N | — | — | Nota Final do Candidato |
| 9 | ClassificacaoGeral | int | N | — | — | Classificação Geral do Candidato |
| 10 | ClassificacaoCota | int | Y | — | — | Classificação no resultado final por cota do Candidato |
| 11 | IdCota | int | Y | FK → dbo.Concursos_CotaConcurso(IdCota) | — | Identificador da Cota |
| 12 | IdVaga | int | Y | FK → dbo.Concursos_VagaConcurso(IdVaga) | — | Identificador da Vaga |

## dbo.Concursos_TipoAtoConcurso

Tabela · ~20 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAtoConcurso | tinyint | N | PK | — | Identificador do Tipo de Ato |
| 2 | DescricaoTipoAtoConcurso | varchar(150) | N | — | — | Descrição do Tipo de Ato |
| 3 | IdTipoClassificacaoAtoConcurso | tinyint | N | FK → dbo.Concursos_TipoClassificacaoAtoConcurso(IdTipoClassificacaoAtoConcurso) | — | Identificador da Classificação do Tipo de Ato |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concursos_TipoClassificacaoAtoConcurso

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoClassificacaoAtoConcurso | tinyint | N | PK | — | Identificador da Classificação do Tipo de Ato |
| 2 | DescricaoTipoClassificacaoAtoConcurso | varchar(50) | N | — | — | Descrição da Classificação do Tipo de Ato |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concursos_TipoConcurso

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoConcurso | tinyint | N | PK | — | Identificador do Tipo de Certame |
| 2 | DescricaoTipoConcurso | varchar(30) | N | — | — | Descrição do Tipo de Certame |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concursos_TipoDistribuicaoVaga

Tabela · ~6 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoDistribuicaoVaga | int | N | PK, IDENT | — | Identificador do Tipo de Distribuição de Vagas |
| 2 | DescricaoTipoDistribuicaoVaga | varchar(50) | N | — | — | Descrição do Tipo de Distribuição de Vagas |

## dbo.Concursos_TipoSituacaoConcurso

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoConcurso | tinyint | N | PK | — | Identificador da Situação do Concurso |
| 2 | DescricaoTipoSituacaoConcurso | varchar(30) | N | — | — | Descrição da Situação do Concurso |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Concursos_TipoSituacaoEnvio

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoSituacaoEnvio | tinyint | N | PK | — | — |
| 2 | DescricaoTipoSituacaoEnvio | varchar(30) | N | — | — | — |
| 3 | DataInclusao | smalldatetime | N | — | — | — |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | — |

## dbo.Concursos_VagaConcurso

Tabela · ~598 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdVaga | int | N | PK, IDENT | — | Identificador da Vaga |
| 2 | IdConcurso | int | N | FK → dbo.Concursos_Concurso(IdConcurso) | — | Identificador do Concurso |
| 3 | IdUnidadeJurisdicionada | int | N | — | — | Identificador da UJ |
| 4 | IdCargo | int | N | FK → dbo.SiaiDp_Cargo(IdCargo) | — | Identificador do Cargo |
| 5 | QuantidadeVagaAC | int | Y | — | — | Quantidade de Vagas AC |
| 7 | ValorRemuneracaoInicial | decimal(14,2) | N | — | — | Valor da Remuneração Inicial |
| 8 | Especialidade | varchar(200) | Y | — | — | Especialidade da Vaga |
| 11 | IsCadastroReserva | bit | Y | — | — | Quando cadastro reserva não precisa incluir número de vagas |
| 12 | QuantidadeVagaTotal | int | Y | — | — | Quantidade de Vagas Totais |
| 15 | CodigoCargoConcurso | varchar(8) | Y | — | — | Código do Cargo do Concurso |
| 16 | IdOrgaoLotacao | int | Y | — | — | Identificador do órgão de lotação |
| 19 | IdLegislacao | int | Y | — | — | — |

## dbo.Envio_CriticaRemessa

Tabela · ~5.933.783 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCriticaRemessa | int | N | PK, IDENT | — | Identificador da Crítica da Remessa |
| 2 | IdEnvioRemessa | int | N | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa |
| 3 | MensagemCriticaRemessa | varchar(MAX) | N | — | — | Mensagem da Crítica da Remessa |
| 4 | TipoCritica | char(1) | N | — | — | Tipo de Crítica ((A)viso; (E)rro; (F)alha) |
| 5 | IdEnvioRemessaUnidadeGestora | int | Y | — | — | Identificador da Remessa da Unidade Gestor (No caso do Estado é a remessa G001) |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |
| 8 | StackTraceErro | varchar(MAX) | Y | — | — | — |
| 9 | InnerException | varchar(MAX) | Y | — | — | — |

## dbo.Envio_DispensaEnvioRemessa

Tabela · ~15 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdDispensaEnvioRemessa | int | N | PK, IDENT | — | Identificador da Dispensa de Envio |
| 2 | IdOrgaoDispensado | int | N | — | — | Identificador do Órgão dispensado |
| 3 | IdOrgaoResponsavelEnvio | int | N | — | — | Identificador do Órgão responsável pelo envio do dados do Órgão dispensado |
| 4 | DataInicioVigencia | smalldatetime | N | — | — | Data do Início da Vigência |
| 5 | DataFimVigencia | smalldatetime | Y | — | — | Data do Fim da Vigência |
| 6 | DescricaoMotivoDispensa | varchar(500) | Y | — | — | Descrição do motivo da Dispensa de Envio |
| 7 | DescricaoMotivoFimDispensa | varchar(500) | Y | — | — | Descrição do motivo do fim da Dispensa de Envio |
| 8 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 9 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 10 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |

## dbo.Envio_PrazoRemessa

Tabela · ~12 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoRemessa | int | N | PK, IDENT | — | Identificador do Prazo da Remessa |
| 2 | PeriodoReferencia | tinyint | N | — | — | Mês do Prazo da Remessa |
| 3 | AnoReferencia | smallint | N | — | — | Ano do Prazo da Remessa |
| 4 | DataPrazoEnvio | date | N | — | — | Data do Prazo final do para o envio da remessa |
| 5 | Descricao | varchar(150) | N | — | — | Texto descritivo do prazo para o envio da remessa |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Envio_Remessa

Tabela · ~108.794 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdEnvioRemessa | int | N | PK, IDENT | — | Identificador do Envio |
| 2 | Ano | char(4) | N | — | — | Ano do envio |
| 3 | Mes | char(2) | N | — | — | Mês do envio |
| 4 | IdOrgao | int | N | — | — | Identificador do órgão que envia dados do SIAIDP |
| 5 | UnidadeGestora | char(4) | Y | — | — | Código LRF do órgão responsável pelo envio dos dados do SIAIP (no caso do Estado é o G001) |
| 6 | IdSituacaoRemessa | tinyint | N | FK → dbo.Envio_SituacaoRemessa(IdSituacaoRemessa) | — | Identificador da situação da remessa |
| 7 | TotalVantagens | decimal(14,2) | Y | — | — | Totalizador do valor total das vantagens de todos os contracheques da remessa |
| 8 | TotalDescontos | decimal(14,2) | Y | — | — | Totalizador do valor total dos descontos de todos os contracheques da remessa |
| 9 | IdEnvioRemessaRetificacao | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa que foi retificada |
| 10 | IdResponsavelInformacao | int | Y | FK → dbo.Envio_ResponsavelInformacao(IdResponsavelInformacao) | — | Identificador do responsável pelos dados do envio |
| 11 | CPFResponsavelEnvio | char(11) | N | — | — | Número do CPF do usuário do sistema que enviou os dados da remessa |
| 12 | NomeResponsavelEnvio | varchar(200) | N | — | — | Nome do usuário do sistema que enviou os dados da remessa |
| 13 | CPFResponsavelInformacao | char(11) | Y | — | — | Número do CPF do responsável pelos dados do envio |
| 14 | NomeResponsavelInformacao | varchar(200) | Y | — | — | Nome do responsável pelos dados do envio |
| 15 | IdProcesso | int | Y | — | — | Identificador do Processo do tipo Documento que é gerado ao final do processamento da remessa |
| 16 | NumeroProcesso | char(6) | Y | — | — | Número do Processo do tipo Documento que é gerado ao final do processamento da remessa |
| 17 | AnoProcesso | smallint | Y | — | — | Ano do Processo do tipo Documento que é gerado ao final do processamento da remessa |
| 18 | NomeSistemaGerador | varchar(50) | Y | — | — | Nome do sistema de TI da empresa ou orgão que gerou o XML do envio da remessa |
| 19 | Observacoes | varchar(800) | Y | — | — | Observações informadas pelo órgão no envio da remessa |
| 20 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 21 | DataInicioProcessamento | smalldatetime | Y | — | — | Data/Hora do início do processamento da remessa |
| 22 | DataFimProcessamento | smalldatetime | Y | — | — | Data/Hora do fim do processamento da remessa |
| 23 | HashMD5Arquivo | char(128) | Y | — | — | Códificação do tipo MD5 do arquivo enviado da remessa |
| 24 | IdTipoEnvioRemessa | tinyint | N | FK → dbo.Envio_TipoRemessa(IdTipoRemessa) | — | Identificador do Tipo de Envio da Remessa (1 - Folha de Pagamento; 2 - Cargos; 3 - Rubricas) |
| 25 | IdEnvioRemessaVinculada | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da remessa principal () |

## dbo.Envio_ResponsavelInformacao

Tabela · ~974 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdResponsavelInformacao | int | N | PK, IDENT | — | Identificador do Responsável pela Informação |
| 2 | CPF | char(11) | N | — | — | Número do CPF do Responsável pela Informação |
| 3 | Nome | varchar(100) | N | — | — | Nome do Responsável pela Informação |
| 4 | Funcao | varchar(40) | Y | — | — | Função do Responsável pela Informação |
| 5 | Email | varchar(60) | N | — | — | Email do Responsável pela Informação |
| 6 | TelefoneComercial | varchar(12) | N | — | — | Telefone Comercial do Responsável pela Informação |
| 7 | TelefoneResidencial | varchar(12) | Y | — | — | Telefone Residencial do Responsável pela Informação |
| 8 | TelefoneCelular | varchar(12) | Y | — | — | Telefone Celular do Responsável pela Informação |
| 9 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |

## dbo.Envio_SituacaoRemessa

Tabela · ~8 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdSituacaoRemessa | tinyint | N | PK | — | Identificador da Situação da Remessa |
| 2 | NomeSituacaoRemessa | varchar(150) | N | — | — | Nome da Situação da Remessa |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.Envio_TipoRemessa

Tabela · ~3 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoRemessa | tinyint | N | PK | — | Identificador do Tipo da Remessa |
| 2 | NomeTipoRemessa | varchar(50) | Y | — | — | Nome do Tipo da Remessa |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDp_Cargo

Tabela · ~81.428 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCargo | int | N | PK, IDENT | — | Identificador do Cargo |
| 2 | IdOrgao | int | N | — | — | Identificador do Órgão ({{ base_url_tceadmin2 }}/v2/UnidadeJurisdicionada/) |
| 3 | IdCarreira | smallint | Y | FK → dbo.Comum_Carreira(IdCarreira) | — | Identificador da Carreira |
| 6 | IdTipoAreaCargo | tinyint | Y | FK → dbo.SiaiDP_TipoAreaCargo(IdTipoAreaCargo) | — | Identificador do Área do Cargo |
| 7 | CodigoCargo | varchar(8) | N | — | — | Código do cargo. Este código é de controle de cada Unidade Judisdicionada |
| 8 | NomeCargo | varchar(200) | N | — | — | Nome do Cargo (deve ser o mesmo nome do cargo criado em lei) |
| 9 | AtribuicoesCargo | varchar(MAX) | Y | — | — | Lista das atribuições do cargo definidas por lei |
| 10 | CargaHoraria | tinyint | N | — | — | Carga Horária do cargo definido em lei |
| 12 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |
| 13 | IdEscolaridade | int | Y | FK → dbo.Comum_Escolaridade(IdEscolaridade) | — | Identificador da Escolaridade |
| 14 | IsCargoExtinto | bit | Y | — | — | Informa se o Cargo foi extinto |
| 15 | IsDedicacaoExclusiva | bit | Y | — | — | Informa se o Cargo tem regime de Dedicação Exclusiva |
| 16 | QtdTotalVagas | smallint | Y | — | — | Informa o total de vagas criadas por Lei para o Cargo |
| 17 | IdTipoNaturezaVinculoCargo | tinyint | Y | FK → dbo.SiaiDP_TipoNaturezaVinculoCargo(IdTipoNaturezaVinculoCargo) | — | Informa o Tipo de Natureza do Cargo |
| 18 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 19 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 20 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 21 | UsuarioInclusao | varchar(11) | Y | — | — | Usuário da Inclusão do Registro |
| 22 | IsCargoValido | bit | Y | — | — | Indica se o cargo é válido |
| 23 | IdRegimeJuridico | int | Y | FK → dbo.Comum_RegimeJuridico(IdRegimeJuridico) | — | Identificador do Regime Jurídico |
| 24 | IsCadastroCompleto | bit | Y | — | — | Indica se o cargo está completo. Um cargo completo possui todos os campos do cadastro preenchidos |
| 25 | NomeCargoAnterior | varchar(200) | Y | — | — | Nome do cargo anterior com o objetivo de manter o histórico de alteracação de nomenclatura do cargo |
| 26 | CodigoCargoAnterior | varchar(8) | Y | — | — | Código do cargo anterior com o objetivo de manter o histórico de alteracação de nomenclatura do cargo |
| 27 | JustificativaExclusao | varchar(200) | Y | — | — | Descrição da justificativa informada na exlusão de um cargo |
| 28 | IsCargoExcluido | bit | Y | — | — | Indica se o cargo foi excluído |
| 29 | DataExclusao | date | Y | — | — | — |
| 30 | DataExtincao | date | Y | — | — | — |

## dbo.SiaiDp_CargoHistorico

Tabela · ~16.821 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCargoHistorico | int | N | PK, IDENT | — | Identificador do Histórico do Cargo |
| 2 | IdCargo | int | N | FK → dbo.SiaiDp_Cargo(IdCargo) | — | Identificador do Cargo |
| 3 | IdLegislacao | int | Y | — | — | Identificador da norma cadastrada na LEGIS |
| 4 | QtdVagas | smallint | Y | — | — | Quantidade de Vagas relacionada ao tipo de movimentação do cargo |
| 5 | IdTipoMovimentacaoCargo | tinyint | N | FK → dbo.SiaiDp_TipoMovimentacaoCargo(IdTipoMovimentacaoCargo) | — | Identificador do tipo de movimentação do cargo |
| 6 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 7 | IdSessao | int | N | — | — | Identificador da Sessão do Registro |
| 8 | IdSessaoOperacao | int | Y | — | — | Identificador da Operação do Registro |
| 9 | UsuarioInclusao | varchar(11) | Y | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDp_CargoRequisito

Tabela · ~17.349 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCargo | int | N | PK, FK → dbo.SiaiDp_Cargo(IdCargo) | — | Identificador do cargo |
| 2 | NomeCargoRequisito | varchar(500) | N | PK | — | Nome do requisito do cargo |

## dbo.SiaiDp_CargoSinonimo

Tabela · ~64.126 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdCargoSinonimo | int | N | PK, IDENT | — | ID dos cargos que estão no SiaiDp_Funcionario e não estão em SiaiDp_Cargo |
| 2 | IdCargo | int | N | FK → dbo.SiaiDp_Cargo(IdCargo) | — | ID do cargo em SiaiDp_Cargo |
| 3 | NomeCargo | varchar(500) | Y | — | — | Nome do cargo que está em SiaiDp_Funcionario e não está em SiaiDp_Cargo |
| 4 | DataInclusao | smalldatetime | N | — | — | — |
| 5 | UsuarioInclusao | varchar(11) | Y | — | — | — |
| 6 | IdSessao | int | Y | — | — | — |

## dbo.SiaiDp_ContraCheque

Tabela · ~34.859.786 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContraCheque | int | N | PK, IDENT | — | Identificador do Contracheque |
| 2 | TotalVantagens | decimal(14,2) | Y | — | — | Totalizador do valor total das vantagens do contracheque |
| 3 | TotalDescontos | decimal(14,2) | Y | — | — | Totalizador do valor total das despesas do contracheque |
| 4 | IdFuncionario | int | Y | FK → dbo.SiaiDp_Funcionario(IdFuncionario) | — | Identificador do servidor relacionado ao contracheque |
| 5 | IdPensionista | int | Y | FK → dbo.SiaiDp_Pensionista(IdPensionista) | — | Identificador do pensionista relacionado ao contracheque |
| 6 | IdFolhaPagamento | int | N | FK → dbo.SiaiDp_FolhaPagamento(IdFolhaPagamento) | — | Identificador da Folha de Pagamento realcionada ao contracheque |
| 7 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 8 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |

## dbo.SiaiDp_ContraChequeItem

Tabela · ~189.029.616 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdContraChequeItem | int | N | PK, IDENT | — | Identificador do item de contracheque |
| 2 | IdContraCheque | int | N | FK → dbo.SiaiDp_ContraCheque(IdContraCheque) | — | Identificador do Contracheque |
| 3 | IdRubrica | int | N | FK → dbo.SiaiDp_Rubrica(IdRubrica) | — | Identificador da Rubrica |
| 4 | IdGrupoFonteRecurso | int | N | — | — | Identificador do grupo de fonte de recurso |
| 5 | IdFonteRecurso | int | N | — | — | Identificador da fonte de recurso |
| 6 | Valor | decimal(14,2) | N | — | — | Valor do item de contracheque |
| 7 | MesReferencia | char(2) | Y | — | — | Mês de referência |
| 8 | AnoReferencia | char(4) | Y | — | — | Ano de referência |
| 9 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 10 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |

## dbo.SiaiDp_FolhaPagamento

Tabela · ~44.049 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFolhaPagamento | int | N | PK, IDENT | — | Identificador da Folha de Pagamento |
| 2 | IdRemessaQuadroFuncional | int | N | FK → dbo.SiaiDp_RemessaQuadroFuncional(IdRemessaQuadroFuncional) | — | Identificador que relaciona a Folha de Pagamento com o quadro |
| 3 | IdRemessaFolhaPagamento | int | Y | FK → dbo.SiaiDp_RemessaFolhaPagamento(IdRemessaFolhaPagamento) | — | Identificador que relaciona a Folha de Pagamento com a remessa |
| 4 | IdTipoFolhaPagamento | smallint | Y | FK → dbo.SiaiDp_TipoFolhaPagamento(IdTipoFolhaPagamento) | — | Identificador do tipo da folha de pagamento |
| 5 | Mes | char(2) | N | — | — | Mês da folha de pagamento |
| 6 | Ano | char(4) | N | — | — | Ano da folha de pagamento |
| 7 | DataInclusao | smalldatetime | Y | — | — | Data da Inclusão do Registro |
| 8 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |

## dbo.SiaiDp_Funcionario

Tabela · ~21.393.894 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFuncionario | int | N | PK, IDENT | — | Identificador do funcionário/servidor |
| 2 | IdRegimeJuridico | int | N | FK → dbo.Comum_RegimeJuridico(IdRegimeJuridico) | — | Identificador do regime jurídico |
| 3 | IdTipoVinculo | int | N | FK → dbo.Comum_TipoVinculo(IdTipoVinculo) | — | Identificador do tipo de vínculo |
| 4 | IdPessoa | int | N | FK → dbo.Comum_Pessoa(IdPessoa) | — | Identificador do dados de pessoais do servidor |
| 5 | IdMotivoDesligamento | int | Y | FK → dbo.Comum_MotivoDesligamento(IdMotivoDesligamento) | — | Identificador do motivo de desligamento |
| 6 | IdCargo | int | Y | FK → dbo.SiaiDp_Cargo(IdCargo) | — | Identificador do cargo. O identificador existe quando o jurisdicionado informou os dados de cargo via xml e fez a associação no xml da folha de pagamento |
| 7 | IdOrgao | int | Y | — | — | Identificador do órgão |
| 8 | Matricula | varchar(20) | N | — | — | Número da matricula do servidor |
| 9 | Lotacao | varchar(150) | N | — | — | Lotação do servidor |
| 10 | DedicacaoExclusiva | bit | N | — | — | Identifica se o servidor exerce o cargo com dedicação exclusiva |
| 11 | DataNomeacao | date | N | — | — | Data de nomeação do servidor |
| 12 | DataPosse | date | N | — | — | Data da posse do servidor |
| 13 | DataExercicio | date | N | — | — | Data de exercício do servidor |
| 14 | DataDesligamento | date | Y | — | — | Data de desligamento do servidor |
| 15 | QuantidadeMesesContratoTemporario | int | Y | — | — | Quantidade de meses do contrato quando o vínculo |
| 16 | SituacaoFuncional | bit | Y | — | — | Situação funcional do servidor. Quando 1 o servidor é ativo, quando 0 o servidor é aposentado |
| 17 | NomeCargo | varchar(150) | Y | — | — | Nome do cargo. Campo é preenchido quando não foi informado o IdCargo, através do código do cargo do Layout de Cargo |
| 18 | CargaHoraria | tinyint | N | — | — | Carga horária do exercício do cargo. Campo é preenchido quando não foi informado o IdCargo, através do código do cargo do Layout de Cargo |
| 19 | CargaHorariaVariavel | tinyint | Y | — | — | Carga Horária Varíavel do cargo definido em lei. Situação em que a lei determina que a opção de hora-extra |
| 20 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 21 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |
| 22 | DataInicial | datetime2(7) | N | — | — | — |
| 23 | DataFinal | datetime2(7) | N | — | — | — |

## dbo.SiaiDp_FuncionarioAfastamento

Tabela · ~649.008 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFuncionarioAfastamento | int | N | PK, IDENT | — | Identificador do Afastamento do Servidor |
| 2 | DataInicio | date | N | — | — | Data de início do afastamento |
| 3 | DataFim | date | Y | — | — | Data fim do afastamento |
| 4 | Remunerado | bit | N | — | — | Indica se o afastamento é remunerado |
| 5 | IdFuncionario | int | N | FK → dbo.SiaiDp_Funcionario(IdFuncionario) | — | Identificador do Servidor |
| 6 | IdTipoAfastamento | int | N | FK → dbo.SiaiDp_TipoAfastamento(IdTipoAfastamento) | — | Identificador do tipo de afastamento |
| 7 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 8 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |

## dbo.SiaiDp_FuncionarioHistorico

Tabela · ~356.144 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdFuncionarioHistorico | int | N | PK, IDENT | — | Identificador do histórico do servidor |
| 2 | DataInicio | date | N | — | — | Data de início do vínculo |
| 3 | DataFim | date | Y | — | — | Dafa fim do vínculo |
| 4 | IdTipoVinculo | int | N | FK → dbo.Comum_TipoVinculo(IdTipoVinculo) | — | Identificador do tipo de vínculo |
| 5 | IdFuncionario | int | N | FK → dbo.SiaiDp_Funcionario(IdFuncionario) | — | Identificador do servidor |

## dbo.SiaiDp_Pensionista

Tabela · ~21.609 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPensionista | int | N | PK, IDENT | — | Identificador do pensionista |
| 2 | IdPessoa | int | N | FK → dbo.Comum_Pessoa(IdPessoa) | — | Identificador dos dados pessoais do servidor |
| 3 | IdTipoPensao | int | N | FK → dbo.SiaiDp_TipoPensao(IdTipoPensao) | — | Identificador do tipo de pensão |
| 4 | DataInicioPensao | date | N | — | — | Data de início da pensão |
| 5 | CpfInstituidorPensao | varchar(11) | Y | — | — | Número do CPF do servidor instituidor da pensão |
| 6 | NomeInstituidorPensao | varchar(200) | Y | — | — | Nome do servidor instituidor da pensão |
| 7 | MatriculaInstituidorPensao | varchar(20) | Y | — | — | Matrícula do servidor instituidor da pensão |
| 8 | UnidadeLotacaoInstituidorPensao | varchar(150) | Y | — | — | Lotação do servidor instituidor da pensão |
| 9 | NomeCargoInstituidorPensao | varchar(100) | Y | — | — | Nome o cargo do servidor instituidor da pensão |
| 10 | IdOrgao | int | Y | — | — | Identificador do órgão do pensionista |
| 11 | Matricula | varchar(20) | N | — | — | Matrícula do pensionista |
| 12 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 13 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |

## dbo.SiaiDp_QuadroFuncional

Tabela · ~14.195.138 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdQuadroFuncional | int | N | PK, IDENT | — | Identificador do quadro funcional |
| 2 | IdRemessa | int | N | FK → dbo.SiaiDp_RemessaQuadroFuncional(IdRemessaQuadroFuncional) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |
| 3 | IdFuncionario | int | Y | FK → dbo.SiaiDp_Funcionario(IdFuncionario) | — | Identificador do servidor |
| 4 | IdPensionista | int | Y | FK → dbo.SiaiDp_Pensionista(IdPensionista) | — | Identificador do pensionista |
| 5 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |

## dbo.SiaiDp_RemessaFolhaPagamento

Tabela · ~76.326 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRemessaFolhaPagamento | int | N | PK, IDENT | — | Identificador da folha de pagamento por remessa |
| 2 | IdEnvioRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |
| 3 | Retificacao | bit | N | — | — | Identifica se a remessa é de retificação |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |

## dbo.SiaiDp_RemessaQuadroFuncional

Tabela · ~84.670 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRemessaQuadroFuncional | int | N | PK, IDENT | — | Identificador do quadro funcional por remessa |
| 2 | IdEnvioRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |
| 3 | Retificacao | bit | N | — | — | Identifica se a remessa é de retificação |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |

## dbo.SiaiDp_Rubrica

Tabela · ~73.097 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdRubrica | int | N | PK, IDENT | — | Identificador da Rubrica |
| 2 | IdOrgao | int | N | — | — | Identificador do órgão da rubrica |
| 3 | IdRubricaESocial | smallint | Y | FK → dbo.SiaiDp_RubricasESocial(Codigo) | — | Identificador do mapaemento da rubrica com o registro do eSocial |
| 4 | Codigo | varchar(20) | N | — | — | Código da rubrica. Este código é de controle de cada Unidade Judisdicionada |
| 5 | Descricao | varchar(100) | N | — | — | Descrição da rubrica |
| 6 | Tipo | char(1) | N | — | — | Tipo da rubrica. O valor 1 refere-se a Vantagens e o valor 2 refere-se a Descontos |
| 7 | FundamentoLegal | varchar(500) | Y | — | — | Descrição do fundamento legal da rubrica |
| 8 | IdRemessa | int | Y | FK → dbo.Envio_Remessa(IdEnvioRemessa) | — | Identificador da Remessa do SIAIDP que gerou ou atualizou o Registro |

## dbo.SiaiDp_RubricasESocial

Tabela · ~208 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | Codigo | smallint | N | PK | — | Código do eSocial |
| 2 | NomeNatureza | varchar(100) | Y | — | — | Natureza do eSocial |
| 3 | DescricaoNatureza | varchar(800) | Y | — | — | Descricao da Natureza do eSocial |
| 4 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 5 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDp_TipoAfastamento

Tabela · ~16 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAfastamento | int | N | PK | — | Identificador do tipo de afastamento |
| 2 | NomeTipoAfastamento | varchar(100) | N | — | — | Nome do tipo de afastamento |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDP_TipoAreaCargo

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoAreaCargo | tinyint | N | PK | — | Identificador da área do cargo |
| 2 | NomeTipoAreaCargo | varchar(100) | N | — | — | Nome da área do cargo |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDp_TipoFolhaPagamento

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoFolhaPagamento | smallint | N | PK | — | Identificador do tipo de folha de pagamento |
| 2 | NomeTipoFolhaPagamento | varchar(100) | N | — | — | Nome do tipo de folha de pagamento |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDp_TipoMovimentacaoCargo

Tabela · ~4 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoMovimentacaoCargo | tinyint | N | PK | — | Identificador do tipo de movimentação de cargo |
| 2 | NomeTipoMovimentacaoCargo | varchar(100) | N | — | — | Nome do tipo de movimentação de cargo |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDP_TipoNaturezaVinculoCargo

Tabela · ~5 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoNaturezaVinculoCargo | tinyint | N | PK | — | Identificador da natureza do vínculo do cargo |
| 2 | NomeTipoNaturezaVinculoCargo | varchar(100) | N | — | — | Nome da natureza do vínculo do cargo |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.SiaiDp_TipoPensao

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdTipoPensao | int | N | PK | — | Identificador do tipo de pensão |
| 2 | NomeTipoPensao | varchar(100) | Y | — | — | Nome do tipo de pensão |
| 3 | DataInclusao | smalldatetime | N | — | — | Data da Inclusão do Registro |
| 4 | UsuarioInclusao | varchar(20) | N | — | — | Usuário da Inclusão do Registro |

## dbo.sysdiagrams

Tabela · ~2 linhas

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | name | sysname | N | — | — | — |
| 2 | principal_id | int | N | — | — | — |
| 3 | diagram_id | int | N | PK, IDENT | — | — |
| 4 | version | int | Y | — | — | — |
| 5 | definition | varbinary(MAX) | Y | — | — | — |

## dbo.vw_EntregaEletronica_PrazoSiaiDP

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | IdPrazoRemessa | int | N | IDENT | — | — |
| 2 | PeriodoReferencia | tinyint | Y | — | — | — |
| 3 | AnoReferencia | smallint | N | — | — | — |
| 4 | DataPrazoEnvio | date | N | — | — | — |
| 5 | Descricao | varchar(58) | Y | — | — | — |

## dbo.vw_SIAIPessoal_UnidadeJurisdicionada_EnviaSIAIDP

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | NomeOrgao | varchar(150) | N | — | — | — |
| 2 | CodigoLRF | char(4) | N | — | — | — |
| 3 | IdOrgao | int | N | — | — | — |
| 4 | IdCidadeOrgao | int | N | — | — | — |
| 5 | NomeCidade | varchar(120) | N | — | — | — |
| 6 | IdOrgaoNatureza | tinyint | N | — | — | — |

## dbo.vw_SIAIPessoal_UnidadeJurisdicionada_GovernoRN

View

| # | Coluna | Tipo | Null | Chave | Default | Descrição |
|---|--------|------|------|-------|---------|-----------|
| 1 | NomeOrgao | varchar(150) | N | — | — | — |
| 2 | CodigoLRF | char(4) | N | — | — | — |
| 3 | IdOrgao | int | N | — | — | — |

