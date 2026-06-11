"""Deploy do stack consolidado (CCD+CGAD+FRAP) no host SSH.

Substitui in-place a app FRAP-only: mesmo diretório remoto (~/frap-controle),
mesmo projeto compose `frap-controle`, anexando à rede `frap-controle` externa
já existente no host. Lê credenciais do .env local; nunca imprime segredos.

Fases:
  pack    — empacota o conteúdo de web/ num tarball (mesmos excludes do .dockerignore)
  upload  — envia o tarball, extrai em ~/frap-controle, escreve o .env de produção, valida o compose
  build   — sobe `docker compose up -d --build` em background (log em ~/frap-controle/deploy-build.log)
  status  — mostra tail do log de build + `docker compose ps`
  logs    — tail dos logs dos serviços (--service backend|worker|frontend|caddy|redis)
  seed    — cria/atualiza usuário admin (senha via --senha)

Uso:
  uv run --with paramiko python deploy/deploy_remote.py pack
  uv run --with paramiko python deploy/deploy_remote.py upload
  uv run --with paramiko python deploy/deploy_remote.py build
  uv run --with paramiko python deploy/deploy_remote.py status
  uv run --with paramiko python deploy/deploy_remote.py seed --login eduardo --email x@y.z --nome "Eduardo" --senha SENHA

Env necessário (em scripts/.env e/ou web/.env, carregados ambos):
  SSH_HOST, SSH_USER, SSH_PASS
  SQL_SERVER_USER/PASS/HOST/PORT/DATABASE
  AZURE_OPENAI_API_KEY, OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT[, AZURE_OPENAI_DEPLOYMENT]
  SHARE_USER, SHARE_PASS, SHARE_DOMAIN   (mount CIFS do share de PDFs; acrescentar ao .env)
"""

from __future__ import annotations

import argparse
import os
import secrets
import sys
import tarfile
import tempfile
from pathlib import Path

from dotenv import load_dotenv

WEB_DIR = Path(__file__).resolve().parents[1]  # .../ccd/web
REPO_ROOT = WEB_DIR.parent  # .../ccd
REMOTE_DIR = "frap-controle"  # relativo ao home do usuário SSH
TARBALL_LOCAL = Path(tempfile.gettempdir()) / "ccd-web-deploy.tar.gz"
TARBALL_REMOTE = "ccd-web-deploy.tar.gz"
COMPOSE = "docker compose -f docker-compose.prod.yml"

# Diretórios/arquivos a NÃO incluir no tarball (espelha web/.dockerignore).
_EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".next",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".deploy",
}
_EXCLUDE_SUFFIXES = (".pyc", ".tsbuildinfo", ".parquet", ".ipynb")


def _load_env() -> None:
    # Carrega ambos: scripts/.env (SSH_* + SQL_*) e web/.env (AZURE_* + SQL_*).
    # override=False => o primeiro a definir vence; valores idênticos não conflitam.
    load_dotenv(REPO_ROOT / "scripts" / ".env", override=False)
    load_dotenv(WEB_DIR / ".env", override=False)


def _conn():
    import paramiko

    _load_env()
    host = os.environ["SSH_HOST"]
    port = int(os.environ.get("SSH_PORT", "22"))  # porta 22 pode estar filtrada nesta rede
    user = os.environ["SSH_USER"]
    pwd = os.environ["SSH_PASS"]
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(host, port=port, username=user, password=pwd, timeout=15)
    return c, host


def _run(c, cmd: str, timeout: int = 120) -> tuple[int, str]:
    i, o, e = c.exec_command(cmd, timeout=timeout)
    out = o.read().decode("utf-8", "replace") + e.read().decode("utf-8", "replace")
    rc = o.channel.recv_exit_status()
    return rc, out.strip()


def _prod_env_text() -> str:
    """Monta o .env de produção a partir das vars locais + segredos novos."""
    _load_env()
    host = os.environ["SSH_HOST"]
    g = os.environ.get
    linhas = [
        # SQL Server (mesma conta do dev; alcançável pela rede do host)
        f"SQL_SERVER_USER={g('SQL_SERVER_USER', '')}",
        f"SQL_SERVER_PASS={g('SQL_SERVER_PASS', '')}",
        f"SQL_SERVER_HOST={g('SQL_SERVER_HOST', '')}",
        f"SQL_SERVER_PORT={g('SQL_SERVER_PORT', '')}",
        f"SQL_SERVER_DATABASE={g('SQL_SERVER_DATABASE', 'BdDIP')}",
        "SQL_SERVER_DRIVER=ODBC Driver 18 for SQL Server",
        # Nomes lógicos de DB (CGAD/CCD)
        f"SQL_SERVER_DB_PROCESSOS={g('SQL_SERVER_DB_PROCESSOS', 'processo')}",
        f"SQL_SERVER_DB_DECISOES={g('SQL_SERVER_DB_DECISOES', 'BdDIP')}",
        f"SQL_SERVER_DB_SIAI={g('SQL_SERVER_DB_SIAI', 'BdSIAI')}",
        # Auth / JWT (segredo novo por deploy)
        f"JWT_SECRET_KEY={secrets.token_hex(32)}",
        "JWT_ALGORITHM=HS256",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60",
        "JWT_REFRESH_TOKEN_EXPIRE_DAYS=7",
        # CORS / Redis (mesma origem via Caddy; CORS p/ acesso direto)
        f"CORS_ALLOWED_ORIGINS=http://{host}",
        "REDIS_URL=redis://redis:6379",
        # Azure OpenAI (CGAD + Antecedentes)
        f"AZURE_OPENAI_API_KEY={g('AZURE_OPENAI_API_KEY', '')}",
        f"OPENAI_API_VERSION={g('OPENAI_API_VERSION', '')}",
        f"AZURE_OPENAI_ENDPOINT={g('AZURE_OPENAI_ENDPOINT', '')}",
        f"AZURE_OPENAI_DEPLOYMENT={g('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')}",
        # Share de PDFs (CIFS) usado pela geração de Antecedentes
        "CCD_INFORMACOES_DIR=/mnt/tce/Informacoes_PDF",
        f"SHARE_USER={g('SHARE_USER', '')}",
        f"SHARE_PASS={g('SHARE_PASS', '')}",
        f"SHARE_DOMAIN={g('SHARE_DOMAIN', '')}",
    ]
    return "\n".join(linhas) + "\n"


