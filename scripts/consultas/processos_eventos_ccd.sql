SELECT pro.numero_processo,
       pro.ano_processo,
       ai.ordem,
       ppe.SequencialProcessoEvento,
       ai.resumo
FROM processo.dbo.Processos pro
INNER JOIN processo.dbo.Ata_Informacao ai 
    ON pro.numero_processo = ai.numero_processo 
    AND pro.ano_processo = ai.ano_processo
INNER JOIN processo.dbo.Pro_ProcessoEvento ppe 
    ON ppe.IdProcesso = pro.IdProcesso 
    AND ppe.IdInformacao = ai.idInformacao
WHERE pro.setor_atual = 'CCD'
AND ppe.SequencialProcessoEvento IN (
    SELECT TOP 3 sub_ppe.SequencialProcessoEvento
    FROM processo.dbo.Pro_ProcessoEvento sub_ppe
    WHERE sub_ppe.IdProcesso = pro.IdProcesso
    ORDER BY sub_ppe.SequencialProcessoEvento DESC
)
ORDER BY pro.numero_processo,
         pro.ano_processo,
         ai.ordem;