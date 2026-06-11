"""Gera um dicionário de dados em Markdown para os bancos MSSQL configurados.

Para cada banco, consulta as views de catálogo (`sys.tables`, `sys.columns`,
`sys.foreign_key_columns`, `sys.indexes`, `sys.extended_properties`) e escreve
um arquivo `<db>.md` no diretório de saída, mais um `INDEX.md` resumo.

Uso:
    python -m scripts.analise.dicionario_dados
    python -m scripts.analise.dicionario_dados --out caminho/saida
    python -m scripts.analise.dicionario_dados --dbs processo BdDIP
"""
from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from datetime import date
from pathlib import Path

import pandas as pd

from ccd.db import get_connection, run_query_df

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_DBS: tuple[str, ...] = (
    "processo",
    "bdcargasigef2023",
    "bdcargasigef2024",
    "bdcargasigef2025",
)

DEFAULT_OUT: Path = Path(__file__).resolve().parent / "dicionario_dados"


SQL_TABLES = """
SELECT
    s.name AS table_schema,
    t.name AS table_name,
    'BASE TABLE' AS table_type,
    SUM(CASE WHEN p.index_id IN (0, 1) THEN p.[rows] ELSE 0 END) AS row_count,
    CAST(ep.value AS NVARCHAR(MAX)) AS table_description
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
LEFT JOIN sys.partitions p ON p.object_id = t.object_id
LEFT JOIN sys.extended_properties ep
    ON ep.major_id = t.object_id
   AND ep.minor_id = 0
   AND ep.name = 'MS_Description'
GROUP BY s.name, t.name, ep.value
UNION ALL
SELECT
    s.name AS table_schema,
    v.name AS table_name,
    'VIEW' AS table_type,
    NULL AS row_count,
    CAST(ep.value AS NVARCHAR(MAX)) AS table_description
FROM sys.views v
JOIN sys.schemas s ON s.schema_id = v.schema_id
LEFT JOIN sys.extended_properties ep
    ON ep.major_id = v.object_id
   AND ep.minor_id = 0
   AND ep.name = 'MS_Description'
ORDER BY table_schema, table_name;
"""

SQL_COLUMNS = """
SELECT
    s.name AS table_schema,
    o.name AS table_name,
    c.column_id AS ordinal_position,
    c.name AS column_name,
    ty.name AS data_type,
    c.max_length,
    c.precision,
    c.scale,
    c.is_nullable,
    c.is_identity,
    c.is_computed,
    OBJECT_DEFINITION(c.default_object_id) AS column_default,
    CAST(ep.value AS NVARCHAR(MAX)) AS column_description
FROM sys.columns c
JOIN sys.objects o ON o.object_id = c.object_id
JOIN sys.schemas s ON s.schema_id = o.schema_id
JOIN sys.types ty ON ty.user_type_id = c.user_type_id
LEFT JOIN sys.extended_properties ep
    ON ep.major_id = c.object_id
   AND ep.minor_id = c.column_id
   AND ep.name = 'MS_Description'
WHERE o.type IN ('U', 'V')
ORDER BY s.name, o.name, c.column_id;
"""

SQL_PK = """
SELECT
    s.name AS table_schema,
    t.name AS table_name,
    c.name AS column_name
FROM sys.indexes i
JOIN sys.tables t ON t.object_id = i.object_id
JOIN sys.schemas s ON s.schema_id = t.schema_id
JOIN sys.index_columns ic
    ON ic.object_id = i.object_id AND ic.index_id = i.index_id
JOIN sys.columns c
    ON c.object_id = ic.object_id AND c.column_id = ic.column_id
WHERE i.is_primary_key = 1;
"""

SQL_FK = """
SELECT
    s.name AS table_schema,
    t.name AS table_name,
    c.name AS column_name,
    rs.name AS ref_schema,
    rt.name AS ref_table,
    rc.name AS ref_column
FROM sys.foreign_key_columns fkc
JOIN sys.tables t ON t.object_id = fkc.parent_object_id
JOIN sys.schemas s ON s.schema_id = t.schema_id
JOIN sys.columns c
    ON c.object_id = fkc.parent_object_id
   AND c.column_id = fkc.parent_column_id
JOIN sys.tables rt ON rt.object_id = fkc.referenced_object_id
JOIN sys.schemas rs ON rs.schema_id = rt.schema_id
JOIN sys.columns rc
    ON rc.object_id = fkc.referenced_object_id
   AND rc.column_id = fkc.referenced_column_id;
"""


