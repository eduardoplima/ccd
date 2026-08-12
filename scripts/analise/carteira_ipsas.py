"""Carteira de créditos da CCD sob a ótica das IPSAS.

Lê `Exe_Debito` e reclassifica cada crédito (multa, ressarcimento) nos estados que
as normas exigem, produzindo uma planilha com a carteira, a matriz de perda
esperada e o resumo para nota explicativa.

Normas em jogo:

- **IPSAS 23** (receita de transações sem contraprestação): multas são citadas
  nominalmente. O ativo é reconhecido quando a entidade controla o recurso — aqui,
  no **trânsito em julgado** (`dataTransito`). Antes disso não há ativo.
- **IPSAS 19** (ativos contingentes): condenação sem trânsito não é reconhecida,
  apenas divulgada. É o estado CONTINGENTE.
- **IPSAS 41** (instrumentos financeiros): perda de crédito esperada por matriz de
  provisão baseada em aging, calibrada com o histórico de prescrições do próprio
  Tribunal.

Uso:
    python -m scripts.analise.carteira_ipsas                  # data de corte = hoje
    python -m scripts.analise.carteira_ipsas --data-corte 2025-12-31
    python -m scripts.analise.carteira_ipsas --self-check     # não acessa o banco
"""
from __future__ import annotations

import argparse
import sys
from datetime import date

import pandas as pd

from ccd.config import REPO_ROOT
from ccd.db import run_query_df

# ---------------------------------------------------------------------------
# Classificação contábil dos códigos de Exe_StatusDivida.
#
# As descrições aqui repetem as de `Exe_StatusDivida` de propósito: o pymssql
# devolve a coluna do banco com acentuação corrompida, e a planilha é para leitura
# humana. A classificação é sempre pelo código, nunca pelo texto.
#
# Quatro destinos, e a distinção entre os três últimos é o ponto contábil do
# exercício — o banco trata tudo como "Cancelada", mas as normas não:
#   REALIZADO      o crédito entrou (baixa por pagamento)
#   BAIXADO_PERDA  o crédito existia e não entrou -> é perda de crédito (IPSAS 41),
#                  e é o que calibra a matriz de provisão
#   DESRECONHECIDO o direito deixou de existir por decisão superveniente -> não é
#                  perda de crédito, é reversão de receita; polui a matriz se for
#                  contado como perda
#   NAO_ATIVO      nunca foi ativo (erro de cadastro, duplicidade, substituição);
#                  sai da base inteira
# ---------------------------------------------------------------------------
STATUS_DIVIDA: dict[int, tuple[str, str]] = {
    1: ("Em Aberto", "ABERTO"),
    2: ("Pago Integralmente", "REALIZADO"),
    3: ("Pago parcialmente", "ABERTO"),
    4: ("Cancelada por extinção", "BAIXADO_PERDA"),
    5: ("Cancelada por Alteração", "NAO_ATIVO"),
    6: ("Cancelada por prescrição", "BAIXADO_PERDA"),
    7: ("Cancelada por decisão do relator", "DESRECONHECIDO"),
    8: ("Parcelado", "ABERTO"),
    9: ("Pago Aguardando Compensação", "REALIZADO"),
    10: ("Cancelada por Perdão de Dívida", "BAIXADO_PERDA"),
    13: ("Cancelada por Reabertura de Parcelamento", "NAO_ATIVO"),
    14: ("Cancelada por Reabertura de Dívida Paga Parcialmente", "NAO_ATIVO"),
    15: ("Cancelada por Erro de Cadastro", "NAO_ATIVO"),
    16: ("Cancelada por Decisão em novo Acórdão", "DESRECONHECIDO"),
    17: ("Cancelada por Óbito do Gestor", "BAIXADO_PERDA"),
    18: ("Cancelada por Unificação da Dívida", "NAO_ATIVO"),
    19: ("Cancelada por Decisão Judicial", "DESRECONHECIDO"),
    20: ("Suspenso", "ABERTO"),
    21: ("Cancelado por duplicidade", "NAO_ATIVO"),
}

TIPO_DEBITO = {
    1: "Ressarcimento",
    2: "Multa",
    3: "Remanejamento",
    4: "Multa Percentual",
    5: "Multa Cominatória",
}

# Buckets de aging em anos completos desde o trânsito em julgado. O último é aberto.
BUCKETS = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 10), (10, 999)]
ROTULO_BUCKET = ["0-1 ano", "1-2 anos", "2-3 anos", "3-5 anos", "5-10 anos", "10+ anos"]

