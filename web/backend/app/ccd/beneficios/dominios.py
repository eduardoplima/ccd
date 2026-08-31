"""Domínios do SisBenefícios lidos ao vivo do BdBeneficio (cross-db, 3 partes).

Sem cópia local: a lista fechada (tipos, subtipos, áreas temáticas, ...) é do
outro sistema e muda lá. Cache em memória com TTL para não bater no banco a
cada render do formulário.
"""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.beneficios.schemas import DominioItem, DominiosResponse

_TTL_SEGUNDOS = 3600
_cache: dict[str, Any] = {"quando": 0.0, "dados": None}


def _listar(
    session: Session, tabela: str, id_col: str, desc_col: str, *, ativo: bool
) -> list[DominioItem]:
    where = "WHERE Ativo = 1" if ativo else ""
    rows = session.execute(
        text(
            f"SELECT {id_col} AS id, {desc_col} AS descricao FROM BdBeneficio.dbo.{tabela} {where} ORDER BY {id_col}"
        )
    ).all()
    # Descrições vêm com \n e espaços presos no cadastro do BdBeneficio.
    return [DominioItem(id=int(r.id), descricao=" ".join(str(r.descricao).split())) for r in rows]


def obter_dominios(session: Session, *, force: bool = False) -> DominiosResponse:
    agora = time.monotonic()
    if not force and _cache["dados"] is not None and agora - _cache["quando"] < _TTL_SEGUNDOS:
        return _cache["dados"]

    tipo_subtipos: dict[int, list[int]] = {}
    for id_tipo, id_subtipo in session.execute(
        text(
            "SELECT IdTipoBeneficio, IdSubTipoBeneficio "
            "FROM BdBeneficio.dbo.Beneficio_Tipo_Subtipo ORDER BY IdTipoBeneficio, IdSubTipoBeneficio"
        )
    ).all():
        tipo_subtipos.setdefault(int(id_tipo), []).append(int(id_subtipo))

    dados = DominiosResponse(
        tipos=_listar(
            session,
            "Beneficio_TipoBeneficio",
            "IdTipoBeneficio",
            "DescricaoTipoBeneficio",
            ativo=True,
        ),
        subtipos=_listar(
            session,
            "Beneficio_SubTipoBeneficio",
            "IdSubTipoBeneficio",
            "DescricaoSubTipoBeneficio",
            ativo=True,
        ),
        tipo_subtipos=tipo_subtipos,
        areas_tematicas=_listar(
            session, "Beneficio_AreaTematica", "IdAreaTematica", "DescricaoAreaTematica", ativo=True
        ),
        caracterizacoes=_listar(
            session,
            "Beneficio_CaracterizacaoBeneficio",
            "IdCaracterizacaoBeneficio",
            "DescricaoCaracterizacaoBeneficio",
            ativo=False,
        ),
        situacoes=_listar(
            session,
            "Beneficio_SituacaoBeneficio",
            "IdBeneficioSituacao",
            "DescricaoBeneficioSituacao",
            ativo=False,
        ),
        situacoes_efetivacao=_listar(
            session,
            "Beneficio_SituacaoEfetivacao",
            "IdBeneficioSituacaoEfetivacao",
            "DescricaoBeneficioSituacaoEfetivacao",
            ativo=False,
        ),
        unidades_medida=_listar(
            session,
            "Beneficio_UnidadeDeMedida",
            "IdUnidadeDeMedida",
            "DescricaoUnidadeDeMedida",
            ativo=False,
        ),
    )
    _cache["quando"] = agora
    _cache["dados"] = dados
    return dados
