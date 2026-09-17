---
name: frap-extrato-bb-armadilhas
description: Extrato BB do FRAP — Documento de TED identifica o remetente (não a transação); exportação pode vir com período errado; publica_extrato falha em período com FRAPMatchGuia
metadata: 
  node_type: memory
  type: project
  originSessionId: 74280fea-9220-4c2a-aef2-48b4a30cc400
  modified: 2026-08-19T11:53:14.677Z
---

Armadilhas do extrato BB nas tabelas FRAP do BdDIP (descobertas em 08/07/2026):

- **`Documento` de TED identifica o remetente, não a transação** — o mesmo doc se repete em dias/valores diferentes (ex.: 552.623.000.300.000 = SME Extremoz, mensal). N linhas idênticas no mesmo dia podem ser N transferências genuínas (validar pela cadeia de varreduras "BB RF": saldo anterior + créditos = débito da varredura). O número codifica **agência+conta do remetente**: `55` + agência + zeros + conta (555.684.000.005.461 = ag 5684-7 / cc 5461-5, confirmado contra comprovante de depósito em 003665/2025; 551.088.* = ag 1088, Lajes/Pedro Avelino). Serve para desambiguar créditos de mesmo valor de municípios diferentes.
- **A exportação do BB pode devolver o período errado** com o nome pedido (4 arquivos de 2020/2021 vieram com fev/2026), e o cabeçalho "Período do extrato" mente o ano em dezenas de arquivos íntegros. Desde 08/07/2026, `frap.extratos.ingest` valida período pelo conteúdo (`dt_movimento`) + fechamento de saldo (`ExtratoInvalido`); os períodos ruins foram substituídos pelos PDFs do share `\\srv-fs01\CCD\Planilhas\FRAP\EXTRATOS BANCÁRIO CC 700000-6`.
- **`publica_extrato` falha ao republicar período cujos lançamentos têm match** (`FK_FRAPMatchGuia_Lancamento`): o DELETE do replace viola a FK e a transação inteira reverte. Republique só períodos novos, ou trate os matches antes.
- Linhas "S A L D O" ficam no banco por design (categoria 5 "Linha de saldo informativa") — excluir em somas por valor. Relaciona-se com [[frap-tables-in-bddip]] e [[arrecadacao-multa-vs-pge]].

**Receita de ingestão mensal (funcionou 19/08/2026, 072026):** `web\.venv\Scripts\frap.exe parse-extratos --pasta extratos --out <tmp>` (valida tudo), depois script curto que filtra o parquet ao período novo e chama `publica_extrato(engine, df, pasta_origem=<repo>/extratos)` — nunca publicar o parquet inteiro (FK de match). `frap.config.load_dotenv` não acha o `.env` em `python -c`; use arquivo de script. Coluna de FRAPConta é `Conta`, não `NumeroConta`.

**Why:** essas três armadilhas produzem análises infladas/erradas de repasses ao FRAP e falhas silenciosas de reingestão.
**How to apply:** ao casar repasses, filtre categoria ≠ 5, deduplique nada (banco já está limpo) e valide quantidades pela varredura BB RF; ao reingerir, rode a validação nova e cuidado com períodos que têm matches.
