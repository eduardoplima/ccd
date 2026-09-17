"""Lança run_extracoes.py dentro do frap-worker no host de deploy, via SSH.

Rodar de web/ (importa deploy.deploy_remote para a conexão paramiko;
--no-sync porque `uv run` na raiz do workspace esvaziaria o venv):
    $env:PYTHONUTF8=1; $env:PYTHONPATH="C:\\Users\\05911205424\\Dev\\ccd\\web"
    uv run --no-sync --with paramiko python ..\\handoff\\lancar_extracoes_remoto.py start 2023 [mes]
    uv run --no-sync --with paramiko python ..\\handoff\\lancar_extracoes_remoto.py status 2023

Log fica no host em ~/extracao_<ano>.log; as linhas em Extracao são a fonte
de verdade do progresso.
"""

import sys
from pathlib import Path

from deploy.deploy_remote import _conn, _run

SCRIPT = Path(__file__).with_name("run_extracoes.py")
CONTAINER = "frap-worker"


def start(ano: str, mes: str = "") -> int:
    c, host = _conn()
    rc, status = _run(c, f"docker ps --filter name={CONTAINER} --format '{{{{.Status}}}}'")
    if not status.startswith("Up"):
        print(f"{CONTAINER} não está Up em {host} (status: {status!r}). Abortando.")
        return 1
    sftp = c.open_sftp()
    sftp.put(str(SCRIPT), "run_extracoes.py")
    sftp.close()
    rc, out = _run(c, f"docker cp run_extracoes.py {CONTAINER}:/tmp/run_extracoes.py")
    if rc != 0:
        print(out)
        return rc
    # Só o docker exec vai para background, com todos os fds redirecionados —
    # senão o canal SSH fica preso no stdout do subshell e o read() estoura.
    rc, out = _run(
        c,
        f"nohup docker exec {CONTAINER} python /tmp/run_extracoes.py {ano} {mes} "
        f"> extracao_{ano}.log 2>&1 < /dev/null & echo LAUNCHED pid=$!",
    )
    print(out)
    c.close()
    return rc


def status(ano: str, _mes: str = "") -> int:
    c, _ = _conn()
    rc, out = _run(c, f"tail -n 30 extracao_{ano}.log")
    print(out)
    c.close()
    return rc


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    sys.exit({"start": start, "status": status}[cmd](*args))
