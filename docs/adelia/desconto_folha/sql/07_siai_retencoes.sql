-- Etapa 7 — confirmação no contracheque (SIAI Pessoal, 2021+): rubricas de desconto do TCE
-- por competência. Usa as tabelas-base (a view é lenta) e deduplica remessas retificadoras.
-- Bancos: BDSiaiPessoal, Bdc.

-- ---------------------------------------------------------------
-- valor retido para o TCE por competência
-- origem: web/backend/app/ccd/siai_pessoal/service.py:72
WITH cc AS (
    SELECT CC.IdContraCheque, F.IdTipoFolhaPagamento, ER.IdOrgao,
           TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) AS ano,
           TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT) AS mes,
           CC.Matricula, CC.NomeCargo, CC.Lotacao, P.Nome,
           CC.TotalVantagens, CC.TotalDescontos,
           ROW_NUMBER() OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento
               ORDER BY ER.IdEnvioRemessa DESC, CC.IdContraCheque DESC) AS rn,
           COUNT(*) OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento) AS remessas
    FROM BDSiaiPessoal.dbo.Comum_Pessoa P
    -- Servidor (SiaiDp_Funcionario) ou pensionista (SiaiDp_Pensionista, ex.: IPERN).
    CROSS APPLY (
        SELECT C.IdContraCheque, C.IdFolhaPagamento, C.TotalVantagens, C.TotalDescontos,
               FU.Matricula, FU.NomeCargo, FU.Lotacao
        FROM BDSiaiPessoal.dbo.SiaiDp_Funcionario FU
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdFuncionario = FU.IdFuncionario
        WHERE FU.IdPessoa = P.IdPessoa
        UNION ALL
        SELECT C.IdContraCheque, C.IdFolhaPagamento, C.TotalVantagens, C.TotalDescontos,
               PE.Matricula,
               'Pensão' + COALESCE(' – ' + LTRIM(RTRIM(PE.NomeCargoInstituidorPensao)), ''),
               PE.UnidadeLotacaoInstituidorPensao
        FROM BDSiaiPessoal.dbo.SiaiDp_Pensionista PE
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdPensionista = PE.IdPensionista
        WHERE PE.IdPessoa = P.IdPessoa
    ) CC
    JOIN BDSiaiPessoal.dbo.SiaiDp_FolhaPagamento F ON F.IdFolhaPagamento = CC.IdFolhaPagamento
    JOIN BDSiaiPessoal.dbo.SiaiDp_RemessaFolhaPagamento RFP
      ON RFP.IdRemessaFolhaPagamento = F.IdRemessaFolhaPagamento
    JOIN BDSiaiPessoal.dbo.Envio_Remessa ER ON ER.IdEnvioRemessa = RFP.IdEnvioRemessa
    WHERE P.CPF = :cpf
      AND ER.IdTipoEnvioRemessa = 1
      AND ER.IdSituacaoRemessa IN (4, 7)
      AND ER.IdEnvioRemessaVinculada IS NOT NULL
      AND TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) >= :ano_min
)

SELECT cc.ano, cc.mes, R.Tipo AS tipo, UPPER(LTRIM(RTRIM(R.Descricao))) AS rubrica,
       SUM(CAST(CCI.Valor AS DECIMAL(18, 2))) AS valor
FROM cc
JOIN BDSiaiPessoal.dbo.SiaiDp_ContraChequeItem CCI ON CCI.IdContraCheque = cc.IdContraCheque
JOIN BDSiaiPessoal.dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
WHERE cc.rn = 1
GROUP BY cc.ano, cc.mes, R.Tipo, UPPER(LTRIM(RTRIM(R.Descricao)))
;

-- ---------------------------------------------------------------
-- contracheque completo de uma competência
-- origem: web/backend/app/ccd/siai_pessoal/service.py:85
WITH cc AS (
    SELECT CC.IdContraCheque, F.IdTipoFolhaPagamento, ER.IdOrgao,
           TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) AS ano,
           TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT) AS mes,
           CC.Matricula, CC.NomeCargo, CC.Lotacao, P.Nome,
           CC.TotalVantagens, CC.TotalDescontos,
           ROW_NUMBER() OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento
               ORDER BY ER.IdEnvioRemessa DESC, CC.IdContraCheque DESC) AS rn,
           COUNT(*) OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento) AS remessas
    FROM BDSiaiPessoal.dbo.Comum_Pessoa P
    -- Servidor (SiaiDp_Funcionario) ou pensionista (SiaiDp_Pensionista, ex.: IPERN).
    CROSS APPLY (
        SELECT C.IdContraCheque, C.IdFolhaPagamento, C.TotalVantagens, C.TotalDescontos,
               FU.Matricula, FU.NomeCargo, FU.Lotacao
        FROM BDSiaiPessoal.dbo.SiaiDp_Funcionario FU
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdFuncionario = FU.IdFuncionario
        WHERE FU.IdPessoa = P.IdPessoa
        UNION ALL
        SELECT C.IdContraCheque, C.IdFolhaPagamento, C.TotalVantagens, C.TotalDescontos,
               PE.Matricula,
               'Pensão' + COALESCE(' – ' + LTRIM(RTRIM(PE.NomeCargoInstituidorPensao)), ''),
               PE.UnidadeLotacaoInstituidorPensao
        FROM BDSiaiPessoal.dbo.SiaiDp_Pensionista PE
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdPensionista = PE.IdPensionista
        WHERE PE.IdPessoa = P.IdPessoa
    ) CC
    JOIN BDSiaiPessoal.dbo.SiaiDp_FolhaPagamento F ON F.IdFolhaPagamento = CC.IdFolhaPagamento
    JOIN BDSiaiPessoal.dbo.SiaiDp_RemessaFolhaPagamento RFP
      ON RFP.IdRemessaFolhaPagamento = F.IdRemessaFolhaPagamento
    JOIN BDSiaiPessoal.dbo.Envio_Remessa ER ON ER.IdEnvioRemessa = RFP.IdEnvioRemessa
    WHERE P.CPF = :cpf
      AND ER.IdTipoEnvioRemessa = 1
      AND ER.IdSituacaoRemessa IN (4, 7)
      AND ER.IdEnvioRemessaVinculada IS NOT NULL
      AND TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) >= :ano_min
)

