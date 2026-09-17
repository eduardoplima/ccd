---
name: evento-e-sequencialprocessoevento
description: "O \"Evento N\" exibido no sistema de processos é Pro_ProcessoEvento.SequencialProcessoEvento, não vw_ata_informacao.ordem"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e38e78fe-b75c-45a6-a5ca-0cbff4198d31
  modified: 2026-08-04T17:11:49.173Z
---

Ao citar "Evento N" no texto de uma informação, o número é
`Pro_ProcessoEvento.SequencialProcessoEvento` — ele conta **todas** as
movimentações/tramitações, não só as peças com documento. `vw_ata_informacao.ordem`
numera apenas as informações e diverge muito (em 002166/2024: Mandado de Citação =
ordem 17, mas Evento 34; em 001325/2020: Citação 000048/2023 = ordem 39, Evento 68).

**Why:** usar a `ordem` produz referências que não existem nos autos — o revisor abre
o Evento citado e encontra uma movimentação vazia.

**How to apply:** mapear com
`Pro_ProcessoEvento e LEFT JOIN vw_ata_informacao i ON i.idInformacao = e.IdInformacao`,
ordenando por `e.SequencialProcessoEvento`, e usar a coluna `seq`. Os PDFs continuam
sendo localizados pelo `ordem` (nome do arquivo `SETOR_NNNNNN_AAAA_ORDEM.pdf` em
[[read-db-lags-area-restrita]] / `ccd.processo`). Ver [[gerar-informacao-legendas-quadros]].
