from __future__ import annotations

import asyncio
from typing import Any


async def task_extrair_resposta_desconto_folha(
    ctx: dict[str, Any], id_frap_job: int, id_cadastro: int
) -> str:
    from app.ccd.desconto_folha.extracao import extrair_resposta
    from app.jobs.tasks import _session_factory, _set_done, _set_failed, _set_running

    factory = _session_factory()
    _set_running(factory, id_frap_job)
    try:
        resultado = await asyncio.to_thread(extrair_resposta, id_cadastro)
        _set_done(factory, id_frap_job, resultado)
        return resultado
    except Exception as exc:
        _set_failed(factory, id_frap_job, repr(exc))
        raise
