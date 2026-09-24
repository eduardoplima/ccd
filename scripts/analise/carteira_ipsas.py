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

from ccd.config import OUTPUT_DIR
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
#
# O grão é a **cadeia**, não a linha. `Exe_Debito.IdDebitoAnterior` encadeia versões
# sucessivas do mesmo crédito: registrar um pagamento fecha o nó atual e cria um filho
# com o saldo remanescente. Logo:
#   - a identidade do crédito é a **raiz** (o valor imputado na decisão);
#   - a situação vigente é a da **folha** (o nó sem filho);
#   - o recuperado é a **soma de ValorPago em toda a cadeia**.
# Filtrar `IdDebitoAnterior IS NULL` e ler status/pago da raiz — como esta consulta
# fazia até 14/08/2026 — devolve o débito ORIGINAL, não o vigente: 1.602 das 17.115
# raízes têm filho, e nelas o status e o ValorPago da raiz estão congelados no
# primeiro pagamento. Ver `docs/notas/ANALISE_CHAMADO_DEBITOS_STATUS3.md`, Anexo B.
SQL = """
WITH pge AS (
    SELECT DISTINCT pp.IdDebitoExecucao AS IdDebito
      FROM processo.dbo.PGE_Processo pp
     WHERE pp.IdDebitoExecucao IS NOT NULL
),
cadeia AS (
    SELECT r.IdDebito AS id_raiz, r.IdDebito AS id_no, 0 AS nivel
      FROM processo.dbo.Exe_Debito r
     WHERE r.IdDebitoAnterior IS NULL
    UNION ALL
    SELECT c.id_raiz, f.IdDebito, c.nivel + 1
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito f ON f.IdDebitoAnterior = c.id_no
),
folhas AS (
    SELECT c.id_raiz, e.*,
           COUNT(*)     OVER (PARTITION BY c.id_raiz) AS folhas_na_cadeia,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz
                              ORDER BY c.nivel DESC, e.datainclusao DESC, e.IdDebito DESC) AS rn
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
     WHERE NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito g
                        WHERE g.IdDebitoAnterior = e.IdDebito)
),
agregado AS (
    SELECT c.id_raiz,
           COUNT(*)                            AS nos_na_cadeia,
           SUM(COALESCE(e.ValorPago, 0))       AS valor_recuperado,
           MIN(e.dataTransito)                 AS data_transito,
           -- Protesto e inscrição em dívida ativa são atributos da cobrança do
           -- crédito, não do registro: valem se ocorreram em qualquer nó da cadeia.
           MAX(CASE WHEN e.StatusProtesto IS NOT NULL AND e.StatusProtesto <> 0
                    THEN 1 ELSE 0 END)         AS flag_protesto,
           -- `Exe_Debito.Status_PGE` é bit e vem incompleto (612 folhas marcadas
           -- contra 1.425 débitos efetivamente em `PGE_Processo`). A fonte da
           -- inscrição em dívida ativa é `PGE_Processo`, que traz CDA e valor.
           MAX(CASE WHEN pge.IdDebito IS NOT NULL THEN 1 ELSE 0 END) AS flag_pge
      FROM cadeia c
      JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
      LEFT JOIN pge ON pge.IdDebito = e.IdDebito
     GROUP BY c.id_raiz
)
SELECT
    r.IdDebito                  AS id_debito,
    f.IdDebito                  AS id_debito_vigente,
    a.nos_na_cadeia             AS nos_na_cadeia,
    f.folhas_na_cadeia          AS folhas_na_cadeia,
    r.CodigoTipoDebito          AS cod_tipo,
    f.CodigoStatusDivida        AS cod_status,
    r.valorOriginalDebito       AS valor_original,
    a.valor_recuperado          AS valor_recuperado,
    f.valorOriginalDebito       AS saldo_registrado,
    r.dataDecisao               AS data_decisao,
    a.data_transito             AS data_transito,
    f.dataBaixa                 AS data_baixa,
    a.flag_protesto             AS status_protesto,
    a.flag_pge                  AS flag_pge,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
       FROM processo.dbo.Processos p
      WHERE p.IdProcesso = COALESCE(r.IdProcessoOrigem, f.IdProcessoOrigem))     AS processo_origem,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
       FROM processo.dbo.Processos p
      WHERE p.IdProcesso = COALESCE(r.IdProcessoExecucao, f.IdProcessoExecucao)) AS processo_execucao
FROM processo.dbo.Exe_Debito r
JOIN agregado a ON a.id_raiz = r.IdDebito
JOIN folhas   f ON f.id_raiz = r.IdDebito AND f.rn = 1
WHERE r.IdDebitoAnterior IS NULL
  AND (r.dataDecisao IS NULL OR r.dataDecisao <= :data_corte)
OPTION (MAXRECURSION 0)
"""


