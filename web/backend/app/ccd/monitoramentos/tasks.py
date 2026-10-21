from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy.orm import Session

from app.ccd.monitoramentos import service
from app.ccd.monitoramentos.schemas import Analise, MonitoramentosResponse


def _calcular(guardadas: dict[str, Analise]) -> tuple[MonitoramentosResponse, dict[str, Analise]]:
    from app.db import get_processo_engine

    with Session(get_processo_engine()) as s:
        return service.montar(
            s, {**service.carregar_seed(), **guardadas}, analisar=service.analisador_llm()
        )


async def task_atualizar_monitoramentos(ctx: dict[str, Any]) -> str:
    """Cron diário: refaz o snapshot dos monitoramentos (LLM só onde há peça nova)."""
    redis = ctx["redis"]
    guardadas = service.analises_de_json(await redis.get(service.ANALISES_KEY))
    resp, novas = await asyncio.to_thread(_calcular, guardadas)
    await redis.set(service.ANALISES_KEY, service.analises_para_json(novas))
    await redis.set(service.SNAPSHOT_KEY, resp.model_dump_json())
    llm = sum(1 for i in resp.items if i.fonte == "llm")
    return f"{resp.total} processo(s); {llm} com análise do LLM"
