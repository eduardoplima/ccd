"""Parser fixed-width dos extratos .txt do BB."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

_DATE_PATTERN = re.compile(r"^\s{2,4}\d{2}/\d{2}/\d{4}")
_VALOR_PATTERN = re.compile(r"([\d.,]+)\s*([CD])")


def parse_extrato(filepath: str | Path) -> pd.DataFrame:
    """Lê um extrato MMYYYY.txt do BB e devolve as linhas de Lançamento como DataFrame.

    Encoding latin-1 é obrigatório (acentos não passam em utf-8). O bloco de lançamentos
    fica entre o header `Dt. movimento` e o próximo separador `----------`. Linhas-cabeça
    de transação começam com `\\s{2,4}\\d{2}/\\d{2}/\\d{4}`; demais não-vazias são
    continuação da `descricao` da transação anterior. Campos extraídos por posição fixa
    em linha padded para 160 caracteres.
    """
    with open(filepath, "r", encoding="latin-1") as f:
        lines = f.readlines()

    in_lancamentos = False
    raw_lines: list[str] = []
    for line in lines:
        if "Dt. movimento" in line:
            in_lancamentos = True
            continue
        if in_lancamentos:
            if line.strip().startswith("----------"):
                break
            raw_lines.append(line.rstrip("\n"))

    records: list[dict] = []
    for line in raw_lines:
        if not line.strip():
            continue
        if _DATE_PATTERN.match(line):
            records.append({"raw": line, "descricao": ""})
        elif records:
            records[-1]["descricao"] = line.strip()

    parsed: list[dict] = []
    for ordem, rec in enumerate(records, start=1):
        raw = rec["raw"].ljust(160)

        valor: float | None = None
        valor_dc = ""
        m = _VALOR_PATTERN.search(raw[100:131])
        if m:
            valor = float(m.group(1).replace(".", "").replace(",", "."))
            valor_dc = m.group(2)

        parsed.append({
            "ordem_no_arquivo": ordem,
            "dt_movimento": raw[3:13].strip(),
            "dt_balancete": raw[13:30].strip(),
            "ag_origem": raw[30:44].strip(),
            "lote": raw[44:58].strip(),
            "historico": raw[58:90].strip(),
            "documento": raw[90:114].strip(),
            "valor": valor,
            "valor_dc": valor_dc,
            "descricao": rec["descricao"],
        })

    return pd.DataFrame(parsed)