def carregar(data_corte: date) -> pd.DataFrame:
    """Busca os créditos (cadeias de débito) vigentes até a data de corte.

    O grão é o débito, não a pessoa: `Exe_DebitoPessoa` liga N responsáveis
    solidários ao mesmo crédito, e juntar a tabela aqui multiplicaria os valores
    da carteira. Solidariedade é matéria de divulgação, não de mensuração.

    ponytail: quando uma cadeia bifurca (351 pais têm mais de um filho — duplo
    registro do mesmo pagamento, ver `debitos_status3_orfaos.py`), a folha eleita é
    a mais profunda e, no empate, a de `datainclusao` mais recente. As demais folhas
    da mesma cadeia são ignoradas e contadas em `folhas_na_cadeia`; o resumo publica
    quantas foram. Trocar por reconciliação caso a caso se a SETIC sanear os forks.
    """
    return run_query_df(SQL, data_corte=data_corte)


def classificar(df: pd.DataFrame, data_corte: date) -> pd.DataFrame:
    """Atribui a cada débito o estado IPSAS, o aging e a mensuração."""
    df = df.copy()
    # Colunas de cadeia: vêm do SQL, mas o self-check monta os créditos já agregados.
    for col, padrao in (("id_debito_vigente", None), ("nos_na_cadeia", 1), ("folhas_na_cadeia", 1)):
        if col not in df.columns:
            df[col] = df["id_debito"] if padrao is None else padrao
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
        # Transparência do critério de grão: quantos créditos são cadeia de mais de um
        # registro e em quantos a cadeia bifurcou (folha eleita, irmãs descartadas).
        ("Créditos com cadeia de mais de um registro", 0.0,
         int((df["nos_na_cadeia"] > 1).sum())),
        ("Créditos com cadeia bifurcada (folhas descartadas)",
         float((df["folhas_na_cadeia"] - 1).clip(lower=0).sum()),
         int((df["folhas_na_cadeia"] > 1).sum())),
    ]
    return pd.DataFrame(linhas, columns=["indicador", "valor", "quantidade"])


