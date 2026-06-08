"""DTOs for the ETL trigger endpoint."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel


JobStatusStr = Literal["queued", "deferred", "in_progress", "complete", "not_found"]
RunStatusStr = Literal["queued", "running", "done", "error"]
EtapaStr = Literal["queued", "decisoes", "obrigacoes", "recomendacoes", "done"]


class ExtractionFiltersBody(BaseModel):
    start_date: date
    end_date: date
    process_numbers: list[str] | None = None
    overwrite: bool = False


class ExtractionTriggerRequest(BaseModel):
    """Body for ``POST /etl/run``. Single-shot orchestration: NER → obrigação
    → recomendação. No ``kind`` field — the orchestrator runs all three stages.
    """

    filters: ExtractionFiltersBody


class ExtractionJobAccepted(BaseModel):
    extracao_id: int
    job_id: str
    status_url: str
    enqueued_at: datetime


class ExtractionJobStatus(BaseModel):
    job_id: str
    status: JobStatusStr
    success: bool | None = None
    result: dict[str, Any] | None = None
    enqueued_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ExtracaoOut(BaseModel):
    """One row from ``ExtracaoORM`` — covers history and live status."""

    model_config = {"from_attributes": True}

    id: int
    data_inicio: date
    data_fim: date
    data_execucao: datetime
    status: RunStatusStr
    etapa_atual: EtapaStr
    decisoes_processadas: int
    obrigacoes_geradas: int
    recomendacoes_geradas: int
    erros: int
    mensagem_erro: str | None = None
    job_id: str | None = None


class ExtracaoListPage(BaseModel):
    items: list[ExtracaoOut]
    page: int
    page_size: int
    total: int


class ExtracaoEventoOut(BaseModel):
    """One activity-feed entry. ``timestamp`` is server time when the event
    was emitted; ``payload`` shape varies per ``tipo`` and is consumed
    opaquely by the frontend (see ``ExtracaoEventoORM`` for the catalog of
    types and their payload conventions).
    """

    model_config = {"from_attributes": True}

    id: int
    extracao_id: int
    timestamp: datetime
    tipo: str
    payload: dict[str, Any] | None = None


class ExtracaoEventoListPage(BaseModel):
    items: list[ExtracaoEventoOut]
    has_more: bool


class DecisaoExtraidaItem(BaseModel):
    """One NERDecisão inside an extraction, with the obrigações and
    recomendações that were extracted from it (joined via the bridge tables).

    ``status`` per item reflects the review workflow:
      - ``pending`` — final row exists, no staging row → in the review queue.
      - ``approved`` / ``rejected`` — a staging row exists with that status.
    """

    id_ner_decisao: int
    id_processo: int
    id_composicao_pauta: int
    id_voto_pauta: int
    data_extracao: datetime | None = None
    obrigacoes: list["DecisaoItemRow"]
    recomendacoes: list["DecisaoItemRow"]


class DecisaoItemRow(BaseModel):
    id: int  # IdObrigacao or IdRecomendacao on the final table
    descricao: str
    status: Literal["pending", "approved", "rejected"]


class DecisaoExtraidaListPage(BaseModel):
    items: list[DecisaoExtraidaItem]
    page: int
    page_size: int
    total: int
