"""ARQ worker for stage-1 (NER) + stage-2 extraction.

A single orchestrator task ``run_full_extraction`` runs the three pipeline
stages back-to-back and updates the ``ExtracaoORM`` row after each stage so
the frontend can poll for live status:

  1. ``decisoes`` — NER extraction on raw decision texts via
     ``tools.utils.run_ner_pipeline_for_dataframe``.
  2. ``obrigacoes`` — stage-2 obrigação extraction.
  3. ``recomendacoes`` — stage-2 recomendação extraction.

Tasks are thin adapters: they build clients via factory functions (no
module-level instantiation — keeps tests importable without touching Azure
or MSSQL), call the pipelines, and update the ``Extracao`` row.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import date
from typing import Any

from sqlalchemy import update

from app.config import get_settings


logger = logging.getLogger(__name__)


# ---- factories (never called at import time) -----------------------------

# Azure deployment + structured-output mode shared by every stage. ``gpt-4``
# era a config anterior; ``gpt-5.4-nano`` não suporta o ``json_schema`` ainda,
# então usamos ``function_calling`` (também mais barato em tokens).
_LLM_DEPLOYMENT = "gpt-5.4-nano"
_LLM_MODEL = "gpt-5.4-nano"
_LLM_METHOD = "function_calling"


def _build_structured(schema_cls):
    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(deployment_name=_LLM_DEPLOYMENT, model_name=_LLM_MODEL)
    return llm.with_structured_output(schema_cls, include_raw=False, method=_LLM_METHOD)


def _build_ner_extractor():
    from cgad.schema import NERDecisao

    return _build_structured(NERDecisao)


def _build_obrigacao_extractor():
    from cgad.schema import Obrigacao

    return _build_structured(Obrigacao)


def _build_recomendacao_extractor():
    from cgad.schema import Recomendacao

    return _build_structured(Recomendacao)


def _build_responsible_extractor():
    from cgad.schema import ResponsibleChoice

    return _build_structured(ResponsibleChoice)


def _build_citation_extractor():
    from cgad.schema import CitationChoice

    return _build_structured(CitationChoice)


def _build_session():
    from sqlalchemy.orm import sessionmaker

    from cgad.utils import DB_DECISOES, get_connection

    return sessionmaker(bind=get_connection(DB_DECISOES))()


def _deserialize_filters(d: dict[str, Any]):
    """Coerce a JSON-compatible dict into ``ExtractionFilters``."""
    from cgad.etl.pipeline import ExtractionFilters

    def _coerce_date(v):
        if v is None or isinstance(v, date):
            return v
        return date.fromisoformat(v)

    return ExtractionFilters(
        start_date=_coerce_date(d.get("start_date")),
        end_date=_coerce_date(d.get("end_date")),
        process_numbers=d.get("process_numbers"),
        overwrite=bool(d.get("overwrite", False)),
    )


# ---- progress updates ---------------------------------------------------


_FIELD_MAP = {
    "status": "Status",
    "etapa": "EtapaAtual",
    "decisoes_processadas": "DecisoesProcessadas",
    "obrigacoes_geradas": "ObrigacoesGeradas",
    "recomendacoes_geradas": "RecomendacoesGeradas",
    "erros": "Erros",
    "mensagem_erro": "MensagemErro",
    "job_id": "JobId",
}


def _update_extracao(session, extracao_id: int, **fields) -> None:
    from cgad.models import ExtracaoORM

    updates = {_FIELD_MAP[k]: v for k, v in fields.items() if k in _FIELD_MAP}
    if not updates:
        return
    session.execute(
        update(ExtracaoORM)
        .where(ExtracaoORM.IdExtracao == extracao_id)
        .values(**updates)
    )
    session.commit()


def _emit_event(
    session, extracao_id: int, tipo: str, payload: dict[str, Any] | None = None
) -> None:
    """Persist one ``ExtracaoEvento`` row. Best-effort: errors are logged but
    do not abort the orchestrator — the live feed degrading is preferable to
    losing the actual extraction work.
    """
    from cgad.models import ExtracaoEventoORM

    try:
        session.add(
            ExtracaoEventoORM(
                IdExtracao=extracao_id,
                Tipo=tipo,
                Payload=payload or {},
            )
        )
        session.commit()
    except Exception:
        session.rollback()
        logger.exception(
            "failed to emit ExtracaoEvento (extracao=%s tipo=%s)",
            extracao_id,
            tipo,
        )


# ---- orchestrator task --------------------------------------------------


async def run_full_extraction(ctx: dict, filters_dict: dict, extracao_id: int) -> dict:
    """Run NER → Obrigação → Recomendação for one date window, updating the
    ``Extracao`` row after each stage and persisting per-decision events to
    ``ExtracaoEvento`` so the frontend's live feed can replay/follow.
    """
    from cgad.etl.pipeline import (
        enqueue_obrigacao_extraction,
        enqueue_recomendacao_extraction,
    )
    from cgad.utils import get_decisions_by_dates, process_decision_row

    filters = _deserialize_filters(filters_dict)
    job_id = ctx.get("job_id")
    run_id = str(extracao_id)
    logger.info("orchestrator job %s starting (extracao=%s)", job_id, extracao_id)

    session = _build_session()
    try:
        _update_extracao(
            session,
            extracao_id,
            status="running",
            etapa="decisoes",
            job_id=job_id,
        )
        _emit_event(session, extracao_id, "stage_started", {"stage": "decisoes"})

        # Stage 1 — NER. We iterate ourselves (instead of calling the
        # convenience wrapper) so we can emit one event per decision and
        # update DecisoesProcessadas live, not just at the end.
        df = get_decisions_by_dates(filters.start_date, filters.end_date)
        total = len(df)
        _emit_event(
            session,
            extracao_id,
            "stage_progress",
            {"stage": "decisoes", "total": total},
        )

        ner_extractor = _build_ner_extractor()
        ner_session = _build_session()
        processed = 0
        ner_errors = 0
        try:
            for _, row in df.iterrows():
                triple = (
                    int(row.id_processo),
                    int(row.id_composicao_pauta),
                    int(row.id_voto_pauta),
                )
                try:
                    ner_id = process_decision_row(
                        session=ner_session,
                        row=row,
                        extractor=ner_extractor,
                        model_name=_LLM_MODEL,
                        prompt_version="v1",
                        run_id=run_id,
                        overwrite=False,
                    )
                except Exception as exc:
                    ner_errors += 1
                    logger.exception("NER failed for %s", triple)
                    _emit_event(
                        session,
                        extracao_id,
                        "error",
                        {
                            "stage": "decisoes",
                            "id_processo": triple[0],
                            "id_composicao_pauta": triple[1],
                            "id_voto_pauta": triple[2],
                            "message": str(exc)[:300],
                        },
                    )
                    continue
                processed += 1
                _emit_event(
                    session,
                    extracao_id,
                    "decision_done",
                    {
                        "id_ner_decisao": ner_id,
                        "id_processo": triple[0],
                        "id_composicao_pauta": triple[1],
                        "id_voto_pauta": triple[2],
                        "processed": processed,
                        "total": total,
                    },
                )
                _update_extracao(
                    session,
                    extracao_id,
                    decisoes_processadas=processed,
                )
        finally:
            ner_session.close()

        _emit_event(
            session,
            extracao_id,
            "stage_done",
            {"stage": "decisoes", "processed": processed, "errors": ner_errors},
        )
        _update_extracao(
            session,
            extracao_id,
            decisoes_processadas=processed,
            erros=ner_errors,
            etapa="obrigacoes",
        )
        _emit_event(session, extracao_id, "stage_started", {"stage": "obrigacoes"})

        # Stage 2a — Obrigação.
        ob_session = _build_session()
        ob_progress = {"extracted": 0, "failed": 0}

        def _on_obrigacao(kind: str, payload: dict) -> None:
            tipo = (
                "obrigacao_extracted"
                if kind == "extracted"
                else "obrigacao_skipped"
                if kind == "skipped"
                else "error"
            )
            _emit_event(
                session,
                extracao_id,
                tipo,
                {**payload, "stage": "obrigacoes"} if kind != "extracted" else payload,
            )
            if kind == "extracted":
                ob_progress["extracted"] += 1
                _update_extracao(
                    session,
                    extracao_id,
                    obrigacoes_geradas=ob_progress["extracted"],
                )
            elif kind == "failed":
                ob_progress["failed"] += 1
                _update_extracao(
                    session,
                    extracao_id,
                    erros=ner_errors + ob_progress["failed"],
                )

        try:
            ob_report = enqueue_obrigacao_extraction(
                filters,
                extractor=_build_obrigacao_extractor(),
                responsible_extractor=_build_responsible_extractor(),
                citation_extractor=_build_citation_extractor(),
                session=ob_session,
                on_item=_on_obrigacao,
            )
        finally:
            ob_session.close()
        _emit_event(
            session,
            extracao_id,
            "stage_done",
            {"stage": "obrigacoes", **asdict(ob_report)},
        )
        _update_extracao(
            session,
            extracao_id,
            obrigacoes_geradas=ob_report.enqueued,
            erros=ner_errors + ob_report.failed,
            etapa="recomendacoes",
        )
        _emit_event(session, extracao_id, "stage_started", {"stage": "recomendacoes"})

        # Stage 2b — Recomendação.
        rec_session = _build_session()
        rec_progress = {"extracted": 0, "failed": 0}

        def _on_recomendacao(kind: str, payload: dict) -> None:
            tipo = (
                "recomendacao_extracted"
                if kind == "extracted"
                else "recomendacao_skipped"
                if kind == "skipped"
                else "error"
            )
            _emit_event(
                session,
                extracao_id,
                tipo,
                {**payload, "stage": "recomendacoes"}
                if kind != "extracted"
                else payload,
            )
            if kind == "extracted":
                rec_progress["extracted"] += 1
                _update_extracao(
                    session,
                    extracao_id,
                    recomendacoes_geradas=rec_progress["extracted"],
                )
            elif kind == "failed":
                rec_progress["failed"] += 1
                _update_extracao(
                    session,
                    extracao_id,
                    erros=ner_errors + ob_progress["failed"] + rec_progress["failed"],
                )

        try:
            rec_report = enqueue_recomendacao_extraction(
                filters,
                extractor=_build_recomendacao_extractor(),
                responsible_extractor=_build_responsible_extractor(),
                citation_extractor=_build_citation_extractor(),
                session=rec_session,
                on_item=_on_recomendacao,
            )
        finally:
            rec_session.close()
        _emit_event(
            session,
            extracao_id,
            "stage_done",
            {"stage": "recomendacoes", **asdict(rec_report)},
        )
        _update_extracao(
            session,
            extracao_id,
            recomendacoes_geradas=rec_report.enqueued,
            erros=ner_errors + ob_report.failed + rec_report.failed,
            etapa="done",
            status="done",
        )

        return {
            "extracao_id": extracao_id,
            "decisoes_processadas": processed,
            "obrigacoes": asdict(ob_report),
            "recomendacoes": asdict(rec_report),
        }
    except Exception as exc:
        logger.exception("orchestrator job %s failed", job_id)
        _emit_event(
            session,
            extracao_id,
            "error",
            {"message": str(exc)[:500], "fatal": True},
        )
        _update_extracao(
            session,
            extracao_id,
            status="error",
            mensagem_erro=str(exc)[:500],
        )
        raise
    finally:
        session.close()