COLUNAS_SAIDA = [
    "id_debito", "id_debito_vigente", "nos_na_cadeia", "folhas_na_cadeia",
    "processo_origem", "processo_execucao", "tipo_debito",
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

    destino = OUTPUT_DIR / "analise" / "ipsas"
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
    # Uma linha por cadeia: a raiz identifica o crédito e não pode repetir.
    assert not df["id_debito"].duplicated().any(), "cadeia devolvida mais de uma vez"
    assert (df["nos_na_cadeia"] >= 1).all(), "cadeia sem nós"
    saldo_matriz = m["saldo_reconhecido"].sum()
    saldo_df = df.loc[df["estado_ipsas"] == "RECONHECIDO", "saldo"].sum()
    assert abs(saldo_matriz - saldo_df) < 0.01, \
        f"buckets não fecham com a carteira: {saldo_matriz} != {saldo_df}"


def _self_check() -> None:
    corte = date(2026, 1, 1)
    # 10 créditos cobrindo cada caminho da classificação. Os 7 primeiros têm trânsito
    # em 2020 e caem no bucket "5-10 anos", onde a matriz fica conferível na mão; os
    # 3 últimos exercem o grão de cadeia e ficam isolados no bucket "2-3 anos".
    #
    # Cada linha já chega agregada por cadeia, como o SQL devolve: `valor_original` é
    # o da raiz, `cod_status` é o da folha e `valor_recuperado` é a soma da cadeia.
    bruto = pd.DataFrame([
        # id, tipo, status,  valor,   pago, decisão,      trânsito,     baixa,        nós, folhas
        (1, 2, 1, 1000.0, 0.0, "2019-01-01", "2020-01-01", None, 1, 1),   # reconhecido
        (2, 2, 6, 1000.0, 0.0, "2019-01-01", "2020-01-01", "2025-01-01", 1, 1),  # prescrito
        (3, 1, 2, 400.0, 400.0, "2019-01-01", "2020-01-01", "2021-01-01", 1, 1),  # pago
        (4, 2, 1, 700.0, 0.0, "2025-06-01", None, None, 1, 1),            # contingente
        (5, 2, 15, 900.0, 0.0, "2019-01-01", "2020-01-01", None, 1, 1),   # erro de cadastro
        (6, 1, 19, 300.0, 0.0, "2019-01-01", "2020-01-01", "2024-01-01", 1, 1),  # decisão judicial
        (7, 1, 3, 250.0, 100.0, "2019-01-01", "2020-01-01", None, 1, 1),  # pago parcialmente
        # Cadeia de 3 níveis quitada: a folha está em "Pago Integralmente" e o
        # recuperado (520, com correção) supera o imputado. Lendo a raiz, este crédito
        # apareceria como "Pago parcialmente" e em aberto.
        (8, 2, 2, 500.0, 520.0, "2023-01-01", "2024-01-01", "2025-06-01", 3, 1),
        # Cadeia bifurcada: 4 nós, 2 folhas. Vale a folha eleita; a irmã é descartada.
        (9, 1, 1, 800.0, 200.0, "2023-01-01", "2024-01-01", None, 4, 2),
        # Cadeia cuja folha é erro de cadastro: sai da base inteira.
        (10, 2, 15, 600.0, 0.0, "2023-01-01", "2024-01-01", None, 2, 1),
    ], columns=["id_debito", "cod_tipo", "cod_status", "valor_original", "valor_recuperado",
                "data_decisao", "data_transito", "data_baixa",
                "nos_na_cadeia", "folhas_na_cadeia"])
    bruto["status_protesto"] = None
    bruto["flag_pge"] = None
    bruto["processo_origem"] = None
    bruto["processo_execucao"] = None

    df = classificar(bruto, corte)
    df = df[df["estado_ipsas"] != "NAO_ATIVO"]
    m = matriz_ecl(df)
    _asserts(df, m)

    estados = dict(zip(df["id_debito"], df["estado_ipsas"], strict=True))
    assert estados == {1: "RECONHECIDO", 2: "BAIXADO_PERDA", 3: "REALIZADO",
                       4: "CONTINGENTE", 6: "DESRECONHECIDO", 7: "RECONHECIDO",
                       8: "REALIZADO", 9: "RECONHECIDO"}, estados
    assert 5 not in estados, "erro de cadastro tinha que ter saído da base"
    assert 10 not in estados, "cadeia com folha em erro de cadastro tinha que sair"

    # Cadeia quitada: recuperado acima do imputado não pode virar saldo negativo.
    saldos = dict(zip(df["id_debito"], df["saldo"], strict=True))
    assert saldos[8] == 0.0, saldos[8]
    assert abs(saldos[9] - 600.0) < 0.01, saldos[9]

    cadeia = m.set_index("bucket_aging").loc["2-3 anos"]
    # Nada perdido nessa faixa; recuperado 520 + 200 = 720 -> taxa 0, provisão 0.
    assert abs(cadeia["valor_recuperado"] - 720.0) < 0.01, cadeia["valor_recuperado"]
    assert cadeia["taxa_perda"] == 0.0, cadeia["taxa_perda"]
    assert abs(cadeia["saldo_reconhecido"] - 600.0) < 0.01, cadeia["saldo_reconhecido"]

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

    # Créditos 8 e 9 são cadeia; só o 9 bifurcou, descartando uma folha.
    idx = resumo.set_index("indicador")
    assert int(idx.loc["Créditos com cadeia de mais de um registro", "quantidade"]) == 2
    assert int(idx.loc["Créditos com cadeia bifurcada (folhas descartadas)", "quantidade"]) == 1
    assert float(idx.loc["Créditos com cadeia bifurcada (folhas descartadas)", "valor"]) == 1.0


if __name__ == "__main__":
    sys.exit(main())
