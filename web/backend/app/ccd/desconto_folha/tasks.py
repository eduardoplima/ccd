from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

_SQL_UPDATE_NOTIFICACAO = """
UPDATE CCDDescontoFolha SET
    NumeroNotificacao = COALESCE(:NumeroNotificacao, NumeroNotificacao),
    DataNotificacao = COALESCE(:DataNotificacao, DataNotificacao),
    TipoNotificacao = COALESCE(:TipoNotificacao, TipoNotificacao),
    EventoNotificacao = COALESCE(:EventoNotificacao, EventoNotificacao),
    IdEventoNotificacao = COALESCE(:IdEventoNotificacao, IdEventoNotificacao),
    NumeroPostagemAr = COALESCE(:NumeroPostagemAr, NumeroPostagemAr),
    DataAr = COALESCE(:DataAr, DataAr),
    TipoRecebimento = COALESCE(:TipoRecebimento, TipoRecebimento),
    EventoRecebimento = COALESCE(:EventoRecebimento, EventoRecebimento),
    IdEventoRecebimento = COALESCE(:IdEventoRecebimento, IdEventoRecebimento),
    DataAtualizacao = :agora
WHERE IdCCDDescontoFolha = :c
"""


def localizar_notificacoes(ids: list[int] | None = None) -> str:
    """Varre os cadastros ativos (ou `ids`) e grava notificação/recebimento achados
    no banco `processo`. Sobrescreve o que encontrou; preserva o que não encontrou."""
    from datetime import datetime

    from app.ccd.desconto_folha import notificacao, processo_lookup
    from app.db import get_processo_engine
    from app.jobs.tasks import _session_factory

    factory = _session_factory()
    with factory() as s:
        sql = "SELECT IdCCDDescontoFolha AS id, IdProcesso FROM CCDDescontoFolha WHERE Ativo = 1"
        if ids:
            marcas = ", ".join(f":i{n}" for n in range(len(ids)))
            rows = (
                s.execute(
                    text(f"{sql} AND IdCCDDescontoFolha IN ({marcas})"),
                    {f"i{n}": v for n, v in enumerate(ids)},
                )
                .mappings()
                .all()
            )
        else:
            rows = s.execute(text(sql)).mappings().all()
        cadastros = [dict(r) for r in rows]

    total = com_notif = eletronicas = com_receb = sem_nada = 0
    with Session(get_processo_engine()) as sp, factory() as s:
        for cad in cadastros:
            total += 1
            p = processo_lookup.processo_por_id(sp, int(cad["IdProcesso"]))
            if p is None:
                sem_nada += 1
                continue
            achado = notificacao.localizar(
                sp,
                id_processo=int(p["IdProcesso"]),
                numero=p["numero"],
                ano=p["ano"],
                id_origem=p["id_origem"],
            )
            tem_notif = bool(achado["DataNotificacao"] or achado["NumeroNotificacao"])
            com_notif += tem_notif
            eletronicas += tem_notif and achado["TipoNotificacao"] == "E"
            com_receb += bool(achado["DataAr"])
            sem_nada += not (tem_notif or achado["DataAr"])
            s.execute(
                text(_SQL_UPDATE_NOTIFICACAO),
                {**achado, "agora": datetime.utcnow().replace(microsecond=0), "c": cad["id"]},
            )
            s.commit()
    return (
        f"{total} cadastro(s): {com_notif} com notificação (eletrônica: {eletronicas}, "
        f"física: {com_notif - eletronicas}), {com_receb} com recebimento, {sem_nada} sem nada"
    )


async def task_localizar_notificacoes_desconto_folha(
    ctx: dict[str, Any], id_frap_job: int, ids: list[int] | None = None
) -> str:
    from app.jobs.tasks import _session_factory, _set_done, _set_failed, _set_running

    factory = _session_factory()
    _set_running(factory, id_frap_job)
    try:
        resultado = await asyncio.to_thread(localizar_notificacoes, ids)
        _set_done(factory, id_frap_job, resultado)
        return resultado
    except Exception as exc:
        _set_failed(factory, id_frap_job, repr(exc))
        raise


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
