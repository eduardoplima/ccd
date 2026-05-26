"""Débitos do Nereu — total, por tipo e por situação.

Recorte: todos os débitos em que NEREU BATISTA LINHARES (CPF 13006444434)
figura como parte em Exe_DebitoPessoa, sem filtrar por CodigoStatusDivida
— para que o quadro mostre todas as situações (ativa, quitada, parcelada,
suspensa, etc.). Usa e.IdDebitoAnterior IS NULL para pegar apenas o
registro "head" de cada débito.

Saídas em --outdir (padrão: scripts/analise/docs/):
  - debitos_nereu_por_tipo_situacao.xlsx     (débitos detalhados)
  - debitos_nereu_por_tipo.png               (qtd + valor por tipo)
  - debitos_nereu_por_situacao.png           (qtd + valor por situação)
  - debitos_nereu_tipo_x_situacao.png        (heatmap)
"""
from __future__ import annotations

import argparse
import locale
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ccd.db import run_query_df

CPF_NEREU = "13006444434"

SQL_DEBITOS_NEREU = """
SELECT
    e.IdDebito AS id_debito,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
        FROM processo.dbo.Processos p
        WHERE p.IdProcesso = e.IdProcessoOrigem) AS processo_origem,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
        FROM processo.dbo.Processos p
        WHERE p.IdProcesso = e.IdProcessoExecucao) AS processo_execucao,
    etd.Descricao AS tipo_debito,
    esd.DescricaoStatusDivida AS situacao_divida,
    e.valorOriginalDebito AS valor_original,
    processo.dbo.fn_Exe_RetornaValorAtualizado(e.IdDebito) AS valor_atualizado,
    e.dataTransito AS data_transito
FROM processo.dbo.Exe_Debito e
INNER JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
INNER JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
LEFT JOIN processo.dbo.Exe_TipoDebito etd ON etd.CodigoTipoDebito = e.CodigoTipoDebito
LEFT JOIN processo.dbo.Exe_StatusDivida esd ON esd.CodigoStatusDivida = e.CodigoStatusDivida
WHERE gp.Documento = :cpf
  AND e.IdDebitoAnterior IS NULL
"""


def _set_pt_br_locale() -> None:
    for loc in ("pt_BR.UTF-8", "pt_BR", "Portuguese_Brazil.1252", "Portuguese_Brazil"):
        try:
            locale.setlocale(locale.LC_ALL, loc)
            return
        except locale.Error:
            continue


def _brl(value: float) -> str:
    try:
        return locale.currency(value, grouping=True, symbol=True)
    except (ValueError, locale.Error):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_debitos(cpf: str = CPF_NEREU) -> pd.DataFrame:
    df = run_query_df(SQL_DEBITOS_NEREU, cpf=cpf)
    df["tipo_debito"] = df["tipo_debito"].fillna("(sem tipo)")
    df["situacao_divida"] = df["situacao_divida"].fillna("(sem situação)")
    return df


def resumo_total(df: pd.DataFrame) -> dict:
    return {
        "quantidade": len(df),
        "valor_original": float(df["valor_original"].sum()),
        "valor_atualizado": float(df["valor_atualizado"].sum()),
    }


