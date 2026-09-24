---
name: siai-despesa-pessoal-vs-siai-pessoal
description: "Folha de 2013-2020 está nas tabelas SiaiDp_* (SIAI Despesa com Pessoal); o SIAI Pessoal atual só cobre 2021+; subsídio de vereador vem lançado como \"Vencimento Básico\""
metadata: 
  node_type: memory
  type: reference
  originSessionId: eab18097-7ad7-419c-85e5-07643f7f5e3d
  modified: 2026-08-21T12:30:57.009Z
---

São **dois** sistemas de prestação de contas de despesa com pessoal:

- **SIAI Despesa com Pessoal** — 2013 a 2021. É o que está em `processo.dbo.SiaiDp_*`
  (`SiaiDp_Arquivo` → `SiaiDp_FpRemessa`/`SiaiDp_QfRemessa` → folha e quadro de servidores).
  Neste banco os dados vão de **2013 a 2020**. Órgão pelo `RTRIM(a.codigoorgao)` casado com
  `processo.dbo.orgaos.codigo`; sempre filtrar `a.inativo IS NULL`.
- **SIAI Pessoal** — 2021 em diante. **Não** está nas tabelas `SiaiDp_*`. Consultar só o SIAI
  Pessoal para fatos anteriores a 2021 devolve vazio e leva à conclusão falsa de que "não há
  registro" (foi o que aconteceu no 000486/2019, Evento 52).

Armadilhas na leitura da folha:

- O subsídio de agente político costuma vir lançado sob a rubrica **`Vencimento Básico`**, não
  `Subsídio` — buscar por "subsídio" não acha nada. A rubrica `Subsídio` aparece de forma
  esparsa (ex.: suplentes empossados no meio do mandato).
- Gratificação pelo exercício da Presidência da Câmara é rubrica **à parte** (`Gratificação`),
  não integra o subsídio.
- Meses parciais (posse/saída) aparecem com valor proporcional — não confundir com mudança do
  subsídio. Conferir o valor **modal** entre os pares de mesmo cargo, não o total de um só
  servidor.
- Colunas `char` do SIAI têm collation própria: usar `COLLATE SQL_Latin1_General_CP1_CI_AS` ao
  comparar/retornar, ou filtrar em pandas.
- Nomes vêm com erros de digitação do jurisdicionado (ex.: `GILAMR` por Gilmar) — casar por CPF.

Modelo de consulta pronto em `scripts/automacao/calculo_vencimentos.ipynb` (`sql_vencimentos`) e
em `processos/informacoes/000486_2019/gerar_informacao.py`. Ver [[gerar-informacao-legendas-quadros]].
