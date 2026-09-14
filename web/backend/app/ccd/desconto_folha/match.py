"""Match dos valores da resposta com créditos do FRAP (BdDIP).

Regra: crédito (ValorDC='C') de OB recebida ou transferência com o valor
exato, a partir da data da resposta do órgão (ou do 1º dia da competência,
quando o valor tem mês/ano). Um único candidato vincula sozinho; vários ou
nenhum ficam para o usuário.
ponytail: valor exato; tolerância/soma de parcelas só se aparecer caso real.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# FRAPCategoria: 1 = OB_RECEBIDA, 3 = TRANSFERENCIA
_CATEGORIAS = (1, 3)


def candidatos(session: Session, valor: float, data_min: date | None) -> list[dict[str, Any]]:
    rows = session.execute(
        text(
            """
            SELECT L.IdLancamento AS id_lancamento, L.DtMovimento AS dt_movimento,
                   L.Documento AS documento, L.Historico AS historico, L.Valor AS valor
            FROM FRAPLancamento L
            WHERE L.ValorDC = 'C' AND L.IdCategoria IN (1, 3)
              AND ABS(L.Valor - :valor) < 0.005
              AND (:data_min IS NULL OR L.DtMovimento >= :data_min)
            ORDER BY L.DtMovimento, L.IdLancamento
            """
        ),
        {"valor": float(valor), "data_min": data_min.isoformat() if data_min else None},
    ).mappings()
    return [dict(r) for r in rows]


def data_minima(
    *, mes: int | None, ano: int | None, data_resposta: datetime | date | None
) -> Optional[date]:
    if mes and ano:
        return date(int(ano), int(mes), 1)
    if isinstance(data_resposta, datetime):
        return data_resposta.date()
    if isinstance(data_resposta, date):
        return data_resposta
    if isinstance(data_resposta, str) and data_resposta:
        return date.fromisoformat(data_resposta[:10])
    return None


def vincular(
    session: Session,
    *,
    id_valor: int,
    id_lancamento: int,
    id_usuario: int | None,
    automatico: bool = False,
    observacao: str | None = None,
) -> int:
    session.execute(
        text("DELETE FROM CCDDescontoFolhaMatch WHERE IdCCDDescontoFolhaValor = :v"),
        {"v": id_valor},
    )
    session.execute(
        text(
            """
            INSERT INTO CCDDescontoFolhaMatch
                (IdCCDDescontoFolhaValor, IdLancamentoFRAP, Automatico, IdUsuario, DataMatch, Observacao)
            VALUES (:v, :l, :auto, :u, :agora, :obs)
            """
        ),
        {
            "v": id_valor,
            "l": id_lancamento,
            "auto": 1 if automatico else 0,
            "u": id_usuario,
            "agora": datetime.utcnow().replace(microsecond=0),
            "obs": observacao,
        },
    )
    session.commit()
    return int(
        session.execute(
            text(
                "SELECT IdCCDDescontoFolhaMatch FROM CCDDescontoFolhaMatch WHERE IdCCDDescontoFolhaValor = :v"
            ),
            {"v": id_valor},
        ).scalar_one()
    )


def desvincular(session: Session, *, id_valor: int) -> int:
    n = session.execute(
        text("DELETE FROM CCDDescontoFolhaMatch WHERE IdCCDDescontoFolhaValor = :v"),
        {"v": id_valor},
    ).rowcount
    session.commit()
    return int(n or 0)


def match_automatico(session: Session, *, id_cadastro: int) -> int:
    """Vincula cada valor sem match ao seu único candidato. Devolve quantos vinculou."""
    data_resposta = session.execute(
        text("SELECT DataResposta FROM CCDDescontoFolha WHERE IdCCDDescontoFolha = :c"),
        {"c": id_cadastro},
    ).scalar()
    valores = session.execute(
        text(
            """
            SELECT v.IdCCDDescontoFolhaValor AS id_valor, v.MesReferencia AS mes,
                   v.AnoReferencia AS ano, v.Valor AS valor
            FROM CCDDescontoFolhaValor v
            LEFT JOIN CCDDescontoFolhaMatch m ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
            WHERE v.IdCCDDescontoFolha = :c AND m.IdCCDDescontoFolhaMatch IS NULL
            """
        ),
        {"c": id_cadastro},
    ).mappings()
    vinculados = 0
    for v in list(valores):
        cands = candidatos(
            session,
            float(v["valor"]),
            data_minima(mes=v["mes"], ano=v["ano"], data_resposta=data_resposta),
        )
        if len(cands) == 1:
            vincular(
                session,
                id_valor=int(v["id_valor"]),
                id_lancamento=int(cands[0]["id_lancamento"]),
                id_usuario=None,
                automatico=True,
            )
            vinculados += 1
    return vinculados
