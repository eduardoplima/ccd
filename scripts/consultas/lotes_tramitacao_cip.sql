SELECT l.*, i.*
	FROM processo.dbo.Processos p 
	LEFT JOIN processo.dbo.Itens_Lote i ON p.IdProcesso = i.IdProcesso
	LEFT JOIN processo.dbo.Lotes l ON i.IdLote = l.IdLote
	WHERE p.numero_processo = '{numero_processo}' and p.ano_processo = '{ano_processo}'