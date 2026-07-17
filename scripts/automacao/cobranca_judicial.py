"""Gera o despacho de cobrança judicial para uma lista de processos.

Para cada processo, busca o relator no banco e renderiza o template
`templates/cobranca_judicial.docx` com as variáveis `processo` e `relator`,
salvando `.docx` e `.pdf` em `saidas/automacao/cobranca_judicial/`.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from docxtpl import DocxTemplate

from ccd.config import REPO_ROOT
from ccd.db import run_query_df
from ccd.docs import docx_to_pdf

PROCESSOS = [
    "000092/2023",
]

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "cobranca_judicial.docx"
OUT_DIR = REPO_ROOT / "saidas" / "automacao" / "cobranca_judicial"


def fetch_relatores(processos: list[str]) -> pd.DataFrame:
    placeholders = ", ".join(f":p{i}" for i in range(len(processos)))
    sql = f"""
SELECT
    CONCAT(pro.numero_processo, '/', pro.ano_processo) AS processo,
    rel.nome AS relator
FROM processo.dbo.Processos pro
INNER JOIN processo.dbo.Relator rel
    ON pro.codigo_relator = rel.codigo
WHERE CONCAT(pro.numero_processo, '/', pro.ano_processo) IN ({placeholders})
"""
    params = {f"p{i}": v for i, v in enumerate(processos)}
    return run_query_df(sql, **params)


def main() -> None:
    df = fetch_relatores(PROCESSOS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    encontrados = set(df["processo"])
    faltando = [p for p in PROCESSOS if p not in encontrados]
    if faltando:
        print(f"AVISO: processos não encontrados no banco: {faltando}")

    for row in df.itertuples():
        doc = DocxTemplate(str(TEMPLATE_PATH))
        doc.render({"processo": row.processo, "relator": row.relator})
        processo_underline = row.processo.replace("/", "_")
        doc_path = OUT_DIR / f"{processo_underline}.docx"
        doc.save(str(doc_path))
        docx_to_pdf(str(doc_path), str(OUT_DIR))
        print(f"Gerado arquivo para o processo {row.processo}")


if __name__ == "__main__":
    main()
