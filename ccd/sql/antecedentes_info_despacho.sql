-- Para cada processo selecionado, a informacao mais recente (último despacho):
-- setor, assunto, interessado, numero/ano e o nome do arquivo PDF no share
-- (input do LLM). Portado de web/backend/app/ccd/antecedentes/sql/info_despacho.sql.
WITH RankedData AS (
    SELECT
        ai.setor,
        CONCAT(pro.numero_processo, '/', pro.ano_processo) AS processo,
        pro.assunto,
        pro.interessado,
        CONCAT(
            RTRIM(ai.setor), '_',
            ai.numero_processo, '_',
            ai.ano_processo, '_',
            RIGHT(CONCAT('0000', ai.ordem), 4), '.pdf'
        ) AS arquivo,
        ai.numero_processo,
        ai.ano_processo,
        ROW_NUMBER() OVER (
            PARTITION BY CONCAT(ai.numero_processo, '/', ai.ano_processo)
            ORDER BY ppe.SequencialProcessoEvento DESC
        ) AS rn
    FROM processo.dbo.vw_Ata_Informacao ai
    LEFT JOIN processo.dbo.Pro_ProcessoEvento ppe
        ON ai.idInformacao = ppe.IdInformacao
    LEFT JOIN processo.dbo.Processos pro
        ON pro.numero_processo = ai.numero_processo
        AND pro.ano_processo = ai.ano_processo
    WHERE CONCAT(ai.numero_processo, '/', ai.ano_processo) IN :processos
)
SELECT setor, processo, assunto, interessado, arquivo, numero_processo, ano_processo
FROM RankedData
WHERE rn = 1
ORDER BY numero_processo, ano_processo
