---
name: contas-cadastro-combos-auditoria
description: "Cadastrar informação digitalizada em processo de CONTAS falha silenciosa se os combos cboRelatorioInicialAuditoria/cboRelatorioAuditoria não forem respondidos (=\"N\")"
metadata: 
  node_type: memory
  type: project
  originSessionId: cc885d18-fb2e-4e97-a684-22fda21d2965
---

Na Área Restrita, o formulário "Cadastrar Informação Digitalizada" de processos de **CONTAS DO CHEFE DO PODER EXECUTIVO** (contas de governo) traz dois combos extras que os demais tipos não têm: `cboRelatorioInicialAuditoria` (vem **em branco**, obrigatório) e `cboRelatorioAuditoria` (default "N"). Se `cboRelatorioInicialAuditoria` for enviado vazio, a **inclusão falha silenciosamente** (POST volta sem o `ocultoNomeArquivoPDF`; os alerts "Tamanho de data não permitido / Este campo deve ser numérico" são JS estático, falso-positivo — ver [[area-restrita-digitalizar-requer-distribuicao]]).

**Why:** em 13/07/2026, 4 de 6 antecedentes (todos "CONTAS") falharam a inclusão; os 2 não-contas (Representação, Apuração) passaram. A causa era o combo em branco, não distribuição.

**How to apply:** `ccd.area_restrita.cadastrar_informacao_digitalizada` já preenche ambos os combos com "N" quando presentes e vazios (uma informação de antecedentes/instrutiva não é relatório de auditoria). Fix commitável em `ccd/area_restrita.py`. Vale para qualquer informação em processo de contas, não só antecedentes.
