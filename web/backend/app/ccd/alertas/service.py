"""Alertas do módulo CCD — situações que exigem ação da equipe.

Hoje há um único tipo: processos com o marcador ativo
"PARCELAMENTO EM CURSO" mas sem nenhum parcelamento vigente (o marcador ficou
desatualizado porque o parcelamento foi cancelado, quitado ou nunca efetivado).

O registro `_ALERTAS` é extensível: cada `_AlertaSpec` casa um `TipoAlerta` com
um coletor que devolve os itens; `listar_alertas` monta a resposta a partir dele.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.alertas.schemas import (
    AlertaOut,
    AlertaParcelamentoCancelado,
    AlertasResponse,
    ParcelamentoCanceladoDetalhe,
    TipoAlerta,
    TipoAlertaInfo,
)

# Setor CCD no banco `processo` (Pro_Marcador.IdSetor).
ID_SETOR_CCD = 762
_MARCADOR = "PARCELAMENTO EM CURSO"

# Exe_Parcelamento.SituacaoParcelamento é char(1) sem tabela de domínio; os
# rótulos abaixo foram inferidos empiricamente e validados por amostras no banco.
_SITUACAO_PARCELAMENTO: dict[str, str] = {
    "1": "Aguardando início",
    "2": "Em curso",
    "3": "Cancelado",
    "4": "Quitado",
    "5": "Cancelado por inadimplência",
    "6": "Indefinida",
}


def _coletar_parcelamento_cancelado(session: Session) -> list[AlertaOut]:
    sql = text(
        """
        WITH marcados AS (
            SELECT mp.IdProcesso, MIN(mp.DataInclusao) AS data_marcador
            FROM dbo.Pro_MarcadorProcesso mp
            JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
            WHERE m.IdSetor = :id_setor
              AND m.Descricao = :marcador
              AND mp.DataExclusao IS NULL
            GROUP BY mp.IdProcesso
        ),
        parc AS (
            -- o débito pode apontar para o processo marcado tanto pela execução
            -- quanto pela origem; COALESCE perderia o vínculo pela origem
            SELECT ep.IdParcelamento, ep.SituacaoParcelamento,
                   ep.DataCancelamentoParcelamento, ed.DataCancelamento,
                   mk.IdProcesso
            FROM dbo.Exe_Parcelamento ep
            JOIN dbo.Exe_Debito ed ON ed.IdDebito = ep.IdDebito
            JOIN marcados mk ON mk.IdProcesso IN (ed.IdProcessoExecucao, ed.IdProcessoOrigem)
        )
        SELECT
            RTRIM(p.numero_processo) AS numero_processo,
            RTRIM(p.ano_processo)    AS ano_processo,
            RTRIM(r.nome)            AS relator,
            mk.data_marcador         AS data_marcador,
            ult.IdParcelamento       AS id_parcelamento,
            RTRIM(ult.SituacaoParcelamento) AS situacao,
            ult.DataCancelamentoParcelamento AS data_cancelamento,
            ult.numero_parcelas      AS numero_parcelas,
            ult.parcelas_pagas       AS parcelas_pagas
        FROM marcados mk
        JOIN dbo.Processos p ON p.IdProcesso = mk.IdProcesso
        LEFT JOIN dbo.Relator r ON r.codigo = p.codigo_relator
        OUTER APPLY (
            SELECT TOP 1
                pc.IdParcelamento,
                pc.SituacaoParcelamento,
                pc.DataCancelamentoParcelamento,
                (SELECT COUNT(*) FROM dbo.Exe_Parcela x
                 WHERE x.IdParcelamento = pc.IdParcelamento) AS numero_parcelas,
                (SELECT COUNT(*) FROM dbo.Exe_Parcela x
                 WHERE x.IdParcelamento = pc.IdParcelamento
                   AND x.SituacaoParcela = '2') AS parcelas_pagas
            FROM parc pc
            WHERE pc.IdProcesso = mk.IdProcesso
            ORDER BY pc.IdParcelamento DESC
        ) ult
        WHERE NOT EXISTS (
            SELECT 1 FROM parc pa
            WHERE pa.IdProcesso = mk.IdProcesso
              AND pa.SituacaoParcelamento IN ('1', '2')
              AND pa.DataCancelamento IS NULL
        )
        ORDER BY p.ano_processo DESC, p.numero_processo DESC
        """
    )
    rows = session.execute(sql, {"id_setor": ID_SETOR_CCD, "marcador": _MARCADOR}).mappings().all()

    items: list[AlertaOut] = []
    for r in rows:
        situacao = r["situacao"]
        detalhe = ParcelamentoCanceladoDetalhe(
            id_parcelamento=r["id_parcelamento"],
            situacao=situacao,
            situacao_descricao=(_SITUACAO_PARCELAMENTO.get(situacao) if situacao else None),
            data_cancelamento=r["data_cancelamento"],
            numero_parcelas=r["numero_parcelas"],
            parcelas_pagas=r["parcelas_pagas"],
        )
        items.append(
            AlertaParcelamentoCancelado(
                processo=f"{r['numero_processo']}/{r['ano_processo']}",
                numero_processo=r["numero_processo"],
                ano_processo=r["ano_processo"],
                relator=r["relator"],
                data_marcador=r["data_marcador"],
                detalhe=detalhe,
            )
        )
    return items


@dataclass(frozen=True)
class _AlertaSpec:
    tipo: TipoAlerta
    titulo: str
    descricao: str
    coletor: Callable[[Session], list[AlertaOut]]


_ALERTAS: tuple[_AlertaSpec, ...] = (
    _AlertaSpec(
        tipo=TipoAlerta.PARCELAMENTO_CANCELADO,
        titulo="Parcelamento cancelado com marcador ativo",
        descricao=(
            'Processos com o marcador "PARCELAMENTO EM CURSO" ativo, mas sem '
            "nenhum parcelamento vigente — cancelado, quitado ou nunca efetivado. "
            "O marcador precisa ser revisado."
        ),
        coletor=_coletar_parcelamento_cancelado,
    ),
)


def listar_alertas(session: Session, *, tipo: TipoAlerta | None = None) -> AlertasResponse:
    tipos: list[TipoAlertaInfo] = []
    items: list[AlertaOut] = []
    for spec in _ALERTAS:
        if tipo is not None and spec.tipo != tipo:
            continue
        coletados = spec.coletor(session)
        tipos.append(
            TipoAlertaInfo(
                tipo=spec.tipo,
                titulo=spec.titulo,
                descricao=spec.descricao,
                quantidade=len(coletados),
            )
        )
        items.extend(coletados)
    return AlertasResponse(tipos=tipos, items=items, total=len(items))