# ponytail: mensuração pelo valor original. `ValorAPagar` existe na tabela mas está
# NULL em 10.144 dos 10.155 débitos em aberto — o campo nunca foi alimentado. Não há
# saldo atualizado utilizável no banco, então a carteira sai a valor histórico e a
# nota explicativa registra a limitação. Trocar por ValorAPagar quando/se o sistema
# de cobrança passar a mantê-lo.
SQL = """
SELECT
    e.IdDebito                  AS id_debito,
    e.CodigoTipoDebito          AS cod_tipo,
    e.CodigoStatusDivida        AS cod_status,
    e.valorOriginalDebito       AS valor_original,
    e.ValorPago                 AS valor_recuperado,
    e.dataDecisao               AS data_decisao,
    e.dataTransito              AS data_transito,
    e.dataBaixa                 AS data_baixa,
    e.StatusProtesto            AS status_protesto,
    e.Status_PGE                AS flag_pge,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
       FROM processo.dbo.Processos p
      WHERE p.IdProcesso = e.IdProcessoOrigem)   AS processo_origem,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
       FROM processo.dbo.Processos p
      WHERE p.IdProcesso = e.IdProcessoExecucao) AS processo_execucao
FROM processo.dbo.Exe_Debito e
WHERE e.IdDebitoAnterior IS NULL
  AND (e.dataDecisao IS NULL OR e.dataDecisao <= :data_corte)
"""


def carregar(data_corte: date) -> pd.DataFrame:
    """Busca os débitos vigentes até a data de corte.

    O grão é o débito, não a pessoa: `Exe_DebitoPessoa` liga N responsáveis
    solidários ao mesmo crédito, e juntar a tabela aqui multiplicaria os valores
    da carteira. Solidariedade é matéria de divulgação, não de mensuração.
    """
    return run_query_df(SQL, data_corte=data_corte)


def classificar(df: pd.DataFrame, data_corte: date) -> pd.DataFrame:
    """Atribui a cada débito o estado IPSAS, o aging e a mensuração."""
    df = df.copy()
    df["tipo_debito"] = df["cod_tipo"].map(TIPO_DEBITO).fillna("Não informado")
    df["situacao_divida"] = df["cod_status"].map(lambda c: STATUS_DIVIDA.get(c, ("Desconhecido", "ABERTO"))[0])
    destino = df["cod_status"].map(lambda c: STATUS_DIVIDA.get(c, ("Desconhecido", "ABERTO"))[1])

    df["valor_original"] = pd.to_numeric(df["valor_original"], errors="coerce").fillna(0.0)
    df["valor_recuperado"] = pd.to_numeric(df["valor_recuperado"], errors="coerce").fillna(0.0)
    # Saldo devedor = original menos o que já entrou. Sem isso os 1.361 créditos
    # pagos parcialmente entrariam na carteira pelo valor cheio, inflando o ativo.
    # `ValorPago` inclui correção e juros, então o piso em zero não é decorativo.
    df["saldo"] = (df["valor_original"] - df["valor_recuperado"]).clip(lower=0.0)
    transito = pd.to_datetime(df["data_transito"], errors="coerce")
    df["data_transito"] = transito

    # IPSAS 23: sem trânsito não há controle do recurso, logo não há ativo. Um
    # crédito sem trânsito só é contingente enquanto ainda está vivo — se já foi
    # cancelado, nunca chegou a existir e não é nem contingente.
    tem_transito = transito.notna()
    df["estado_ipsas"] = destino.where(tem_transito, other="CONTINGENTE")
    df.loc[~tem_transito & (destino != "ABERTO"), "estado_ipsas"] = "NAO_ATIVO"
    df.loc[tem_transito & (destino == "ABERTO"), "estado_ipsas"] = "RECONHECIDO"

    corte = pd.Timestamp(data_corte)
    df["anos_desde_transito"] = ((corte - transito).dt.days / 365.25).round(2)
    df["bucket_aging"] = pd.cut(
        df["anos_desde_transito"],
        bins=[b[0] for b in BUCKETS] + [BUCKETS[-1][1]],
        labels=ROTULO_BUCKET,
        right=False,
    )

    df["em_protesto"] = df["status_protesto"].notna() & (df["status_protesto"] != 0)
    df["em_divida_ativa"] = df["flag_pge"].notna() & (df["flag_pge"] != 0)
    return df


