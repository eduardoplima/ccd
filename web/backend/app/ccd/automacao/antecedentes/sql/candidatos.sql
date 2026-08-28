-- Processos candidatos a antecedentes: setor CCD, com (ou sem) o filtro de
-- marcador `%antecedente%`. Espelha o join setor/marcador de
-- app.ccd.service.listar_processos (Pro_MarcadorProcesso -> Pro_Marcador,
-- filtrando por IdSetor) e devolve só o que a página precisa para a seleção.
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
