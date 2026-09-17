---
name: vwdespesa-views-sem-bdinfocex
description: uCCD não acessa BdINFOCEX; views vwDespesa* do BdDIP foram alteradas (09/07/2026) para remover essa dependência
metadata: 
  node_type: memory
  type: project
  originSessionId: 59e303b7-1442-4985-89d8-6a33f269e1f8
---

O login `uCCD` não tem acesso ao banco `BdINFOCEX` (erro 916). Em 09/07/2026 as quatro views
`vwDespesa{Empenho,Liquidacao,Pagamento,ELP}` do **BdDIP** foram alteradas (ALTER VIEW) para
remover a dependência: coluna `hash_edital` (subquery em `BdINFOCEX.dbo.vwEdital`) removida das
3 views base, e `vwDespesaELP` reapontada de `[BdINFOCEX].dbo.vwDespesa*` para as views locais
do BdDIP.

**Why:** as views são a via preferida para apurar despesas do SIAI (limpam/organizam o Anexo 14
— empenho→liquidação→pagamento, situação de arquivo 4, credor do empenho), mas quebravam para
uCCD por causa do único campo vindo de BdINFOCEX.

**How to apply:** para apuração de pagamentos (ex.: liquidações da CCD), usar
`BdDIP.dbo.vwDespesaPagamento` filtrando `cpf_cnpj_favorecido` e `id_orgao` — captura
pagamentos-satélite que a consulta direta a `Anexo14_Pagamento.CPFCNPJCredor` perde (o credor da
view vem do empenho). Órgãos em `Dim_Orgao`/`vw_Gen_UnidadeJurisdicionada` (ex.: PMCRUZETA=369,
PMJUCURUTU=400, PMLNOVA=405, PMSNNORTE=475). Definições originais salvas em
[[frap-tables-in-bddip]].
