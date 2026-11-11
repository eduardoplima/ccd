"""Remoção lógica de obrigações/recomendações curadas do CGAD.

Um acórdão posterior (desconstituição, rescisão…) tira itens do acervo: a linha
de staging vai a ``Status='removed'`` com o acórdão, a justificativa, quem e
quando. Nada é apagado; painéis, "aguardando envio" e ``vwCCDDeterminacao``
filtram ``approved``/``dispatched`` e deixam de ver o item sozinhos.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.cgad.remocoes import schemas
from cgad.etl.staging import ObrigacaoStagingORM, RecomendacaoStagingORM, ReviewStatus
from cgad.utils import DB_PROCESSOS, get_connection

_ATIVOS = (ReviewStatus.approved, ReviewStatus.dispatched)
_VISIVEIS = (*_ATIVOS, ReviewStatus.removed)
_ORM: dict[str, Any] = {"obrigacao": ObrigacaoStagingORM, "recomendacao": RecomendacaoStagingORM}


class RemocaoInvalida(Exception):
    pass


def _id_processo(numero: int, ano: int) -> int | None:
    with get_connection(DB_PROCESSOS).connect() as conn:
        return conn.execute(
            text(
                "SELECT IdProcesso FROM processo.dbo.Processos "
                "WHERE numero_processo = :n AND ano_processo = :a"
            ),
            {"n": f"{numero:06d}", "a": ano},
        ).scalar()


def _acordaos_do_processo(id_processo: int) -> list[dict[str, Any]]:
    # a view repete a decisão por voto/pessoa: agrupa por composição
    with get_connection(DB_PROCESSOS).connect() as conn:
        rows = conn.execute(
            text(
                "SELECT d.IdComposicaoPauta AS idc, MAX(d.numeroResultado) AS numero, "
                "MAX(d.anoResultado) AS ano, MAX(d.resultadoTipo) AS tipo, "
                "MAX(d.DataSessao) AS data_sessao "
                "FROM processo.dbo.vw_ia_votos_acordaos_decisoes d "
                "WHERE d.IdProcesso = :p GROUP BY d.IdComposicaoPauta "
                "ORDER BY MAX(d.DataSessao)"
            ),
            {"p": id_processo},
        ).all()
    return [
        dict(
            id_composicao_pauta=int(r.idc),
            numero=str(r.numero or "").strip() or None,
            ano=str(r.ano or "").strip() or None,
            tipo=str(r.tipo or "").strip() or None,
            data_sessao=r.data_sessao.date()
            if isinstance(r.data_sessao, datetime)
            else r.data_sessao,
        )
        for r in rows
    ]


def _status(v: Any) -> str:
    return v.value if isinstance(v, ReviewStatus) else str(v)


def _item(tipo: str, x: Any, id_: int, descricao: str | None) -> schemas.ItemCurado:
    return schemas.ItemCurado(
        tipo=tipo,  # type: ignore[arg-type]
        id=id_,
        id_composicao_pauta=x.IdComposicaoPauta,
        descricao=descricao or "",
        orgao=x.OrgaoResponsavel,
        status=_status(x.Status),  # type: ignore[arg-type]
        id_composicao_pauta_remocao=x.IdComposicaoPautaRemocao,
        justificativa_remocao=x.JustificativaRemocao,
        removido_por=x.RemovidoPor,
        data_remocao=x.DataRemocao,
    )


def _itens(session: Session, id_processo: int) -> list[schemas.ItemCurado]:
    o, r = ObrigacaoStagingORM, RecomendacaoStagingORM
    # .all(): sem MARS o MSSQL não aceita dois cursores abertos na mesma conexão
    obrigacoes = session.scalars(
        select(o).where(o.IdProcesso == id_processo, o.Status.in_(_VISIVEIS))
    ).all()
    recomendacoes = session.scalars(
        select(r).where(r.IdProcesso == id_processo, r.Status.in_(_VISIVEIS))
    ).all()
    return [
        _item("obrigacao", x, x.IdObrigacaoStaging, x.DescricaoObrigacao) for x in obrigacoes
    ] + [
        _item("recomendacao", x, x.IdRecomendacaoStaging, x.DescricaoRecomendacao)
        for x in recomendacoes
    ]


def consultar(session: Session, numero: int, ano: int) -> schemas.Consulta | None:
    id_processo = _id_processo(numero, ano)
    if id_processo is None:
        return None
    return schemas.Consulta(
        id_processo=id_processo,
        processo=f"{numero:06d}/{ano}",
        acordaos=[schemas.Acordao(**a) for a in _acordaos_do_processo(id_processo)],
        itens=_itens(session, id_processo),
    )


def remover(
    session: Session, payload: schemas.RemocaoPayload, usuario: str
) -> schemas.RemocaoResultado:
    justificativa = payload.justificativa.strip()
    if not justificativa:
        raise RemocaoInvalida("justificativa is required")
    acordaos = {a["id_composicao_pauta"] for a in _acordaos_do_processo(payload.id_processo)}
    if payload.id_composicao_pauta_remocao not in acordaos:
        raise RemocaoInvalida("acordao does not belong to the processo")
    agora = datetime.now()
    for ref in payload.itens:
        linha = session.get(_ORM[ref.tipo], ref.id)
        if linha is None or linha.IdProcesso != payload.id_processo:
            raise RemocaoInvalida(f"{ref.tipo} {ref.id} not found in processo")
        if linha.Status not in _ATIVOS:
            raise RemocaoInvalida(f"{ref.tipo} {ref.id} is {_status(linha.Status)}")
        linha.Status = ReviewStatus.removed
        linha.IdComposicaoPautaRemocao = payload.id_composicao_pauta_remocao
        linha.JustificativaRemocao = justificativa
        linha.RemovidoPor = usuario
        linha.DataRemocao = agora
    session.commit()
    return schemas.RemocaoResultado(removidos=len(payload.itens))