def matriz_ecl(df: pd.DataFrame) -> pd.DataFrame:
    """Matriz de provisão do IPSAS 41, calibrada pelo histórico do próprio Tribunal.

    Para cada faixa de aging: do valor que já teve desfecho, que fração virou perda.
    O denominador soma o perdido com o **efetivamente recuperado** — inclusive as
    recuperações parciais de créditos ainda abertos, que são caixa que entrou e
    contam contra a taxa de perda. Essa taxa é aplicada ao saldo ainda reconhecido
    da mesma faixa.

    ponytail: matriz de aging simples, sem segmentar por tipo de débito nem por
    situação de cobrança. Duas limitações que a nota explicativa precisa registrar:
    (a) censura à direita — créditos antigos ainda abertos podem vir a prescrever, o
    que subestima a taxa das faixas longas; (b) a taxa é retrospectiva, não
    prospectiva como a norma pede. Corrigir com análise de sobrevivência se a
    provisão virar número oficial.
    """
    def por_bucket(d: pd.DataFrame, col: str) -> pd.Series:
        return d.groupby("bucket_aging", observed=False)[col].sum()

    m = pd.DataFrame({
        "valor_perdido": por_bucket(df[df["estado_ipsas"] == "BAIXADO_PERDA"], "valor_original"),
        "valor_recuperado": por_bucket(df, "valor_recuperado"),
        "saldo_reconhecido": por_bucket(df[df["estado_ipsas"] == "RECONHECIDO"], "saldo"),
    }).reindex(ROTULO_BUCKET).fillna(0.0)
    m["valor_resolvido"] = m["valor_perdido"] + m["valor_recuperado"]
    m["taxa_perda"] = (m["valor_perdido"] / m["valor_resolvido"]).fillna(0.0).clip(0.0, 1.0)
    m["provisao"] = (m["saldo_reconhecido"] * m["taxa_perda"]).round(2)
    m["valor_liquido"] = (m["saldo_reconhecido"] - m["provisao"]).round(2)
    return m.reset_index(names="bucket_aging")


def resumir(df: pd.DataFrame, m: pd.DataFrame) -> pd.DataFrame:
    """Números para a nota explicativa."""
    def total(estado: str) -> float:
        return float(df.loc[df["estado_ipsas"] == estado, "valor_original"].sum())

    def qtd(estado: str) -> int:
        return int((df["estado_ipsas"] == estado).sum())

    bruto = float(m["saldo_reconhecido"].sum())
    provisao = float(m["provisao"].sum())
    linhas = [
        ("Ativo reconhecido, bruto (IPSAS 23)", bruto, qtd("RECONHECIDO")),
        ("Provisão para perdas esperadas (IPSAS 41)", -provisao, 0),
        ("Ativo reconhecido, líquido", bruto - provisao, qtd("RECONHECIDO")),
        ("Taxa média de provisão (%)", round(100 * provisao / bruto, 2) if bruto else 0.0, 0),
        ("Ativo contingente, apenas divulgado (IPSAS 19)", total("CONTINGENTE"), qtd("CONTINGENTE")),
        ("Perdas históricas acumuladas", total("BAIXADO_PERDA"), qtd("BAIXADO_PERDA")),
        ("Receita efetivamente recuperada", float(df["valor_recuperado"].sum()),
         int((df["valor_recuperado"] > 0).sum())),
        ("Desreconhecido por decisão superveniente", total("DESRECONHECIDO"), qtd("DESRECONHECIDO")),
    ]
    return pd.DataFrame(linhas, columns=["indicador", "valor", "quantidade"])


COLUNAS_SAIDA = [
    "id_debito", "processo_origem", "processo_execucao", "tipo_debito",
    "situacao_divida", "estado_ipsas", "valor_original", "valor_recuperado", "saldo",
    "data_transito", "anos_desde_transito", "bucket_aging", "em_protesto", "em_divida_ativa",
]


def executar(data_corte: date) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = classificar(carregar(data_corte), data_corte)
    df = df[df["estado_ipsas"] != "NAO_ATIVO"]
    m = matriz_ecl(df)
    return df, m, resumir(df, m)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-corte", type=date.fromisoformat, default=date.today(),
                    help="data-base da carteira (AAAA-MM-DD); padrão hoje")
    ap.add_argument("--self-check", action="store_true", help="roda os asserts e sai")
    args = ap.parse_args()

    if args.self_check:
        _self_check()
        print("self-check OK")
        return

    df, m, resumo = executar(args.data_corte)
    _asserts(df, m)

    destino = REPO_ROOT / "saidas" / "analise" / "ipsas"
    destino.mkdir(parents=True, exist_ok=True)
    saida = destino / f"carteira_ipsas_{args.data_corte:%Y%m%d}.xlsx"
    with pd.ExcelWriter(saida) as xls:
        df[COLUNAS_SAIDA].to_excel(xls, sheet_name="carteira", index=False)
        m.to_excel(xls, sheet_name="matriz_ecl", index=False)
        resumo.to_excel(xls, sheet_name="resumo", index=False)

    print(resumo.to_string(index=False))
    print(f"\n{len(df)} créditos -> {saida}")


