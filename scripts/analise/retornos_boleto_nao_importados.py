"""Dinheiro que o banco creditou e o sistema de execução não registrou.

O BB deposita todo dia útil o total das guias pagas (histórico "617 Recebimento de
guias" no extrato do FRAP) e manda um arquivo de retorno com o detalhe boleto a boleto.
`Exe_Retorno` guarda o total declarado no arquivo; `Exe_Retorno_Boleto`, as linhas que a
rotina de importação conseguiu aceitar. **Quando os dois não batem, entrou dinheiro na
conta sem baixar o crédito correspondente** — o pagamento existe no extrato e some da
carteira.

O motivo dominante é `"Boleto ID = N já está com status pago"`: um pagamento anterior
marcou o boleto como quitado, e o pagamento de verdade é recusado na importação. Basta
um crédito irrisório contra o boleto (R$ 1,01, R$ 2,02) para envenenar a linha — daí a
terceira aba.

Caso que originou o script: processo 004164/2020, débito 23232, parcela 10 (venc.
27/02/2026, R$ 948,27). Em 06/02/2026 um pagamento de R$ 2,02 marcou o boleto 36991 como
pago; em 27/02 o responsável pagou os R$ 948,27, o crédito entrou no arquivo
`rcb001.bco001.28022601180287` (60 boletos, R$ 24.843,18, creditado em 02/03/2026) e a
linha 41 foi rejeitada. O arquivo importou 59 boletos e R$ 23.894,91 — exatamente
R$ 948,27 a menos.

Uso:
    python -m scripts.analise.retornos_boleto_nao_importados
    python -m scripts.analise.retornos_boleto_nao_importados --desde 2026-01-01
    python -m scripts.analise.retornos_boleto_nao_importados --self-check
"""
from __future__ import annotations

import argparse
import sys

import pandas as pd

from ccd.config import OUTPUT_DIR
from ccd.db import run_query_df

# Tolerância de centavo: `ValorTotal` e `ValorPago` são `money`, o mesmo critério do
# matcher de guia do FRAP (`frap/matching/guia.py`).
TOLERANCIA = 0.005

# Um crédito abaixo disto contra um boleto não é pagamento — é sonda. Marca o boleto
# como pago e derruba o pagamento verdadeiro que vier depois.
FRACAO_IRRISORIA = 0.05

SQL_ARQUIVOS = """
SELECT r.IDRetorno, r.NomeArquivo, CAST(r.DataArquivo AS DATE) AS DataArquivo,
       r.QtdBoletos, r.ValorTotal,
       COUNT(rb.IdRetornoBoleto)      AS qtd_importada,
       COALESCE(SUM(rb.ValorPago), 0) AS soma_importada
  FROM dbo.Exe_Retorno r
  LEFT JOIN dbo.Exe_Retorno_Boleto rb ON rb.IdRetorno = r.IDRetorno
 WHERE r.DataArquivo >= :desde
 GROUP BY r.IDRetorno, r.NomeArquivo, CAST(r.DataArquivo AS DATE),
          r.QtdBoletos, r.ValorTotal
"""

SQL_REJEITADAS = """
SELECT l.IDRetornoLog, l.IDRetorno, r.NomeArquivo,
       CAST(r.DataArquivo AS DATE) AS DataArquivo, l.Motivo, l.LinhaArquivo
  FROM dbo.Exe_Retorno_Log l
  JOIN dbo.Exe_Retorno r ON r.IDRetorno = l.IDRetorno
 WHERE l.Motivo NOT LIKE 'Importado com Sucesso%'
   AND r.DataArquivo >= :desde
"""

# Mapa boleto -> débito -> processo. ~34 mil linhas: cabe inteiro na memória e evita
# montar um IN gigante. O débito aponta para o processo pela execução OU pela origem —
# COALESCE perderia o vínculo pela origem, então as duas colunas vêm separadas.
# `PagoRegistrado` é a soma do que a importação aceitou para aquele boleto: é ela que
# separa a rejeição benigna (reprocessamento de arquivo já importado) da perda real.
SQL_BOLETOS = """
SELECT b.IdBoleto, b.ValorTotalAPagar AS ValorTitulo, b.DataVencimento, b.StatusBoleto,
       db.IdDebito, pg.total AS PagoRegistrado,
       pe.numero_processo AS proc_execucao_num, pe.ano_processo AS proc_execucao_ano,
       po.numero_processo AS proc_origem_num,   po.ano_processo AS proc_origem_ano
  FROM dbo.Exe_Boleto b
  LEFT JOIN dbo.Exe_DebitoBoleto db ON db.IdBoleto = b.IdBoleto
  LEFT JOIN dbo.Exe_Debito ed       ON ed.IdDebito = db.IdDebito
  LEFT JOIN dbo.Processos pe        ON pe.IdProcesso = ed.IdProcessoExecucao
  LEFT JOIN dbo.Processos po        ON po.IdProcesso = ed.IdProcessoOrigem
  OUTER APPLY (SELECT SUM(rb.ValorPago) AS total
                 FROM dbo.Exe_Retorno_Boleto rb
                WHERE rb.IdBoleto = b.IdBoleto) pg
"""

