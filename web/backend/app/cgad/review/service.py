"""Review business logic.

Pendente = a final-table row (``Obrigacao`` / ``Recomendacao``) without a
matching ``*Staging`` audit row. Approve/reject INSERTs the audit row keyed
to the final row by FK; claim state lives on the final row.

The atomic claim uses a conditional ``UPDATE`` guarded by the current claim
state, which is MSSQL-compatible (no ``SELECT … FOR UPDATE SKIP LOCKED``):
exactly one concurrent caller's WHERE clause matches, so exactly one
succeeds.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Literal, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, text, update
from sqlalchemy.orm import Session

from app.cgad.review import schemas
from cgad.etl.staging import (
    ObrigacaoStagingORM,
    RecomendacaoStagingORM,
    ReviewStatus,
)
from cgad.etl.text_alignment import find_span_with_status
from cgad.models import (
    ObrigacaoORM,
    RecomendacaoORM,
    UserORM,
)
from cgad.utils import DB_PROCESSOS, SQL_DIR, get_connection


logger = logging.getLogger(__name__)

CLAIM_TTL = timedelta(minutes=15)

Kind = Literal["obrigacao", "recomendacao"]


# ----- helpers -------------------------------------------------------------


def _final_orm(kind: Kind):
    return ObrigacaoORM if kind == "obrigacao" else RecomendacaoORM


def _final_pk(kind: Kind):
    orm = _final_orm(kind)
    return orm.IdObrigacao if kind == "obrigacao" else orm.IdRecomendacao


def _staging_orm(kind: Kind):
    return ObrigacaoStagingORM if kind == "obrigacao" else RecomendacaoStagingORM


def _staging_fk(kind: Kind):
    """Column on the staging audit table that links to the final-table PK."""
    orm = _staging_orm(kind)
    return orm.IdObrigacao if kind == "obrigacao" else orm.IdRecomendacao


def _staging_pk(kind: Kind):
    orm = _staging_orm(kind)
    return orm.IdObrigacaoStaging if kind == "obrigacao" else orm.IdRecomendacaoStaging


def _load_final(session: Session, kind: Kind, id: int):
    row = session.get(_final_orm(kind), id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="review not found"
        )
    return row


def _load_audit(session: Session, kind: Kind, final_id: int):
    """Return the (single) audit row linked to the given final-table row, or None."""
    stmt = select(_staging_orm(kind)).where(_staging_fk(kind) == final_id)
    return session.execute(stmt).scalar_one_or_none()


def _has_active_claim_by(final_row, user: UserORM) -> bool:
    if final_row.ReservadoPor != user.NomeUsuario:
        return False
    if final_row.DataReserva is None:
        return False
    return final_row.DataReserva >= datetime.utcnow() - CLAIM_TTL


def _final_descricao(final_row, kind: Kind) -> str:
    if kind == "obrigacao":
        return final_row.DescricaoObrigacao or ""
    return final_row.DescricaoRecomendacao or ""


def _final_id(final_row, kind: Kind) -> int:
    return final_row.IdObrigacao if kind == "obrigacao" else final_row.IdRecomendacao


def _coerce_solidarios(raw: Any) -> Optional[list[dict[str, Any]]]:
    """Normalize stored ``SolidariosMultaCominatoria`` to the new
    ``[{nome, documento}]`` shape. Legacy rows wrote a flat ``list[str]`` of
    names — coerce those to objects with ``documento=None`` so the form can
    render uniformly.
    """
    if raw is None:
        return None
    if not isinstance(raw, list):
        return None
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, str):
            out.append({"nome": item, "documento": None})
        elif isinstance(item, dict):
            out.append(
                {
                    "nome": item.get("nome") or item.get("name") or "",
                    "documento": item.get("documento") or item.get("document"),
                }
            )
    return out


def _final_fields(final_row, kind: Kind) -> dict[str, Any]:
    if kind == "obrigacao":
        return {
            "descricao_obrigacao": final_row.DescricaoObrigacao,
            "de_fazer": final_row.DeFazer,
            "prazo": final_row.Prazo,
            "data_cumprimento": final_row.DataCumprimento,
            "orgao_responsavel": final_row.OrgaoResponsavel,
            "id_orgao_responsavel": final_row.IdOrgaoResponsavel,
            "tem_multa_cominatoria": final_row.TemMultaCominatoria,
            "nome_responsavel_multa_cominatoria": final_row.NomeResponsavelMultaCominatoria,
            "documento_responsavel_multa_cominatoria": final_row.DocumentoResponsavelMultaCominatoria,
            "id_pessoa_multa_cominatoria": final_row.IdPessoaMultaCominatoria,
            "valor_multa_cominatoria": final_row.ValorMultaCominatoria,
            "periodo_multa_cominatoria": final_row.PeriodoMultaCominatoria,
            "e_multa_cominatoria_solidaria": final_row.EMultaCominatoriaSolidaria,
            "solidarios_multa_cominatoria": _coerce_solidarios(
                final_row.SolidariosMultaCominatoria
            ),
        }
    return {
        "descricao_recomendacao": final_row.DescricaoRecomendacao,
        "prazo_cumprimento_recomendacao": final_row.PrazoCumprimentoRecomendacao,
        "data_cumprimento_recomendacao": final_row.DataCumprimentoRecomendacao,
        "nome_responsavel": final_row.NomeResponsavel,
        "id_pessoa_responsavel": final_row.IdPessoaResponsavel,
        "orgao_responsavel": final_row.OrgaoResponsavel,
        "id_orgao_responsavel": final_row.IdOrgaoResponsavel,
        "cancelado": final_row.Cancelado,
    }


def _audit_fields(audit_row, kind: Kind) -> dict[str, Any]:
    """Reviewer-edited values stored on the audit row."""
    if kind == "obrigacao":
        return {
            "descricao_obrigacao": audit_row.DescricaoObrigacao,
            "de_fazer": audit_row.DeFazer,
            "prazo": audit_row.Prazo,
            "data_cumprimento": audit_row.DataCumprimento,
            "orgao_responsavel": audit_row.OrgaoResponsavel,
            "id_orgao_responsavel": audit_row.IdOrgaoResponsavel,
            "tem_multa_cominatoria": audit_row.TemMultaCominatoria,
            "nome_responsavel_multa_cominatoria": audit_row.NomeResponsavelMultaCominatoria,
            "documento_responsavel_multa_cominatoria": audit_row.DocumentoResponsavelMultaCominatoria,
            "id_pessoa_multa_cominatoria": audit_row.IdPessoaMultaCominatoria,
            "valor_multa_cominatoria": audit_row.ValorMultaCominatoria,
            "periodo_multa_cominatoria": audit_row.PeriodoMultaCominatoria,
            "e_multa_cominatoria_solidaria": audit_row.EMultaCominatoriaSolidaria,
            "solidarios_multa_cominatoria": _coerce_solidarios(
                audit_row.SolidariosMultaCominatoria
            ),
        }
    return {
        "descricao_recomendacao": audit_row.DescricaoRecomendacao,
        "prazo_cumprimento_recomendacao": audit_row.PrazoCumprimentoRecomendacao,
        "data_cumprimento_recomendacao": audit_row.DataCumprimentoRecomendacao,
        "nome_responsavel": audit_row.NomeResponsavel,
        "id_pessoa_responsavel": audit_row.IdPessoaResponsavel,
        "orgao_responsavel": audit_row.OrgaoResponsavel,
        "id_orgao_responsavel": audit_row.IdOrgaoResponsavel,
        "cancelado": audit_row.Cancelado,
    }


def _to_list_item(
    final_row,
    audit_row,
    kind: Kind,
    numero_ano: tuple[Optional[int], Optional[int]] = (None, None),
) -> schemas.ReviewListItem:
    if audit_row is None:
        status_value = ReviewStatus.pending.value
        reviewer = None
        reviewed_at = None
    else:
        status_value = (
            audit_row.Status.value
            if isinstance(audit_row.Status, ReviewStatus)
            else str(audit_row.Status)
        )
        reviewer = audit_row.Revisor
        reviewed_at = audit_row.DataRevisao
    numero, ano = numero_ano
    return schemas.ReviewListItem(
        id=_final_id(final_row, kind),
        kind=kind,
        status=status_value,
        descricao=_final_descricao(final_row, kind),
        id_processo=final_row.IdProcesso,
        id_composicao_pauta=final_row.IdComposicaoPauta,
        id_voto_pauta=final_row.IdVotoPauta,
        numero_processo=numero,
        ano_processo=ano,
        claimed_by=final_row.ReservadoPor,
        claimed_at=final_row.DataReserva,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )


def _load_processo_numero_ano(
    id_processos: list[int],
) -> dict[int, tuple[Optional[int], Optional[int]]]:
    """Batch-resolve ``IdProcesso → (Numero_Processo, Ano_Processo)`` from
    ``processo.dbo.Processos``. Returns ``{}`` on failure or empty input so the
    list endpoint never fails because of MSSQL — frontend falls back to
    ``id_processo``.
    """
    unique = sorted({int(i) for i in id_processos if i is not None})
    if not unique:
        return {}
    try:
        placeholders = ", ".join(str(i) for i in unique)
        sql = (
            "SELECT IdProcesso, Numero_Processo, Ano_Processo "
            "FROM processo.dbo.Processos "
            f"WHERE IdProcesso IN ({placeholders})"
        )
        with get_connection(DB_PROCESSOS).connect() as conn:
            rows = conn.execute(text(sql)).all()
        out: dict[int, tuple[Optional[int], Optional[int]]] = {}
        for row in rows:
            id_proc = getattr(row, "IdProcesso", None)
            numero = getattr(row, "Numero_Processo", None)
            ano = getattr(row, "Ano_Processo", None)
            if id_proc is None:
                continue
            out[int(id_proc)] = (
                int(numero) if numero is not None else None,
                int(ano) if ano is not None else None,
            )
        return out
    except Exception as exc:
        logger.exception(
            "failed to resolve numero/ano for %d processos: %s", len(unique), exc
        )
        return {}


def _resolve_processo_ids(processo: str) -> list[int]:
    """Resolve a user-typed ``"<numero>[/<ano>]"`` (e.g. ``"5202/2020"``) to the
    matching ``IdProcesso`` set in ``processo.dbo.Processos``. ``Numero_Processo``
    is stored zero-padded (``"005202"``), so we match on ``TRY_CAST(... AS INT)``.
    Returns ``[]`` when the input is unparseable or the query fails/finds nothing
    — the caller turns that into an empty page.
    """
    parts = processo.strip().replace("-", "/").split("/")
    numero_digits = re.sub(r"\D", "", parts[0]) if parts else ""
    if not numero_digits:
        return []
    params: dict[str, int] = {"num": int(numero_digits)}
    sql = (
        "SELECT IdProcesso FROM processo.dbo.Processos "
        "WHERE TRY_CAST(Numero_Processo AS INT) = :num"
    )
    if len(parts) > 1:
        ano_digits = re.sub(r"\D", "", parts[1])
        if ano_digits:
            sql += " AND TRY_CAST(Ano_Processo AS INT) = :ano"
            params["ano"] = int(ano_digits)
    try:
        with get_connection(DB_PROCESSOS).connect() as conn:
            rows = conn.execute(text(sql), params).all()
        return [int(r.IdProcesso) for r in rows]
    except Exception:
        logger.exception("failed to resolve processo %r", processo)
        return []


def _load_decisao_context(
    id_processo: int, id_composicao: int, id_voto: int
) -> dict[str, Any]:
    """Read ``texto_acordao`` plus ``numero_processo`` / ``ano_processo`` via
    ``sql/decisions_full_text.sql``. Returns a dict with all three keys
    (values may be None) so the detail endpoint degrades gracefully when the
    query can't run (e.g. in tests without a real MSSQL backend) — the
    frontend then falls back to ``id_processo`` and ``span_match_status``
    handles the missing text.
    """
    empty: dict[str, Any] = {
        "texto_acordao": None,
        "numero_processo": None,
        "ano_processo": None,
        "pessoas": [],
    }
    try:
        with open(os.path.join(SQL_DIR, "decisions_full_text.sql")) as f:
            sql = f.read()
        sql = sql.format(
            id_processo=id_processo,
            id_composicao_pauta=id_composicao,
            id_voto_pauta=id_voto,
        )
        with get_connection(DB_PROCESSOS).connect() as conn:
            rows = conn.execute(text(sql)).all()
        if not rows:
            logger.warning(
                "no decisao row for (%s, %s, %s) in vw_ia_votos_acordaos_decisoes",
                id_processo,
                id_composicao,
                id_voto,
            )
            return empty
        # The query joins Pro_ProcessosResponsavelDespesa/GenPessoa, returning
        # one row per responsible person. Decision-level columns repeat across
        # rows; pessoas are deduped by ``documento`` (or ``nome`` when no doc).
        head = rows[0]
        processo = getattr(head, "processo", None)
        numero, ano = _split_processo(processo)
        seen: set[str] = set()
        pessoas: list[dict[str, Any]] = []
        for row in rows:
            nome = getattr(row, "nome_responsavel", None)
            documento = getattr(row, "documento_responsavel", None)
            if not nome:
                continue
            key = (documento or "").strip() or f"nome:{nome}"
            if key in seen:
                continue
            seen.add(key)
            pessoas.append({"nome": nome, "documento": documento})
        return {
            "texto_acordao": getattr(head, "texto_acordao", None),
            "numero_processo": numero,
            "ano_processo": ano,
            "pessoas": pessoas,
        }
    except Exception as exc:
        logger.exception(
            "failed to load decisao context for (%s, %s, %s): %s",
            id_processo,
            id_composicao,
            id_voto,
            exc,
        )
        return empty


def _split_processo(processo: str | None) -> tuple[int | None, int | None]:
    """Parse ``"<numero>/<ano>"`` from ``decisions_full_text.sql``."""
    if not processo or "/" not in processo:
        return None, None
    numero_str, _, ano_str = processo.partition("/")
    try:
        return int(numero_str.strip()), int(ano_str.strip())
    except ValueError:
        return None, None


def _to_detail(
    session: Session, final_row, audit_row, kind: Kind
) -> schemas.ReviewDetail:
    """Detail without ``texto_acordao`` — fast, no MSSQL hit on the heavy text
    column. The frontend fetches the text separately via
    ``GET /reviews/{kind}/{id}/texto-acordao``.
    """
    if audit_row is None:
        staged = _final_fields(final_row, kind)
        original_payload = None
        status_value = ReviewStatus.pending.value
        reviewer = None
        reviewed_at = None
        review_notes = None
    else:
        staged = _audit_fields(audit_row, kind)
        original_payload = _final_fields(final_row, kind)
        status_value = (
            audit_row.Status.value
            if isinstance(audit_row.Status, ReviewStatus)
            else str(audit_row.Status)
        )
        reviewer = audit_row.Revisor
        reviewed_at = audit_row.DataRevisao
        review_notes = audit_row.ObservacoesRevisao

    return schemas.ReviewDetail(
        id=_final_id(final_row, kind),
        kind=kind,
        status=status_value,
        id_processo=final_row.IdProcesso,
        id_composicao_pauta=final_row.IdComposicaoPauta,
        id_voto_pauta=final_row.IdVotoPauta,
        staged=staged,
        original_payload=original_payload,
        claimed_by=final_row.ReservadoPor,
        claimed_at=final_row.DataReserva,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        review_notes=review_notes,
    )


def get_review_texto(
    session: Session, *, kind: Kind, id: int, current_user: UserORM
) -> schemas.ReviewTexto:
    """Fetch ``texto_acordao`` and the matched span for a single review item."""
    final_row = _load_final(session, kind, id)
    audit_row = _load_audit(session, kind, id)

    if audit_row is None:
        descricao = _final_descricao(final_row, kind)
    else:
        edited = _audit_fields(audit_row, kind)
        descricao = edited.get(
            "descricao_obrigacao" if kind == "obrigacao" else "descricao_recomendacao"
        ) or _final_descricao(final_row, kind)

    ctx = _load_decisao_context(
        final_row.IdProcesso,
        final_row.IdComposicaoPauta,
        final_row.IdVotoPauta,
    )
    texto_acordao = ctx["texto_acordao"]
    span, match_status = find_span_with_status(descricao or "", texto_acordao or "")
    return schemas.ReviewTexto(
        texto_acordao=texto_acordao,
        matched_span=span,
        span_match_status=match_status,
        numero_processo=ctx["numero_processo"],
        ano_processo=ctx["ano_processo"],
        pessoas=ctx.get("pessoas", []),
    )


# ----- list / get ----------------------------------------------------------


def list_reviews(
    session: Session,
    *,
    kind: Kind,
    status_filter: ReviewStatus,
    page: int,
    page_size: int,
    current_user: UserORM,
    processo: Optional[str] = None,
) -> schemas.ReviewListPage:
    final = _final_orm(kind)
    staging = _staging_orm(kind)
    fk = _staging_fk(kind)
    pk = _final_pk(kind)
    cutoff = datetime.utcnow() - CLAIM_TTL
    me = current_user.NomeUsuario

    if status_filter == ReviewStatus.pending:
        # LEFT JOIN final ↔ staging; pending = staging row missing.
        # Plus claim filter: exclude rows held by another reviewer (within TTL).
        stmt = (
            select(final, staging)
            .outerjoin(staging, fk == pk)
            .where(_staging_pk(kind).is_(None))
            .where(
                or_(
                    final.ReservadoPor.is_(None),
                    final.ReservadoPor == me,
                    final.DataReserva < cutoff,
                )
            )
        )
    else:
        # approved / rejected → INNER JOIN with status filter.
        stmt = (
            select(final, staging)
            .join(staging, fk == pk)
            .where(staging.Status == status_filter)
        )

    if processo and processo.strip():
        stmt = stmt.where(final.IdProcesso.in_(_resolve_processo_ids(processo)))

    total = session.execute(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    ).scalar_one()

    rows = session.execute(
        stmt.order_by(pk.asc()).offset((page - 1) * page_size).limit(page_size)
    ).all()

    numero_ano_by_id = _load_processo_numero_ano(
        [final_row.IdProcesso for final_row, _ in rows]
    )

    return schemas.ReviewListPage(
        items=[
            _to_list_item(
                final_row,
                audit_row,
                kind,
                numero_ano_by_id.get(final_row.IdProcesso, (None, None)),
            )
            for final_row, audit_row in rows
        ],
        page=page,
        page_size=page_size,
        total=total,
    )


def get_review(
    session: Session, *, kind: Kind, id: int, current_user: UserORM
) -> schemas.ReviewDetail:
    final_row = _load_final(session, kind, id)
    audit_row = _load_audit(session, kind, id)
    return _to_detail(session, final_row, audit_row, kind)


def list_awaiting_dispatch(
    session: Session,
    *,
    page: int,
    page_size: int,
    current_user: UserORM,
) -> schemas.AwaitingDispatchPage:
    """List approved staging rows (Obrigação + Recomendação combined),
    ordered by review date desc. These are records awaiting downstream
    dispatch — i.e., approved but not yet sent.
    """
    obrig_stmt = select(
        ObrigacaoStagingORM.IdObrigacao.label("final_id"),
        ObrigacaoStagingORM.IdProcesso.label("id_processo"),
        ObrigacaoStagingORM.DescricaoObrigacao.label("descricao"),
        ObrigacaoStagingORM.Revisor.label("reviewer"),
        ObrigacaoStagingORM.DataRevisao.label("reviewed_at"),
    ).where(ObrigacaoStagingORM.Status == ReviewStatus.approved)

    recom_stmt = select(
        RecomendacaoStagingORM.IdRecomendacao.label("final_id"),
        RecomendacaoStagingORM.IdProcesso.label("id_processo"),
        RecomendacaoStagingORM.DescricaoRecomendacao.label("descricao"),
        RecomendacaoStagingORM.Revisor.label("reviewer"),
        RecomendacaoStagingORM.DataRevisao.label("reviewed_at"),
    ).where(RecomendacaoStagingORM.Status == ReviewStatus.approved)

    obrig_rows = [
        ("obrigacao", row) for row in session.execute(obrig_stmt).mappings().all()
    ]
    recom_rows = [
        ("recomendacao", row) for row in session.execute(recom_stmt).mappings().all()
    ]
    combined = obrig_rows + recom_rows
    # Sort by reviewed_at desc, treating None as oldest.
    combined.sort(
        key=lambda pair: pair[1]["reviewed_at"] or datetime.min,
        reverse=True,
    )

    total = len(combined)
    start = (page - 1) * page_size
    page_rows = combined[start : start + page_size]

    numero_ano_by_id = _load_processo_numero_ano(
        [row["id_processo"] for _, row in page_rows]
    )

    items = [
        schemas.AwaitingDispatchItem(
            id=row["final_id"],
            kind=kind,
            id_processo=row["id_processo"],
            numero_processo=numero_ano_by_id.get(row["id_processo"], (None, None))[0],
            ano_processo=numero_ano_by_id.get(row["id_processo"], (None, None))[1],
            descricao=row["descricao"] or "",
            reviewer=row["reviewer"],
            reviewed_at=row["reviewed_at"],
        )
        for kind, row in page_rows
    ]

    return schemas.AwaitingDispatchPage(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


# ----- claim / release ----------------------------------------------------


def claim(
    session: Session, *, kind: Kind, id: int, current_user: UserORM
) -> schemas.ClaimResponse:
    final = _final_orm(kind)
    pk = _final_pk(kind)
    now = datetime.utcnow()
    cutoff = now - CLAIM_TTL
    me = current_user.NomeUsuario

    # Refuse if already reviewed (audit row exists).
    audit_row = _load_audit(session, kind, id)
    if audit_row is not None:
        status_value = (
            audit_row.Status.value
            if isinstance(audit_row.Status, ReviewStatus)
            else str(audit_row.Status)
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"review is {status_value}, not pending",
        )

    stmt = (
        update(final)
        .where(
            pk == id,
            or_(
                final.ReservadoPor.is_(None),
                final.ReservadoPor == me,
                final.DataReserva < cutoff,
            ),
        )
        .values(ReservadoPor=me, DataReserva=now)
        .execution_options(synchronize_session=False)
    )
    result = session.execute(stmt)
    session.commit()

    if result.rowcount == 1:
        row = session.get(final, id)
        return schemas.ClaimResponse(
            claimed_by=row.ReservadoPor,
            claimed_at=row.DataReserva,
            expires_at=row.DataReserva + CLAIM_TTL,
        )

    # rowcount == 0 → 404 vs 409.
    row = session.get(final, id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="review not found"
        )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"claimed by {row.ReservadoPor}",
    )


def release(session: Session, *, kind: Kind, id: int, current_user: UserORM) -> None:
    """Idempotent: release the claim if it's held by the caller."""
    final = _final_orm(kind)
    pk = _final_pk(kind)
    me = current_user.NomeUsuario

    stmt = (
        update(final)
        .where(pk == id, final.ReservadoPor == me)
        .values(ReservadoPor=None, DataReserva=None)
        .execution_options(synchronize_session=False)
    )
    session.execute(stmt)
    session.commit()


