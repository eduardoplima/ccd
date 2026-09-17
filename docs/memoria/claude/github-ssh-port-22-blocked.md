---
name: github-ssh-port-22-blocked
description: outbound TCP port 22 is blocked on this network (github push AND the deploy host 10.24.0.197); use SSH-over-443 for github, SSH_PORT for deploy
metadata: 
  node_type: memory
  type: project
  originSessionId: 8ff4d5c1-638f-41bd-ba49-ca50bc1e617e
---

On this machine/network (TCE), outbound TCP to `github.com:22` is blocked — `git push` to the `git@github.com:eduardoplima/ccd.git` SSH remote fails with `ssh: connect to host github.com port 22: Connection timed out`. GitHub's SSH-over-443 endpoint (`ssh.github.com:443`) **does** work, and HTTPS to github.com (443) is reachable too.

**Why:** the corporate firewall permits 443 but not 22. The repo's `origin` is an SSH URL, so the default route hits the blocked port.

**How to apply:** for a one-off push without changing anything, override the URL:
`git -c "url.ssh://git@ssh.github.com:443/.insteadOf=git@github.com:" push origin main`.
For a permanent fix, add to `~/.ssh/config`:
```
Host github.com
  Hostname ssh.github.com
  Port 443
```
then plain `git push` works. SSH key auth already succeeds (`Hi eduardoplima!`). Related: [[repo-moved-stale-editable-install]], [[mssql-plain-ip-not-named-instance]].

**Generalização (2026-06-09):** o bloqueio de saída na porta 22 **não é só github** — também atinge o host de deploy interno `10.24.0.197`: `:22` e `:2222` dão *timeout* (filtrado), enquanto `:443` dá *connection refused* (host alcançável, porta fechada) e o SQL Server `10.24.0.77:59678` abre normal. Ou seja, o `deploy_remote.py` (paramiko, porta 22) **não conecta desta máquina**. O script agora aceita `SSH_PORT` (default 22) — se o host expõe SSH em outra porta não-filtrada, setar `SSH_PORT`; senão, rodar o deploy de uma máquina que alcance `10.24.0.197:22` (ou via jump host/VPN). Artefatos de deploy em `web/` (compose.prod, Caddyfile, deploy_remote.py) ficam prontos independentemente.
