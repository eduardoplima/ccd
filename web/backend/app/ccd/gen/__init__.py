"""Infra compartilhada de geração de documentos do módulo CCD.

Reúne o que é comum às páginas que produzem despachos em PDF a partir de
templates `.docx` (Desconto em Folha, Antecedentes, ...):

- `paths`  — onde os artefatos de cada job ficam em disco.
- `render` — render de template `.docx` + conversão para PDF + empacotamento
             (PDF único ou ZIP de vários).
- `jobs`   — enfileiramento de um job CCD na fila ARQ e leitura do `input.json`
             pelo worker; transições de estado da linha em `FRAPJob`.

As features (desconto_folha, antecedentes) implementam só a parte de domínio
(SQL de candidatos + montagem do contexto + geração dos PDFs); a mecânica de
job/artefato/download é toda daqui.
"""