# ----- approve / reject ---------------------------------------------------


def _require_active_claim(final_row, user: UserORM) -> None:
    if not _has_active_claim_by(final_row, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no active claim by caller",
        )


def _refuse_if_already_reviewed(audit_row) -> None:
    if audit_row is None:
        return
    status_value = (
        audit_row.Status.value
        if isinstance(audit_row.Status, ReviewStatus)
        else str(audit_row.Status)
    )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"review is {status_value}",
    )


def _clear_claim(session: Session, kind: Kind, id: int) -> None:
    stmt = (
        update(_final_orm(kind))
        .where(_final_pk(kind) == id)
        .values(ReservadoPor=None, DataReserva=None)
        .execution_options(synchronize_session=False)
    )
    session.execute(stmt)


def approve_obrigacao(
    session: Session,
    *,
    id: int,
    payload: schemas.ObrigacaoReview,
    current_user: UserORM,
) -> schemas.ReviewDetail:
    final_row = _load_final(session, "obrigacao", id)
    _require_active_claim(final_row, current_user)
    _refuse_if_already_reviewed(_load_audit(session, "obrigacao", id))

    try:
        now = datetime.utcnow()
        audit = ObrigacaoStagingORM(
            IdObrigacao=final_row.IdObrigacao,
            IdProcesso=final_row.IdProcesso,
            IdComposicaoPauta=final_row.IdComposicaoPauta,
            IdVotoPauta=final_row.IdVotoPauta,
            DescricaoObrigacao=payload.descricao_obrigacao,
            DeFazer=payload.de_fazer,
            Prazo=payload.prazo,
            DataCumprimento=payload.data_cumprimento,
            OrgaoResponsavel=payload.orgao_responsavel,
            IdOrgaoResponsavel=payload.id_orgao_responsavel,
            TemMultaCominatoria=payload.tem_multa_cominatoria,
            NomeResponsavelMultaCominatoria=payload.nome_responsavel_multa_cominatoria,
            DocumentoResponsavelMultaCominatoria=payload.documento_responsavel_multa_cominatoria,
            IdPessoaMultaCominatoria=payload.id_pessoa_multa_cominatoria,
            ValorMultaCominatoria=payload.valor_multa_cominatoria,
            PeriodoMultaCominatoria=payload.periodo_multa_cominatoria,
            EMultaCominatoriaSolidaria=payload.e_multa_cominatoria_solidaria,
            SolidariosMultaCominatoria=(
                [s.model_dump() for s in payload.solidarios_multa_cominatoria]
                if payload.solidarios_multa_cominatoria
                else None
            ),
            Status=ReviewStatus.approved,
            Revisor=current_user.NomeUsuario,
            DataRevisao=now,
        )
        session.add(audit)
        _clear_claim(session, "obrigacao", id)
        session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        session.rollback()
        logger.exception("approval transaction failed for obrigacao %s", id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="approval transaction failed",
        ) from exc

    session.refresh(final_row)
    return _to_detail(session, final_row, audit, "obrigacao")


