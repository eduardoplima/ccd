---
name: cancelar-tramitacao-lote
description: "Como cancelar tramitação de lotes na Área Restrita (tela nova, só funciona via navegador)"
metadata: 
  node_type: memory
  type: project
  originSessionId: d01ba2e0-bff5-4bad-a352-83f0750ead20
---

Tela Administrativo / Processo / Cancelar Tramitação de Processo (`SISTEMAS/Processo/CancelarTramitacao.asp?tcenet_Sistema=Administrativo&tcenet_Modulo=Processo`):

- Lista apenas lotes **pendentes de recebimento** cuja origem é o **setor ativo** da sessão.
- A tela foi **reformulada**: os resultados vêm numa tabela "Lotes Pendentes" com radios `name=rbTramitacao value=NNNNNNAAAA` (não o dhtmlxGrid `gridLotes` do JS legado `js/CancelaTramitacao.js`, que ainda é servido mas não é usado).
- **POST via requests (padrão ccd.area_restrita) NÃO retorna resultados** — a mesma consulta `oculto=C` + `txtDataInicio/txtDataFim` volta a página vazia com as datas ecoadas. Só funciona no navegador com o frameset real: `telaDeTrabalho.asp?url=SISTEMAS/Processo/CancelarTramitacao.asp%3F...` (frames `form` + `botoes`).
- Fluxo que funciona (Playwright, mesmo login/padrão de [[webpki-playwright-assinatura]] sem extensão): preencher datas no frame `form`, clicar `#C input` no frame `botoes` (Consultar), marcar o radio do lote, clicar `#E input` (Cancelar Lote), aceitar o confirm "Tem certeza que deseja Cancelar este lote?". A data fim do filtro funciona melhor como dia seguinte (18/07→21/07 pegou lotes de 20/07).
- Script pronto usado em 20/07/2026 (cancelou 53 lotes CCD→DIP do Eduardo): foi salvo no scratchpad da sessão como `cancelar_lotes_eduardo.py` — se precisar de novo, recriar a partir desta receita.
- O banco `processo` (réplica) atrasa horas: lotes de hoje não aparecem em `Lotes`/`Itens_Lote` ([[read-db-lags-area-restrita]]).
