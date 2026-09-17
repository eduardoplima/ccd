---
name: node-fetch-tls-corporate-mitm
description: Node fetch falha com SELF_SIGNED_CERT_IN_CHAIN nesta máquina (TLS interceptado pelo TCE); curl funciona. Conserto via NODE_EXTRA_CA_CERTS.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6164e904-28aa-4901-8c21-d63f8699bba4
---

A rede do TCE **intercepta TLS** (proxy com CA própria). O `curl` funciona porque usa o cert store do Windows; já o **Node** (e ferramentas baseadas nele, como o `qmd`) falha em downloads HTTPS com `fetch failed` / `SELF_SIGNED_CERT_IN_CHAIN`, pois usa a lista de CAs embutida.

**Conserto:** exportar as CAs raiz do Windows para um bundle PEM e apontar o Node a ele:
- Bundle já gerado em `C:\Users\05911205424\.qmd-ca-bundle.pem` (via `Get-ChildItem Cert:\LocalMachine\Root, Cert:\CurrentUser\Root` → base64 PEM).
- Usar: `NODE_EXTRA_CA_CERTS="C:/Users/05911205424/.qmd-ca-bundle.pem" <comando node/qmd>`.

Aplica-se a qualquer ferramenta Node que baixe da internet aqui. No caso do qmd, o modelo de embeddings (~333 MB) já está em cache; o reranker do `qmd query` híbrido (~1,28 GB) ainda exige o bundle no 1º uso. Ver o schema da wiki em `vault/CLAUDE.md` (seção Busca).
