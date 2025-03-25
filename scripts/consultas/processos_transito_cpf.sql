SELECT 
	(SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
		FROM processo.dbo.Processos p
		WHERE p.IdProcesso = e.IdProcessoOrigem) 
	as processo_origem,
(SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
		FROM processo.dbo.Processos p
		WHERE p.IdProcesso = e.IdProcessoExecucao) 
	as processo_execucao,
(
SELECT Descricao
FROM processo.dbo.Exe_TipoDebito etd
WHERE etd.CodigoTipoDebito = e.CodigoTipoDebito
) as tipo_debito,
e.valorOriginalDebito as valor_original,
e.ValorAPagar as valor_atualizado,
CONVERT(NVARCHAR(30), e.dataTransito, 103) as transito_julgado,
(
SELECT DescricaoStatusDivida
FROM processo.dbo.Exe_StatusDivida esd
WHERE esd.CodigoStatusDivida = e.CodigoStatusDivida 
) as situacao_divida,
(
	SELECT Descricao
	FROM processo.dbo.Exe_StatusProtesto esp
	WHERE esp.IdExe_StatusProtesto = e.StatusProtesto 
) as status_protesto,
(
	SELECT DescricaoStatusProcessoPGE
	FROM processo.dbo.PGE_StatusProcesso psp
	WHERE psp.IdStatusProcessoPGE = e.Status_PGE
) as status_pge
FROM processo.dbo.Exe_Debito e
WHERE IdProcessoOrigem IN (
	select p.IdProcesso 
	from processo.dbo.Processos p 
		INNER JOIN processo.dbo.Processo_TransitoJulgado ptj ON 
		p.numero_processo = ptj.numero_processo AND 
		p.ano_processo = ptj.ano_processo 
	WHERE lower(ptj.Responsavel) LIKE lower('%{nome}%')
)
AND e.IdDebitoAnterior IS NULL