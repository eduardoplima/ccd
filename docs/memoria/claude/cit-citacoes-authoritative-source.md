---
name: cit-citacoes-authoritative-source
description: "Cit_Citacoes é a fonte autoritativa de citações; Tipo='C05' = 5 dias; Data_envio_AR vazia; citação pode estar na origem OU na execução"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 73526d54-64a4-4271-897d-b65629111654
---

A tabela `processo.dbo.Cit_Citacoes` registra toda citação e é mais completa/confiável que
varrer `vw_ata_informacao` + LLM sobre PDFs (numa comparação para o Nereu: tabela é superconjunto
estrito do resultado do LLM em todo ano de 2002–2026).

- `IdProcesso` — processo exato da citação; **pode ser o processo de ORIGEM ou o de EXECUÇÃO** do
  débito. Para achar todas, busque nos dois (UNION de `Exe_Debito.IdProcessoOrigem` e
  `IdProcessoExecucao`).
- `Tipo` — código do ato: `C05` = citação de 5 dias; registros novos usam `Tipo='C'` + `Prazo=5`
  (`PrazoTipo='DU'`). Outros: `C60`/`C90`/`C20`/`C15`, intimações `I05`/`I15`.
- `IdPessoa` — destinatário (não precisa de LLM para confirmar o endereçado).
- `IdInformacao` — vincula a `vw_ata_informacao` (data/setor/PDF) e a `Pro_ProcessoEvento`
  (`SequencialProcessoEvento`).
- **`Data_envio_AR` está sempre NULL** (ao menos p/ o Nereu) — use
  `COALESCE(inf.DataPublicacao, inf.data_ultima_atualizacao, c.DataInclusao)`.
- Filtrar `c.DataExclusao IS NULL` para excluir citações apagadas.

Usado para corrigir a busca de citações em `scripts/analise/planilha_nereu.ipynb` (que antes só
olhava o processo de origem via LLM e perdia citações na execução). Ver também
[[mssql-plain-ip-not-named-instance]].
