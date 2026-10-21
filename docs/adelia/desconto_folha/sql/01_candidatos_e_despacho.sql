-- Etapa 1 — processos na CCD com o marcador 'DESCONTO EM FOLHA - Implementar'
-- (:id_setor = 762, :marcador = 'DESCONTO EM FOLHA - Implementar') e dados do despacho
-- de implantação (débito atualizado + órgão pagador pelo SIAI). Bancos: processo, BdDIP.

-- ---------------------------------------------------------------
-- candidatos (marcador mais recente do setor CCD)
-- origem: web/backend/app/ccd/automacao/desconto_folha/service.py:58
WITH marc AS (
    SELECT mp.IdProcesso, m.Descricao AS marcador,
           ROW_NUMBER() OVER (
               PARTITION BY mp.IdProcesso ORDER BY mp.DataInclusao DESC
           ) AS rn
    FROM dbo.Pro_MarcadorProcesso mp
    JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
    WHERE m.IdSetor = :id_setor AND mp.DataExclusao IS NULL
)
SELECT
    RTRIM(p.numero_processo) AS numero_processo,
    RTRIM(p.ano_processo)    AS ano_processo,
    RTRIM(p.assunto)         AS assunto
FROM dbo.Processos p
JOIN marc mc ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
WHERE p.setor_atual = 'CCD'
  AND p.IdProcessoApensador IS NULL
  AND mc.marcador = :marcador
ORDER BY p.ano_processo DESC, p.numero_processo DESC
;

-- ---------------------------------------------------------------
-- dados do despacho por processo (:processos = lista 'NNNNNN/AAAA', bind expansível)
-- origem: web/backend/app/ccd/automacao/desconto_folha/service.py:98
SELECT
    RTRIM(pro.numero_processo) AS numero_processo,
    RTRIM(pro.ano_processo)    AS ano_processo,
    pro.assunto,
    CONCAT(gp.Nome, ' (CPF: ', gp.Documento, ')') AS nome,
    processo.dbo.fn_Exe_RetornaValorAtualizado(ed.IdDebito) AS valor_multa,
    orgao_info.nome_orgao,
    ed.CodigoStatusDivida AS status_divida,
    ed.IdDebito
FROM processo.dbo.Processos pro
INNER JOIN processo.dbo.Pro_MarcadorProcesso pmp ON pmp.IdProcesso = pro.IdProcesso
INNER JOIN processo.dbo.Pro_Marcador pm        ON pmp.IdMarcador = pm.IdMarcador
LEFT JOIN processo.dbo.Exe_Debito ed           ON ed.IdProcessoExecucao = pro.IdProcesso
LEFT JOIN processo.dbo.Exe_DebitoPessoa edp    ON edp.IDDebito = ed.IdDebito
LEFT JOIN processo.dbo.GenPessoa gp            ON gp.IdPessoa = edp.IDPessoa
OUTER APPLY (
    SELECT TOP 1 vspfr.nome_orgao
    FROM BdDIP.dbo.vwSiaiPessoalFolhaResumida vspfr
    WHERE vspfr.cpf = gp.Documento COLLATE SQL_Latin1_General_CP1_CI_AS
    ORDER BY vspfr.ano DESC, vspfr.mes DESC
) AS orgao_info
WHERE pro.setor_atual = 'CCD'
  AND CONCAT(RTRIM(pro.numero_processo), '/', RTRIM(pro.ano_processo)) IN :processos
;
