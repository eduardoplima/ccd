"""Decision-level review business logic.

The review unit is one ``NERDecisao``. Pendente = ``RevisadoPor IS NULL`` and
at least one NER child. Approving inserts ``*Staging`` audit rows for every
entity (all four types) in a single transaction and stamps
``RevisadoPor``/``DataRevisao`` on the decision — final tables are never
mutated (audit-only model).

A reserva (``ReservadoPor``/``DataReserva``) é informativa, não um lock: não
expira e qualquer usuário pode reservar por cima de outro. Serve só para
mostrar na fila quem está com a decisão aberta.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import date, datetime
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import bindparam, func, select, text, update
from sqlalchemy.orm import Session

from app.cgad.review import schemas
from app.db import get_engine
from cgad.etl.staging import (
    MultaStagingORM,
    ObrigacaoStagingORM,
    RecomendacaoStagingORM,
    RessarcimentoStagingORM,
    ReviewStatus,
)
from cgad.etl.text_alignment import find_span_offsets
from cgad.models import (
    NERDecisaoORM,
    NERMultaORM,
    NERObrigacaoORM,
    NERRecomendacaoORM,
    NERRessarcimentoORM,
    ObrigacaoORM,
    ProcessedObrigacaoORM,
    ProcessedRecomendacaoORM,
    RecomendacaoORM,
    UserORM,
)
from cgad.utils import DB_PROCESSOS, SQL_DIR, get_connection


logger = logging.getLogger(__name__)

TIPOS: tuple[schemas.Tipo, ...] = ("multa", "obrigacao", "recomendacao", "ressarcimento")

_NER_ORM = {
    "multa": NERMultaORM,
    "obrigacao": NERObrigacaoORM,
    "recomendacao": NERRecomendacaoORM,
    "ressarcimento": NERRessarcimentoORM,
}
_NER_PK = {
    "multa": NERMultaORM.IdNerMulta,
    "obrigacao": NERObrigacaoORM.IdNerObrigacao,
    "recomendacao": NERRecomendacaoORM.IdNerRecomendacao,
    "ressarcimento": NERRessarcimentoORM.IdNerRessarcimento,
}
_NER_DESCRICAO_ATTR = {
    "multa": "DescricaoMulta",
    "obrigacao": "DescricaoObrigacao",
    "recomendacao": "DescricaoRecomendacao",
    "ressarcimento": "DescricaoRessarcimento",
}
_STAGING_ORM = {
    "multa": MultaStagingORM,
    "obrigacao": ObrigacaoStagingORM,
    "recomendacao": RecomendacaoStagingORM,
    "ressarcimento": RessarcimentoStagingORM,
}
_STAGING_NER_FK = {
    "multa": MultaStagingORM.IdNerMulta,
    "obrigacao": ObrigacaoStagingORM.IdNerObrigacao,
    "recomendacao": RecomendacaoStagingORM.IdNerRecomendacao,
    "ressarcimento": RessarcimentoStagingORM.IdNerRessarcimento,
}


def _ner_id(ner_row) -> int:
    for attr in ("IdNerMulta", "IdNerObrigacao", "IdNerRecomendacao", "IdNerRessarcimento"):
        value = getattr(ner_row, attr, None)
        if value is not None:
            return value
    raise ValueError("NER row without id")


# ----- shared helpers (unchanged from the per-entity flow) ------------------


def _coerce_solidarios(raw: Any) -> Optional[list[dict[str, Any]]]:
    """Normalize stored solidários JSON to ``[{nome, documento}]``. Legacy rows
    wrote a flat ``list[str]`` of names — coerce those to objects with
    ``documento=None`` so the form can render uniformly."""
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
        logger.exception("failed to resolve numero/ano for %d processos: %s", len(unique), exc)
        return {}


def list_orgaos() -> list[schemas.OrgaoOut]:
    """Órgãos de ``processo.dbo.Orgaos`` para o campo Órgão responsável.
    Retorna ``[]`` em falha (ex.: testes sem MSSQL) — o campo degrada para
    texto livre no frontend.
    """
    try:
        with get_connection(DB_PROCESSOS).connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT DISTINCT IdOrgao, Nome FROM processo.dbo.Orgaos "
                    "WHERE Nome IS NOT NULL ORDER BY Nome"
                )
            ).all()
        return [schemas.OrgaoOut(id=int(r.IdOrgao), nome=str(r.Nome).strip()) for r in rows]
    except Exception:
        logger.exception("failed to list orgaos")
        return []


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


_SQL_CARGOS_ANEXO42 = text(
    """
    SELECT DISTINCT resp.CPF,
           respuni.Cargo,
           uni.NomeUnidade,
           respuni.DataInicioGestao,
           respuni.DataTerminoGestao
    FROM BdSIAI.dbo.Anexo42_Responsavel resp
    INNER JOIN BdSIAI.dbo.Anexo42_ResponsavelUnidade respuni
        ON respuni.IdResponsavel = resp.IdResponsavel
    INNER JOIN BdSIAI.dbo.Anexo42_UnidadeJurisdicionada uni
        ON uni.IdUnidadeJurisdicionada = respuni.IdUnidadeJurisdicionada
    WHERE resp.CPF IN :cpfs
    """
).bindparams(bindparam("cpfs", expanding=True))

# SiaiDp_Funcionario tem uma linha por remessa da folha — agrega por cargo/órgão.
_SQL_CARGOS_SIAI_PESSOAL = text(
    """
    SELECT cp.CPF,
           COALESCE(c.NomeCargo, f.NomeCargo) AS Cargo,
           LTRIM(RTRIM(og.NomeOrgao)) AS Orgao,
           MIN(f.DataInicial) AS Inicio,
           MAX(f.DataFinal) AS Fim
    FROM BdSIAIPessoal.dbo.Comum_Pessoa cp
    INNER JOIN BdSIAIPessoal.dbo.SiaiDp_Funcionario f ON f.IdPessoa = cp.IdPessoa
    LEFT JOIN BdSIAIPessoal.dbo.SiaiDp_Cargo c ON c.IdCargo = f.IdCargo
    LEFT JOIN Bdc.dbo.vw_Gen_Orgao og ON og.IdOrgao = f.IdOrgao
    WHERE cp.CPF IN :cpfs
    GROUP BY cp.CPF, COALESCE(c.NomeCargo, f.NomeCargo), LTRIM(RTRIM(og.NomeOrgao))
    """
).bindparams(bindparam("cpfs", expanding=True))


def _cargos_por_cpfs(cpfs: list[str]) -> dict[str, list[schemas.PessoaCargo]]:
    """Cargos por CPF nas bases Anexo 42 (BdSIAI) e SIAI Pessoal (BdSIAIPessoal),
    via cross-DB no engine BdDIP. Cada fonte degrada isoladamente para nada."""
    if not cpfs:
        return {}
    out: dict[str, list[schemas.PessoaCargo]] = {}

    def _add(cpf: str, cargo: schemas.PessoaCargo) -> None:
        # CPF é char(11) no MSSQL — pode vir com padding.
        out.setdefault((cpf or "").strip(), []).append(cargo)

    try:
        with get_engine().connect() as conn:
            rows = conn.execute(_SQL_CARGOS_ANEXO42, {"cpfs": cpfs}).all()
        for r in rows:
            if r.Cargo:
                _add(
                    r.CPF,
                    schemas.PessoaCargo(
                        fonte="anexo42",
                        cargo=r.Cargo,
                        orgao=r.NomeUnidade,
                        inicio=r.DataInicioGestao,
                        fim=r.DataTerminoGestao,
                    ),
                )
    except Exception:
        logger.exception("cargo lookup (anexo42) failed for %d cpfs", len(cpfs))
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(_SQL_CARGOS_SIAI_PESSOAL, {"cpfs": cpfs}).all()
        for r in rows:
            if r.Cargo:
                inicio = r.Inicio.date() if isinstance(r.Inicio, datetime) else r.Inicio
                fim = r.Fim.date() if isinstance(r.Fim, datetime) else r.Fim
                # DataFinal 9999-12-31 é sentinela de vínculo vigente.
                if fim is not None and fim.year == 9999:
                    fim = None
                _add(
                    r.CPF,
                    schemas.PessoaCargo(
                        fonte="siai_pessoal",
                        cargo=r.Cargo,
                        orgao=r.Orgao,
                        inicio=inicio,
                        fim=fim,
                    ),
                )
    except Exception:
        logger.exception("cargo lookup (siai_pessoal) failed for %d cpfs", len(cpfs))
    for cargos in out.values():
        cargos.sort(key=lambda c: (c.fim or date.max, c.inicio or date.min), reverse=True)
    return out


def _load_decisao_context(id_processo: int, id_composicao: int, id_voto: int) -> dict[str, Any]:
    """Read ``texto_acordao`` plus ``numero_processo`` / ``ano_processo`` via
    ``sql/decisions_full_text.sql``. Returns a dict with all keys (values may
    be None) so the texto endpoint degrades gracefully when the query can't
    run (e.g. in tests without a real MSSQL backend).
    """
    empty: dict[str, Any] = {
        "texto_acordao": None,
        "numero_processo": None,
        "ano_processo": None,
        "pessoas": [],
        "relatorio": None,
        "fundamentacao_voto": None,
        "conclusao": None,
        "orgao_responsavel": None,
        "orgao_origem": None,
        "interessado": None,
        "numero_acordao": None,
        "ano_acordao": None,
        "tipo_acordao": None,
        "data_sessao": None,
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

        # Enriquecimento: cargos por CPF (só pessoa física — 11 dígitos).
        def _cpf(p: dict[str, Any]) -> str:
            return re.sub(r"\D", "", p["documento"] or "")

        cargos = _cargos_por_cpfs(sorted({c for p in pessoas if len(c := _cpf(p)) == 11}))
        for p in pessoas:
            p["cargos"] = cargos.get(_cpf(p), [])
        # Gestores (com cargo no Anexo 42) primeiro — sort estável preserva a
        # ordem do processo nos empates.
        pessoas.sort(key=lambda p: not any(c.fonte == "anexo42" for c in p["cargos"]))
        return {
            "texto_acordao": getattr(head, "texto_acordao", None),
            "numero_processo": numero,
            "ano_processo": ano,
            "pessoas": pessoas,
            "relatorio": getattr(head, "relatorio", None),
            "fundamentacao_voto": getattr(head, "fundamentacao_voto", None),
            "conclusao": getattr(head, "conclusao", None),
            "orgao_responsavel": getattr(head, "orgao_responsavel", None),
            "orgao_origem": getattr(head, "orgao_origem", None),
            # interessado é char(255) no MSSQL — vem com padding à direita
            "interessado": (getattr(head, "interessado", None) or "").strip() or None,
            # numeroResultado é char no MSSQL — idem
            "numero_acordao": (str(getattr(head, "numero_resultado", "") or "")).strip() or None,
            "ano_acordao": (str(getattr(head, "ano_resultado", "") or "")).strip() or None,
            "tipo_acordao": (str(getattr(head, "resultado_tipo", "") or "")).strip() or None,
            # DataSessao chega como datetime à meia-noite — só a data interessa.
            "data_sessao": (
                ds.date() if isinstance(ds := getattr(head, "data_sessao", None), datetime) else ds
            ),
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


# ----- decision loading -----------------------------------------------------


def _load_decisao(session: Session, id: int) -> NERDecisaoORM:
    row = session.get(NERDecisaoORM, id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="decisao not found")
    return row


def _ner_children(session: Session, id_ner_decisao: int) -> dict[str, list]:
    out: dict[str, list] = {}
    for tipo in TIPOS:
        orm = _NER_ORM[tipo]
        rows = (
            session.execute(
                select(orm).where(orm.IdNerDecisao == id_ner_decisao).order_by(orm.Ordem.asc())
            )
            .scalars()
            .all()
        )
        out[tipo] = list(rows)
    return out


def _staging_by_ner(session: Session, tipo: str, ner_ids: list[int]) -> dict[int, Any]:
    """Staging audit rows keyed by NER id (new decision-level flow)."""
    if not ner_ids:
        return {}
    fk = _STAGING_NER_FK[tipo]
    rows = session.execute(select(_STAGING_ORM[tipo]).where(fk.in_(ner_ids))).scalars().all()
    return {getattr(row, fk.key): row for row in rows}


def _final_and_legacy_staging(
    session: Session, tipo: str, ner_ids: list[int]
) -> tuple[dict[int, Any], dict[int, Any]]:
    """For obrigação/recomendação: resolve stage-2 final rows via the
    ``Processed*`` bridges, plus legacy staging rows keyed by the final-row FK
    (written by the old per-entity flow, which didn't fill ``IdNer*``).
    Returns ``({id_ner: final_row}, {id_ner: staging_row})``.
    """
    if not ner_ids or tipo not in ("obrigacao", "recomendacao"):
        return {}, {}
    if tipo == "obrigacao":
        stmt = (
            select(ProcessedObrigacaoORM.IdNerObrigacao, ObrigacaoORM, ObrigacaoStagingORM)
            .join(
                ObrigacaoORM,
                ObrigacaoORM.IdObrigacao == ProcessedObrigacaoORM.IdObrigacao,
            )
            .outerjoin(
                ObrigacaoStagingORM,
                ObrigacaoStagingORM.IdObrigacao == ObrigacaoORM.IdObrigacao,
            )
            .where(ProcessedObrigacaoORM.IdNerObrigacao.in_(ner_ids))
        )
    else:
        stmt = (
            select(
                ProcessedRecomendacaoORM.IdNerRecomendacao,
                RecomendacaoORM,
                RecomendacaoStagingORM,
            )
            .join(
                RecomendacaoORM,
                RecomendacaoORM.IdRecomendacao == ProcessedRecomendacaoORM.IdRecomendacao,
            )
            .outerjoin(
                RecomendacaoStagingORM,
                RecomendacaoStagingORM.IdRecomendacao == RecomendacaoORM.IdRecomendacao,
            )
            .where(ProcessedRecomendacaoORM.IdNerRecomendacao.in_(ner_ids))
        )
    finals: dict[int, Any] = {}
    legacy: dict[int, Any] = {}
    for id_ner, final_row, staging_row in session.execute(stmt).all():
        finals[id_ner] = final_row
        if staging_row is not None:
            legacy[id_ner] = staging_row
    return finals, legacy


def _default_campos(tipo: str, descricao: str) -> dict[str, Any]:
    if tipo == "multa":
        return {
            "descricao_multa": descricao,
            "valor_fixo": None,
            "percentual": None,
            "base_calculo": None,
            "nome_responsavel": None,
            "documento_responsavel": None,
            "e_multa_solidaria": False,
            "solidarios": None,
        }
    if tipo == "ressarcimento":
        return {
            "descricao_ressarcimento": descricao,
            "valor_dano": None,
            "percentual_imputado": None,
            "valor_imputado": None,
            "nome_responsavel": None,
            "documento_responsavel": None,
        }
    if tipo == "obrigacao":
        return {
            "descricao_obrigacao": descricao,
            "de_fazer": True,
            "prazo": None,
            "data_cumprimento": None,
            "orgao_responsavel": None,
            "id_orgao_responsavel": None,
            "tem_multa_cominatoria": False,
            "nome_responsavel_multa_cominatoria": None,
            "documento_responsavel_multa_cominatoria": None,
            "id_pessoa_multa_cominatoria": None,
            "valor_multa_cominatoria": None,
            "periodo_multa_cominatoria": None,
            "e_multa_cominatoria_solidaria": False,
            "solidarios_multa_cominatoria": None,
        }
    return {
        "descricao_recomendacao": descricao,
        "prazo_cumprimento_recomendacao": None,
        "data_cumprimento_recomendacao": None,
        "nome_responsavel": None,
        "id_pessoa_responsavel": None,
        "orgao_responsavel": None,
        "id_orgao_responsavel": None,
        "cancelado": None,
    }


def _obrigacao_campos_from_row(row) -> dict[str, Any]:
    """Fields dict from either the final ``Obrigacao`` row or a staging row —
    both share the column names."""
    return {
        "descricao_obrigacao": row.DescricaoObrigacao,
        "de_fazer": row.DeFazer,
        "prazo": row.Prazo,
        "data_cumprimento": row.DataCumprimento,
        "orgao_responsavel": row.OrgaoResponsavel,
        "id_orgao_responsavel": row.IdOrgaoResponsavel,
        "tem_multa_cominatoria": row.TemMultaCominatoria,
        "nome_responsavel_multa_cominatoria": row.NomeResponsavelMultaCominatoria,
        "documento_responsavel_multa_cominatoria": row.DocumentoResponsavelMultaCominatoria,
        "id_pessoa_multa_cominatoria": row.IdPessoaMultaCominatoria,
        "valor_multa_cominatoria": row.ValorMultaCominatoria,
        "periodo_multa_cominatoria": row.PeriodoMultaCominatoria,
        "e_multa_cominatoria_solidaria": row.EMultaCominatoriaSolidaria,
        "solidarios_multa_cominatoria": _coerce_solidarios(row.SolidariosMultaCominatoria),
    }


def _recomendacao_campos_from_row(row) -> dict[str, Any]:
    return {
        "descricao_recomendacao": row.DescricaoRecomendacao,
        "prazo_cumprimento_recomendacao": row.PrazoCumprimentoRecomendacao,
        "data_cumprimento_recomendacao": row.DataCumprimentoRecomendacao,
        "nome_responsavel": row.NomeResponsavel,
        "id_pessoa_responsavel": row.IdPessoaResponsavel,
        "orgao_responsavel": row.OrgaoResponsavel,
        "id_orgao_responsavel": row.IdOrgaoResponsavel,
        "cancelado": row.Cancelado,
    }


def _multa_campos_from_staging(row) -> dict[str, Any]:
    return {
        "descricao_multa": row.DescricaoMulta,
        "valor_fixo": row.ValorFixo,
        "percentual": row.Percentual,
        "base_calculo": row.BaseCalculo,
        "nome_responsavel": row.NomeResponsavel,
        "documento_responsavel": row.DocumentoResponsavel,
        "e_multa_solidaria": row.EMultaSolidaria,
        "solidarios": _coerce_solidarios(row.Solidarios),
    }


def _ressarcimento_campos_from_staging(row) -> dict[str, Any]:
    return {
        "descricao_ressarcimento": row.DescricaoRessarcimento,
        "valor_dano": row.ValorDano,
        "percentual_imputado": row.PercentualImputado,
        "valor_imputado": row.ValorImputado,
        "nome_responsavel": row.NomeResponsavel,
        "documento_responsavel": row.DocumentoResponsavel,
    }


def _status_str(raw) -> str:
    return raw.value if isinstance(raw, ReviewStatus) else str(raw)


def _to_entidade_out(tipo: str, ner_row, staging_row, final_row) -> schemas.EntidadeOut:
    descricao = getattr(ner_row, _NER_DESCRICAO_ATTR[tipo]) or ""

    if staging_row is not None:
        status_value = _status_str(staging_row.Status)
        reviewer = staging_row.Revisor
        reviewed_at = staging_row.DataRevisao
        observacoes = staging_row.ObservacoesRevisao
        if tipo == "obrigacao":
            campos = _obrigacao_campos_from_row(staging_row)
        elif tipo == "recomendacao":
            campos = _recomendacao_campos_from_row(staging_row)
        elif tipo == "multa":
            campos = _multa_campos_from_staging(staging_row)
        else:
            campos = _ressarcimento_campos_from_staging(staging_row)
    else:
        status_value = ReviewStatus.pending.value
        reviewer = None
        reviewed_at = None
        observacoes = None
        if tipo == "obrigacao" and final_row is not None:
            campos = _obrigacao_campos_from_row(final_row)
        elif tipo == "recomendacao" and final_row is not None:
            campos = _recomendacao_campos_from_row(final_row)
        else:
            campos = _default_campos(tipo, descricao)

    return schemas.EntidadeOut(
        tipo=tipo,  # type: ignore[arg-type]
        id_ner=_ner_id(ner_row),
        descricao=descricao,
        status=status_value,  # type: ignore[arg-type]
        campos=campos,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        observacoes=observacoes,
    )


def _gather_entidades(
    session: Session, decisao: NERDecisaoORM
) -> dict[str, list[tuple[Any, Any, Any]]]:
    """Per tipo, list of ``(ner_row, staging_row_or_None, final_row_or_None)``.

    Staging is matched first by ``IdNer*`` (decision-level flow) and, for
    obrigação/recomendação, falls back to the legacy per-entity rows keyed by
    the final-table FK.
    """
    children = _ner_children(session, decisao.IdNerDecisao)
    out: dict[str, list[tuple[Any, Any, Any]]] = {}
    for tipo in TIPOS:
        rows = children[tipo]
        ner_ids = [_ner_id(r) for r in rows]
        staged = _staging_by_ner(session, tipo, ner_ids)
        finals, legacy = _final_and_legacy_staging(session, tipo, ner_ids)
        out[tipo] = [
            (
                ner_row,
                staged.get(id_ner) or legacy.get(id_ner),
                finals.get(id_ner),
            )
            for ner_row, id_ner in zip(rows, ner_ids)
        ]
    return out


# ----- list / detail / texto -------------------------------------------------


def _load_acordao_por_decisao(
    triples: list[tuple[int, int, int]],
) -> dict[tuple[int, int, int], tuple[Optional[str], Optional[str], Optional[str]]]:
    """Batch-resolve o número do acórdão/decisão de cada triple via
    ``vw_ia_votos_acordaos_decisoes`` → ``(numeroResultado, anoResultado,
    resultadoTipo)``. Colunas char no MSSQL vêm com padding — trimmed aqui.
    Retorna ``{}`` em falha para a lista nunca quebrar por causa do MSSQL.
    """
    unique = sorted(set(triples))
    if not unique:
        return {}
    conds = []
    params: dict[str, int] = {}
    for i, (idp, idc, idv) in enumerate(unique):
        conds.append(
            f"(d.IdProcesso = :p{i} AND d.IdComposicaoPauta = :c{i} AND d.idVotoPauta = :v{i})"
        )
        params.update({f"p{i}": idp, f"c{i}": idc, f"v{i}": idv})
    sql = (
        "SELECT d.IdProcesso AS idp, d.IdComposicaoPauta AS idc, d.idVotoPauta AS idv, "
        "d.numeroResultado AS numero, d.anoResultado AS ano, d.resultadoTipo AS tipo "
        "FROM processo.dbo.vw_ia_votos_acordaos_decisoes d "
        f"WHERE {' OR '.join(conds)}"
    )
    try:
        with get_connection(DB_PROCESSOS).connect() as conn:
            rows = conn.execute(text(sql), params).all()
        out: dict[tuple[int, int, int], tuple[Optional[str], Optional[str], Optional[str]]] = {}
        for row in rows:
            key = (int(row.idp), int(row.idc), int(row.idv))
            out[key] = (
                (str(row.numero or "")).strip() or None,
                (str(row.ano or "")).strip() or None,
                (str(row.tipo or "")).strip() or None,
            )
        return out
    except Exception:
        logger.exception("failed to resolve acordao for %d decisoes", len(unique))
        return {}


def list_decisoes(
    session: Session,
    *,
    page: int,
    page_size: int,
    current_user: UserORM,
    processo: Optional[str] = None,
    lista_completa: bool = False,
    reserva: str = "pendentes",
) -> schemas.DecisaoListPage:
    counts = {
        tipo: (
            select(func.count())
            .where(_NER_ORM[tipo].IdNerDecisao == NERDecisaoORM.IdNerDecisao)
            .correlate(NERDecisaoORM)
            .scalar_subquery()
        )
        for tipo in TIPOS
    }

    # Multas e ressarcimentos são tratados em outra interface: a fila padrão só
    # traz decisões com obrigação ou recomendação; `lista_completa` reabre tudo.
    na_fila = (
        counts["multa"] + counts["obrigacao"] + counts["recomendacao"] + counts["ressarcimento"]
        if lista_completa
        else counts["obrigacao"] + counts["recomendacao"]
    )

    stmt = (
        select(
            NERDecisaoORM,
            counts["multa"].label("multas"),
            counts["obrigacao"].label("obrigacoes"),
            counts["recomendacao"].label("recomendacoes"),
            counts["ressarcimento"].label("ressarcimentos"),
        )
        .where(NERDecisaoORM.RevisadoPor.is_(None))
        .where(na_fila > 0)
    )

    # `lista_completa` é a visão de auditoria: mostra tudo, inclusive reservadas.
    if not lista_completa:
        if reserva == "minhas":
            stmt = stmt.where(NERDecisaoORM.ReservadoPor == current_user.NomeUsuario)
        else:
            stmt = stmt.where(NERDecisaoORM.ReservadoPor.is_(None))

    if processo and processo.strip():
        stmt = stmt.where(NERDecisaoORM.IdProcesso.in_(_resolve_processo_ids(processo)))

    total = session.execute(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    ).scalar_one()

    rows = session.execute(
        stmt.order_by(NERDecisaoORM.IdNerDecisao.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    numero_ano_by_id = _load_processo_numero_ano([row[0].IdProcesso for row in rows])
    acordao_by_triple = _load_acordao_por_decisao(
        [(row[0].IdProcesso, row[0].IdComposicaoPauta, row[0].IdVotoPauta) for row in rows]
    )

    items = []
    for decisao, multas, obrigacoes, recomendacoes, ressarcimentos in rows:
        numero, ano = numero_ano_by_id.get(decisao.IdProcesso, (None, None))
        numero_acordao, ano_acordao, tipo_acordao = acordao_by_triple.get(
            (decisao.IdProcesso, decisao.IdComposicaoPauta, decisao.IdVotoPauta),
            (None, None, None),
        )
        items.append(
            schemas.DecisaoListItem(
                id=decisao.IdNerDecisao,
                id_processo=decisao.IdProcesso,
                id_composicao_pauta=decisao.IdComposicaoPauta,
                id_voto_pauta=decisao.IdVotoPauta,
                numero_processo=numero,
                ano_processo=ano,
                numero_acordao=numero_acordao,
                ano_acordao=ano_acordao,
                tipo_acordao=tipo_acordao,
                data_extracao=decisao.DataExtracao,
                multas=multas,
                obrigacoes=obrigacoes,
                recomendacoes=recomendacoes,
                ressarcimentos=ressarcimentos,
                claimed_by=decisao.ReservadoPor,
                claimed_at=decisao.DataReserva,
            )
        )

    return schemas.DecisaoListPage(items=items, page=page, page_size=page_size, total=total)


def get_decisao(session: Session, *, id: int, current_user: UserORM) -> schemas.DecisaoDetail:
    decisao = _load_decisao(session, id)
    gathered = _gather_entidades(session, decisao)
    entidades = [
        _to_entidade_out(tipo, ner_row, staging_row, final_row)
        for tipo in TIPOS
        for ner_row, staging_row, final_row in gathered[tipo]
    ]
    return schemas.DecisaoDetail(
        id=decisao.IdNerDecisao,
        id_processo=decisao.IdProcesso,
        id_composicao_pauta=decisao.IdComposicaoPauta,
        id_voto_pauta=decisao.IdVotoPauta,
        data_extracao=decisao.DataExtracao,
        claimed_by=decisao.ReservadoPor,
        claimed_at=decisao.DataReserva,
        revisado_por=decisao.RevisadoPor,
        data_revisao=decisao.DataRevisao,
        entidades=entidades,
    )


def get_decisao_texto(session: Session, *, id: int, current_user: UserORM) -> schemas.DecisaoTexto:
    """Fetch ``texto_acordao`` and per-entity span offsets for one decision."""
    decisao = _load_decisao(session, id)
    ctx = _load_decisao_context(decisao.IdProcesso, decisao.IdComposicaoPauta, decisao.IdVotoPauta)
    texto_acordao = ctx["texto_acordao"] or ""

    spans: list[schemas.EntidadeSpan] = []
    children = _ner_children(session, decisao.IdNerDecisao)
    for tipo in TIPOS:
        for ner_row in children[tipo]:
            descricao = getattr(ner_row, _NER_DESCRICAO_ATTR[tipo]) or ""
            start, end, match_status = find_span_offsets(descricao, texto_acordao)
            spans.append(
                schemas.EntidadeSpan(
                    id_ner=_ner_id(ner_row),
                    tipo=tipo,  # type: ignore[arg-type]
                    char_start=start,
                    char_end=end,
                    match_status=match_status,
                )
            )

    return schemas.DecisaoTexto(
        texto_acordao=ctx["texto_acordao"],
        numero_processo=ctx["numero_processo"],
        ano_processo=ctx["ano_processo"],
        numero_acordao=ctx.get("numero_acordao"),
        ano_acordao=ctx.get("ano_acordao"),
        tipo_acordao=ctx.get("tipo_acordao"),
        data_sessao=ctx.get("data_sessao"),
        pessoas=ctx.get("pessoas", []),
        relatorio=ctx.get("relatorio"),
        fundamentacao_voto=ctx.get("fundamentacao_voto"),
        conclusao=ctx.get("conclusao"),
        orgao_responsavel=ctx.get("orgao_responsavel"),
        orgao_origem=ctx.get("orgao_origem"),
        interessado=ctx.get("interessado"),
        spans=spans,
    )


# ----- awaiting dispatch ------------------------------------------------------


def list_awaiting_dispatch(
    session: Session,
    *,
    page: int,
    page_size: int,
    current_user: UserORM,
) -> schemas.AwaitingDispatchPage:
    """Approved staging rows of all four types, ordered by review date desc."""
    stmts = {
        "multa": select(
            MultaStagingORM.IdMultaStaging.label("id"),
            MultaStagingORM.IdProcesso.label("id_processo"),
            MultaStagingORM.DescricaoMulta.label("descricao"),
            MultaStagingORM.Revisor.label("reviewer"),
            MultaStagingORM.DataRevisao.label("reviewed_at"),
        ).where(MultaStagingORM.Status == ReviewStatus.approved),
        "obrigacao": select(
            ObrigacaoStagingORM.IdObrigacaoStaging.label("id"),
            ObrigacaoStagingORM.IdProcesso.label("id_processo"),
            ObrigacaoStagingORM.DescricaoObrigacao.label("descricao"),
            ObrigacaoStagingORM.Revisor.label("reviewer"),
            ObrigacaoStagingORM.DataRevisao.label("reviewed_at"),
        ).where(ObrigacaoStagingORM.Status == ReviewStatus.approved),
        "recomendacao": select(
            RecomendacaoStagingORM.IdRecomendacaoStaging.label("id"),
            RecomendacaoStagingORM.IdProcesso.label("id_processo"),
            RecomendacaoStagingORM.DescricaoRecomendacao.label("descricao"),
            RecomendacaoStagingORM.Revisor.label("reviewer"),
            RecomendacaoStagingORM.DataRevisao.label("reviewed_at"),
        ).where(RecomendacaoStagingORM.Status == ReviewStatus.approved),
        "ressarcimento": select(
            RessarcimentoStagingORM.IdRessarcimentoStaging.label("id"),
            RessarcimentoStagingORM.IdProcesso.label("id_processo"),
            RessarcimentoStagingORM.DescricaoRessarcimento.label("descricao"),
            RessarcimentoStagingORM.Revisor.label("reviewer"),
            RessarcimentoStagingORM.DataRevisao.label("reviewed_at"),
        ).where(RessarcimentoStagingORM.Status == ReviewStatus.approved),
    }

    combined = [
        (tipo, row)
        for tipo, stmt in stmts.items()
        for row in session.execute(stmt).mappings().all()
    ]
    # Sort by reviewed_at desc, treating None as oldest.
    combined.sort(
        key=lambda pair: pair[1]["reviewed_at"] or datetime.min,
        reverse=True,
    )

    total = len(combined)
    start = (page - 1) * page_size
    page_rows = combined[start : start + page_size]

    numero_ano_by_id = _load_processo_numero_ano([row["id_processo"] for _, row in page_rows])

    items = [
        schemas.AwaitingDispatchItem(
            id=row["id"],
            tipo=tipo,  # type: ignore[arg-type]
            id_processo=row["id_processo"],
            numero_processo=numero_ano_by_id.get(row["id_processo"], (None, None))[0],
            ano_processo=numero_ano_by_id.get(row["id_processo"], (None, None))[1],
            descricao=row["descricao"] or "",
            reviewer=row["reviewer"],
            reviewed_at=row["reviewed_at"],
        )
        for tipo, row in page_rows
    ]

    return schemas.AwaitingDispatchPage(items=items, page=page, page_size=page_size, total=total)


# ----- claim / release --------------------------------------------------------


def _holds_claim(decisao: NERDecisaoORM, user: UserORM) -> bool:
    return decisao.ReservadoPor == user.NomeUsuario


def claim(session: Session, *, id: int, current_user: UserORM) -> schemas.ClaimResponse:
    """Reserva a decisão para o usuário — sempre vence, inclusive por cima da
    reserva de outro (poucos usuários, sem lock)."""
    now = datetime.utcnow()
    me = current_user.NomeUsuario

    decisao = _load_decisao(session, id)
    if decisao.RevisadoPor is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="decisao already reviewed",
        )

    session.execute(
        update(NERDecisaoORM)
        .where(NERDecisaoORM.IdNerDecisao == id)
        .values(ReservadoPor=me, DataReserva=now)
        .execution_options(synchronize_session=False)
    )
    session.commit()
    return schemas.ClaimResponse(claimed_by=me, claimed_at=now)


def claim_lote(
    session: Session, *, quantidade: int, current_user: UserORM
) -> schemas.ClaimLoteResponse:
    """Reserva as N decisões livres mais antigas da fila padrão. Diferente do
    ``claim`` individual, não toma a reserva de outro usuário."""
    now = datetime.utcnow()
    me = current_user.NomeUsuario

    na_fila = sum(
        select(func.count())
        .where(_NER_ORM[tipo].IdNerDecisao == NERDecisaoORM.IdNerDecisao)
        .correlate(NERDecisaoORM)
        .scalar_subquery()
        for tipo in ("obrigacao", "recomendacao")
    )
    ids = list(
        session.scalars(
            select(NERDecisaoORM.IdNerDecisao)
            .where(
                NERDecisaoORM.RevisadoPor.is_(None),
                NERDecisaoORM.ReservadoPor.is_(None),
                na_fila > 0,
            )
            .order_by(NERDecisaoORM.IdNerDecisao.asc())
            .limit(quantidade)
        )
    )
    if not ids:
        return schemas.ClaimLoteResponse(ids=[], quantidade=0)

    # O WHERE repetido fecha a corrida entre dois usuários reservando ao mesmo
    # tempo: quem chegar depois simplesmente reserva menos do que pediu.
    session.execute(
        update(NERDecisaoORM)
        .where(
            NERDecisaoORM.IdNerDecisao.in_(ids),
            NERDecisaoORM.ReservadoPor.is_(None),
            NERDecisaoORM.RevisadoPor.is_(None),
        )
        .values(ReservadoPor=me, DataReserva=now)
        .execution_options(synchronize_session=False)
    )
    session.commit()

    reservadas = list(
        session.scalars(
            select(NERDecisaoORM.IdNerDecisao)
            .where(NERDecisaoORM.IdNerDecisao.in_(ids), NERDecisaoORM.ReservadoPor == me)
            .order_by(NERDecisaoORM.IdNerDecisao.asc())
        )
    )
    return schemas.ClaimLoteResponse(ids=reservadas, quantidade=len(reservadas))


def release(session: Session, *, id: int, current_user: UserORM) -> None:
    """Idempotent: release the claim if it's held by the caller."""
    me = current_user.NomeUsuario
    stmt = (
        update(NERDecisaoORM)
        .where(NERDecisaoORM.IdNerDecisao == id, NERDecisaoORM.ReservadoPor == me)
        .values(ReservadoPor=None, DataReserva=None)
        .execution_options(synchronize_session=False)
    )
    session.execute(stmt)
    session.commit()


# ----- approve ------------------------------------------------------------------


def _build_staging_row(
    entidade: schemas.EntidadeReview,
    decisao: NERDecisaoORM,
    *,
    descricao_original: str,
    final_id: Optional[int],
    revisor: str,
    now: datetime,
):
    """Build the audit ORM row for one payload entity. Rejections copy the
    original NER description; approvals carry the reviewer-edited fields."""
    tipo = entidade.tipo
    approved = entidade.resultado == "approved"
    campos = entidade.campos
    base = dict(
        IdProcesso=decisao.IdProcesso,
        IdComposicaoPauta=decisao.IdComposicaoPauta,
        IdVotoPauta=decisao.IdVotoPauta,
        Status=ReviewStatus.approved if approved else ReviewStatus.rejected,
        Revisor=revisor,
        DataRevisao=now,
        ObservacoesRevisao=entidade.observacoes,
    )

    if tipo == "multa":
        assert campos is None or isinstance(campos, schemas.MultaFields)
        return MultaStagingORM(
            IdNerMulta=entidade.id_ner,
            DescricaoMulta=campos.descricao_multa if approved else descricao_original,
            ValorFixo=campos.valor_fixo if approved else None,
            Percentual=campos.percentual if approved else None,
            BaseCalculo=campos.base_calculo if approved else None,
            NomeResponsavel=campos.nome_responsavel if approved else None,
            DocumentoResponsavel=campos.documento_responsavel if approved else None,
            EMultaSolidaria=campos.e_multa_solidaria if approved else None,
            Solidarios=(
                [s.model_dump() for s in campos.solidarios]
                if approved and campos.solidarios
                else None
            ),
            **base,
        )
    if tipo == "ressarcimento":
        assert campos is None or isinstance(campos, schemas.RessarcimentoFields)
        return RessarcimentoStagingORM(
            IdNerRessarcimento=entidade.id_ner,
            DescricaoRessarcimento=(
                campos.descricao_ressarcimento if approved else descricao_original
            ),
            ValorDano=campos.valor_dano if approved else None,
            PercentualImputado=campos.percentual_imputado if approved else None,
            ValorImputado=campos.valor_imputado if approved else None,
            NomeResponsavel=campos.nome_responsavel if approved else None,
            DocumentoResponsavel=campos.documento_responsavel if approved else None,
            **base,
        )
    if tipo == "obrigacao":
        assert campos is None or isinstance(campos, schemas.ObrigacaoFields)
        return ObrigacaoStagingORM(
            IdNerObrigacao=entidade.id_ner,
            IdObrigacao=final_id,
            DescricaoObrigacao=(campos.descricao_obrigacao if approved else descricao_original),
            DeFazer=campos.de_fazer if approved else None,
            Prazo=campos.prazo if approved else None,
            DataCumprimento=campos.data_cumprimento if approved else None,
            OrgaoResponsavel=campos.orgao_responsavel if approved else None,
            IdOrgaoResponsavel=campos.id_orgao_responsavel if approved else None,
            TemMultaCominatoria=campos.tem_multa_cominatoria if approved else None,
            NomeResponsavelMultaCominatoria=(
                campos.nome_responsavel_multa_cominatoria if approved else None
            ),
            DocumentoResponsavelMultaCominatoria=(
                campos.documento_responsavel_multa_cominatoria if approved else None
            ),
            IdPessoaMultaCominatoria=(campos.id_pessoa_multa_cominatoria if approved else None),
            ValorMultaCominatoria=campos.valor_multa_cominatoria if approved else None,
            PeriodoMultaCominatoria=(campos.periodo_multa_cominatoria if approved else None),
            EMultaCominatoriaSolidaria=(campos.e_multa_cominatoria_solidaria if approved else None),
            SolidariosMultaCominatoria=(
                [s.model_dump() for s in campos.solidarios_multa_cominatoria]
                if approved and campos.solidarios_multa_cominatoria
                else None
            ),
            **base,
        )
    assert campos is None or isinstance(campos, schemas.RecomendacaoFields)
    return RecomendacaoStagingORM(
        IdNerRecomendacao=entidade.id_ner,
        IdRecomendacao=final_id,
        DescricaoRecomendacao=(campos.descricao_recomendacao if approved else descricao_original),
        PrazoCumprimentoRecomendacao=(campos.prazo_cumprimento_recomendacao if approved else None),
        DataCumprimentoRecomendacao=(campos.data_cumprimento_recomendacao if approved else None),
        NomeResponsavel=campos.nome_responsavel if approved else None,
        IdPessoaResponsavel=campos.id_pessoa_responsavel if approved else None,
        OrgaoResponsavel=campos.orgao_responsavel if approved else None,
        IdOrgaoResponsavel=campos.id_orgao_responsavel if approved else None,
        Cancelado=campos.cancelado if approved else None,
        **base,
    )


def _proxima_decisao(session: Session, *, excluir: int, current_user: UserORM) -> Optional[int]:
    """Próxima decisão da fila padrão (obrigação/recomendação) — primeiro a
    reserva do próprio usuário, depois as livres; reserva de outro fica fora."""
    total_entidades = sum(
        select(func.count())
        .where(_NER_ORM[tipo].IdNerDecisao == NERDecisaoORM.IdNerDecisao)
        .correlate(NERDecisaoORM)
        .scalar_subquery()
        for tipo in ("obrigacao", "recomendacao")
    )

    def _next(cond: Any) -> Optional[int]:
        return session.scalar(
            select(NERDecisaoORM.IdNerDecisao)
            .where(
                NERDecisaoORM.IdNerDecisao != excluir,
                NERDecisaoORM.RevisadoPor.is_(None),
                total_entidades > 0,
                cond,
            )
            .order_by(NERDecisaoORM.IdNerDecisao.asc())
            .limit(1)
        )

    minha = _next(NERDecisaoORM.ReservadoPor == current_user.NomeUsuario)
    return minha if minha is not None else _next(NERDecisaoORM.ReservadoPor.is_(None))


def approve_decisao(
    session: Session,
    *,
    id: int,
    payload: schemas.DecisaoReviewPayload,
    current_user: UserORM,
) -> schemas.DecisaoDetail:
    decisao = _load_decisao(session, id)

    if not _holds_claim(decisao, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no active claim by caller",
        )
    if decisao.RevisadoPor is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="decisao already reviewed",
        )

    gathered = _gather_entidades(session, decisao)
    # Open = NER children without a staging audit row yet. Entities reviewed
    # under the legacy per-entity flow stay closed and out of the payload.
    open_by_tipo: dict[str, dict[int, tuple[Any, Any]]] = {
        tipo: {
            _ner_id(ner_row): (ner_row, final_row)
            for ner_row, staging_row, final_row in gathered[tipo]
            if staging_row is None
        }
        for tipo in TIPOS
    }

    seen: set[tuple[str, int]] = set()
    for entidade in payload.entidades:
        if entidade.id_ner is None:
            continue
        key = (entidade.tipo, entidade.id_ner)
        if key in seen:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"entidade duplicada no payload: {key}",
            )
        seen.add(key)
        if entidade.id_ner not in open_by_tipo[entidade.tipo]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(f"entidade desconhecida ou já revisada: {key} — recarregue a página"),
            )

    missing = [
        (tipo, id_ner)
        for tipo in TIPOS
        for id_ner in open_by_tipo[tipo]
        if (tipo, id_ner) not in seen
    ]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"entidades ausentes do payload: {missing} — recarregue a página",
        )

    try:
        now = datetime.utcnow()
        for entidade in payload.entidades:
            if entidade.id_ner is not None:
                ner_row, final_row = open_by_tipo[entidade.tipo][entidade.id_ner]
                descricao_original = getattr(ner_row, _NER_DESCRICAO_ATTR[entidade.tipo]) or ""
                final_id = (
                    (
                        final_row.IdObrigacao
                        if entidade.tipo == "obrigacao"
                        else final_row.IdRecomendacao
                    )
                    if final_row is not None and entidade.tipo in ("obrigacao", "recomendacao")
                    else None
                )
            else:
                descricao_original = ""
                final_id = None
            session.add(
                _build_staging_row(
                    entidade,
                    decisao,
                    descricao_original=descricao_original,
                    final_id=final_id,
                    revisor=current_user.NomeUsuario,
                    now=now,
                )
            )

        decisao.RevisadoPor = current_user.NomeUsuario
        decisao.DataRevisao = now
        decisao.ReservadoPor = None
        decisao.DataReserva = None
        session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        session.rollback()
        logger.exception("approve transaction failed for decisao %s", id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="approve transaction failed",
        ) from exc

    session.refresh(decisao)
    detail = get_decisao(session, id=id, current_user=current_user)
    detail.proximo_id = _proxima_decisao(session, excluir=id, current_user=current_user)
    return detail
