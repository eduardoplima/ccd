"""Painel de indicadores da CCD (página inicial do app).

Recorte da CCD sobre a proposta de indicadores estratégicos 2027-2028 da DPG
(docs/indicadores/). Cada indicador traz o valor por ano, a linha de base
(média dos dois anos anteriores ao corrente) e uma explicação (hover do card). Todas as consultas vão nas
tabelas-base — a vwCCDDebito leva minutos na varredura completa.
"""

from __future__ import annotations

import time
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.indicadores.schemas import Indicador, Painel, Sentido, Unidade
from app.cgad.multas_nao_cominadas import service as multas_service

_FOLHA = "NOT EXISTS (SELECT 1 FROM dbo.Exe_Debito g WHERE g.IdDebitoAnterior = e.IdDebito)"


def _por_ano(session: Session, sql: str, ini: date) -> dict[int, float]:
    """SQL que devolve (ano, valor) -> {ano: valor}."""
    rows = session.execute(text(sql), {"ini": ini}).all()
    return {int(a): float(v) for a, v in rows if v is not None}


def _linha_base(valores: dict[int, float | None], ano: int) -> float | None:
    anteriores = [v for a, v in valores.items() if a in (ano - 2, ano - 1) and v is not None]
    return sum(anteriores) / len(anteriores) if anteriores else None


def _serie(valores: dict[int, float], anos: list[int]) -> dict[int, float | None]:
    return {a: valores.get(a) for a in anos}


# ponytail: cache por processo do uvicorn (~7 s para montar); redis se houver vários workers
_TTL_S = 3600
_cache: tuple[float, Painel] | None = None


def painel_cacheado(bddip: Session, processo: Session) -> Painel:
    global _cache
    if _cache is None or time.monotonic() - _cache[0] > _TTL_S:
        _cache = (time.monotonic(), painel(bddip, processo))
    return _cache[1]