def _excluded(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & _EXCLUDE_DIRS:
        return True
    name = rel.name
    if name == ".env" or name.endswith(".env.local"):
        return True
    if rel.suffix in _EXCLUDE_SUFFIXES:
        return True
    # dados/artefatos locais
    rel_posix = rel.as_posix()
    if rel_posix.startswith(("data/", "docs/extratos_frap/", "backend/.artifacts/")):
        return True
    if rel.match("docs/*.xlsx"):
        return True
    return False


def cmd_pack(_args) -> int:
    """Empacota o conteúdo de web/ (na raiz do tar) aplicando os excludes."""
    n = 0
    with tarfile.open(TARBALL_LOCAL, "w:gz") as tar:
        for path in sorted(WEB_DIR.rglob("*")):
            rel = path.relative_to(WEB_DIR)
            if _excluded(rel):
                continue
            if path.is_file():
                tar.add(path, arcname=rel.as_posix())
                n += 1
    print(f"-> tarball: {TARBALL_LOCAL} ({n} arquivos, {TARBALL_LOCAL.stat().st_size // 1024} KiB)")
    return 0


def cmd_upload(_args) -> int:
    if not TARBALL_LOCAL.exists():
        rc = cmd_pack(_args)
        if rc != 0:
            return rc
    c, host = _conn()
    sftp = c.open_sftp()
    print(f"-> enviando tarball para {host} ...")
    sftp.put(str(TARBALL_LOCAL), TARBALL_REMOTE)
    rc, out = _run(
        c,
        f"rm -rf {REMOTE_DIR} && mkdir -p {REMOTE_DIR} && "
        f"tar xzf {TARBALL_REMOTE} -C {REMOTE_DIR} && echo EXTRACT_OK",
    )
    print(out)
    if rc != 0:
        return rc
    # escreve .env de produção (sem imprimir conteúdo)
    with sftp.file(f"{REMOTE_DIR}/.env", "w") as f:
        f.write(_prod_env_text())
    sftp.chmod(f"{REMOTE_DIR}/.env", 0o600)
    print("-> .env de produção escrito (JWT novo gerado).")
    # NUNCA criar/alterar rede: exige que a rede externa frap-controle_default já exista
    rc, out = _run(
        c,
        "docker network inspect frap-controle_default >/dev/null 2>&1 || "
        "{ echo 'ERRO: rede frap-controle_default ausente — abortando'; exit 1; }; "
        f"cd {REMOTE_DIR} && {COMPOSE} config >/dev/null && echo COMPOSE_VALID",
    )
    print(out if out else "(compose config sem saída)")
    sftp.close()
    c.close()
    return rc


def cmd_build(_args) -> int:
    c, _ = _conn()
    # build+up em background; sobrevive ao fechamento da sessão.
    rc, out = _run(
        c,
        f"cd {REMOTE_DIR} && nohup {COMPOSE} up -d --build --remove-orphans > deploy-build.log 2>&1 & echo LAUNCHED pid=$!",
    )
    print(out)
    c.close()
    return rc


def cmd_status(_args) -> int:
    c, _ = _conn()
    rc, out = _run(
        c,
        f"cd {REMOTE_DIR} && tail -n 30 deploy-build.log 2>/dev/null; "
        f"echo '----- ps -----'; {COMPOSE} ps",
    )
    print(out)
    c.close()
    return rc


def cmd_logs(args) -> int:
    c, _ = _conn()
    svc = args.service or ""
    rc, out = _run(c, f"cd {REMOTE_DIR} && {COMPOSE} logs --tail=60 {svc}")
    print(out)
    c.close()
    return rc


def cmd_seed(args) -> int:
    c, _ = _conn()
    # senha passada por env var no exec p/ não vazar no ps da máquina remota
    inner = (
        "python -m app.scripts.create_user "
        f"--login {args.login} --email {args.email} --nome '{args.nome}' "
        f'--papel admin --senha "$ADMIN_SENHA"'
    )
    rc, out = _run(
        c,
        f"cd {REMOTE_DIR} && ADMIN_SENHA={args.senha!r} {COMPOSE} exec -T -e ADMIN_SENHA backend sh -lc {inner!r}",
        timeout=120,
    )
    print(out)
    c.close()
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="phase", required=True)
    sub.add_parser("pack")
    sub.add_parser("upload")
    sub.add_parser("build")
    sub.add_parser("status")
    lg = sub.add_parser("logs")
    lg.add_argument("--service", default="")
    sd = sub.add_parser("seed")
    sd.add_argument("--login", required=True)
    sd.add_argument("--email", required=True)
    sd.add_argument("--nome", required=True)
    sd.add_argument("--senha", required=True)
    args = ap.parse_args()
    return {
        "pack": cmd_pack,
        "upload": cmd_upload,
        "build": cmd_build,
        "status": cmd_status,
        "logs": cmd_logs,
        "seed": cmd_seed,
    }[args.phase](args)


if __name__ == "__main__":
    sys.exit(main())
