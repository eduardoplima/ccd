-- Etapa 3 — localiza a notificação ao órgão e a data de recebimento (certidão eletrônica,
-- AR postal ou certidão da Diretoria de Expediente). O nº do mandado eletrônico só está
-- no PDF: o texto é lido localmente por expressão regular. Banco: processo.

-- ---------------------------------------------------------------
-- informações/eventos do processo
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:182
SELECT inf.idInformacao AS id_informacao, ppe.SequencialProcessoEvento AS evento,
       ppe.IdProcessoEvento AS id_evento,
       RTRIM(inf.setor) AS setor, inf.ordem, inf.nome_informacao, inf.resumo,
       inf.data_resumo, inf.Inativa, inf.Titulo_Modelo_informacao AS titulo,
       CONCAT(RTRIM(inf.setor), '_', inf.numero_processo, '_', inf.ano_processo, '_',
              RIGHT(CONCAT('0000', inf.ordem), 4), '.pdf') AS arquivo
FROM dbo.vw_ata_informacao inf
JOIN dbo.Pro_ProcessoEvento ppe ON ppe.IdInformacao = inf.idInformacao
WHERE inf.numero_processo = :numero AND inf.ano_processo = :ano
ORDER BY inf.ordem
;

-- ---------------------------------------------------------------
-- informação de notificação alusiva a folha (vw_ata_informacao)
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:213
SELECT TOP 1 idInformacao, data_resumo FROM dbo.vw_ata_informacao
WHERE numero_processo = :numero AND ano_processo = :ano
  AND (nome_informacao LIKE '%NOTIFICA%' OR resumo LIKE '%Notifica%')
  AND (nome_informacao LIKE '%FOLHA%' OR resumo LIKE '%folha%')
ORDER BY data_resumo DESC
;

-- ---------------------------------------------------------------
-- certidão de notificação (Cit_Certidao, Classe NOT)
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:228
SELECT TOP 1 NumeroCitacao, AnoCitacao, DataInclusao FROM dbo.Cit_Certidao
WHERE Numero_processo = :numero AND Ano_processo = :ano AND Classe = 'NOT'
  AND inativo IS NULL
ORDER BY DataInclusao DESC
;

-- ---------------------------------------------------------------
-- notificação no Cit_Citacoes (processo ou origem)
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:243
SELECT TOP 1 Numero_Citacao, Ano_citacao, DataInicioContagem, DataInclusao,
       NumeroPostagem, IdCitacao
FROM dbo.Cit_Citacoes
WHERE IdProcesso IN (:id, :id_origem) AND Tipo LIKE 'N%' AND DataExclusao IS NULL
ORDER BY DataInclusao DESC
;

-- ---------------------------------------------------------------
-- fallback de numeração: certidão NOT por processo
-- origem: web/backend/app/ccd/desconto_folha/notificacao.py:129
SELECT TOP 1 NumeroCitacao, AnoCitacao, DataInclusao FROM dbo.Cit_Certidao
WHERE Numero_processo = :numero AND Ano_processo = :ano AND Classe = 'NOT'
  AND inativo IS NULL AND NumeroCitacao IS NOT NULL
ORDER BY DataInclusao DESC
;

-- ---------------------------------------------------------------
-- AR postal — objeto
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:271
SELECT TOP 1 RTRIM(g.NumeroPostagem) AS postagem, g.DataRecebimento, ret.DataEntregaAR
FROM dbo.Cit_ItensGuiaPostagem g
LEFT JOIN dbo.Cit_ItensArquivoRetorno ret ON RTRIM(ret.NumeroObjeto) = RTRIM(g.NumeroPostagem)
WHERE (g.IdInformacao = :idi) OR (g.IdCitacao = :idc)
   OR (RTRIM(g.NumeroPostagem) = :post)
ORDER BY g.DataInclusao DESC
;

-- ---------------------------------------------------------------
-- AR postal — data de entrega
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:287
SELECT TOP 1 DataEntregaAR FROM dbo.Cit_ItensArquivoRetorno WHERE RTRIM(NumeroObjeto) = :post ORDER BY DataEntregaAR DESC
;