def approve_recomendacao(
    session: Session,
    *,
    id: int,
    payload: schemas.RecomendacaoReview,
    current_user: UserORM,
) -> schemas.ReviewDetail:
    final_row = _load_final(session, "recomendacao", id)
    _require_active_claim(final_row, current_user)
    _refuse_if_already_reviewed(_load_audit(session, "recomendacao", id))

    try:
        now = datetime.utcnow()
        audit = RecomendacaoStagingORM(
            IdRecomendacao=final_row.IdRecomendacao,
            IdProcesso=final_row.IdProcesso,
            IdComposicaoPauta=final_row.IdComposicaoPauta,
            IdVotoPauta=final_row.IdVotoPauta,
            DescricaoRecomendacao=payload.descricao_recomendacao,
            PrazoCumprimentoRecomendacao=payload.prazo_cumprimento_recomendacao,
            DataCumprimentoRecomendacao=payload.data_cumprimento_recomendacao,
            NomeResponsavel=payload.nome_responsavel,
            IdPessoaResponsavel=payload.id_pessoa_responsavel,
            OrgaoResponsavel=payload.orgao_responsavel,
            IdOrgaoResponsavel=payload.id_orgao_responsavel,
            Cancelado=payload.cancelado,
            Status=ReviewStatus.approved,
            Revisor=current_user.NomeUsuario,
            DataRevisao=now,
        )
        session.add(audit)
        _clear_claim(session, "recomendacao", id)
        session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        session.rollback()
        logger.exception("approval transaction failed for recomendacao %s", id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="approval transaction failed",
        ) from exc

    session.refresh(final_row)
    return _to_detail(session, final_row, audit, "recomendacao")


