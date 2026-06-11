# Frontend Next.js 15. Contexto de build = raiz do repo.
# Runtime enxuto via output "standalone" (sem node_modules de dev).
FROM node:20-bookworm-slim AS build
WORKDIR /app
RUN npm install -g pnpm@9
# Não baixar navegadores do Playwright (devDep só p/ e2e): poupa ~400MB no /var pequeno do host.
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    HUSKY=0
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
# Mesma origem via Caddy: API em /api/v1 relativo. NEXT_PUBLIC_API_URL vazio => baseURL "".
ARG NEXT_PUBLIC_API_URL=""
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

FROM node:20-bookworm-slim AS run
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
# Saída standalone: server.js + node_modules mínimo tracejado + estáticos.
# (sem `public/` neste projeto — não copiar para não quebrar o build)
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
