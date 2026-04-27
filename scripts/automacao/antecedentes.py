"""Generate the 'antecedentes' despacho for one or more responsáveis.

Despite the legacy name, the underlying SQL filters by `nome` (LIKE), not by
CPF — the parameter is the responsável's name pattern.
"""
from __future__ import annotations

import argparse
import json
import locale
import math
from pathlib import Path

import pandas as pd
from docxtpl import DocxTemplate

from ccd.config import read_sql
from ccd.db import get_connection, run_query_df

TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "antecedentes.docx"


def _set_pt_br_locale() -> None:
    for name in ("pt_BR.UTF-8", "pt_BR.utf8", "Portuguese_Brazil.1252", "pt_BR"):
        try:
            locale.setlocale(locale.LC_ALL, name)
            return
        except locale.Error:
            continue


def _format_currency(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    try:
        return locale.currency(value, grouping=True, symbol=False)
    except (locale.Error, TypeError, ValueError):
        return f"{value:,.2f}"


def get_processos_transito_by_nome(nome: str) -> pd.DataFrame:
    """Return execution debts whose responsável name matches `nome` (LIKE)."""
    sql = read_sql("processos_transito_nome.sql")
    pattern = f"%{nome.lower()}%"
    with get_connection().connect() as conn:
        return run_query_df(sql, conn, nome_pattern=pattern)


def create_antecedentes_doc(nome: str, context: dict) -> DocxTemplate:
    """Render the antecedentes template against the given context."""
    _set_pt_br_locale()
    df = get_processos_transito_by_nome(nome)
    df["valor_original"] = df["valor_original"].apply(_format_currency)
    df["valor_atualizado"] = df["valor_atualizado"].apply(_format_currency)
    df.fillna("", inplace=True)

    doc = DocxTemplate(str(TEMPLATE_PATH))
    context = {**context, "valores": df.to_dict(orient="records")}
    doc.render(context)
    return doc


def create_antecedentes_file(nome: str, context: dict, doc_name: str | Path) -> Path:
    doc = create_antecedentes_doc(nome, context)
    out = Path(doc_name)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def create_context_processo(numero_processo: str, ano_processo: str | int) -> dict:
    sql = read_sql("processo.sql")
    df = run_query_df(
        sql,
        numero_processo=str(numero_processo),
        ano_processo=str(ano_processo),
    )
    if df.empty:
        raise ValueError(f"Processo {numero_processo}/{ano_processo} não encontrado.")
    return df.to_dict(orient="records")[0]


def create_antecedentes(nome: str, json_file: str | Path, doc_name: str | Path) -> Path:
    context = json.loads(Path(json_file).read_text(encoding="utf-8"))
    return create_antecedentes_file(nome, context, doc_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="antecedentes", description="Cria despacho de antecedentes")
    parser.add_argument("--nome", "-n", required=True, help="Nome do responsável (LIKE pattern)")
    parser.add_argument("--json", "-j", required=True, help="Arquivo JSON com o contexto do despacho")
    parser.add_argument("--doc_name", "-d", required=True, help="Caminho do .docx de saída")
    args = parser.parse_args()
    create_antecedentes(args.nome, args.json, args.doc_name)
