---
name: exe-parcelamento-semantica
description: Semântica empírica de Exe_Parcelamento.SituacaoParcelamento e o vínculo duplo débito↔processo
metadata: 
  node_type: memory
  type: project
  originSessionId: bea3cc03-1072-4c03-9b2c-29219b5b8150
---

No banco `processo`, `Exe_Parcelamento.SituacaoParcelamento` (char(1)) **não tem tabela de domínio** nem procedure que a use. Semântica inferida empiricamente (jun/2026): 1=aguardando início, 2=em curso, 3=cancelado (junto com o cancelamento do débito), 4=quitado, 5=cancelado automaticamente por inadimplência (job noturno das ~04:00), 6=indefinida.

**Why:** alertas/regras sobre parcelamento dependem desses códigos; `DataCancelamentoParcelamento` NÃO serve sozinha como critério — ela persiste após reabertura (`DataReabertura`) e aparece até em situação 2.

**How to apply:**
- Parcelamento "ativo" = `SituacaoParcelamento IN ('1','2')` em débito com `Exe_Debito.DataCancelamento IS NULL`. Quando um parcelamento é cancelado, o débito costuma ser cancelado/substituído junto — filtrar só débitos vigentes zera os cancelados.
- `Exe_Debito` liga ao processo por `IdProcessoExecucao` **OU** `IdProcessoOrigem` — nunca `COALESCE` (perde o vínculo pela origem; causou falso positivo no alerta do CCD).
- Domínios que existem: `Exe_StatusDivida` (1=Em Aberto, 2=Pago Integralmente, 8=Parcelado...) e `Exe_SituacaoDebito`.
- Implementação de referência: `web/backend/app/ccd/alertas/service.py`. Relacionado: [[cit-citacoes-authoritative-source]].