def _asserts(df: pd.DataFrame, m: pd.DataFrame) -> None:
    """Invariantes que valem tanto para os dados reais quanto para os sintéticos."""
    assert df["estado_ipsas"].notna().all(), "há crédito sem estado IPSAS"
    assert "NAO_ATIVO" not in set(df["estado_ipsas"]), "NAO_ATIVO deveria ter saído da base"
    assert df.loc[df["estado_ipsas"] == "CONTINGENTE", "data_transito"].isna().all(), \
        "contingente não pode ter trânsito em julgado"
    assert df.loc[df["estado_ipsas"] == "RECONHECIDO", "data_transito"].notna().all(), \
        "reconhecido exige trânsito em julgado"
    assert m["taxa_perda"].between(0, 1).all(), "taxa de perda fora de [0,1]"
    assert (df["saldo"] <= df["valor_original"] + 0.01).all(), "saldo maior que o valor original"
    saldo_matriz = m["saldo_reconhecido"].sum()
    saldo_df = df.loc[df["estado_ipsas"] == "RECONHECIDO", "saldo"].sum()
    assert abs(saldo_matriz - saldo_df) < 0.01, \
        f"buckets não fecham com a carteira: {saldo_matriz} != {saldo_df}"


def _self_check() -> None:
    corte = date(2026, 1, 1)
    # 7 créditos cobrindo cada caminho da classificação. Todos com trânsito em
    # 2020 caem no bucket "5-10 anos" para a matriz ficar conferível na mão.
    bruto = pd.DataFrame([
        # id, tipo, status,       valor,   pago, decisão,      trânsito,     baixa
        (1, 2, 1, 1000.0, 0.0, "2019-01-01", "2020-01-01", None),   # reconhecido
        (2, 2, 6, 1000.0, 0.0, "2019-01-01", "2020-01-01", "2025-01-01"),  # prescrito
        (3, 1, 2, 400.0, 400.0, "2019-01-01", "2020-01-01", "2021-01-01"),  # pago
        (4, 2, 1, 700.0, 0.0, "2025-06-01", None, None),            # contingente
        (5, 2, 15, 900.0, 0.0, "2019-01-01", "2020-01-01", None),   # erro de cadastro
        (6, 1, 19, 300.0, 0.0, "2019-01-01", "2020-01-01", "2024-01-01"),  # decisão judicial
        (7, 1, 3, 250.0, 100.0, "2019-01-01", "2020-01-01", None),  # pago parcialmente
    ], columns=["id_debito", "cod_tipo", "cod_status", "valor_original", "valor_recuperado",
                "data_decisao", "data_transito", "data_baixa"])
    bruto["status_protesto"] = None
    bruto["flag_pge"] = None
    bruto["processo_origem"] = None
    bruto["processo_execucao"] = None

    df = classificar(bruto, corte)
    df = df[df["estado_ipsas"] != "NAO_ATIVO"]
    m = matriz_ecl(df)
    _asserts(df, m)

    estados = dict(zip(df["id_debito"], df["estado_ipsas"]))
    assert estados == {1: "RECONHECIDO", 2: "BAIXADO_PERDA", 3: "REALIZADO",
                       4: "CONTINGENTE", 6: "DESRECONHECIDO", 7: "RECONHECIDO"}, estados
    assert 5 not in estados, "erro de cadastro tinha que ter saído da base"

    faixa = m.set_index("bucket_aging").loc["5-10 anos"]
    # Perdido 1000; recuperado 400 (pago) + 100 (parcial) = 500 -> taxa 1000/1500 = 2/3.
    # O desreconhecido de 300 fica fora do cálculo: direito extinto por decisão
    # superveniente não é perda de crédito.
    assert abs(faixa["taxa_perda"] - 2 / 3) < 1e-9, faixa["taxa_perda"]
    # Saldo = 1000 (íntegro) + 150 (250 menos os 100 já pagos).
    assert abs(faixa["saldo_reconhecido"] - 1150.0) < 0.01, faixa["saldo_reconhecido"]
    assert abs(faixa["provisao"] - round(1150 * 2 / 3, 2)) < 0.01, faixa["provisao"]

    resumo = resumir(df, m)
    contingente = resumo.loc[resumo["indicador"].str.startswith("Ativo contingente"), "valor"]
    assert abs(float(contingente.iloc[0]) - 700.0) < 0.01, "contingente errado"


if __name__ == "__main__":
    sys.exit(main())
