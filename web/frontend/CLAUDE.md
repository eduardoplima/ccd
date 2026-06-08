# CLAUDE.md — frontend

Convenções específicas do app Next.js.

## Regras

- **App Router only.** Server Components por padrão; `"use client"` somente onde necessário (forms, hooks de TanStack Query, qualquer coisa que use APIs do browser).
- **shadcn/ui vive em `src/components/ui/` como cópias** (convenção shadcn). Não adicionar uma segunda lib de componentes.
- Toda interação com servidor passa por hooks de TanStack Query em `src/hooks/`. Sem `fetch` solto em componentes; sem `useEffect` + `setInterval` para polling — use `refetchInterval`.
- **Cliente HTTP único** em `src/lib/api-client.ts`: instância axios, request interceptor anexa `Bearer <access>`, response interceptor trata 401 → refresh único in-flight → retry. Em 401 do `/auth/login`: rejeita (credencial inválida). Em 401 do `/auth/refresh` ou sem refresh token: limpa storage e redireciona pra `/login`.
- **Storage de tokens:** access token em memória de módulo (perdido em hard reload, re-hidratado via refresh na próxima chamada); refresh token em `localStorage` com chave namespaced. Documentado como dívida técnica de XSS para migrar a HTTP-only cookies.
- **Schemas Zod espelham DTOs Pydantic do backend 1:1.** Comentário `// mirrors backend <DTOName>` em cada um.
- Prettier + ESLint (`next/core-web-vitals`). `pnpm lint && pnpm format` antes do commit.
- Default sem comentários. Identificadores em inglês; strings de UI em pt-BR.

## Visual

Fonte Roboto (Google Font), pesos 400/500/700, exposta como `--font-sans`. `lang="pt-BR"` no `<html>`. Paleta primária verde `#347d6b`, brand-dark `#1c4433`, brand-accent `#d4a017` (faixa de 1px abaixo do header).
