"""Notificações de desconto em folha (Nereu) classificadas por tema: SESAP × Outros Assuntos.

Cruza a aba "Notificações desconto em folha" de debitos_nereu_planilha_final.xlsx com a
classificação da coluna `sesap` da aba TodosDebitos de analise_debitos_nereu_definitiva.xlsx.
Join por id_debito (ids_debitos → id_debito); a linha sem id cai num fallback por processo.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DOCS = Path("scripts/analise/docs")
TEMA = {"SESAP": "SESAP", "OUTROS": "Outros Assuntos"}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--final", default=str(DOCS / "debitos_nereu_planilha_final.xlsx"))
    p.add_argument("--definitiva", default=str(DOCS / "analise_debitos_nereu_definitiva.xlsx"))
    p.add_argument("--out", default=str(DOCS / "notificacoes_desconto_folha_por_tema.xlsx"))
    args = p.parse_args()

    nf = pd.read_excel(args.final, sheet_name="Notificações desconto em folha")
    td = pd.read_excel(args.definitiva, sheet_name="TodosDebitos")[
        ["id_debito", "processo_execucao", "sesap", "tipo_multa", "servidores_envolvidos"]
    ]

    nf["id_debito"] = pd.to_numeric(nf["ids_debitos"], errors="coerce").astype("Int64")

    # 1) merge principal por id_debito
    m = nf.merge(td.drop(columns="processo_execucao"), on="id_debito", how="left")

    # 2) fallback por processo para linhas sem id_debito: usa o sesap dos débitos do processo
    #    (se o processo tiver temas mistos vira "(verificar)").
    por_proc = (
        td.groupby("processo_execucao")["sesap"]
        .agg(lambda s: s.iloc[0] if s.nunique() == 1 else "MISTO")
        .to_dict()
    )
    falta = m["sesap"].isna()
    m.loc[falta, "sesap"] = m.loc[falta, "processo"].map(por_proc)

    m["tema"] = m["sesap"].map(TEMA).fillna(
        m["sesap"].map({"MISTO": "(verificar)"})
    ).fillna("(não classificado)")

    cols = ["processo", "evento", "data_notificacao", "id_debito", "tema",
            "valor_original_total", "valor_atualizado_total", "tipo_multa",
            "servidores_envolvidos"]
    out = m[cols].sort_values(["tema", "processo"]).reset_index(drop=True)

    resumo = (
        out.groupby("tema")
        .agg(qtd=("processo", "size"), valor_atualizado=("valor_atualizado_total", "sum"))
        .reset_index()
        .sort_values("qtd", ascending=False)
    )

    outpath = Path(args.out)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(outpath) as xw:
        out.to_excel(xw, sheet_name="Notificações", index=False)
        resumo.to_excel(xw, sheet_name="Resumo", index=False)

    print(f"Notificações de desconto em folha classificadas: {len(out)}")
    print(resumo.to_string(index=False))
    nao_class = out[out["tema"].isin(["(verificar)", "(não classificado)"])]
    if len(nao_class):
        print(f"\nATENÇÃO — {len(nao_class)} linha(s) sem tema definido:")
        print(nao_class[["processo", "id_debito", "tema"]].to_string(index=False))
    print(f"\nPlanilha: {outpath.resolve()}")


if __name__ == "__main__":
    main()
