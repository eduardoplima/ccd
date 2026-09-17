---
name: cgad-cancelado-mostly-null
description: BdDIP.Obrigacao/Recomendacao — Cancelado é quase sempre NULL; filtrar com IS NULL OR =0; IPERN espalhado em vários IdOrgao
metadata: 
  node_type: memory
  type: project
  originSessionId: db1b4f7d-ff8d-44f6-a91a-9d232c89ef5b
---

Em `BdDIP.Obrigacao` e `BdDIP.Recomendacao`, a coluna **`Cancelado` é majoritariamente NULL** (não 0). Filtrar registros ativos com `(Cancelado IS NULL OR Cancelado=0)` — usar `Cancelado=0` sozinho retorna quase nada (ex.: 7 obrigações em vez de 1.333).

Contagens ativas (jun/2026): **1.333 obrigações** e **899 recomendações**. Não há tabela `Decisao`; decisões classificadas estão em `ClassificacaoDecisao` (375: 198 DETERMINACAO + 177 OUTROS).

**ARMADILHA: `DataCumprimento` NÃO é comprovação de cumprimento — é a data-LIMITE (prazo).** Há datas no futuro (até 2027) e descrições "prazo de 18 meses"; a coluna `Prazo` é o termo em texto. A base **não registra cumprimento efetivo** (não há flag de status confiável; `ObrigacaoStaging.Status` é só do pipeline). Não diga "X% cumpridas". Dos 684 com prazo fixado, 679 já venceram (situação de prazo, não cumprimento). Mesmo cuidado com `Recomendacao.DataCumprimentoRecomendacao`.

**Resolução de entidade do órgão responsável é suja**: o mesmo IPERN estadual aparece sob `IdOrgaoResponsavel` 308 **e** 521 (registros duplicados) e em dezenas de grafias; há também muitos RPPS municipais distintos. Para "obrigações do IPERN", consolidar por `IdOrgaoResponsavel IN (308,521)` + nomes claramente estaduais (≈446 obrigações, 33%). Previdência no total ≈ 48%. Liga ao [[nereu-presidente-ipern]].

Ver [[frap-tables-in-bddip]].
