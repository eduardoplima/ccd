from __future__ import annotations

import asyncio
from typing import Any


async def task_gerar_desconto_folha(ctx: dict[str, Any], id_frap_job: int) -> str:
    from app.ccd.desconto_folha.service import gerar_documentos
    from app.ccd.gen.jobs import run_generation

    return await asyncio.to_thread(run_generation, id_frap_job, gerar_documentos)
