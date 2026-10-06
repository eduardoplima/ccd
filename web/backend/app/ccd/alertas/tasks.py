from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy.orm import Session

from app.ccd.alertas.schemas import AlertasResponse
from app.ccd.alertas.service import SNAPSHOT_KEY, calcular_snapshot


def _calcular() -> AlertasResponse:
    from app.db import get_processo_engine

    with Session(get_processo_engine()) as s:
        return calcular_snapshot(s)


async def task_calcular_alertas(ctx: dict[str, Any]) -> str:
    """Cron diário (00:00 de Brasília): grava o snapshot dos alertas no Redis."""
    resp = await asyncio.to_thread(_calcular)
    await ctx["redis"].set(SNAPSHOT_KEY, resp.model_dump_json())
    return f"{resp.total} processo(s) com alerta"