def _safe_str(value: object) -> str | None:
    """Normaliza None/NaN/'' para None; senão devolve string limpa."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    return s or None


def _md_cell(value: str | None) -> str:
    if not value:
        return "—"
    return value.replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def format_type(row) -> str:
    t = row.data_type
    n = row.max_length
    if t in ("char", "varchar", "binary", "varbinary"):
        return f"{t}({'MAX' if n == -1 else n})"
    if t in ("nchar", "nvarchar"):
        return f"{t}({'MAX' if n == -1 else n // 2})"
    if t in ("decimal", "numeric"):
        return f"{t}({row.precision},{row.scale})"
    if t in ("datetime2", "datetimeoffset", "time"):
        return f"{t}({row.scale})"
    return t


def render_db(
    db: str,
    tables: pd.DataFrame,
    columns: pd.DataFrame,
    pks: pd.DataFrame,
    fks: pd.DataFrame,
) -> str:
    pk_set = {
        (r.table_schema, r.table_name, r.column_name) for r in pks.itertuples()
    }
    fk_map = {
        (r.table_schema, r.table_name, r.column_name):
            f"FK → {r.ref_schema}.{r.ref_table}({r.ref_column})"
        for r in fks.itertuples()
    }

    cols_by_table: dict[tuple[str, str], pd.DataFrame] = {
        key: grp.sort_values("ordinal_position")
        for key, grp in columns.groupby(["table_schema", "table_name"])
    }

    out: list[str] = []
    out.append(f"# Dicionário de dados — {db}")
    out.append("")
    out.append(
        f"Gerado em {date.today().isoformat()}. "
        f"{len(tables)} objetos · {len(columns)} colunas."
    )
    out.append("")

    for t in tables.itertuples():
        schema, name = t.table_schema, t.table_name
        kind = "Tabela" if t.table_type == "BASE TABLE" else "View"
        meta = [kind]
        if pd.notna(t.row_count):
            n = int(t.row_count)
            meta.append(f"~{n:,} linhas".replace(",", "."))
        out.append(f"## {schema}.{name}")
        out.append("")
        out.append(" · ".join(meta))
        out.append("")
        desc = _safe_str(t.table_description)
        if desc:
            out.append(desc)
            out.append("")

        cols = cols_by_table.get((schema, name))
        if cols is None or cols.empty:
            out.append("_(sem colunas listadas)_")
            out.append("")
            continue

        out.append("| # | Coluna | Tipo | Null | Chave | Default | Descrição |")
        out.append("|---|--------|------|------|-------|---------|-----------|")
        for c in cols.itertuples():
            key_parts: list[str] = []
            if (schema, name, c.column_name) in pk_set:
                key_parts.append("PK")
            fk = fk_map.get((schema, name, c.column_name))
            if fk:
                key_parts.append(fk)
            if bool(c.is_identity):
                key_parts.append("IDENT")
            if bool(c.is_computed):
                key_parts.append("COMP")
            key = ", ".join(key_parts) or "—"
            null = "Y" if bool(c.is_nullable) else "N"
            default = _md_cell(_safe_str(c.column_default))
            description = _md_cell(_safe_str(c.column_description))
            out.append(
                f"| {c.ordinal_position} "
                f"| {c.column_name} "
                f"| {format_type(c)} "
                f"| {null} "
                f"| {key} "
                f"| {default} "
                f"| {description} |"
            )
        out.append("")
    return "\n".join(out) + "\n"


def render_index(rendered: dict[str, tuple[int, int]]) -> str:
    out = [
        "# Dicionários de dados",
        "",
        f"Gerado em {date.today().isoformat()}.",
        "",
        "| Banco | Objetos | Colunas | Arquivo |",
        "|-------|---------|---------|---------|",
    ]
    for db, (n_tab, n_col) in rendered.items():
        out.append(f"| {db} | {n_tab} | {n_col} | [{db}.md]({db}.md) |")
    return "\n".join(out) + "\n"


def _load_existing_index(out_dir: Path) -> dict[str, tuple[int, int]]:
    """Lê contadores (objetos, colunas) dos .md já gerados no diretório."""
    result: dict[str, tuple[int, int]] = {}
    for md_file in sorted(out_dir.glob("*.md")):
        if md_file.name == "INDEX.md":
            continue
        db_name = md_file.stem
        # Primeira linha: "# Dicionário de dados — <db>"
        # Segunda linha não vazia: "Gerado em ... X objetos · Y colunas."
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        n_obj = n_col = 0
        for line in text.splitlines():
            # "Gerado em 2026-05-21. 490 objetos · 3802 colunas."
            m = re.search(r"(\d+)\s+objetos\s+·\s+(\d+)\s+colunas", line)
            if m:
                n_obj, n_col = int(m.group(1)), int(m.group(2))
                break
        result[db_name] = (n_obj, n_col)
    return result


def dump_db(db: str, out_dir: Path) -> tuple[int, int]:
    print(f"[{db}] consultando metadados…")
    engine = get_connection(db)
    try:
        tables = run_query_df(SQL_TABLES, conn=engine)
        columns = run_query_df(SQL_COLUMNS, conn=engine)
        pks = run_query_df(SQL_PK, conn=engine)
        fks = run_query_df(SQL_FK, conn=engine)
    finally:
        engine.dispose()

    md = render_db(db, tables, columns, pks, fks)
    out_path = out_dir / f"{db}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"[{db}] {len(tables)} objetos · {len(columns)} colunas → {out_path}")
    return len(tables), len(columns)


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Diretório de saída (default: scripts/analise/dicionario_dados/).",
    )
    parser.add_argument(
        "--dbs",
        nargs="+",
        default=list(DEFAULT_DBS),
        help=f"Bancos a documentar (default: {' '.join(DEFAULT_DBS)}).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    args.out.mkdir(parents=True, exist_ok=True)

    summary: dict[str, tuple[int, int]] = {}
    for db in args.dbs:
        try:
            summary[db] = dump_db(db, args.out)
        except Exception as exc:
            print(f"[{db}] FALHOU: {exc}")

    if summary:
        # Preserva entradas de rodadas anteriores que já têm .md no diretório.
        merged: dict[str, tuple[int, int]] = _load_existing_index(args.out)
        merged.update(summary)  # rodada atual sobrepõe entradas antigas do mesmo banco
        index_path = args.out / "INDEX.md"
        index_path.write_text(render_index(merged), encoding="utf-8")
        print(f"Index → {index_path}")


if __name__ == "__main__":
    main()
