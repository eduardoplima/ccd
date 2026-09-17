---
name: fila-prioridade-ccd-inicio
description: Página CCD/Início virou fila de prioridade (3 abas); endpoints dias_ccd e /prescricao; regra Tema 899
metadata: 
  node_type: memory
  type: project
  originSessionId: 904823ad-5b92-4a9b-8dff-342af4c5be94
  modified: 2026-08-28T18:35:18.337Z
---

Em 28/08/2026 a página CCD/Início da webapp virou fila de prioridade com 3 abas: "Tempo na CCD" (sort fixo `dias_ccd` desc, via CTE `Lotes`/`Itens_Lote` destino='CCD', MAX(recebido_em)), "Risco de prescrição" (`GET /api/v1/ccd/prescricao`, sem paginação, sort client-side) e "Todos" (tabela antiga em `_todos-tab.tsx`). Toggle "Ocultar marcadores de permanência" (nuqs `permanencia`, default ligado) usa `MARCADORES_PERMANENCIA` duplicado em `web/backend/app/ccd/service.py` (espelho de `scripts/analise/instrucao_ccd.py` — manter em sincronia).

**Regra de prescrição adotada (decisão do usuário):** STF Tema 899 — multa E ressarcimento prescrevem em 5 anos, da citação C05 mais recente (origem OU execução) ou, na falta, do trânsito (`Exe_Debito.dataTransito` → fallback `Processo_TransitoJulgado`). Categorias: prescrito ≥5a, risco ≥4a. Difere do [[nereu-desconto-folha-progresso]]/planilha_nereu.py, que trata ressarcimento como imprescritível. Débito aberto = folha da cadeia ([[exe-debito-cadeia-folha-vigente]]) com `Exe_StatusDivida.StatusCancelamento IS NULL`; pagamento integral confia no marcador 5797.

Números no primeiro smoke (28/08/2026): 505 processos na CCD, 358 sem permanência; prescrição 274 (18 prescritos, 64 risco).
