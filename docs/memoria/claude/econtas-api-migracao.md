---
name: econtas-api-migracao
description: "e-Contas (processos.tce.rn.gov.br) substitui a Área Restrita ASP; API REST mapeada (auth SSO tceauth, tramitarAutomatico, Informacao/formfile); assinatura segue Web PKI"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ea31f53-fb1d-4919-badc-355d0d0d10f9
  modified: 2026-07-23T12:40:09.588Z
---

Desde 23/07/2026 as ações da Área Restrita (cadastrar informação, assinar, tramitar) devem ir pelo **e-Contas** (`https://processos.tce.rn.gov.br` — SPA Angular, NÃO é a ASP em outro host). Implementado em `ccd/econtas.py` + CLI `scripts/automacao/econtas.py` (subcomando `certificar` = dry-run; certificado OK em 23/07/2026).

API (extraída do bundle Angular):
- Auth SSO: GET `https://tceauth.tce.rn.gov.br/api/servicos` (público) → ClientId do operador interno (idTipoOperadorServico=1); POST `tceauth/v2/token` form-urlencoded `{grant_type: password, username: CPF, password, client_id, sistema: "e-Contas"}` → access_token; GET `https://tceadmin2.tce.rn.gov.br/api/v3/operador/auth/informacoes/login` com header `Authorization: <token cru, sem Bearer>`.
- AR_USER já é o CPF → mesmas credenciais funcionam.
- Consulta: GET `/api/Processo?numeroProcesso=N&anoProcesso=A` → dict com `idProcesso`, `setorAtual` (vem com padding de espaços, ex. `'CCD       '`).
- Tramitar: POST `/api/tramitacao/tramitarAutomatico?setorDestino=X` json `{idProcesso, numeroProcesso, anoProcesso, setorAtual, setorDestino}` — sem campo de providência (diferente do ASP).
- Informação: POST multipart `/api/Informacao/formfile` — nomes dos campos ainda NÃO confirmados (inferidos; validar via DevTools no primeiro uso real).
- Setores do operador: GET `/api/Setor/GetAllSetorByToken`.
- Assinatura: `/api/AssinaturaDigital/PrepararAssinatura` + `ConcluirAssinatura` em `https://tce-commonapi.tce.rn.gov.br`, mas usa Lacuna Web PKI no navegador (A3) → impossível por requests; [[webpki-playwright-assinatura]] continua valendo (migrar o Playwright para a tela do e-Contas exige sessão ao vivo para mapear seletores).

**Why:** a ASP `novaarearestrita` está sendo descontinuada; a tramitação CCD→gabinete já estava bloqueada lá ([[ccd-tramitacao-gabinete-bloqueada]]) — tramitarAutomatico do e-Contas pode contornar.
**How to apply:** usar `EContas` para consultar/tramitar/cadastrar; rodar `python -m scripts.automacao.econtas certificar --processo N/A` após mudanças; não recriar login SSO fora de `ccd/econtas.py`.
