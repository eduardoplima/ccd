"""Confronto entre o regime de competência (carteira) e o de caixa (FRAP).

A carteira de créditos diz o que era devido e o que foi baixado; o extrato do FRAP
diz o que entrou na conta do Fundo. As duas séries nunca foram postas lado a lado, e
a diferença entre elas é a prova real da provisão para perdas.

O confronto não é uma igualdade, e a lista das razões é o próprio resultado:

- **Ressarcimento não passa pelo FRAP.** Multa é receita do Tribunal (LC 464/2012,
  art. 165, I); ressarcimento é recolhido "na forma estabelecida pelos entes públicos
  credores" (Res. 013/2015, art. 2º). Só a multa deveria aparecer nas duas lentes.
- **Rendimento de aplicação não é receita de sanção** — categorias 4 e 5 do
  `FRAPCategoria` saem do caixa comparável.
- **A baixa do crédito e o crédito em conta não são o mesmo evento.** `dataBaixa`
  registra quando a CCD reconheceu o pagamento; `DtMovimento` registra quando o
  dinheiro entrou. Desconto em folha e repasse da PGE separam os dois em semanas.

Uso:
    python -m scripts.analise.conciliacao_competencia_caixa
    python -m scripts.analise.conciliacao_competencia_caixa --de 2021 --ate 2026
    python -m scripts.analise.conciliacao_competencia_caixa --self-check
"""
from __future__ import annotations

import argparse
import sys

import pandas as pd

from ccd.config import OUTPUT_DIR
from ccd.db import run_query_df

# Tipos de débito que geram receita do próprio Tribunal (vão ao FRAP).
# 1 = Ressarcimento vai ao ente credor e por isso fica fora da coluna comparável.
TIPOS_MULTA = (2, 4, 5)

# Categorias de `FRAPCategoria` que representam entrada de recurso de terceiro.
# 4 (aplicação/resgate) e 5 (linha de saldo) são movimento interno da conta.
CATEGORIAS_CAIXA = (1, 2, 3, 9)

SQL_CAIXA = """
SELECT YEAR(l.DtMovimento)  AS ano,
       c.Codigo             AS categoria,
       SUM(l.Valor)         AS valor
  FROM BdDIP.dbo.FRAPLancamento l
  JOIN BdDIP.dbo.FRAPCategoria c ON c.IdCategoria = l.IdCategoria
 WHERE l.ValorDC = 'C'
   AND l.IdCategoria IN (1, 2, 3, 9)
   AND YEAR(l.DtMovimento) BETWEEN :de AND :ate
 GROUP BY YEAR(l.DtMovimento), c.Codigo
"""

# Baixa na carteira: o evento está no nó da cadeia que recebeu o pagamento, com a
# sua própria `dataBaixa`. Aqui o grão é a linha, não a cadeia — cada linha é um
# evento de baixa distinto (ver `carteira_ipsas.py` para o grão de cadeia).
SQL_BAIXA = """
SELECT YEAR(e.dataBaixa) AS ano,
       CASE WHEN e.CodigoTipoDebito IN (2, 4, 5) THEN 'baixa_multa'
            ELSE 'baixa_ressarcimento' END AS origem,
       SUM(COALESCE(e.ValorPago, 0)) AS valor
  FROM processo.dbo.Exe_Debito e
 WHERE e.dataBaixa IS NOT NULL
   AND e.ValorPago IS NOT NULL
   AND YEAR(e.dataBaixa) BETWEEN :de AND :ate
 GROUP BY YEAR(e.dataBaixa),
          CASE WHEN e.CodigoTipoDebito IN (2, 4, 5) THEN 'baixa_multa'
               ELSE 'baixa_ressarcimento' END
"""

