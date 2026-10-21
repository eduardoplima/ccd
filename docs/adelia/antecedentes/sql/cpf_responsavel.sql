-- CPF do responsável de despesa do processo cujo nome casa com o extraído pelo LLM.
-- origem: scripts/automacao/gerar_antecedentes.py:112-119
-- parâmetros: :numero, :ano, :nome_pattern (ex.: '%fulano de tal%', minúsculo)
SELECT DISTINCT gp.Documento AS cpf, gp.Nome AS nome
FROM processo.dbo.Processos p
INNER JOIN processo.dbo.Pro_ProcessosResponsavelDespesa pprd ON pprd.IdProcesso = p.IdProcesso
INNER JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = pprd.IdPessoa
WHERE p.numero_processo = :numero AND p.ano_processo = :ano
  AND lower(gp.Nome) LIKE :nome_pattern
