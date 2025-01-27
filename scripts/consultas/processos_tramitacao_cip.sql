SELECT p.*
	FROM processo.dbo.Processos p 
	LEFT JOIN processo.dbo.Itens_Lote i ON p.IdProcesso = i.IdProcesso
	LEFT JOIN processo.dbo.Lotes l ON i.IdLote = l.IdLote
	WHERE (l.origem IN ('DAM_FGE', 'DAM_FGO') AND l.destino IN ('CIP'))
	AND p.setor_atual = 'CIP'
	AND p.numero_apensador IS NULL