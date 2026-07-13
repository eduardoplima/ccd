"""Aba "Antonio Ed": parados do Nereu (planilha existente) cujo relator é o cons. Antonio Ed.

Reaproveita as linhas da aba "Parados Nereu" de docs/processos_parados_nereu.xlsx
(sem re-rodar a LLM) e filtra pelos processos cujo relator é Antonio Ed Souza Santana,
acrescentando uma nova aba no mesmo arquivo.

Rodar (na rede do TCE):
  .venv/Scripts/python.exe scripts/analise/parados_nereu_antonio_ed.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import bindparam, text

from ccd.db import get_connection

OUT = Path(__file__).resolve().parent / "docs" / "processos_parados_nereu.xlsx"


def main() -> None:
    parados = pd.read_excel(OUT, sheet_name="Parados Nereu")
    procos = parados["processo"].tolist()
    with get_connection().connect() as c:
        rel = pd.DataFrame(c.execute(text("""
            SELECT CONCAT(RTRIM(p.numero_processo),'/',RTRIM(p.ano_processo)) processo,
                   RTRIM(r.nome) relator
            FROM processo.dbo.Processos p
            LEFT JOIN processo.dbo.Relator r ON r.codigo=p.codigo_relator
            WHERE CONCAT(RTRIM(p.numero_processo),'/',RTRIM(p.ano_processo)) IN :p""")
            .bindparams(bindparam("p", expanding=True)), {"p": procos}).mappings().all())

    ed = rel[rel["relator"].str.upper().str.startswith("ANTONIO ED", na=False)]
    df = ed.merge(parados, on="processo")[["processo", "relator", "marcador", "resumo", "sugestao"]]
    assert (df["relator"].str.upper().str.startswith("ANTONIO ED")).all()

    with pd.ExcelWriter(OUT, mode="a", if_sheet_exists="replace") as w:
        df.to_excel(w, index=False, sheet_name="Antonio Ed")
    print(f"Salvo aba 'Antonio Ed': {len(df)} processos\n{df['processo'].tolist()}")


if __name__ == "__main__":
    main()
