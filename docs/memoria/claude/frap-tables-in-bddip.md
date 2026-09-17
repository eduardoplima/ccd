---
name: frap-tables-in-bddip
description: "Tabelas FRAP* (arrecadação) vivem no banco BdDIP, não em processo; como medir arrecadação real"
metadata: 
  node_type: memory
  type: project
  originSessionId: db1b4f7d-ff8d-44f6-a91a-9d232c89ef5b
---

As tabelas `FRAP*` (FRAPLancamento, FRAPCategoria, FRAPConta, FRAPMetricaPessoa, FRAPMatch*, FRAPDescontoFolha*) ficam no banco **BdDIP** — `get_connection(db="BdDIP")`. Não existem no banco `processo`.

**Arrecadação efetiva** = `FRAPLancamento` com `ValorDC='C'` (crédito = entrada) e `IdCategoria IN (1,2,3,9)`. Excluir cat **4 (APLICACAO_RESGATE)** e **5 (SALDO)** — não são arrecadação. Categorias (FRAPCategoria): 1=OB_RECEBIDA (Ordem Bancária SIGEF), 2=GUIA_RECEBIMENTO (boleto/guia), 3=TRANSFERENCIA (TED/PIX), 4=aplicação/resgate, 5=saldo, 9=outros. Agrupar por `YEAR(DtMovimento)`.

O piloto Pix/Cartão é separado: CSV `scripts/docs/info_pix_cartao_042026.csv` (solicitações via API BB; `CodigoTipoPagamento` P=Pix, C=Cartão). Não é tabela no banco. Em jun/2026 quase nada estava com pagamento confirmado — são *solicitações*, não arrecadação conciliada.

Ver [[cgad-cancelado-mostly-null]].
