"""Gera o despacho de inviabilidade para os processos da CCD com o marcador
"LUZENILDO - Enviar à DIP" e relatoria de ANTONIO ED SOUZA SANTANA.

Consulta o banco `processo` pelo conjunto que casa marcador + relator e, para
cada processo, renderiza `templates/inviabilidade.docx` com as variáveis
`processo` e `relator`, salvando `.docx` e `.pdf` em `saidas/automacao/inviabilidade/`.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from docxtpl import DocxTemplate

from ccd.config import REPO_ROOT
from ccd.db import run_query_df
from ccd.docs import docx_to_pdf

# Setor CCD no banco `processo` (Pro_Marcador.IdSetor), espelha o webapp.
ID_SETOR_CCD = 762
MARCADOR = "LUZENILDO - Enviar à DIP"
RELATOR_NOME = "ANTONIO ED SOUZA SANTANA"

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "inviabilidade.docx"
OUT_DIR = REPO_ROOT / "saidas" / "automacao" / "inviabilidade"

# Marcador mais recente por processo (mc.rn = 1), mesma semântica do módulo
# CCD em web/backend/app/ccd/service.py.
SQL = """
WITH marc AS (
    SELECT mp.IdProcesso, m.Descricao AS marcador,
           ROW_NUMBER() OVER (
               PARTITION BY mp.IdProcesso ORDER BY mp.DataInclusao DESC
           ) AS rn
    FROM dbo.Pro_MarcadorProcesso mp
    JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
    WHERE m.IdSetor = :id_setor AND mp.DataExclusao IS NULL
)
SELECT
    CONCAT(RTRIM(p.numero_processo), '/', RTRIM(p.ano_processo)) AS processo,
    RTRIM(r.nome) AS relator
FROM dbo.Processos p
JOIN marc mc       ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
JOIN dbo.Relator r ON r.codigo = p.codigo_relator
WHERE p.setor_atual = 'CCD'
  AND p.IdProcessoApensador IS NULL
  AND mc.marcador = :marcador
  AND RTRIM(r.nome) = :relator_nome
ORDER BY p.ano_processo, p.numero_processo
"""


def fetch_processos() -> pd.DataFrame:
    return run_query_df(
        SQL,
        id_setor=ID_SETOR_CCD,
        marcador=MARCADOR,
        relator_nome=RELATOR_NOME,
    )


def main() -> None:
    df = fetch_processos()
    if df.empty:
        print(
            f"Nenhum processo com marcador {MARCADOR!r} e relator "
            f"{RELATOR_NOME!r}. Confira o nome do relator e o texto do marcador."
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
