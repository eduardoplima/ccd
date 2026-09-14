"""Dashboards business logic.

Um ponto de entrada: ``compute_summary`` carrega todas as obrigações e
recomendações aprovadas/enviadas do staging (sem recorte de período), enriquece
cada linha com o que vem do banco ``processo`` (número/ano, tipo, relator) e
agrega tudo em Python — o volume é de centenas de linhas, e a mesma lista
alimenta os rankings, os treemaps e a tabela da página.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.cgad.dashboards import schemas
from app.cgad.review.service import _load_processo_numero_ano
from cgad.etl.staging import (
    ObrigacaoStagingORM,
    RecomendacaoStagingORM,
    ReviewStatus,
)
from cgad.models import NERDecisaoORM
from cgad.utils import DB_PROCESSOS, get_connection

logger = logging.getLogger(__name__)

# Placeholder que o pipeline e o prompt gravam quando não identificam órgão ou
# responsável (cgad/etl/pipeline.py, cgad/utils.py). Não é um valor: fica fora dos rankings.
_DESCONHECIDO = "Desconhecido"
_ATIVOS = (ReviewStatus.approved, ReviewStatus.dispatched)
_TREEMAP_MAX = 30  # ponytail: corte fixo + "Outros"; parametrizar se pedirem


# ----- carregar --------------------------------------------------------------


def _carregar(session: Session) -> list[dict[str, Any]]:
    """Uma linha por entidade aprovada/enviada, com os campos crus do staging."""
    linhas: list[dict[str, Any]] = []
    o = ObrigacaoStagingORM
    for r in session.execute(
        select(
            o.IdObrigacaoStaging,
            o.IdProcesso,
            o.IdComposicaoPauta,
            o.IdVotoPauta,
            o.DescricaoObrigacao,
            o.Status,
            o.Revisor,
            o.DataRevisao,
            o.DataEnvio,
            o.OrgaoResponsavel,
            o.TemMultaCominatoria,
            o.NomeResponsavelMultaCominatoria,
            o.DocumentoResponsavelMultaCominatoria,
            o.IdPessoaMultaCominatoria,
        ).where(o.Status.in_(_ATIVOS))
    ).all():
        com_multa = bool(r[10])
        linhas.append(
            dict(
                tipo="obrigacao",
                id=r[0],
                id_processo=r[1],
                tripla=(r[1], r[2], r[3]),
                descricao=r[4] or "",
                status=_status_str(r[5]),
                revisor=r[6],
                data_revisao=r[7],
                data_envio=r[8],
                orgao=r[9],
                nome=r[11] if com_multa else None,
                documento=r[12] if com_multa else None,
                id_pessoa=r[13] if com_multa else None,
            )
        )
    c = RecomendacaoStagingORM
    for r in session.execute(
        select(
            c.IdRecomendacaoStaging,
            c.IdProcesso,
            c.IdComposicaoPauta,
            c.IdVotoPauta,
            c.DescricaoRecomendacao,
            c.Status,
            c.Revisor,
            c.DataRevisao,
            c.DataEnvio,
            c.OrgaoResponsavel,
            c.NomeResponsavel,
            c.IdPessoaResponsavel,
        ).where(c.Status.in_(_ATIVOS))
    ).all():
        linhas.append(
            dict(
                tipo="recomendacao",
                id=r[0],
                id_processo=r[1],
                tripla=(r[1], r[2], r[3]),
                descricao=r[4] or "",
                status=_status_str(r[5]),
                revisor=r[6],
                data_revisao=r[7],
                data_envio=r[8],
                orgao=r[9],
                nome=r[10],
                documento=None,
                id_pessoa=r[11],
            )
        )
    return linhas


def _status_str(raw) -> str:
    return raw.value if isinstance(raw, ReviewStatus) else str(raw)


# ----- enriquecer (banco processo) -------------------------------------------


def _load_tipo_relator(
    id_processos: list[int],
) -> dict[int, tuple[Optional[str], Optional[str]]]:
    """``IdProcesso → (tipo de processo, relator)`` do banco ``processo``.
    ``{}`` em falha (ex.: testes sem MSSQL) — as dimensões degradam para
    "Desconhecido"."""
    unique = sorted({int(i) for i in id_processos})
    if not unique:
        return {}
    out: dict[int, tuple[Optional[str], Optional[str]]] = {}
    try:
        with get_connection(DB_PROCESSOS).connect() as conn:
            for i in range(0, len(unique), 1000):
                placeholders = ", ".join(str(x) for x in unique[i : i + 1000])
                rows = conn.execute(
                    text(
                        "SELECT p.IdProcesso, RTRIM(t.descricao) AS tipo, RTRIM(r.nome) AS relator "
                        "FROM dbo.Processos p "
                        "LEFT JOIN dbo.Tipo t ON t.codigo = p.codigo_tipo_processo "
                        "LEFT JOIN dbo.Relator r ON r.codigo = p.codigo_relator "
                        f"WHERE p.IdProcesso IN ({placeholders})"
                    )
                ).all()
                for row in rows:
                    out[int(row.IdProcesso)] = (row.tipo or None, row.relator or None)
        return out
    except Exception:
        logger.exception("failed to resolve tipo/relator for %d processos", len(unique))
        return {}


def _enriquecer(session: Session, linhas: list[dict[str, Any]]) -> None:
    ids = [ln["id_processo"] for ln in linhas]
    numero_ano = _load_processo_numero_ano(ids)
    tipo_relator = _load_tipo_relator(ids)
    decisao_por_tripla = {
        (d.IdProcesso, d.IdComposicaoPauta, d.IdVotoPauta): d.IdNerDecisao
        for d in session.execute(
            select(NERDecisaoORM).where(NERDecisaoORM.IdProcesso.in_(sorted(set(ids)) or [-1]))
        ).scalars()
    }
    for ln in linhas:
        ln["numero_processo"], ln["ano_processo"] = numero_ano.get(ln["id_processo"], (None, None))
        tipo, relator = tipo_relator.get(ln["id_processo"], (None, None))
        ln["tipo_processo"] = tipo or _DESCONHECIDO
        ln["relator"] = relator or _DESCONHECIDO
        ln["id_decisao"] = decisao_por_tripla.get(ln["tripla"])
        if not ln["orgao"]:
            ln["orgao"] = _DESCONHECIDO


# ----- agregar ---------------------------------------------------------------


def _aggregate_orgaos(linhas: list[dict[str, Any]]) -> list[schemas.OrgaoBucket]:
    by_nome: dict[str, dict[str, int]] = defaultdict(lambda: {"obrigacoes": 0, "recomendacoes": 0})
    for ln in linhas:
        if ln["orgao"] != _DESCONHECIDO:
            by_nome[ln["orgao"]][
                "obrigacoes" if ln["tipo"] == "obrigacao" else "recomendacoes"
            ] += 1
    return [
        schemas.OrgaoBucket(
            nome=nome,
            obrigacoes=c["obrigacoes"],
            recomendacoes=c["recomendacoes"],
            total=c["obrigacoes"] + c["recomendacoes"],
        )
        for nome, c in by_nome.items()
    ]


def _nome_norm(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.upper().split())


def _aggregate_pessoas(linhas: list[dict[str, Any]]) -> list[schemas.PessoaBucket]:
    """Combina o responsável pela multa cominatória (obrigação) com o
    responsável da recomendação. A mesma pessoa chega com id, documento ou só
    nome, em grafias diferentes — e nos dados o mesmo CPF vem com IdPessoa
    diferentes —, então nenhum campo sozinho serve de chave: union-find liga
    documento, id e nome normalizado de cada linha num só grupo. Carimba
    ``pessoa`` (nome canônico do grupo) em cada linha, para o filtro por clique.
    ponytail: homônimos distintos se fundem; separar por CPF se incomodar.
    """
    com_pessoa = [ln for ln in linhas if ln["nome"] and ln["nome"] != _DESCONHECIDO]

    def digitos(documento) -> str:
        return re.sub(r"\D", "", documento or "")

    pai: dict[tuple, tuple] = {}

    def find(x: tuple) -> tuple:
        pai.setdefault(x, x)
        while pai[x] != x:
            pai[x] = pai[pai[x]]
            x = pai[x]
        return x

    def union(x: tuple, y: tuple) -> None:
        pai[find(x)] = find(y)

    for ln in com_pessoa:
        raiz = ("nome", _nome_norm(ln["nome"]))
        if ln["id_pessoa"] is not None:
            union(("id", int(ln["id_pessoa"])), raiz)
        if digitos(ln["documento"]):
            union(("doc", digitos(ln["documento"])), raiz)

    buckets: dict[tuple, dict] = {}
    for ln in com_pessoa:
        b = buckets.setdefault(
            find(("nome", _nome_norm(ln["nome"]))),
            {
                "nomes": defaultdict(int),
                "docs": defaultdict(int),
                "obrigacoes": 0,
                "recomendacoes": 0,
            },
        )
        b["nomes"][ln["nome"]] += 1
        if digitos(ln["documento"]):
            b["docs"][ln["documento"]] += 1
        b["obrigacoes" if ln["tipo"] == "obrigacao" else "recomendacoes"] += 1

    canonico = {chave: max(b["nomes"], key=b["nomes"].get) for chave, b in buckets.items()}
    for ln in linhas:
        ln["pessoa"] = (
            canonico[find(("nome", _nome_norm(ln["nome"])))]
            if ln["nome"] and ln["nome"] != _DESCONHECIDO
            else None
        )

    return [
        schemas.PessoaBucket(
            nome=canonico[chave],
            documento=max(b["docs"], key=b["docs"].get) if b["docs"] else None,
            obrigacoes=b["obrigacoes"],
            recomendacoes=b["recomendacoes"],
            total=b["obrigacoes"] + b["recomendacoes"],
        )
        for chave, b in buckets.items()
    ]


def _buckets(contagens: dict[str, int]) -> list[schemas.TreemapBucket]:
    ordenado = sorted(contagens.items(), key=lambda kv: kv[1], reverse=True)
    top = [schemas.TreemapBucket(nome=nome, total=n) for nome, n in ordenado[:_TREEMAP_MAX]]
    resto = sum(n for _, n in ordenado[_TREEMAP_MAX:])
    if resto:
        top.append(schemas.TreemapBucket(nome="Outros", total=resto))
    return top


def _treemap(linhas: list[dict[str, Any]], tipo: str) -> schemas.TreemapSet:
    por_orgao: dict[str, int] = defaultdict(int)
    por_tipo: dict[str, int] = defaultdict(int)
    por_relator: dict[str, int] = defaultdict(int)
    for ln in linhas:
        if ln["tipo"] != tipo:
            continue
        if ln["orgao"] != _DESCONHECIDO:
            por_orgao[ln["orgao"]] += 1
        por_tipo[ln["tipo_processo"]] += 1
        por_relator[ln["relator"]] += 1
    return schemas.TreemapSet(
        por_orgao=_buckets(por_orgao),
        por_tipo=_buckets(por_tipo),
        por_relator=_buckets(por_relator),
    )


def compute_summary(session: Session, *, top_n: int = 10) -> schemas.DashboardSummary:
    linhas = _carregar(session)
    _enriquecer(session, linhas)

    orgaos = _aggregate_orgaos(linhas)
    orgaos.sort(key=lambda b: b.total, reverse=True)
    pessoas = _aggregate_pessoas(linhas)
    pessoas.sort(key=lambda b: b.total, reverse=True)

    linhas.sort(key=lambda ln: ln["data_revisao"] or datetime.min, reverse=True)
    campos = schemas.EntidadeCadastrada.model_fields
    return schemas.DashboardSummary(
        top_orgaos=orgaos[:top_n],
        top_pessoas=pessoas[:top_n],
        treemap_obrigacao=_treemap(linhas, "obrigacao"),
        treemap_recomendacao=_treemap(linhas, "recomendacao"),
        entidades=[
            schemas.EntidadeCadastrada(**{k: v for k, v in ln.items() if k in campos})
            for ln in linhas
        ],
    )
