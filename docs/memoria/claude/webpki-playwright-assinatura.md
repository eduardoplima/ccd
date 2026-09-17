---
name: webpki-playwright-assinatura
description: "Setup da assinatura digital (Lacuna Web PKI) via Playwright — extensão por --load-extension, registro espelhado, Web Store bloqueada"
metadata: 
  node_type: memory
  type: project
  originSessionId: f4382f7d-2123-4918-aca3-adbc61d6941e
---

`scripts/automacao/assinar_informacoes.py` assina informações pendentes na Área Restrita (página `AssinarInformacoesPendentes.asp`) dirigindo o **Chromium do Playwright** e chamando `prepararAssinatura(...)` por JS. Estado da máquina (fora do repo) do qual ele depende:

- Extensão Web PKI copiada em `~/.ccd_webpki_ext` (do perfil Default do Chrome, `dcngeagmmhegagicpcmpinaoklddcgon/2.17.5_0`; o manifest tem `key`, então o ID oficial se mantém ao carregar descompactada).
- Host nativo Lacuna espelhado no registro (HKCU, sem admin): `HKCU\SOFTWARE\Chromium\NativeMessagingHosts\com.lacunasoftware.webpki` e `HKCU\SOFTWARE\Google\Chrome for Testing\...` → `%LOCALAPPDATA%\Lacuna Software\Web PKI\native-host-chrome.json`.
- Perfil persistente em `~/.ccd_chrome_assinatura`.

**Why:** a Chrome Web Store é bloqueada por política ("A instalação não está ativada") e o Chrome estável ≥137 ignora `--load-extension` — só o Chromium/Chrome for Testing do Playwright aceita a flag. `playwright install chromium` precisa de `NODE_EXTRA_CA_CERTS=~/.qmd-ca-bundle.pem` ([[node-fetch-tls-corporate-mitm]]).
**How to apply:** se os certificados não carregarem, conferir os 3 itens acima (extensão copiada, registro, token conectado). PIN é pedido 1x por lote (máx. 20 processos/lote, limite da página). É preciso visitar `telaPrincipalMenu.asp` antes da página (ASPSESSIONID). O "confiar no site" (senão o Web PKI pede "permitir" por documento) fica em `chrome.storage.sync`+`local` da extensão como `trust:<domínio>:<thumbprint>`; o script grava isso automaticamente a cada rodada (`_confiar_site`) — gravado em 08/07/2026, a confirmar na próxima assinatura real. Ver [[nereu-ms-envio-progresso]].