SQL_BAIXA_IRRISORIA = """
SELECT rb.IdRetornoBoleto, rb.IdRetorno, rb.IdBoleto, CAST(rb.DataPagamento AS DATE) AS DataPagamento,
       rb.ValorPago, b.ValorTotalAPagar AS ValorTitulo, rb.FormaPagamento, rb.NumeroAutenticacao
  FROM dbo.Exe_Retorno_Boleto rb
  JOIN dbo.Exe_Boleto b ON b.IdBoleto = rb.IdBoleto
 WHERE b.ValorTotalAPagar > 0
   AND rb.ValorPago < :fracao * b.ValorTotalAPagar
"""


def divergencias(arquivos: pd.DataFrame) -> pd.DataFrame:
    """Arquivos de retorno em que o total declarado não bate com o importado.

    A diferença é positiva quando falta dinheiro (linha rejeitada) e negativa quando
    sobra (o mesmo arquivo foi importado duas vezes — acontece, ver IDRetorno 1948/1949).
    """
    df = arquivos.copy()
    df["diferenca"] = (df["ValorTotal"] - df["soma_importada"]).round(2)
    df["boletos_faltando"] = df["QtdBoletos"] - df["qtd_importada"]
    return (df[df["diferenca"].abs() > TOLERANCIA]
            .sort_values("DataArquivo", ascending=False)
            .reset_index(drop=True))


def enriquece(rejeitadas: pd.DataFrame, boletos: pd.DataFrame) -> pd.DataFrame:
    """Anexa débito, processo e valor do título a cada linha rejeitada.

    O id do boleto vem do texto do motivo ("Boleto ID = 36991 já está com status
    pago."); linhas de erro de layout/sequencial não têm id e ficam sem vínculo.
    """
    df = rejeitadas.copy()
    df["IdBoleto"] = pd.to_numeric(
        df["Motivo"].str.extract(r"Boleto ID = (\d+)", expand=False), errors="coerce"
    )
    return classifica(df.merge(boletos, on="IdBoleto", how="left"))


def classifica(rejeitadas: pd.DataFrame) -> pd.DataFrame:
    """Separa a rejeição inofensiva da perda de dinheiro.

    A esmagadora maioria das rejeições por "já está com status pago" é reprocessamento:
    o boleto já tinha o pagamento certo registrado e o banco reenviou o arquivo. Só há
    perda quando o que ficou registrado é **menor que o título** — ou quando não ficou
    nada. Sem este corte, 998 linhas de ruído escondem as 3 que importam.
    """
    df = rejeitadas.copy()
    pago, titulo = df["PagoRegistrado"], df["ValorTitulo"]
    df["classificacao"] = "erro de layout/sequencial (sem boleto)"
    df.loc[titulo.notna(), "classificacao"] = "benigna (pagamento já registrado)"
    df.loc[titulo.notna() & (pago < 0.95 * titulo), "classificacao"] = "PERDA: registrado menor que o título"
    df.loc[titulo.notna() & pago.isna(), "classificacao"] = "PERDA: nada registrado"
    return df


