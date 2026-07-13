-- ============================================================================
-- Liquidação do Acórdão nº 197/2026 - TC (processo 000068/2024)
-- Pagamentos das Prefeituras de Cruzeta (369), Jucurutu (400) e Lagoa Nova (405)
-- ao escritório Fernanda de Paula Sociedade Individual de Advocacia
-- (CNPJ 48.581.488/0001-14), apurados no SIAI (Anexo 14) via BdDIP.
--
-- Executar conectado ao banco BdDIP (as views leem o BdSIAI por trás e já
-- filtram arquivos processados com sucesso — situação 4).
-- Serra Negra do Norte (item II.h do acórdão): incluir id_orgao 475.
-- ============================================================================

-- 1) Pagamentos detalhados (base da tabela analítica da informação)
SELECT  p.id_orgao,
        p.codigo_orgao,
        p.municipio,
        p.data,
        p.documento,
        p.valor,
        ISNULL(p.valor_anulado, 0)            AS valor_anulado,
        p.valor - ISNULL(p.valor_anulado, 0)  AS valor_liquido,
        p.numero_processo                     AS processo_despesa,
        p.fonte_recurso,
        p.descricao_fonte_recurso
FROM    dbo.vwDespesaPagamento p
WHERE   p.cpf_cnpj_favorecido = '48581488000114'
  AND   p.id_orgao IN (369, 400, 405)
ORDER BY p.id_orgao, p.data, p.documento;

-- 2) Resumo por município: total pago x teto indenizatório x valor a restituir
--    (tetos por ciclo fixados no item II.c do Acórdão nº 197/2026 - TC;
--     ciclo único 2023/2024 — sem pagamentos no ciclo 2024/2025)
SELECT  p.municipio,
        SUM(p.valor - ISNULL(p.valor_anulado, 0))        AS total_pago,
        t.teto,
        SUM(p.valor - ISNULL(p.valor_anulado, 0)) - t.teto AS valor_a_restituir
FROM    dbo.vwDespesaPagamento p
JOIN    (VALUES (369, 480000.00),   -- Cruzeta
                (400, 250000.00),   -- Jucurutu
                (405, 320000.00))   -- Lagoa Nova
        AS t (id_orgao, teto) ON t.id_orgao = p.id_orgao
WHERE   p.cpf_cnpj_favorecido = '48581488000114'
GROUP BY p.municipio, t.teto
ORDER BY p.municipio;

-- 3) Empenhos de origem dos pagamentos (tabela do §3 da informação)
SELECT DISTINCT
        e.municipio,
        e.documento       AS empenho,
        e.justificativa   AS descricao,
        e.fonte_recurso,
        e.descricao_fonte_recurso
FROM    dbo.vwDespesaPagamento p
JOIN    dbo.vwDespesaEmpenho  e ON e.id_empenho = p.id_empenho
WHERE   p.cpf_cnpj_favorecido = '48581488000114'
  AND   p.id_orgao IN (369, 400, 405)
ORDER BY e.municipio, e.documento;
