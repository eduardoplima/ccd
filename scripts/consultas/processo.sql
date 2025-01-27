SELECT 
	CONCAT(numero_processo, '/', ano_processo) as numero_processo,
	assunto,
	interessado
FROM processo.dbo.Processos p 
WHERE numero_processo = '%{numero_processo}%' AND ano_processo = '%{ano_processo}%'