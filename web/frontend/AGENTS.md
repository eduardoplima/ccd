# Frontend CCD — instruções para o Codex

Leia [CLAUDE.md](CLAUDE.md) para App Router, componentes, cliente HTTP, hooks, schemas e identidade visual. Aplique também o `AGENTS.md` da raiz.

- A aplicação consolidada está em `web/frontend/`; as árvores em `repos/` são referências separadas.
- Use os scripts e dependências de `package.json`. Preserve a correspondência entre os DTOs do backend e os schemas Zod, o cliente HTTP único e o acesso por hooks de TanStack Query.
- Limite a formatação aos arquivos do pedido; não execute `pnpm format` sobre toda a árvore como efeito lateral de uma edição pontual.
- Confira se arquivos novos em `src/lib/` entram no Git: há histórico de exclusão pela regra global `lib/`.
- Consulte [as memórias da aplicação](../../docs/memoria/README.md) para decisões anteriores e limitações do ambiente; revalide relatos históricos antes de mudar o código.
