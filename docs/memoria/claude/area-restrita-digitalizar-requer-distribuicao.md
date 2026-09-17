---
name: area-restrita-digitalizar-requer-distribuicao
description: Cadastrar Informação Digitalizada só funciona com o processo distribuído para o usuário; falha é silenciosa e _mensagem raspa alerts estáticos (falso positivo)
metadata: 
  node_type: memory
  type: project
  originSessionId: cc885d18-fb2e-4e97-a684-22fda21d2965
  modified: 2026-08-27T14:55:42.608Z
---

Na Área Restrita, **Cadastrar Informação Digitalizada exige que o processo esteja distribuído para o usuário** (Distribuição Própria + Iniciar Análise). A distribuição encerra quando a informação anterior é publicada — por isso uma segunda informação no mesmo processo falha até redistribuir. Fluxo correto: `distribuir` → `informacao`. **Cancelar uma tramitação também encerra a análise** (27/08/2026, 001324/2024): após [[cancelar-tramitacao-lote]], a consulta do cadastro ainda abre ("cadastro disponível"), mas a inclusão volta com `ocultoNomeArquivoPDF` vazio — redistribuir resolve. Não é colisão de nome de PDF (reupload com outro nome falha igual).

**Why:** Em 13/07/2026, 21 de 26 inclusões falharam **silenciosamente** (POST volta a mesma tela, `status=` vazio no frame de botões, sem mensagem); só funcionou nos 5 que ainda estavam distribuídos. Após `distribuir_propria`, 21/21 passaram.

**How to apply:** No CLI [[web-consolidacao-ccd]] `scripts/automacao/area_restrita.py`, rodar `distribuir` antes de `informacao`/`informacao-lote` quando o processo não estiver em análise com o usuário. Cuidado: `AreaRestrita._mensagem` raspa `alert(...)` **estáticos** das funções JS da página ("Tamanho de data não permitido; Caracter inválido.; Este campo deve ser numérico." é falso positivo nas telas Digitalizar/Substituir) — confie nas verificações reais do CLI (identificador retornado, item que sai da lista), não na mensagem. No `substituir`, `--ordem` é a ordem do **evento** do processo (ex.: 39), não o sufixo do arquivo CCD_..._0019 (ver [[evento-e-sequencialprocessoevento]]).
