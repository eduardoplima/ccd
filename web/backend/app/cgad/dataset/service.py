"""Conjunto de dados anotado (CGAD) — anotação independente por 3 anotadores.

A unidade de trabalho é ``(DatasetDocumento, anotador)``. Toda leitura e toda
escrita filtram por ``Anotador == current_user.NomeUsuario``: um anotador nunca vê a
anotação de outro, que é o que mantém a reanotação **cega** e torna a
concordância entre anotadores mensurável.

Não há claim/TTL como em ``app.cgad.review`` — aqui a fila é atribuída no seed,
não disputada.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import case, extract, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.cgad.dataset import schemas
from cgad.models import DatasetAnotacaoORM, DatasetDocumentoORM


# Mesma tokenização do corpus (``app.cgad.dataset_corrections.dataset``) — é o
# que faz o export bater byte a byte com o decicontas.json.
_TOKEN_RE = re.compile(r"\S+")

_IOU_MIN = 0.5
_TRECHO = 240

# Triagem: um documento "provavelmente tem entidade" se o eduardo (corpus
# DeciContas.br) OU o deepseek (``cgad.dataset_pretag``) marcaram algo nele.
# União porque os dois erram para lados diferentes — o modelo perdeu 5 dos 232 do
# eduardo, e achou 53 que ele deixou vazios. Os spans em si nunca são devolvidos
# ao anotador: a aba filtra a fila, a anotação segue cega.
_FONTES_ENTIDADE = ("eduardo", "deepseek")

# Códigos de atos de pessoal, apurados em processo.dbo.Tipo. São 46% do conjunto
# (281 só de APO) e a fila fica repetitiva; o filtro esconde da lista sem tirar
# nada do conjunto — a maioria dos que têm entidade traz multa e determinação de
# verdade, então não dá para descartá-los do corpus.
CODIGOS_ATOS_PESSOAL = (
    "APO",
    "APP",
    "ASS",
    "CEM",
    "CTT",
    "CVP",
    "FCO",
    "INC",
    "INM",
    "NCE",
    "NOM",
    "PDR",
    "PEN",
    "PEP",
    "RBN",
)


# ----- helpers ---------------------------------------------------------------


def _parse_spans(raw: Optional[str]) -> list[schemas.Span]:
    if not raw:
        return []
    return [schemas.Span(**s) for s in json.loads(raw)]


def _anotacao(session: Session, *, id_documento: int, anotador: str) -> DatasetAnotacaoORM:
    row = session.scalar(
        select(DatasetAnotacaoORM).where(
            DatasetAnotacaoORM.IdDocumento == id_documento,
            DatasetAnotacaoORM.Anotador == anotador,
        )
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document not assigned to this annotator",
        )
    return row


def _tem_entidades():
    """``EXISTS`` de uma triagem (eduardo ou deepseek) com pelo menos um span."""
    triagem = aliased(DatasetAnotacaoORM)
    return (
        select(1)
        .where(
            triagem.IdDocumento == DatasetDocumentoORM.IdDocumento,
            triagem.Anotador.in_(_FONTES_ENTIDADE),
            triagem.Spans.is_not(None),
            triagem.Spans != "[]",
        )
        .exists()
    )


def _to_bio(text: str, spans: list[schemas.Span]) -> tuple[list[str], list[str], list[list[int]]]:
    """Tokens + BIO + offsets: por span, o primeiro token sobreposto recebe
    ``B-``, os seguintes ``I-`` — mesma regra de
    ``app.cgad.dataset_corrections.dataset``.

    O ``ner_tags`` do decicontas.json diverge disso em 7 dos 861 documentos, onde
    dois spans anotados são adjacentes (ex.: [361,586] e [587,624]): lá o segundo
    span começa com ``I-``, apagando a fronteira. O campo ``entities``, que é a
    anotação de fato, bate nos 861. Mantemos a regra correta.
    """
    matches = list(_TOKEN_RE.finditer(text or ""))
    tokens = [m.group() for m in matches]
    offsets = [[m.start(), m.end()] for m in matches]
    tags = ["O"] * len(tokens)
    for span in sorted(spans, key=lambda s: (s.start, s.end)):
        primeiro = True
        for i, (ini, fim) in enumerate(offsets):
            if ini < span.end and fim > span.start:
                tags[i] = ("B-" if primeiro else "I-") + span.label
                primeiro = False
    return tokens, tags, offsets


# ----- consultas -------------------------------------------------------------


def list_documentos(
    session: Session,
    *,
    anotador: str,
    page: int,
    page_size: int,
    status_filtro: Optional[str] = None,
    origem: Optional[str] = None,
    ano: Optional[int] = None,
    com_entidades: Optional[bool] = None,
    sem_atos_pessoal: Optional[bool] = None,
) -> schemas.DocumentoListPage:
    base = (
        select(DatasetDocumentoORM, DatasetAnotacaoORM)
        .join(
            DatasetAnotacaoORM,
            DatasetAnotacaoORM.IdDocumento == DatasetDocumentoORM.IdDocumento,
        )
        .where(DatasetAnotacaoORM.Anotador == anotador)
    )
    if origem:
        base = base.where(DatasetDocumentoORM.Origem == origem)
    if ano:
        base = base.where(extract("year", DatasetDocumentoORM.DataSessao) == ano)
    if sem_atos_pessoal:
        # 66 documentos estão sem tipo; ficam na lista (not_in com NULL some).
        base = base.where(
            or_(
                DatasetDocumentoORM.CodigoTipoProcesso.is_(None),
                DatasetDocumentoORM.CodigoTipoProcesso.not_in(CODIGOS_ATOS_PESSOAL),
            )
        )

    contagens = dict(
        session.execute(
            base.with_only_columns(DatasetAnotacaoORM.Status, func.count())
            .group_by(DatasetAnotacaoORM.Status)
            .order_by(None)
        ).all()
    )

    # Contagens dos cartões: sempre sobre a fila inteira, não sobre a aba aberta.
    total_com_entidades = (
        session.scalar(select(func.count()).select_from(base.where(_tem_entidades()).subquery()))
        or 0
    )

    filtrada = base
    if status_filtro:
        filtrada = filtrada.where(DatasetAnotacaoORM.Status == status_filtro)
    if com_entidades is not None:
        filtrada = filtrada.where(_tem_entidades() if com_entidades else ~_tem_entidades())

    total = session.scalar(select(func.count()).select_from(filtrada.subquery())) or 0

    linhas = session.execute(
        filtrada.order_by(DatasetDocumentoORM.IdDocumento)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = [
        schemas.DocumentoListItem(
            id=doc.IdDocumento,
            processo=doc.Processo,
            codigo_tipo_processo=doc.CodigoTipoProcesso,
            data_sessao=doc.DataSessao,
            origem=doc.Origem,
            trecho=(doc.Texto or "")[:_TRECHO],
            status=anot.Status,
            total_spans=len(_parse_spans(anot.Spans)),
        )
        for doc, anot in linhas
    ]
    return schemas.DocumentoListPage(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pendentes=contagens.get("pending", 0),
        concluidos=contagens.get("done", 0),
        com_entidades=total_com_entidades,
    )


def get_documento(session: Session, *, id: int, anotador: str) -> schemas.DocumentoDetail:
    anot = _anotacao(session, id_documento=id, anotador=anotador)
    doc = session.get(DatasetDocumentoORM, id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="document not found")

    proximo = session.scalar(
        select(DatasetAnotacaoORM.IdDocumento)
        .where(
            DatasetAnotacaoORM.Anotador == anotador,
            DatasetAnotacaoORM.Status == "pending",
            DatasetAnotacaoORM.IdDocumento != id,
        )
        .order_by(DatasetAnotacaoORM.IdDocumento)
        .limit(1)
    )

    return schemas.DocumentoDetail(
        id=doc.IdDocumento,
        processo=doc.Processo,
        codigo_tipo_processo=doc.CodigoTipoProcesso,
        data_sessao=doc.DataSessao,
        origem=doc.Origem,
        texto=doc.Texto,
        spans=_parse_spans(anot.Spans),
        status=anot.Status,
        data_conclusao=anot.DataConclusao,
        proximo_pendente=proximo,
    )


# ----- escrita ---------------------------------------------------------------


def salvar_anotacao(
    session: Session,
    *,
    id: int,
    payload: schemas.AnotacaoPayload,
    anotador: str,
) -> schemas.DocumentoDetail:
    anot = _anotacao(session, id_documento=id, anotador=anotador)
    doc = session.get(DatasetDocumentoORM, id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="document not found")

    tamanho = len(doc.Texto or "")
    for span in payload.spans:
        if span.end > tamanho:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"span [{span.start},{span.end}) excede o texto ({tamanho} caracteres)",
            )

    agora = datetime.now()
    anot.Spans = json.dumps([s.model_dump() for s in payload.spans], ensure_ascii=False)
    anot.Status = payload.status
    if anot.DataInicio is None:
        anot.DataInicio = agora
    anot.DataConclusao = agora if payload.status == "done" else None
    session.commit()

    return get_documento(session, id=id, anotador=anotador)


# ----- progresso e concordância ----------------------------------------------


def _iou(a: schemas.Span, b: schemas.Span) -> float:
    intersecao = max(0, min(a.end, b.end) - max(a.start, b.start))
    uniao = max(a.end, b.end) - min(a.start, b.start)
    return intersecao / uniao if uniao else 0.0


def _casar(a: list[schemas.Span], b: list[schemas.Span]) -> tuple[int, int, int]:
    """Casamento guloso 1:1 pelo mesmo critério que ``cgad.ner_metrics`` usa no
    corpus (IoU >= 0.5 e mesmo rótulo), reimplementado para não arrastar spacy
    para dentro da API. Devolve ``(acertos, sobras_de_b, sobras_de_a)``."""
    restantes = list(b)
    acertos = 0
    for span_a in a:
        for span_b in restantes:
            if span_a.label == span_b.label and _iou(span_a, span_b) >= _IOU_MIN:
                restantes.remove(span_b)
                acertos += 1
                break
    return acertos, len(restantes), len(a) - acertos


def progresso(session: Session) -> schemas.Progresso:
    documentos = session.scalar(select(func.count()).select_from(DatasetDocumentoORM)) or 0

    por_anotador = session.execute(
        select(
            DatasetAnotacaoORM.Anotador,
            func.count(),
            func.sum(case((DatasetAnotacaoORM.Status == "done", 1), else_=0)),
        ).group_by(DatasetAnotacaoORM.Anotador)
    ).all()

    concluidas = session.execute(
        select(
            DatasetAnotacaoORM.Anotador,
            DatasetAnotacaoORM.IdDocumento,
            DatasetAnotacaoORM.Spans,
        ).where(DatasetAnotacaoORM.Status == "done")
    ).all()

    spans_por: dict[str, dict[int, list[schemas.Span]]] = {}
    for anotador, id_doc, raw in concluidas:
        spans_por.setdefault(anotador, {})[id_doc] = _parse_spans(raw)

    anotadores = [
        schemas.ProgressoAnotador(
            anotador=nome,
            total=total,
            concluidos=int(feitos or 0),
            spans=sum(len(v) for v in spans_por.get(nome, {}).values()),
        )
        for nome, total, feitos in sorted(por_anotador)
    ]

    pares: list[schemas.ConcordanciaPar] = []
    nomes = sorted(spans_por)
    for i, a in enumerate(nomes):
        for b in nomes[i + 1 :]:
            comuns = sorted(set(spans_por[a]) & set(spans_por[b]))
            acertos = so_b = so_a = 0
            for id_doc in comuns:
                x, y, z = _casar(spans_por[a][id_doc], spans_por[b][id_doc])
                acertos, so_b, so_a = acertos + x, so_b + y, so_a + z
            tp, fp, fn = acertos, so_b, so_a
            denominador = 2 * tp + fp + fn
            pares.append(
                schemas.ConcordanciaPar(
                    a=a,
                    b=b,
                    documentos_comuns=len(comuns),
                    f1=(2 * tp / denominador) if denominador else None,
                )
            )

    return schemas.Progresso(documentos=documentos, anotadores=anotadores, concordancia=pares)


# ----- export ----------------------------------------------------------------


def export(session: Session, *, anotador: str) -> list[schemas.DocumentoExport]:
    linhas = session.execute(
        select(DatasetDocumentoORM, DatasetAnotacaoORM)
        .join(
            DatasetAnotacaoORM,
            DatasetAnotacaoORM.IdDocumento == DatasetDocumentoORM.IdDocumento,
        )
        .where(
            DatasetAnotacaoORM.Anotador == anotador,
            DatasetAnotacaoORM.Status == "done",
        )
        .order_by(DatasetDocumentoORM.IdDocumento)
    ).all()

    saida: list[schemas.DocumentoExport] = []
    for doc, anot in linhas:
        spans = _parse_spans(anot.Spans)
        tokens, tags, offsets = _to_bio(doc.Texto, spans)
        saida.append(
            schemas.DocumentoExport(
                id=doc.IdExterno if doc.IdExterno is not None else doc.IdDocumento,
                text=doc.Texto,
                tokens=tokens,
                ner_tags=tags,
                token_offsets=offsets,
                entities=spans,
            )
        )
    return saida