def reject(
    session: Session,
    *,
    kind: Kind,
    id: int,
    notes: str,
    current_user: UserORM,
) -> schemas.ReviewDetail:
    final_row = _load_final(session, kind, id)
    _require_active_claim(final_row, current_user)
    _refuse_if_already_reviewed(_load_audit(session, kind, id))

    try:
        now = datetime.utcnow()
        if kind == "obrigacao":
            audit = ObrigacaoStagingORM(
                IdObrigacao=final_row.IdObrigacao,
                IdProcesso=final_row.IdProcesso,
                IdComposicaoPauta=final_row.IdComposicaoPauta,
                IdVotoPauta=final_row.IdVotoPauta,
                DescricaoObrigacao=final_row.DescricaoObrigacao,
                Status=ReviewStatus.rejected,
                Revisor=current_user.NomeUsuario,
                DataRevisao=now,
                ObservacoesRevisao=notes,
            )
        else:
            audit = RecomendacaoStagingORM(
                IdRecomendacao=final_row.IdRecomendacao,
                IdProcesso=final_row.IdProcesso,
                IdComposicaoPauta=final_row.IdComposicaoPauta,
                IdVotoPauta=final_row.IdVotoPauta,
                DescricaoRecomendacao=final_row.DescricaoRecomendacao,
                Status=ReviewStatus.rejected,
                Revisor=current_user.NomeUsuario,
                DataRevisao=now,
                ObservacoesRevisao=notes,
            )
        session.add(audit)
        _clear_claim(session, kind, id)
        session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        session.rollback()
        logger.exception("reject transaction failed for %s %s", kind, id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="reject transaction failed",
        ) from exc

    session.refresh(final_row)
    return _to_detail(session, final_row, audit, kind)
