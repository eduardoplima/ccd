SELECT DISTINCT
       'anexo42' AS Fonte,
       resp.CPF,
       respuni.Cargo,
       uni.NomeUnidade AS Orgao,
       CAST(respuni.DataInicioGestao AS date) AS Inicio,
       CAST(respuni.DataTerminoGestao AS date) AS Fim
FROM BdSIAI.dbo.Anexo42_Responsavel resp
INNER JOIN BdSIAI.dbo.Anexo42_ResponsavelUnidade respuni
    ON respuni.IdResponsavel = resp.IdResponsavel
INNER JOIN BdSIAI.dbo.Anexo42_UnidadeJurisdicionada uni
    ON uni.IdUnidadeJurisdicionada = respuni.IdUnidadeJurisdicionada
WHERE resp.CPF IN :cpfs
  AND respuni.Cargo IS NOT NULL

UNION ALL

-- SiaiDp_Funcionario tem uma linha por remessa da folha — agrega por cargo/órgão.
-- DataFinal 9999-12-31 é sentinela de vínculo vigente.
SELECT 'siai_pessoal' AS Fonte,
       cp.CPF,
       COALESCE(c.NomeCargo, f.NomeCargo) AS Cargo,
       LTRIM(RTRIM(og.NomeOrgao)) AS Orgao,
       CAST(MIN(f.DataInicial) AS date) AS Inicio,
       NULLIF(CAST(MAX(f.DataFinal) AS date), '9999-12-31') AS Fim
FROM BdSIAIPessoal.dbo.Comum_Pessoa cp
INNER JOIN BdSIAIPessoal.dbo.SiaiDp_Funcionario f ON f.IdPessoa = cp.IdPessoa
LEFT JOIN BdSIAIPessoal.dbo.SiaiDp_Cargo c ON c.IdCargo = f.IdCargo
LEFT JOIN Bdc.dbo.vw_Gen_Orgao og ON og.IdOrgao = f.IdOrgao
WHERE cp.CPF IN :cpfs
GROUP BY cp.CPF, COALESCE(c.NomeCargo, f.NomeCargo), LTRIM(RTRIM(og.NomeOrgao))
HAVING COALESCE(c.NomeCargo, f.NomeCargo) IS NOT NULL

ORDER BY CPF, Fim DESC, Inicio DESC;
