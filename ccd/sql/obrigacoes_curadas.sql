-- Obrigações e recomendações CURADAS pela revisão do CGAD, com o contexto
-- processual necessário ao monitoramento (NBASP 100, "Monitoramento").
--
-- A informação curada é a linha de *Staging: sua existência é o registro da
-- revisão humana, e `Status` guarda o veredito do revisor. Passe :status.
--
-- Armadilhas tratadas aqui, todas verificadas no banco:
--   * `vw_ia_votos_acordaos_decisoes` devolve mais de uma linha para algumas
--     chaves (IdProcesso, IdComposicaoPauta, IdVotoPauta) — um JOIN simples
--     infla 470 obrigações para 509. Daí o OUTER APPLY ... TOP 1.
--   * `Processo_TransitoJulgado` NÃO tem coluna IdProcesso; a junção é por
--     numero_processo + ano_processo, com RTRIM (colunas char).
--   * Interessa o trânsito POSTERIOR à decisão que fixou a obrigação — é dele
--     que corre o prazo (Res. 028/2012, art. 27).
WITH curadas AS (
    SELECT
        'obrigacao'                       AS tipo,
        s.IdObrigacaoStaging              AS id_staging,
        s.IdProcesso                      AS IdProcesso,
        s.IdComposicaoPauta               AS IdComposicaoPauta,
        s.IdVotoPauta                     AS IdVotoPauta,
        s.DescricaoObrigacao              AS descricao,
        s.Prazo                           AS prazo_texto,
        s.DataCumprimento                 AS data_cumprimento,
        s.OrgaoResponsavel                AS orgao_responsavel,
        s.NomeResponsavelMultaCominatoria AS nome_responsavel,
        s.TemMultaCominatoria             AS tem_multa_cominatoria,
        s.ValorMultaCominatoria           AS valor_multa_cominatoria,
        s.DeFazer                         AS de_fazer,
        s.Revisor                         AS revisor,
        s.DataRevisao                     AS data_revisao
    FROM dbo.ObrigacaoStaging s
    WHERE s.Status = :status

    UNION ALL

    SELECT
        'recomendacao',
        r.IdRecomendacaoStaging,
        r.IdProcesso,
        r.IdComposicaoPauta,
        r.IdVotoPauta,
        r.DescricaoRecomendacao,
        r.PrazoCumprimentoRecomendacao,
        r.DataCumprimentoRecomendacao,
        r.OrgaoResponsavel,
        r.NomeResponsavel,
        CAST(0 AS BIT),
        CAST(NULL AS FLOAT),
        CAST(NULL AS BIT),
        r.Revisor,
        r.DataRevisao
    FROM dbo.RecomendacaoStaging r
    WHERE r.Status = :status
)
SELECT
    c.tipo,
    c.id_staging,
    c.IdProcesso                                                AS id_processo,
    RTRIM(p.numero_processo) + '/' + RTRIM(p.ano_processo)      AS processo,
    RTRIM(p.setor_atual)                                        AS setor_atual,
    RTRIM(p.assunto)                                            AS assunto,
    RTRIM(p.interessado)                                        AS interessado,
    RTRIM(rel.nome)                                             AS relator,
    v.acordao                                                   AS acordao,
    v.DataSessao                                                AS data_sessao,
    tj.data_transito                                            AS data_transito,
    CASE WHEN cgr.IdProcessoOriginario IS NULL THEN 0 ELSE 1 END AS tem_cgr,
    c.descricao,
    c.prazo_texto,
    c.data_cumprimento,
    c.orgao_responsavel,
    c.nome_responsavel,
    c.tem_multa_cominatoria,
    c.valor_multa_cominatoria,
    c.de_fazer,
    c.revisor,
    c.data_revisao
FROM curadas c
JOIN processo.dbo.Processos p
    ON p.IdProcesso = c.IdProcesso
LEFT JOIN processo.dbo.Relator rel
    ON rel.codigo = p.codigo_relator
OUTER APPLY (
    SELECT TOP 1
        vw.DataSessao,
        CONCAT(RTRIM(vw.numeroResultado), '/', RTRIM(vw.anoResultado)) AS acordao
    FROM processo.dbo.vw_ia_votos_acordaos_decisoes vw
    WHERE vw.IdProcesso        = c.IdProcesso
      AND vw.IdComposicaoPauta = c.IdComposicaoPauta
      AND vw.idVotoPauta       = c.IdVotoPauta
    ORDER BY vw.DataSessao DESC
) v
OUTER APPLY (
    SELECT TOP 1 t.datatransito AS data_transito
    FROM processo.dbo.Processo_TransitoJulgado t
    WHERE RTRIM(t.numero_processo) = RTRIM(p.numero_processo)
      AND RTRIM(t.ano_processo)    = RTRIM(p.ano_processo)
      AND (t.inativo = 0 OR t.inativo IS NULL)
      AND (v.DataSessao IS NULL OR t.datatransito >= v.DataSessao)
    ORDER BY t.datatransito ASC
) tj
OUTER APPLY (
    SELECT TOP 1 og.IdProcessoOriginario
    FROM processo.dbo.Obg_Obrigacao og
    WHERE og.IdProcessoOriginario = c.IdProcesso
) cgr
ORDER BY processo, c.tipo, c.id_staging
