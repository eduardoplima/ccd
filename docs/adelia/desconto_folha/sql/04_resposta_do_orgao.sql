-- Etapa 4 — resposta do órgão: PDFs dos processos apensados ao principal. Quando não há
-- apensado, a resposta é a informação do próprio principal cujo resumo contém 'resposta'
-- e o nº da notificação (ou é posterior a ela) — filtro sobre 03 (informações), sem SQL
-- próprio. O texto vai para o prompt prompts/extrair_resposta.md. Banco: processo.

-- ---------------------------------------------------------------
-- processos apensados
-- origem: web/backend/app/ccd/desconto_folha/processo_lookup.py:299
SELECT IdProcesso AS id_processo, RTRIM(numero_processo) AS numero,
       RTRIM(ano_processo) AS ano, data_registro
FROM dbo.Processos WHERE IdProcessoApensador = :id
ORDER BY data_registro DESC
;
