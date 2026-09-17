# Backend CCD — instruções para o Codex

Leia [CLAUDE.md](CLAUDE.md) para as convenções FastAPI, sessões, autenticação, ARQ, migrações e testes. Aplique também o `AGENTS.md` da raiz.

Atualizações conferidas em 09/09/2026:

- A autenticação usa `dbo.Usuarios` e `TokensRenovacao`, conforme `app/auth/models.py`. A descrição antiga de `FRAPUsuario`/`FRAPRefreshToken` como tabelas de autenticação está superada; esses nomes permanecem como aliases de compatibilidade.
- A aplicação consolidada atende CCD, CGAD e FRAP. Além de BdDIP, há consultas ao banco `processo`; use as dependências de sessão existentes para cada banco.
- O ambiente pertence ao workspace `web/`: instale com `uv sync --all-packages` nessa pasta e execute pelo Python de `web/.venv`. Não criar outro ambiente nem sincronizar apenas o projeto raiz vazio.
- Consulte [as memórias da aplicação](../../docs/memoria/README.md) antes de alterações em autenticação, monitoramento, ETL ou implantação. Pendências e números antigos precisam de confirmação no código atual.
- Execute lint e testes pertinentes aos arquivos alterados. O erro histórico de fixtures com `NomeCompleto` é contexto para diagnóstico, não dispensa de verificar regressões.
