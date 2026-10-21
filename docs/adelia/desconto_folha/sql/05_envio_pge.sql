-- Etapa 5 — cadastro sai do acompanhamento quando o débito (ou todos os débitos vigentes
-- da pessoa, pela FOLHA da cadeia) foi enviado à PGE. Bancos: processo, BdDIP.

-- ---------------------------------------------------------------
-- débitos com envio vivo à PGE (4 = cancelado)
-- origem: web/backend/app/ccd/desconto_folha/tasks.py:114
SELECT DISTINCT p.IdDebitoExecucao FROM dbo.PGE_Processo p WHERE p.DataCancelamento IS NULL AND p.IdStatusEnvio <> 4
;

-- ---------------------------------------------------------------
-- cadastros a desativar
-- origem: web/backend/app/ccd/desconto_folha/tasks.py:131
SELECT c.* FROM CCDDescontoFolha c
WHERE c.Ativo = 1 AND (
    (c.IdDebito IS NOT NULL AND EXISTS (SELECT 1 FROM processo.dbo.PGE_Processo p WHERE p.IdDebitoExecucao = c.IdDebito AND p.DataCancelamento IS NULL AND p.IdStatusEnvio <> 4))
    OR (c.IdDebito IS NULL AND c.IdPessoa IS NOT NULL
        AND EXISTS (SELECT 1 
    FROM processo.dbo.Exe_Debito d
    JOIN processo.dbo.Exe_DebitoPessoa dp ON dp.IDDebito = d.IdDebito
    WHERE dp.IDPessoa = c.IdPessoa
      AND (d.IdProcessoExecucao = c.IdProcesso OR d.IdProcessoOrigem = c.IdProcesso)
      AND d.DataCancelamento IS NULL
      AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito f
                      WHERE f.IdDebitoAnterior = d.IdDebito AND f.DataCancelamento IS NULL)

                    AND EXISTS (SELECT 1 FROM processo.dbo.PGE_Processo p WHERE p.IdDebitoExecucao = d.IdDebito AND p.DataCancelamento IS NULL AND p.IdStatusEnvio <> 4))
        AND NOT EXISTS (SELECT 1 
    FROM processo.dbo.Exe_Debito d
    JOIN processo.dbo.Exe_DebitoPessoa dp ON dp.IDDebito = d.IdDebito
    WHERE dp.IDPessoa = c.IdPessoa
      AND (d.IdProcessoExecucao = c.IdProcesso OR d.IdProcessoOrigem = c.IdProcesso)
      AND d.DataCancelamento IS NULL
      AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito f
                      WHERE f.IdDebitoAnterior = d.IdDebito AND f.DataCancelamento IS NULL)

                        AND NOT EXISTS (SELECT 1 FROM processo.dbo.PGE_Processo p WHERE p.IdDebitoExecucao = d.IdDebito AND p.DataCancelamento IS NULL AND p.IdStatusEnvio <> 4)))
)
;
