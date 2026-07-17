"""Gera o despacho de envio à DAP para os processos em DIP_SOBR com o
marcador "Nereu - dúvida quanto*".

Consulta o banco `processo` pelos processos que estão no setor DIP_SOBR com um
marcador ativo cuja descrição casa o padrão e, para cada processo, renderiza
`templates/envio_dap.docx` com as variáveis `processo` e `relator`, salvando
`.docx` e `.pdf` em `saidas/automacao/envio_dap/`.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from docxtpl import DocxTemplate

from ccd.config import REPO_ROOT
from ccd.db import run_query_df
from ccd.docs import docx_to_pdf

SETOR = "DIP_SOBR"
MARCADOR_LIKE = "Nereu - dúvida quanto%"

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "envio_dap.docx"
OUT_DIR = REPO_ROOT / "saidas" / "automacao" / "envio_dap"

SQL = """
SELECT DISTINCT
    CONCAT(RTRIM(p.numero_processo), '/', RTRIM(p.ano_processo)) AS processo,
    RTRIM(r.nome) AS relator
FROM dbo.Processos p
JOIN dbo.Pro_MarcadorProcesso mp
    ON mp.IdProcesso = p.IdProcesso AND mp.DataExclusao IS NULL
JOIN dbo.Pro_Marcador m  ON m.IdMarcador = mp.IdMarcador
JOIN dbo.Relator r       ON r.codigo = p.codigo_relator
WHERE p.setor_atual = :setor
  AND p.IdProcessoApensador IS NULL
  AND m.Descricao LIKE :marcador
ORDER BY processo
"""


def fetch_processos() -> pd.DataFrame:
    return run_query_df(SQL, setor=SETOR, marcador=MARCADOR_LIKE)


def main() -> None:
    df = fetch_processos()
    if df.empty:
        print(
            f"Nenhum processo em {SETOR!r} com marcador {MARCADOR_LIKE!r}. "
            "Confira o código do setor e o texto do marcador."
        )
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for row in df.itertuples():
        doc = DocxTemplate(str(TEMPLATE_PATH))
        doc.render({"processo": row.processo, "relator": row.relator})
        nome_arq = row.processo.replace("/", "_")
        doc_path = OUT_DIR / f"{nome_arq}.docx"
        doc.save(str(doc_path))
        docx_to_pdf(str(doc_path), str(OUT_DIR))
        print(f"Gerado: {row.processo}")

    print(f"{len(df)} processo(s) em {OUT_DIR}")


if __name__ == "__main__":
    main()