def _fmt(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--desde", default="2020-01-01", help="data inicial do arquivo de retorno")
    ap.add_argument("--self-check", action="store_true", help="roda os asserts e sai")
    args = ap.parse_args()

    if args.self_check:
        _self_check()
        print("self-check OK")
        return

    arquivos = run_query_df(SQL_ARQUIVOS, desde=args.desde)
    div = divergencias(arquivos)
    boletos = run_query_df(SQL_BOLETOS)
    rej = enriquece(run_query_df(SQL_REJEITADAS, desde=args.desde), boletos)
    irrisorias = run_query_df(SQL_BAIXA_IRRISORIA, fracao=FRACAO_IRRISORIA).merge(
        boletos.drop(columns=["ValorTitulo"]), on="IdBoleto", how="left"
    )

    falta = div.loc[div["diferenca"] > 0, "diferenca"].sum()
    sobra = -div.loc[div["diferenca"] < 0, "diferenca"].sum()
    print(f"arquivos de retorno desde {args.desde}: {len(arquivos)}")
    print(f"  com divergência declarado x importado: {len(div)}")
    print(f"  faltando (crédito no banco sem baixa): {_fmt(falta)}")
    print(f"  sobrando (arquivo importado em duplicidade): {_fmt(sobra)}")
    print(f"linhas rejeitadas na importação: {len(rej)}"
          f"  ({rej['Motivo'].str.contains('status pago').sum()} por 'já está com status pago')")
    print(f"baixas por valor irrisório (< {FRACAO_IRRISORIA:.0%} do título): {len(irrisorias)}")

    print("\nclassificação das rejeições:")
    print(rej["classificacao"].value_counts().to_string())

    # Um boleto pode ser rejeitado em dois arquivos (o banco reenvia o mesmo retorno,
    # ver IDRetorno 1948/1949). O dinheiro que falta é um só: dedup pelo boleto.
    perdas = (rej[rej["classificacao"].str.startswith("PERDA")]
              .drop_duplicates(subset=["IdBoleto"])
              .sort_values("DataArquivo"))
    print(f"\nPagamentos que entraram no banco e não baixaram o crédito "
          f"({_fmt(perdas['ValorTitulo'].sum())}):")
    print(perdas[["DataArquivo", "NomeArquivo", "IdBoleto", "ValorTitulo",
                  "PagoRegistrado", "IdDebito", "proc_origem_num", "proc_origem_ano",
                  "classificacao"]].to_string(index=False))

    destino = OUTPUT_DIR / "analise"
    destino.mkdir(parents=True, exist_ok=True)
    saida = destino / "retornos_boleto_nao_importados.xlsx"
    with pd.ExcelWriter(saida) as xls:
        div.to_excel(xls, sheet_name="arquivos", index=False)
        rej.to_excel(xls, sheet_name="rejeitadas", index=False)
        irrisorias.to_excel(xls, sheet_name="baixa_irrisoria", index=False)
    print(f"\n-> {saida}")


def _self_check() -> None:
    arquivos = pd.DataFrame([
        # falta uma linha: é o caso 004164/2020
        (1923, "rcb001.28022601", "2026-02-28", 60, 24843.18, 59, 23894.91),
        # importado em duplicidade: diferença negativa
        (1912, "rcb001.11022601", "2026-02-11", 1, 222.78, 2, 445.56),
        # fecha certinho: não pode aparecer
        (1924, "rcb001.05032601", "2026-03-05", 4, 1600.38, 4, 1600.38),
    ], columns=["IDRetorno", "NomeArquivo", "DataArquivo", "QtdBoletos", "ValorTotal",
                "qtd_importada", "soma_importada"])

    div = divergencias(arquivos)
    assert len(div) == 2, div
    assert 1924 not in set(div["IDRetorno"]), "arquivo que fecha não é divergência"
    linha = div.set_index("IDRetorno")
    assert linha.loc[1923, "diferenca"] == 948.27, linha.loc[1923, "diferenca"]
    assert linha.loc[1923, "boletos_faltando"] == 1
    assert linha.loc[1912, "diferenca"] == -222.78, "duplicidade tem diferença negativa"
    assert linha.loc[1912, "boletos_faltando"] == -1

    rejeitadas = pd.DataFrame([
        (17755, 1923, "Boleto ID = 36991 já está com status pago. - Linha 41  - Coluna 74"),
        (17756, 1923, "Layout incorreto (@Header) - Quantidade de Caracteres difere"),
        (23005, 1948, "Boleto ID = 38259 já está com status pago. - Linha 1  - Coluna 74"),
        (99999, 1900, "Boleto ID = 11111 já está com status pago. - Linha 2  - Coluna 74"),
    ], columns=["IDRetornoLog", "IDRetorno", "Motivo"])
    boletos = pd.DataFrame([
        (36991, 948.27, 23232, 2.02),     # sonda de R$ 2,02 barrou o pagamento real
        (38259, 1481.87, 28484, None),    # nada registrado
        (11111, 500.00, 999, 500.00),     # reprocessamento: o pagamento certo já entrou
    ], columns=["IdBoleto", "ValorTitulo", "IdDebito", "PagoRegistrado"])

    enr = enriquece(rejeitadas, boletos).set_index("IDRetornoLog")
    assert enr.loc[17755, "IdBoleto"] == 36991
    assert enr.loc[17755, "ValorTitulo"] == 948.27
    assert enr.loc[17755, "classificacao"] == "PERDA: registrado menor que o título"
    assert enr.loc[23005, "classificacao"] == "PERDA: nada registrado"
    # o caso dominante (7.075 linhas na base real) não pode virar alarme falso
    assert enr.loc[99999, "classificacao"] == "benigna (pagamento já registrado)"
    # erro de layout não cita boleto: fica sem vínculo em vez de casar com o errado
    assert pd.isna(enr.loc[17756, "IdBoleto"])
    assert pd.isna(enr.loc[17756, "ValorTitulo"])
    assert enr.loc[17756, "classificacao"] == "erro de layout/sequencial (sem boleto)"


if __name__ == "__main__":
    sys.exit(main())
