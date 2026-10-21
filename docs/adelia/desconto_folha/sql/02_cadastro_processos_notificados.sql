-- Etapa 2 — cadastro automático (cron diário): processos com informação de notificação
-- alusiva a desconto em folha desde :desde, e seus débitos/pessoas. Banco: processo.

-- ---------------------------------------------------------------
-- processos notificados para desconto em folha
-- origem: web/backend/app/ccd/desconto_folha/tasks.py:101
SELECT DISTINCT p.IdProcesso
FROM dbo.vw_ata_informacao inf
JOIN dbo.Processos p
  ON RTRIM(p.numero_processo) = RTRIM(inf.numero_processo)
 AND RTRIM(p.ano_processo) = RTRIM(inf.ano_processo)
WHERE (inf.nome_informacao LIKE '%NOTIFICA%' OR inf.resumo LIKE '%Notifica%')
  AND (inf.nome_informacao LIKE '%FOLHA%' OR inf.resumo LIKE '%folha%')
  AND inf.data_resumo >= :desde
;

-- ---------------------------------------------------------------
-- dados do processo
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:31
SELECT IdProcesso, RTRIM(numero_processo) AS numero, RTRIM(ano_processo) AS ano,
       RTRIM(codigo_tipo_processo) AS tipo, data_registro, idprocessoorigemexecucao AS id_origem,
       IdProcessoApensador
FROM dbo.Processos
WHERE IdProcesso = :id
;

-- ---------------------------------------------------------------
-- débitos do processo
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:85
SELECT d.IdDebito AS id_debito, d.valorOriginalDebito AS valor_original,
       RTRIM(td.Descricao) AS tipo, RTRIM(sd.DescricaoStatusDivida) AS status,
       d.DataCancelamento AS data_cancelamento,
       dp.IDPessoa AS id_pessoa, gp.Nome AS nome_pessoa, gp.Documento AS documento,
       CASE WHEN EXISTS (SELECT 1 FROM dbo.Exe_Debito f
                         WHERE f.IdDebitoAnterior = d.IdDebito
                           AND f.DataCancelamento IS NULL)
            THEN 1 ELSE 0 END AS desdobrado
FROM dbo.Exe_Debito d
LEFT JOIN dbo.Exe_TipoDebito td ON td.CodigoTipoDebito = d.CodigoTipoDebito
LEFT JOIN dbo.Exe_StatusDivida sd ON sd.CodigoStatusDivida = d.CodigoStatusDivida
LEFT JOIN dbo.Exe_DebitoPessoa dp ON dp.IDDebito = d.IdDebito
LEFT JOIN dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
WHERE (d.IdProcessoExecucao = :id OR d.IdProcessoOrigem = :id)
ORDER BY d.DataCancelamento, desdobrado, d.IdDebito
;

-- ---------------------------------------------------------------
-- valores da cadeia do débito
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:116
WITH cadeia AS (
    SELECT IdDebito FROM dbo.Exe_Debito WHERE IdDebito = :id
    UNION ALL
    SELECT f.IdDebito FROM dbo.Exe_Debito f
    JOIN cadeia c ON f.IdDebitoAnterior = c.IdDebito
)
SELECT (SELECT valorOriginalDebito FROM dbo.Exe_Debito WHERE IdDebito = :id)
           AS original,
       SUM(dbo.fn_Exe_RetornaValorAtualizado(d.IdDebito)) AS atualizado
FROM cadeia JOIN dbo.Exe_Debito d ON d.IdDebito = cadeia.IdDebito
WHERE d.DataCancelamento IS NULL
  AND NOT EXISTS (SELECT 1 FROM dbo.Exe_Debito f
                   WHERE f.IdDebitoAnterior = d.IdDebito
                     AND f.DataCancelamento IS NULL)
;

-- ---------------------------------------------------------------
-- pessoa
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:150
SELECT IdPessoa AS id_pessoa, Nome AS nome, Documento AS documento FROM dbo.GenPessoa WHERE IdPessoa = :id
;

-- ---------------------------------------------------------------
-- órgão notificado (responsável de despesa)
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:165
SELECT TOP 1 gp.Nome
FROM dbo.Pro_ProcessosResponsavelDespesa r
JOIN dbo.GenPessoa gp ON gp.IdPessoa = r.IdPessoa
WHERE r.IdProcesso = :id AND gp.TipoPessoa = 'J'
ORDER BY r.DataInclusao DESC
;
