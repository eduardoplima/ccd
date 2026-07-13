"""Gera docs/debitos_nereu_03072026.xlsx: uma linha por débito (id_debito explícito),
com o setor atual do processo de origem e do processo de execução em colunas separadas
(no lugar da única `setor atual` da 02072026). Reusa build_enriched_df() da 02072026.
"""
from __future__ import annotations

import pandas as pd

from ccd.db import get_connection
from scripts.analise.gerar_debitos_nereu_02072026 import COLS, DOCS, build_enriched_df

OUT = DOCS / "debitos_nereu_03072026.xlsx"


def _proc(n: pd.Series, a: pd.Series) -> pd.Series:
    n, a = n.astype(str).str.strip(), a.astype(str).str.strip()
    p = n + "/" + a
    return p.where(n != "", "")


def main() -> None:
    out = build_enriched_df()
    out["proc origem"] = _proc(out["nprocorig"], out["anoprocorig"])
    out["proc execução"] = _proc(out["nprocexe"], out["anoprocexe"])

    procs = sorted({p for p in pd.concat([out["proc origem"], out["proc execução"]]) if p})
    eng = get_connection()
    lst = ", ".join(f"'{p}'" for p in procs)
    smap = pd.read_sql(
        "SELECT CONCAT(p.numero_processo,'/',p.ano_processo) AS numproc, "
        "RTRIM(p.setor_atual) AS setoratual FROM processo.dbo.Processos p "
        f"WHERE CONCAT(p.numero_processo,'/',p.ano_processo) IN ({lst})", eng,
    ).drop_duplicates("numproc").set_index("numproc")["setoratual"]

    out["setor origem"] = out["proc origem"].map(smap).fillna("")
    out["setor execução"] = out["proc execução"].map(smap).fillna("")

    # colunas: id_debito na frente; troca a única "setor atual" pelas duas de origem/execução.
    base = [c for c in COLS if c != "setor atual"]
    i = base.index("verba transitório") + 1
    cols = ["id_debito", *base[:i], "setor origem", "setor execução", *base[i:]]
    out[cols].to_excel(OUT, index=False)
    print(f"Gravado: {OUT}  ({len(out)} débitos)")


if __name__ == "__main__":
    main()
