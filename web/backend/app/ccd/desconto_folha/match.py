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


def _dialeto(session: Session) -> str:
    return session.bind.dialect.name if session.bind is not None else "mssql"


def creditos(
    session: Session,
    *,
    texto: str | None,
    valor: float | None,
    desde: date | None,
) -> list[dict[str, Any]]:
    """Créditos do extrato (OB/transferência) por texto do órgão, valor e data mínima.

    "FRAP-first": acha o repasse sem depender da resposta do órgão. Devolve também
    a que cadastro o lançamento já está vinculado, se estiver — sinaliza, não esconde.
    """
    concat = "+" if _dialeto(session) == "mssql" else "||"
    sql = f"""
        SELECT L.IdLancamento AS id_lancamento, L.DtMovimento AS dt_movimento,
               L.Documento AS documento, L.Historico AS historico, L.Descricao AS descricao,
               L.Valor AS valor,
               (SELECT MIN(v.IdCCDDescontoFolha)
                  FROM CCDDescontoFolhaMatch m
                  JOIN CCDDescontoFolhaValor v ON v.IdCCDDescontoFolhaValor = m.IdCCDDescontoFolhaValor
                 WHERE m.IdLancamentoFRAP = L.IdLancamento) AS id_cadastro_vinculado
        FROM FRAPLancamento L
        WHERE L.ValorDC = 'C' AND L.IdCategoria IN (1, 3)
          AND (:desde IS NULL OR L.DtMovimento >= :desde)
          AND (:valor IS NULL OR ABS(L.Valor - :valor) < 0.005)
          AND (:texto IS NULL
               OR UPPER(COALESCE(L.Descricao, '') {concat} ' ' {concat} COALESCE(L.Historico, ''))
                  LIKE :padrao)
        ORDER BY L.Valor, L.DtMovimento, L.IdLancamento
    """
    rows = session.execute(
        text(sql),
        {
            "desde": desde.isoformat() if desde else None,
            "valor": float(valor) if valor else None,
            "texto": texto or None,
            "padrao": f"%{(texto or '').upper()}%",
        },
    ).mappings()
    return [dict(r) for r in rows]


def adotar(
    session: Session, *, id_cadastro: int, ids_lancamento: list[int], id_usuario: int | None
) -> int:
    """Cria um valor manual por lançamento (competência = mês do crédito) já vinculado.

    Pula lançamento inexistente, não-crédito ou já vinculado a algum cadastro.
    """
    prox = int(
        session.execute(
            text(
                "SELECT COALESCE(MAX(NumeroParcela), 0) FROM CCDDescontoFolhaValor "
                "WHERE IdCCDDescontoFolha = :c"
            ),
            {"c": id_cadastro},
        ).scalar_one()
    )
    n = 0
    for id_l in ids_lancamento:
        row = (
            session.execute(
                text(
                    """
                    SELECT L.DtMovimento AS dt, L.Valor AS valor,
                           (SELECT COUNT(*) FROM CCDDescontoFolhaMatch m
                             WHERE m.IdLancamentoFRAP = L.IdLancamento) AS vinculado
                    FROM FRAPLancamento L
                    WHERE L.IdLancamento = :l AND L.ValorDC = 'C'
                    """
                ),
                {"l": int(id_l)},
            )
            .mappings()
            .first()
        )
        if row is None or int(row["vinculado"] or 0) > 0:
            continue
        dt = row["dt"]
        if isinstance(dt, str):
            dt = date.fromisoformat(dt[:10])
        prox += 1
        session.execute(
            text(
                "INSERT INTO CCDDescontoFolhaValor "
                "(IdCCDDescontoFolha, NumeroParcela, MesReferencia, AnoReferencia, Valor, Origem) "
                "VALUES (:c, :n, :m, :a, :v, 'M')"
            ),
            {
                "c": id_cadastro,
                "n": prox,
                "m": dt.month if dt else None,
                "a": dt.year if dt else None,
                "v": round(float(row["valor"]), 2),
            },
        )
        id_valor = int(
            session.execute(
                text(
                    "SELECT MAX(IdCCDDescontoFolhaValor) FROM CCDDescontoFolhaValor "
                    "WHERE IdCCDDescontoFolha = :c"
                ),
                {"c": id_cadastro},
            ).scalar_one()
        )
        vincular(
            session,
            id_valor=id_valor,
            id_lancamento=int(id_l),
            id_usuario=id_usuario,
            automatico=False,
            observacao="adotado do extrato FRAP",
        )
        n += 1
    session.commit()
    return n


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
    """Vincula cada valor sem match ao seu único candidato. Devolve quantos vinculou.

    Parcelas mensais iguais (ex.: 3 x 1.800,00) nunca têm candidato único; quando o
    grupo de N parcelas de mesmo valor encontra exatamente N créditos a partir da
    primeira competência, vincula em ordem de data.
    """
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
    pendentes = list(valores)
    por_valor: dict[float, list[Any]] = {}
    for v in pendentes:
        por_valor.setdefault(round(float(v["valor"]), 2), []).append(v)
    for grupo in por_valor.values():
        if len(grupo) < 2:
            continue
        grupo.sort(key=lambda v: ((v["ano"] or 0), (v["mes"] or 0), v["id_valor"]))
        primeiro = grupo[0]
        cands = candidatos(
            session,
            float(primeiro["valor"]),
            data_minima(mes=primeiro["mes"], ano=primeiro["ano"], data_resposta=data_resposta),
        )
        if len(cands) != len(grupo):
            continue
        for v, c in zip(grupo, cands):
            vincular(
                session,
                id_valor=int(v["id_valor"]),
                id_lancamento=int(c["id_lancamento"]),
                id_usuario=None,
                automatico=True,
            )
            vinculados += 1
        pendentes = [v for v in pendentes if v not in grupo]
    for v in pendentes:
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