def painel(bddip: Session, processo: Session, hoje: date | None = None) -> Painel:
    hoje = hoje or date.today()
    ano = hoje.year
    anos = [ano - 2, ano - 1, ano]
    ini = date(ano - 2, 1, 1)

    frap = _por_ano(
        bddip,
        """SELECT YEAR(DtMovimento), SUM(Valor) FROM dbo.FRAPLancamento
           WHERE ValorDC = 'C' AND IdCategoria IN (1, 2, 3, 9) AND DtMovimento >= :ini
           GROUP BY YEAR(DtMovimento)""",
        ini,
    )
    # multas em aberto hoje (folha da cadeia): denominador da taxa de recuperação,
    # já que o FRAP só recebe multa (ressarcimento vai ao ente)
    carteira_multas = float(
        processo.execute(
            text(
                f"""SELECT SUM(e.valorOriginalDebito) FROM dbo.Exe_Debito e
                    WHERE e.CodigoStatusDivida IN (1, 3, 8) AND e.DataCancelamento IS NULL
                      AND e.CodigoTipoDebito IN (2, 4, 5) AND {_FOLHA}"""
            )
        ).scalar()
        or 0
    )
    # ponytail: movimentação por lote (Lotes/Itens_Lote); só há saídas da CCD a partir de 2025
    fluxo = processo.execute(
        text(
            """SELECT YEAR(l.enviado_em),
                      COUNT(DISTINCT CASE WHEN l.destino = 'CCD' THEN i.IdProcesso END),
                      COUNT(DISTINCT CASE WHEN l.origem = 'CCD' THEN i.IdProcesso END)
               FROM dbo.Lotes l JOIN dbo.Itens_Lote i ON i.IdLote = l.IdLote
               WHERE (l.origem = 'CCD' OR l.destino = 'CCD') AND l.origem <> l.destino
                 AND l.enviado_em >= :ini
               GROUP BY YEAR(l.enviado_em)"""
        ),
        {"ini": ini},
    ).all()
    produtividade = {int(a): 100.0 * s / e for a, e, s in fluxo if e}
    tramitados = {int(a): float(s) for a, e, s in fluxo if s}
    fluxo_atual = next(((e, s) for a, e, s in fluxo if a == ano), (0, 0))
    # débitos cadastrados = raiz da cadeia (IdDebitoAnterior NULL), pela data de inclusão
    cadastrados = processo.execute(
        text(
            """SELECT YEAR(datainclusao),
                      SUM(CASE WHEN CodigoTipoDebito IN (2, 4, 5) THEN 1 ELSE 0 END),
                      SUM(CASE WHEN CodigoTipoDebito IN (2, 4, 5)
                               THEN valorOriginalDebito ELSE 0 END),
                      SUM(CASE WHEN CodigoTipoDebito = 1 THEN 1 ELSE 0 END),
                      SUM(CASE WHEN CodigoTipoDebito = 1 THEN valorOriginalDebito ELSE 0 END)
               FROM dbo.Exe_Debito
               WHERE IdDebitoAnterior IS NULL AND datainclusao >= :ini
               GROUP BY YEAR(datainclusao)"""
        ),
        {"ini": ini},
    ).all()
    multas_cad = {int(r[0]): float(r[1]) for r in cadastrados}
    ress_cad = {int(r[0]): float(r[3]) for r in cadastrados}
    cad_atual = next((r for r in cadastrados if r[0] == ano), (ano, 0, 0, 0, 0))
    estoque_qtd, estoque_dias = processo.execute(
        text(
            """WITH entrada AS (
                   SELECT ie.IdProcesso, MAX(ie.recebido_em) AS recebido_em
                   FROM dbo.Itens_Lote ie JOIN dbo.Lotes lt ON lt.IdLote = ie.IdLote
                   WHERE lt.destino = 'CCD' GROUP BY ie.IdProcesso)
               SELECT COUNT(*), AVG(CAST(DATEDIFF(DAY, ent.recebido_em, GETDATE()) AS float))
               FROM dbo.Processos p LEFT JOIN entrada ent ON ent.IdProcesso = p.IdProcesso
               WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL"""
        )
    ).one()

    multas = multas_service.listar(bddip)

    def ind(
        chave: str,
        titulo: str,
        unidade: Unidade,
        sentido: Sentido,
        explicacao: str,
        valores: dict[int, float] | None = None,
        atual: float | None = None,
        detalhe: str | None = None,
    ) -> Indicador:
        serie = _serie(valores, anos) if valores is not None else {}
        return Indicador(
            chave=chave,
            titulo=titulo,
            unidade=unidade,
            sentido=sentido,
            explicacao=explicacao,
            valores=serie,
            atual=atual,
            linha_base=_linha_base(serie, ano),
            detalhe=detalhe,
        )

    def brl(v: float) -> str:
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return Painel(
        ano=ano,
        anos=anos,
        indicadores=[
            ind(
                "processos_tramitados",
                "Processos tramitados pela CCD",
                "qtd",
                "maior",
                "Processos distintos que a CCD enviou a outro setor no ano, contados pelos lotes de "
                "tramitação. Quanto mais, melhor.",
                tramitados,
                detalhe="processos distintos enviados pela CCD a outro setor no ano",
            ),
            ind(
                "multas_cadastradas",
                "Multas cadastradas",
                "qtd",
                "maior",
                "Débitos de multa (tipos 2, 4 e 5) incluídos no ano, contando só o débito original "
                "da cadeia (sem as atualizações).",
                multas_cad,
                detalhe=f"{ano}: {brl(float(cad_atual[2] or 0))} imputados",
            ),
            ind(
                "ressarcimentos_cadastrados",
                "Ressarcimentos cadastrados",
                "qtd",
                "maior",
                "Débitos de ressarcimento (tipo 1) incluídos no ano, contando só o débito original "
                "da cadeia (sem as atualizações).",
                ress_cad,
                detalhe=f"{ano}: {brl(float(cad_atual[4] or 0))} imputados",
            ),
            ind(
                "arrecadacao_frap",
                "Arrecadação do FRAP",
                "brl",
                "maior",
                "Soma, por ano, dos créditos de arrecadação no extrato do FRAP (categorias 1, 2, 3 "
                "e 9).",
                frap,
                detalhe="créditos de arrecadação no extrato (categorias 1, 2, 3 e 9)",
            ),
            ind(
                "taxa_recuperacao",
                "Taxa de recuperação de multas",
                "pct",
                "maior",
                "Arrecadação do FRAP no ano ÷ total das multas em aberto hoje (débito vigente da "
                "cadeia). O FRAP só recebe multa; ressarcimento vai ao ente.",
                {a: 100.0 * v / carteira_multas for a, v in frap.items()}
                if carteira_multas
                else {},
                detalhe=f"arrecadação FRAP ÷ multas em aberto hoje ({brl(carteira_multas)})",
            ),
            ind(
                "estoque",
                "Tempo médio de estoque na CCD",
                "dias",
                "menor",
                "Média de dias desde o último recebimento na CCD dos processos que estão hoje no "
                "setor (sem apensados). Quanto menos, melhor.",
                atual=float(estoque_dias) if estoque_dias is not None else None,
                detalhe=f"{estoque_qtd} processos no setor hoje",
            ),
            ind(
                "produtividade",
                "Produtividade da CCD",
                "pct",
                "maior",
                "Saídas ÷ entradas de processos na CCD no ano. Acima de 100%, o estoque do setor "
                "está diminuindo.",
                produtividade,
                detalhe=f"{ano}: {fluxo_atual[1]} saídas ÷ {fluxo_atual[0]} entradas",
            ),
            ind(
                "multas_nao_cominadas",
                "Multas cominatórias sem débito",
                "qtd",
                "menor",
                "Obrigações aprovadas no CGAD com multa cominatória, mas sem débito de multa "
                "cominatória (tipo 5) cadastrado no processo. Quanto menos, melhor.",
                atual=float(multas.total_obrigacoes),
                detalhe=f"{multas.total_processos} processos",
            ),
        ],
    )
