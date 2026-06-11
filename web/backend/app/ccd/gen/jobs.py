"""Enfileiramento e ciclo de vida dos jobs de geração de documentos do CCD.

Reaproveita a tabela `FRAPJob` e a fila ARQ. Diferente de
`app.jobs.service.enqueue_job`, a lista de processos selecionados **não** vai
na coluna `Argumentos` (que tem limite de tamanho): ela é gravada em
`<artifact_dir>/input.json` e o worker a lê de lá. `Argumentos` guarda só um
resumo (`modo` + `qtd`) para exibição no histórico.

Convenção de `Tipo`: prefixo `ccd-` (`ccd-desconto-folha`, `ccd-antecedentes`).
O endpoint de download (em `app.ccd.router`) só serve artefatos de jobs com
esse prefixo.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from arq import ArqRedis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario
from app.ccd.gen.paths import artifact_dir
from app.ccd.gen.render import montar_saida
from app.config import get_settings
from app.jobs.models import FRAPJob

TIPO_PREFIXO = "ccd-"


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Enfileiramento (lado HTTP)
# ---------------------------------------------------------------------------


async def enqueue_ccd_job(
    pool: ArqRedis,
    session: Session,
    *,
    user: FRAPUsuario,
    tipo: str,
    funcao: str,
    processos: list[str],
    modo: str,
) -> FRAPJob:
    """Cria a linha em `FRAPJob`, grava `input.json` e enfileira o job ARQ.

    `funcao` é o nome registrado em `WorkerSettings.functions`; o worker recebe
    apenas o `id_job` e lê os processos do `input.json`.
    """
    if not tipo.startswith(TIPO_PREFIXO):
        raise ValueError(f"tipo de job CCD deve começar com {TIPO_PREFIXO!r}")

    row = FRAPJob(
        ArqJobId="pending",
        Tipo=tipo,
        Argumentos=json.dumps({"modo": modo, "qtd": len(processos)}),
        Status="pending",
        IdUsuario=user.IdUsuario,
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    d = artifact_dir(row.IdFRAPJob)
    (d / "input.json").write_text(
        json.dumps({"processos": processos, "modo": modo}, ensure_ascii=False),
        encoding="utf-8",
    )

    arq_job = await pool.enqueue_job(funcao, row.IdFRAPJob)
    if arq_job is None:
        row.Status = "failed"
        row.ErroMensagem = "não foi possível enfileirar o job no Redis"
        session.commit()
        return row

    row.ArqJobId = arq_job.job_id
    session.commit()
    session.refresh(row)
    return row


def read_input(id_job: int) -> list[str]:
    """Lê a lista de processos gravada no enfileiramento (lado worker)."""
    p = artifact_dir(id_job) / "input.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return list(data.get("processos", []))


# ---------------------------------------------------------------------------
# Ciclo de vida (lado worker) — sessão própria contra o BdDIP
# ---------------------------------------------------------------------------


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(get_settings().database_url, future=True, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def set_running(factory: sessionmaker[Session], id_job: int) -> None:
    with factory() as s:
        job = s.get(FRAPJob, id_job)
        if job is None or job.Status == "cancelled":
            return
        job.Status = "running"
        job.DataInicio = _utcnow()
        s.commit()


def set_done(factory: sessionmaker[Session], id_job: int, resultado: str) -> None:
    with factory() as s:
        job = s.get(FRAPJob, id_job)
        if job is None or job.Status == "cancelled":
            return
        job.Status = "done"
        job.DataFim = _utcnow()
        job.Resultado = resultado[-3500:]
        s.commit()


def set_failed(factory: sessionmaker[Session], id_job: int, erro: str) -> None:
    with factory() as s:
        job = s.get(FRAPJob, id_job)
        if job is None or job.Status == "cancelled":
            return
        job.Status = "failed"
        job.DataFim = _utcnow()
        job.ErroMensagem = erro[-1900:]
        s.commit()


def run_generation(
    id_job: int,
    gerar_fn: Callable[[list[str], Path], list[Path]],
) -> str:
    """Driver síncrono de um job de geração.

    Marca `running`, chama `gerar_fn(processos, out_dir)` (que produz os PDFs por
    processo), empacota em `final.pdf`/`final.zip` e marca `done`. Em erro, marca
    `failed` e relança. `gerar_fn` é a parte de domínio de cada feature.
    """
    factory = session_factory()
    set_running(factory, id_job)
    try:
        processos = read_input(id_job)
        out_dir = artifact_dir(id_job)
        pdfs = gerar_fn(processos, out_dir)
        final = montar_saida(pdfs, out_dir)
        resultado = f"{len(pdfs)} documento(s) gerado(s) → {final.name}"
        set_done(factory, id_job, resultado)
        return resultado
    except Exception as exc:
        set_failed(factory, id_job, repr(exc))
        raise
