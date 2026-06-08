"""ARQ tasks que disparam o pipeline de `tools/frap` via subprocess.

Cada task abre uma sessão própria contra o BdDIP para atualizar a linha
correspondente em `FRAPJob` em cada transição (running → done | failed).
"""

from __future__ import annotations

import asyncio
import sys
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth.models import FRAPUsuario  # noqa: F401  registra FK target no metadata
from app.config import get_settings
from app.jobs.models import FRAPJob

ROOT = Path(__file__).resolve().parents[3]


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _session_factory():
    engine = create_engine(get_settings().database_url, future=True, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _cmd(*args: str) -> list[str]:
    return [sys.executable, "-m", "frap.cli", *args]


async def _run(args: list[str]) -> str:
    proc = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        stdout_b, _ = await proc.communicate()
    except asyncio.CancelledError:
        with suppress(ProcessLookupError):
            proc.kill()
        with suppress(Exception):
            await proc.wait()
        raise
    output = stdout_b.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"comando falhou (rc={proc.returncode}):\n{output[-2000:]}")
    return output


def _set_running(factory, id_job: int) -> None:
    with factory() as s:
        job = s.get(FRAPJob, id_job)
        if job is None or job.Status == "cancelled":
            return
        job.Status = "running"
        job.DataInicio = _utcnow()
        s.commit()


def _set_done(factory, id_job: int, resultado: str) -> None:
    with factory() as s:
        job = s.get(FRAPJob, id_job)
        if job is None or job.Status == "cancelled":
            return
        job.Status = "done"
        job.DataFim = _utcnow()
        job.Resultado = resultado[-3500:]
        s.commit()


def _set_failed(factory, id_job: int, erro: str) -> None:
    with factory() as s:
        job = s.get(FRAPJob, id_job)
        if job is None or job.Status == "cancelled":
            return
        job.Status = "failed"
        job.DataFim = _utcnow()
        job.ErroMensagem = erro[-1900:]
        s.commit()


async def task_parse_e_publicar(ctx: dict[str, Any], id_frap_job: int) -> str:
    factory = _session_factory()
    _set_running(factory, id_frap_job)
    try:
        output = await _run(_cmd("parse-extratos"))
        output += "\n" + await _run(_cmd("publicar-extrato"))
        _set_done(factory, id_frap_job, output)
        return output
    except Exception as exc:
        _set_failed(factory, id_frap_job, repr(exc))
        raise


async def task_conciliar_mes(ctx: dict[str, Any], id_frap_job: int, ano: int, mes: int) -> str:
    factory = _session_factory()
    _set_running(factory, id_frap_job)
    sufixo_ano = str(ano)
    sufixo_mes = str(mes)
    contas = ("700000-6", "600000-2")
    plano: list[list[str]] = [
        _cmd("conciliar-ob", "--ano", sufixo_ano, "--mes", sufixo_mes),
        _cmd("conciliar-pessoa", "--ano", sufixo_ano, "--mes", sufixo_mes),
        _cmd("conciliar-guia", "--ano", sufixo_ano, "--mes", sufixo_mes),
        _cmd("conciliar-desconto-folha", "--ano", sufixo_ano, "--mes", sufixo_mes),
    ]
    for conta in contas:
        for matcher in ("ob", "pessoa", "guia"):
            plano.append(
                _cmd(
                    f"publicar-match-{matcher}",
                    "--ano",
                    sufixo_ano,
                    "--mes",
                    sufixo_mes,
                    "--conta",
                    conta,
                )
            )
    plano.append(_cmd("publicar-match-desconto-folha", "--ano", sufixo_ano, "--mes", sufixo_mes))

    saidas: list[str] = []
    try:
        for cmd_args in plano:
            label = " ".join(cmd_args[2:])
            saidas.append(f"$ {label}")
            saidas.append(await _run(cmd_args))
        resultado = "\n".join(saidas)
        _set_done(factory, id_frap_job, resultado)
        return resultado
    except Exception as exc:
        saidas.append(f"!! {exc!r}")
        _set_failed(factory, id_frap_job, "\n".join(saidas))
        raise