SELECT cc.IdContraCheque, cc.IdOrgao, O.NomeOrgao, TF.NomeTipoFolhaPagamento AS tipo_folha,
       cc.Matricula, cc.NomeCargo, cc.Lotacao, cc.Nome, cc.TotalVantagens, cc.TotalDescontos,
       cc.remessas, R.Codigo AS codigo, R.Descricao AS descricao, R.Tipo AS tipo,
       CCI.Valor AS valor
FROM cc
JOIN BDSiaiPessoal.dbo.SiaiDp_TipoFolhaPagamento TF
  ON TF.IdTipoFolhaPagamento = cc.IdTipoFolhaPagamento
LEFT JOIN Bdc.dbo.vw_Gen_Orgao O ON O.IdOrgao = cc.IdOrgao
JOIN BDSiaiPessoal.dbo.SiaiDp_ContraChequeItem CCI ON CCI.IdContraCheque = cc.IdContraCheque
JOIN BDSiaiPessoal.dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
WHERE cc.rn = 1 AND cc.ano = :ano AND cc.mes = :mes
ORDER BY cc.IdOrgao, cc.IdTipoFolhaPagamento, R.Tipo, R.Codigo
;

-- ---------------------------------------------------------------
-- retenções detalhadas
-- origem: web/backend/app/ccd/siai_pessoal/service.py:164
WITH cc AS (
    SELECT CC.IdContraCheque, F.IdTipoFolhaPagamento, ER.IdOrgao,
           TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) AS ano,
           TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT) AS mes,
           CC.Matricula, CC.NomeCargo, CC.Lotacao, P.Nome,
           CC.TotalVantagens, CC.TotalDescontos,
           ROW_NUMBER() OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento
               ORDER BY ER.IdEnvioRemessa DESC, CC.IdContraCheque DESC) AS rn,
           COUNT(*) OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento) AS remessas
    FROM BDSiaiPessoal.dbo.Comum_Pessoa P
    -- Servidor (SiaiDp_Funcionario) ou pensionista (SiaiDp_Pensionista, ex.: IPERN).
    CROSS APPLY (
        SELECT C.IdContraCheque, C.IdFolhaPagamento, C.TotalVantagens, C.TotalDescontos,
               FU.Matricula, FU.NomeCargo, FU.Lotacao
        FROM BDSiaiPessoal.dbo.SiaiDp_Funcionario FU
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdFuncionario = FU.IdFuncionario
        WHERE FU.IdPessoa = P.IdPessoa
        UNION ALL
        SELECT C.IdContraCheque, C.IdFolhaPagamento, C.TotalVantagens, C.TotalDescontos,
               PE.Matricula,
               'Pensão' + COALESCE(' – ' + LTRIM(RTRIM(PE.NomeCargoInstituidorPensao)), ''),
               PE.UnidadeLotacaoInstituidorPensao
        FROM BDSiaiPessoal.dbo.SiaiDp_Pensionista PE
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdPensionista = PE.IdPensionista
        WHERE PE.IdPessoa = P.IdPessoa
    ) CC
    JOIN BDSiaiPessoal.dbo.SiaiDp_FolhaPagamento F ON F.IdFolhaPagamento = CC.IdFolhaPagamento
    JOIN BDSiaiPessoal.dbo.SiaiDp_RemessaFolhaPagamento RFP
      ON RFP.IdRemessaFolhaPagamento = F.IdRemessaFolhaPagamento
    JOIN BDSiaiPessoal.dbo.Envio_Remessa ER ON ER.IdEnvioRemessa = RFP.IdEnvioRemessa
    WHERE P.CPF = :cpf
      AND ER.IdTipoEnvioRemessa = 1
      AND ER.IdSituacaoRemessa IN (4, 7)
      AND ER.IdEnvioRemessaVinculada IS NOT NULL
      AND TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) >= :ano_min
)

SELECT cc.ano, cc.mes, cc.IdOrgao AS id_orgao, O.NomeOrgao AS orgao,
       R.Codigo AS codigo, R.Descricao AS descricao, R.Tipo AS tipo,
       SUM(CAST(CCI.Valor AS DECIMAL(18, 2))) AS valor
FROM cc
LEFT JOIN Bdc.dbo.vw_Gen_Orgao O ON O.IdOrgao = cc.IdOrgao
JOIN BDSiaiPessoal.dbo.SiaiDp_ContraChequeItem CCI ON CCI.IdContraCheque = cc.IdContraCheque
JOIN BDSiaiPessoal.dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
WHERE cc.rn = 1 AND R.Tipo = '2'
GROUP BY cc.ano, cc.mes, cc.IdOrgao, O.NomeOrgao, R.Codigo, R.Descricao, R.Tipo
;