# Boleto e repasse da PGE entram inteiros na coluna "identificado" sem segregar por
# tipo de débito porque a segregação foi conferida e é degenerada: em 2021–2026,
# 100% dos boletos pagos (`Exe_DebitoBoleto` ⨝ `Exe_Debito`, 6.214 pagamentos,
# R$ 3,65 mi) e 100% dos repasses da PGE (`PGE_Pagamento` ⨝ `PGE_Processo` ⨝
# `Exe_Debito`) são de multa. É o que a norma manda: multa só se quita por guia
# bancária (Res. 013/2015, art. 3º) e ressarcimento é recolhido ao ente credor
# (art. 2º), sem passar pelo caixa do Fundo.
SQL_BOLETO = """
SELECT YEAR(r.DataPagamento) AS ano, 'boleto_confirmado' AS origem, SUM(r.ValorPago) AS valor
  FROM processo.dbo.Exe_Retorno_Boleto r
 WHERE r.DataPagamento IS NOT NULL
   AND YEAR(r.DataPagamento) BETWEEN :de AND :ate
 GROUP BY YEAR(r.DataPagamento)
"""

SQL_PGE = """
SELECT YEAR(p.DataPagamento) AS ano, 'repasse_pge' AS origem,
       SUM(COALESCE(p.ValorPrincipal, 0) + COALESCE(p.Multa, 0) + COALESCE(p.Juros, 0)) AS valor
  FROM processo.dbo.PGE_Pagamento p
 WHERE p.DataPagamento IS NOT NULL
   AND YEAR(p.DataPagamento) BETWEEN :de AND :ate
 GROUP BY YEAR(p.DataPagamento)
"""

# A comparação só é legítima nos meses em que o extrato foi publicado. Sem isto, um
# ano parcial (2026 vai até junho) aparece como se a arrecadação tivesse caído.
SQL_COBERTURA = """
-- `Periodo` é char 'MMAAAA': ordenar direto colocaria 122025 depois de 062026.
SELECT c.Conta,
       MIN(RIGHT(a.Periodo, 4) + LEFT(a.Periodo, 2)) AS primeiro_periodo,
       MAX(RIGHT(a.Periodo, 4) + LEFT(a.Periodo, 2)) AS ultimo_periodo,
       COUNT(*) AS meses_publicados
  FROM BdDIP.dbo.FRAPExtratoArquivo a
  JOIN BdDIP.dbo.FRAPConta c ON c.IdConta = a.IdConta
 GROUP BY c.Conta
"""

COLUNAS = [
    "OB_RECEBIDA", "GUIA_RECEBIMENTO", "TRANSFERENCIA", "OUTROS", "caixa_frap",
    "boleto_confirmado", "repasse_pge", "identificado", "nao_identificado",
    "baixa_multa", "baixa_ressarcimento",
]