def agrupar(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    return (
        df.groupby(coluna)
        .agg(
            quantidade=("id_debito", "count"),
            valor_original=("valor_original", "sum"),
            valor_atualizado=("valor_atualizado", "sum"),
        )
        .sort_values("valor_atualizado", ascending=False)
    )


def _formatar_brl(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ("valor_original", "valor_atualizado"):
        if col in out.columns:
            out[col] = out[col].apply(_brl)
    return out


def plot_por(df_grp: pd.DataFrame, coluna: str, titulo: str, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    df_plot = df_grp.reset_index()

    sns.barplot(data=df_plot, x=coluna, y="quantidade", palette="viridis", ax=axes[0])
    axes[0].set_title(f"{titulo} — quantidade")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Quantidade")
    axes[0].tick_params(axis="x", rotation=30)
    for lbl in axes[0].get_xticklabels():
        lbl.set_ha("right")

    sns.barplot(data=df_plot, x=coluna, y="valor_atualizado", palette="mako", ax=axes[1])
    axes[1].set_title(f"{titulo} — valor atualizado")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("R$ (atualizado)")
    axes[1].tick_params(axis="x", rotation=30)
    for lbl in axes[1].get_xticklabels():
        lbl.set_ha("right")

    sns.despine()
    plt.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_cross_heatmap(df: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    cross_valor = pd.crosstab(
        df["tipo_debito"],
        df["situacao_divida"],
        values=df["valor_atualizado"],
        aggfunc="sum",
        margins=True,
        margins_name="Total",
    ).fillna(0)

    fig = plt.figure(figsize=(11, 5))
    sns.heatmap(
        cross_valor.iloc[:-1, :-1],
        annot=True,
        fmt=".0f",
        cmap="YlGnBu",
        cbar_kws={"label": "R$ (atualizado)"},
    )
    plt.title("Débitos do Nereu — valor atualizado por tipo × situação")
    plt.xlabel("Situação")
    plt.ylabel("Tipo de débito")
    plt.xticks(rotation=30, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)

    return cross_valor


def imprimir_relatorio(df: pd.DataFrame) -> None:
    total = resumo_total(df)
    print("=" * 70)
    print("Débitos do Nereu — total geral")
    print("=" * 70)
    print(f"Quantidade de débitos:     {total['quantidade']}")
    print(f"Valor original total:      {_brl(total['valor_original'])}")
    print(f"Valor atualizado total:    {_brl(total['valor_atualizado'])}")

    print()
    print("=" * 70)
    print("Por tipo de débito")
    print("=" * 70)
    print(_formatar_brl(agrupar(df, "tipo_debito")).to_string())

    print()
    print("=" * 70)
    print("Por situação da dívida")
    print("=" * 70)
    print(_formatar_brl(agrupar(df, "situacao_divida")).to_string())

    print()
    print("=" * 70)
    print("Cruzamento tipo × situação (quantidade)")
    print("=" * 70)
    cross_qtd = pd.crosstab(
        df["tipo_debito"], df["situacao_divida"],
        margins=True, margins_name="Total",
    )
    print(cross_qtd.to_string())

    print()
    print("=" * 70)
    print("Top 10 maiores débitos (valor atualizado)")
    print("=" * 70)
    top = (
        df.nlargest(10, "valor_atualizado")[
            ["id_debito", "processo_origem", "processo_execucao",
             "tipo_debito", "situacao_divida", "valor_original", "valor_atualizado"]
        ]
    )
    print(_formatar_brl(top).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpf", default=CPF_NEREU,
                        help=f"CPF da pessoa (padrão: {CPF_NEREU})")
    parser.add_argument("--outdir", default="scripts/analise/docs",
                        help="Diretório de saída para xlsx + PNGs")
    args = parser.parse_args()

    matplotlib.use("Agg")
    _set_pt_br_locale()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = carregar_debitos(args.cpf)
    print(f"Débitos do CPF {args.cpf}: {len(df)}\n")

    imprimir_relatorio(df)

    xlsx_path = outdir / "debitos_nereu_por_tipo_situacao.xlsx"
    df.to_excel(xlsx_path, index=False)

    plot_por(agrupar(df, "tipo_debito"), "tipo_debito",
             "Débitos do Nereu — por tipo",
             outdir / "debitos_nereu_por_tipo.png")
    plot_por(agrupar(df, "situacao_divida"), "situacao_divida",
             "Débitos do Nereu — por situação",
             outdir / "debitos_nereu_por_situacao.png")
    plot_cross_heatmap(df, outdir / "debitos_nereu_tipo_x_situacao.png")

    print()
    print(f"Artefatos salvos em: {outdir.resolve()}")


if __name__ == "__main__":
    main()
