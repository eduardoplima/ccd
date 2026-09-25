"""Obrigações aprovadas com multa cominatória prevista mas não cadastrada.

Cruza o staging do CGAD (``TemMultaCominatoria``) com ``processo.dbo.Exe_Debito``
(``CodigoTipoDebito = 5``) pelo ``IdProcessoOrigem``. A ligação é por processo,
não por obrigação: se o processo tem algum débito tipo 5, todas as suas
obrigações saem da lista.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.cgad.multas_nao_cominadas import schemas
from app.cgad.review.service import _load_processo_numero_ano
from cgad.etl.staging import ObrigacaoStagingORM, ReviewStatus
from cgad.models import NERDecisaoORM
from cgad.utils import DB_PROCESSOS, get_connection

_ATIVOS = (ReviewStatus.approved, ReviewStatus.dispatched)
TIPO_MULTA_COMINATORIA = 5  # Exe_Debito.CodigoTipoDebito


def _carregar(session: Session) -> list[dict[str, Any]]:
    o = ObrigacaoStagingORM
    rows = session.execute(
        select(
            o.IdObrigacaoStaging,
            o.IdProcesso,
            o.IdComposicaoPauta,
            o.IdVotoPauta,
            o.DescricaoObrigacao,
            o.Prazo,
            o.DataCumprimento,
            o.OrgaoResponsavel,
            o.NomeResponsavelMultaCominatoria,
            o.DocumentoResponsavelMultaCominatoria,
            o.ValorMultaCominatoria,
            o.PeriodoMultaCominatoria,
            o.Status,
            o.Revisor,
            o.DataRevisao,
        ).where(o.Status.in_(_ATIVOS), o.TemMultaCominatoria == True)  # noqa: E712 — `.is_(True)` vira `IS 1`, inválido no MSSQL
    ).all()
    return [
        dict(
            id=r[0],
            id_processo=r[1],
            tripla=(r[1], r[2], r[3]),
            descricao=r[4] or "",
            prazo=r[5],
            data_cumprimento=r[6],
            orgao=r[7],
            responsavel=r[8],
            documento=r[9],
            valor_dia=r[10],
            periodo=r[11],
            status=r[12].value if isinstance(r[12], ReviewStatus) else str(r[12]),
            revisor=r[13],
            data_revisao=r[14],
        )
        for r in rows
    ]


def _processos_com_multa_cadastrada(id_processos: list[int]) -> set[int]:
    """``IdProcesso`` (origem) com algum débito tipo 5 em ``Exe_Debito``.
    Levanta em falha: devolver vazio faria a lista mentir "nada cadastrado"."""
    unique = sorted({int(i) for i in id_processos})
    out: set[int] = set()
    if not unique:
        return out
    with get_connection(DB_PROCESSOS).connect() as conn:
        for i in range(0, len(unique), 1000):
            placeholders = ", ".join(str(x) for x in unique[i : i + 1000])
            rows = conn.execute(
                text(
                    "SELECT DISTINCT IdProcessoOrigem FROM dbo.Exe_Debito "
                    f"WHERE CodigoTipoDebito = {TIPO_MULTA_COMINATORIA} "
                    f"AND IdProcessoOrigem IN ({placeholders})"
                )
            ).all()
            out.update(int(r[0]) for r in rows)
    return out


def listar(session: Session) -> schemas.MultasNaoCominadas:
    linhas = _carregar(session)
    cadastradas = _processos_com_multa_cadastrada([ln["id_processo"] for ln in linhas])
    linhas = [ln for ln in linhas if ln["id_processo"] not in cadastradas]

    ids = sorted({ln["id_processo"] for ln in linhas})
    numero_ano = _load_processo_numero_ano(ids)
    decisao_por_tripla = {
        (d.IdProcesso, d.IdComposicaoPauta, d.IdVotoPauta): d.IdNerDecisao
        for d in session.execute(
            select(NERDecisaoORM).where(NERDecisaoORM.IdProcesso.in_(ids or [-1]))
        ).scalars()
    }
    for ln in linhas:
        ln["numero_processo"], ln["ano_processo"] = numero_ano.get(ln["id_processo"], (None, None))
        ln["id_decisao"] = decisao_por_tripla.get(ln["tripla"])
    linhas.sort(key=lambda ln: ln["data_revisao"] or datetime.min, reverse=True)

    campos = schemas.MultaNaoCominada.model_fields
    return schemas.MultasNaoCominadas(
        total_obrigacoes=len(linhas),
        total_processos=len(ids),
        items=[
            schemas.MultaNaoCominada(**{k: v for k, v in ln.items() if k in campos})
            for ln in linhas
        ],
    )