def carregar(de: int, ate: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    caixa = run_query_df(SQL_CAIXA, de=de, ate=ate)
    competencia = pd.concat(
        [run_query_df(sql, de=de, ate=ate) for sql in (SQL_BAIXA, SQL_BOLETO, SQL_PGE)],
        ignore_index=True,
    )
    return caixa, competencia


def consolidar(caixa: pd.DataFrame, competencia: pd.DataFrame, de: int, ate: int) -> pd.DataFrame:
    """Uma linha por ano, as duas lentes lado a lado e o resíduo não identificado."""
    anos = list(range(de, ate + 1))
    piv_caixa = (caixa.pivot_table(index="ano", columns="categoria", values="valor", aggfunc="sum")
                 .reindex(anos))
    piv_comp = (competencia.pivot_table(index="ano", columns="origem", values="valor", aggfunc="sum")
                .reindex(anos))
    df = piv_caixa.join(piv_comp, how="outer").reindex(anos)
    for col in COLUNAS:
        if col not in df.columns:
            df[col] = 0.0
    df = df.fillna(0.0).astype(float)

    df["caixa_frap"] = df[["OB_RECEBIDA", "GUIA_RECEBIMENTO", "TRANSFERENCIA", "OUTROS"]].sum(axis=1)
    # O que a lente de competência consegue nomear dentro do caixa do Fundo: boleto
    # confirmado pelo banco + repasse da PGE. O resto entra por ordem bancária de
    # desconto em folha e por TED/PIX de prefeituras, sem vínculo com o crédito.
    df["identificado"] = df["boleto_confirmado"] + df["repasse_pge"]
    df["nao_identificado"] = df["caixa_frap"] - df["identificado"]
    df["cobertura_%"] = (100 * df["identificado"] / df["caixa_frap"].where(df["caixa_frap"] != 0)).round(1)

    df = df[COLUNAS + ["cobertura_%"]].round(2)
    df.loc["TOTAL"] = df.sum(numeric_only=True)
    total = df.loc["TOTAL"]
    df.loc["TOTAL", "cobertura_%"] = round(100 * total["identificado"] / total["caixa_frap"], 1)
    return df.reset_index(names="ano")


def _asserts(df: pd.DataFrame) -> None:
    corpo = df[df["ano"] != "TOTAL"]
    soma = df[df["ano"] == "TOTAL"].iloc[0]
    for col in ("caixa_frap", "identificado", "baixa_multa"):
        assert abs(corpo[col].sum() - soma[col]) < 0.01, f"TOTAL não fecha em {col}"
    assert (abs(corpo["caixa_frap"]
                - corpo[["OB_RECEBIDA", "GUIA_RECEBIMENTO", "TRANSFERENCIA", "OUTROS"]].sum(axis=1))
            < 0.01).all(), "caixa_frap não é a soma das categorias"
    assert (abs(corpo["nao_identificado"] - (corpo["caixa_frap"] - corpo["identificado"]))
            < 0.01).all(), "resíduo não fecha"
    assert (corpo["caixa_frap"] >= -0.01).all(), "caixa negativo — crédito não pode ser negativo"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--de", type=int, default=2021)
    ap.add_argument("--ate", type=int, default=2026)
    ap.add_argument("--self-check", action="store_true", help="roda os asserts e sai")
    args = ap.parse_args()

    if args.self_check:
        _self_check()
        print("self-check OK")
        return

    df = consolidar(*carregar(args.de, args.ate), args.de, args.ate)
    _asserts(df)

    destino = OUTPUT_DIR / "analise" / "ipsas"
    destino.mkdir(parents=True, exist_ok=True)
    saida = destino / f"conciliacao_competencia_caixa_{args.de}_{args.ate}.xlsx"
    df.to_excel(saida, sheet_name="competencia_x_caixa", index=False)

    print(df.to_string(index=False))
    print("\nCobertura dos extratos publicados (a série de caixa só existe onde há extrato):")
    print(run_query_df(SQL_COBERTURA).to_string(index=False))
    print(f"\n-> {saida}")


def _self_check() -> None:
    caixa = pd.DataFrame([
        (2021, "OB_RECEBIDA", 100.0),
        (2021, "GUIA_RECEBIMENTO", 40.0),
        (2022, "TRANSFERENCIA", 25.0),
        (2022, "OUTROS", 5.0),
    ], columns=["ano", "categoria", "valor"])
    competencia = pd.DataFrame([
        (2021, "boleto_confirmado", 40.0),
        (2021, "repasse_pge", 30.0),
        (2021, "baixa_multa", 60.0),
        (2021, "baixa_ressarcimento", 900.0),
        (2022, "boleto_confirmado", 5.0),
    ], columns=["ano", "origem", "valor"])

    df = consolidar(caixa, competencia, 2021, 2022)
    _asserts(df)

    linha = df.set_index("ano")
    assert linha.loc[2021, "caixa_frap"] == 140.0, linha.loc[2021, "caixa_frap"]
    assert linha.loc[2021, "identificado"] == 70.0
    assert linha.loc[2021, "nao_identificado"] == 70.0
    assert linha.loc[2021, "cobertura_%"] == 50.0
    # Ressarcimento não entra no FRAP: os 900 de baixa não podem contaminar o caixa.
    assert linha.loc[2021, "baixa_ressarcimento"] == 900.0
    assert linha.loc[2022, "caixa_frap"] == 30.0
    assert linha.loc["TOTAL", "caixa_frap"] == 170.0
    assert linha.loc["TOTAL", "identificado"] == 75.0


if __name__ == "__main__":
    sys.exit(main())
