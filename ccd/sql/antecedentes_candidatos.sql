-- Processos candidatos a antecedentes: setor CCD, com (:todos=0) o filtro de
-- marcador `%antecedente%` (Pro_MarcadorProcesso -> Pro_Marcador por IdSetor).
-- Portado de web/backend/app/ccd/antecedentes/sql/candidatos.sql.
WITH marc AS (
    SELECT mp.IdProcesso, m.Descricao AS marcador,
           ROW_NUMBER() OVER (
               PARTITION BY mp.IdProcesso ORDER BY mp.DataInclusao DESC
           ) AS rn
    FROM processo.dbo.Pro_MarcadorProcesso mp
    JOIN processo.dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
    WHERE m.IdSetor = :id_setor AND mp.DataExclusao IS NULL
)
SELECT
    CONCAT(RTRIM(p.numero_processo), '/', RTRIM(p.ano_processo)) AS processo,
    RTRIM(p.assunto)      AS assunto,
    RTRIM(p.interessado)  AS interessado
FROM processo.dbo.Processos p
LEFT JOIN marc mc ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
WHERE p.setor_atual = 'CCD'
  AND p.IdProcessoApensador IS NULL
  AND (:todos = 1 OR LOWER(mc.marcador) LIKE '%antecedente%')
ORDER BY p.ano_processo DESC, p.numero_processo DESC
