-- Etapa 6 — conciliação das parcelas descontadas com os créditos na conta do FRAP
-- (FRAPLancamento, crédito 'C', categorias 1 e 3; um crédito quita só uma parcela). Banco: BdDIP.

-- ---------------------------------------------------------------
-- créditos com valor exato a partir da data mínima, ainda não vinculados
-- origem: web/backend/app/ccd/desconto_folha/match.py:24
SELECT L.IdLancamento AS id_lancamento, L.DtMovimento AS dt_movimento,
       L.Documento AS documento, L.Historico AS historico, L.Valor AS valor
FROM FRAPLancamento L
WHERE L.ValorDC = 'C' AND L.IdCategoria IN (1, 3)
  AND ABS(L.Valor - :valor) < 0.005
  AND (:data_min IS NULL OR L.DtMovimento >= :data_min)
  AND NOT EXISTS (SELECT 1 FROM CCDDescontoFolhaMatch m
                   WHERE m.IdLancamentoFRAP = L.IdLancamento)
ORDER BY L.DtMovimento, L.IdLancamento
;

-- ---------------------------------------------------------------
-- cadastros com parcelas sem crédito vinculado
-- origem: web/backend/app/ccd/desconto_folha/tasks.py:246
SELECT DISTINCT d.IdCCDDescontoFolha
FROM CCDDescontoFolha d
JOIN CCDDescontoFolhaValor v ON v.IdCCDDescontoFolha = d.IdCCDDescontoFolha
LEFT JOIN CCDDescontoFolhaMatch m
    ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
WHERE d.Ativo = 1 AND m.IdCCDDescontoFolhaMatch IS NULL
;

-- ---------------------------------------------------------------
-- parcelas ainda sem crédito de um cadastro
-- origem: web/backend/app/ccd/desconto_folha/match.py:256
SELECT v.IdCCDDescontoFolhaValor AS id_valor, v.MesReferencia AS mes,
       v.AnoReferencia AS ano, v.Valor AS valor
FROM CCDDescontoFolhaValor v
LEFT JOIN CCDDescontoFolhaMatch m ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
WHERE v.IdCCDDescontoFolha = :c AND m.IdCCDDescontoFolhaMatch IS NULL
;
-- ---------------------------------------------------------------
-- busca 'FRAP-first' por texto do órgão, valor e data
-- origem: web/backend/app/ccd/desconto_folha/match.py:59
SELECT L.IdLancamento AS id_lancamento, L.DtMovimento AS dt_movimento,
       L.Documento AS documento, L.Historico AS historico, L.Descricao AS descricao,
       L.Valor AS valor,
       (SELECT MIN(v.IdCCDDescontoFolha)
          FROM CCDDescontoFolhaMatch m
          JOIN CCDDescontoFolhaValor v ON v.IdCCDDescontoFolhaValor = m.IdCCDDescontoFolhaValor
         WHERE m.IdLancamentoFRAP = L.IdLancamento) AS id_cadastro_vinculado
FROM FRAPLancamento L
WHERE L.ValorDC = 'C' AND L.IdCategoria IN (1, 3)
  AND (:desde IS NULL OR L.DtMovimento >= :desde)
  AND (:valor IS NULL OR ABS(L.Valor - :valor) < 0.005)
  AND (:texto IS NULL
       OR UPPER(COALESCE(L.Descricao, '') + ' ' + COALESCE(L.Historico, ''))
          LIKE :padrao)   -- :padrao = '%' + UPPER(:texto) + '%'
ORDER BY L.Valor, L.DtMovimento, L.IdLancamento
;
